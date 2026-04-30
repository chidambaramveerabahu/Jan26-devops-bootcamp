"""
Lambda: Stock Trades CSV → RDS Postgres → SES notification

Trigger: S3 ObjectCreated event on the configured prefix.
Flow:
  1. Read S3 event, download CSV from S3
  2. Parse and validate rows
  3. Connect to RDS Postgres (over VPC)
  4. Create tables if not exist
  5. Bulk insert trades with idempotency (ON CONFLICT DO NOTHING on trade_id)
  6. Send SES email summary on success or failure

Environment variables (set on the Lambda):
  DB_HOST              - RDS endpoint (e.g. mydb.xxxx.ap-south-1.rds.amazonaws.com)
  DB_PORT              - default 5432
  DB_NAME              - database name
  DB_USER              - database user
  DB_SECRET_ARN        - Secrets Manager ARN holding {"password": "..."} (recommended)
                         OR set DB_PASSWORD directly (less secure, for dev only)
  SES_SENDER           - verified SES sender address
  SES_RECIPIENT        - recipient email (comma-separated for multiple)
  SES_REGION           - region for SES client (defaults to AWS_REGION)
  EXPECTED_PREFIX      - optional, validates S3 key starts with this prefix

Required IAM permissions:
  s3:GetObject on the source bucket/prefix
  secretsmanager:GetSecretValue on DB_SECRET_ARN
  ses:SendEmail
  VPC execution role (Lambda must be in the same VPC as RDS,
    with SG allowing 5432 from Lambda SG)
"""
import csv
import io
import json
import logging
import os
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import unquote_plus

import boto3
import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Reuse clients across invocations (warm starts)
_s3 = boto3.client("s3")
_secrets = boto3.client("secretsmanager")
_ses = boto3.client("ses", region_name=os.environ.get("SES_REGION") or os.environ.get("AWS_REGION"))

# Cache DB password and connection across warm invocations
_db_password_cache: str | None = None
_conn = None


# ---------- Schema ----------

DDL_TRADES = """
CREATE TABLE IF NOT EXISTS stock_trades (
    trade_id          VARCHAR(64)    PRIMARY KEY,
    trade_timestamp   TIMESTAMP      NOT NULL,
    ticker            VARCHAR(16)    NOT NULL,
    side              VARCHAR(8)     NOT NULL CHECK (side IN ('BUY', 'SELL')),
    quantity          INTEGER        NOT NULL CHECK (quantity > 0),
    price             NUMERIC(14, 4) NOT NULL CHECK (price > 0),
    trader_id         VARCHAR(32)    NOT NULL,
    exchange          VARCHAR(16)    NOT NULL,
    commission        NUMERIC(14, 4) NOT NULL DEFAULT 0,
    trade_value       NUMERIC(18, 4) NOT NULL,
    source_s3_key     VARCHAR(1024),
    ingested_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);
"""

DDL_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_trades_ticker_ts ON stock_trades (ticker, trade_timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_trades_trader ON stock_trades (trader_id);",
    "CREATE INDEX IF NOT EXISTS idx_trades_date ON stock_trades ((trade_timestamp::date));",
]

DDL_INGESTION_LOG = """
CREATE TABLE IF NOT EXISTS ingestion_log (
    id              BIGSERIAL PRIMARY KEY,
    s3_bucket       VARCHAR(255) NOT NULL,
    s3_key          VARCHAR(1024) NOT NULL,
    rows_total      INTEGER NOT NULL,
    rows_inserted   INTEGER NOT NULL,
    rows_skipped    INTEGER NOT NULL,
    rows_failed     INTEGER NOT NULL,
    status          VARCHAR(16) NOT NULL,
    error_message   TEXT,
    started_at      TIMESTAMPTZ NOT NULL,
    finished_at     TIMESTAMPTZ NOT NULL
);
"""

INSERT_SQL = """
INSERT INTO stock_trades (
    trade_id, trade_timestamp, ticker, side, quantity, price,
    trader_id, exchange, commission, trade_value, source_s3_key
) VALUES %s
ON CONFLICT (trade_id) DO NOTHING;
"""

REQUIRED_COLUMNS = {
    "trade_id", "trade_timestamp", "ticker", "side",
    "quantity", "price", "trader_id", "exchange",
    "commission", "trade_value",
}


# ---------- DB helpers ----------

def _get_db_password() -> str:
    """Fetch password from Secrets Manager, or fall back to env var."""
    global _db_password_cache
    if _db_password_cache:
        return _db_password_cache

    secret_arn = os.environ.get("DB_SECRET_ARN")
    if secret_arn:
        resp = _secrets.get_secret_value(SecretId=secret_arn)
        secret = json.loads(resp["SecretString"])
        _db_password_cache = secret["password"]
    else:
        pw = os.environ.get("DB_PASSWORD")
        if not pw:
            raise RuntimeError("Neither DB_SECRET_ARN nor DB_PASSWORD is set")
        _db_password_cache = pw
    return _db_password_cache


def _get_conn():
    """Get a Postgres connection, reusing across warm invocations."""
    global _conn
    if _conn is not None and _conn.closed == 0:
        try:
            with _conn.cursor() as cur:
                cur.execute("SELECT 1;")
            return _conn
        except psycopg2.Error:
            logger.warning("Stale DB connection, reconnecting")
            try:
                _conn.close()
            except Exception:
                pass
            _conn = None

    _conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "5432")),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=_get_db_password(),
        connect_timeout=10,
        # RDS supports sslmode=require; use it whenever possible
        sslmode=os.environ.get("DB_SSLMODE", "require"),
    )
    _conn.autocommit = False
    return _conn


def _ensure_schema(conn) -> None:
    """Create tables and indexes if they don't exist. Idempotent."""
    with conn.cursor() as cur:
        cur.execute(DDL_TRADES)
        for stmt in DDL_INDEXES:
            cur.execute(stmt)
        cur.execute(DDL_INGESTION_LOG)
    conn.commit()
    logger.info("Schema ensured")


# ---------- Parsing ----------

def _parse_row(row: dict, line_no: int) -> tuple | None:
    """Validate one CSV row and convert to a tuple ready for insertion.
    Returns None if the row is invalid (logged, counted as failed)."""
    try:
        # Validate side
        side = (row["side"] or "").strip().upper()
        if side not in ("BUY", "SELL"):
            raise ValueError(f"invalid side: {side!r}")

        ts = datetime.strptime(row["trade_timestamp"].strip(), "%Y-%m-%d %H:%M:%S")
        quantity = int(row["quantity"])
        if quantity <= 0:
            raise ValueError("quantity must be > 0")

        price = Decimal(row["price"])
        if price <= 0:
            raise ValueError("price must be > 0")

        commission = Decimal(row.get("commission") or "0")
        trade_value = Decimal(row["trade_value"])

        return (
            row["trade_id"].strip(),
            ts,
            row["ticker"].strip().upper(),
            side,
            quantity,
            price,
            row["trader_id"].strip(),
            row["exchange"].strip().upper(),
            commission,
            trade_value,
            None,  # source_s3_key, filled in by caller
        )
    except (KeyError, ValueError, InvalidOperation) as e:
        logger.warning("Row %d invalid: %s | row=%s", line_no, e, row)
        return None


def _parse_csv(body: bytes, s3_key: str) -> tuple[list[tuple], int, int]:
    """Parse the CSV body. Returns (valid_rows, total_seen, failed_count)."""
    text = body.decode("utf-8-sig")  # tolerate BOM
    reader = csv.DictReader(io.StringIO(text))

    # Validate header
    if reader.fieldnames is None:
        raise ValueError("CSV is empty or has no header")
    missing = REQUIRED_COLUMNS - set(reader.fieldnames)
    if missing:
        raise ValueError(f"CSV missing required columns: {sorted(missing)}")

    valid: list[tuple] = []
    total = 0
    failed = 0
    for i, row in enumerate(reader, start=2):  # line 1 is header
        total += 1
        parsed = _parse_row(row, i)
        if parsed is None:
            failed += 1
            continue
        # Replace placeholder with actual S3 key
        valid.append(parsed[:-1] + (s3_key,))
    return valid, total, failed


# ---------- Email ----------

def _send_email(subject: str, body_text: str, body_html: str | None = None) -> None:
    sender = os.environ.get("SES_SENDER")
    recipients = os.environ.get("SES_RECIPIENT", "")
    if not sender or not recipients:
        logger.warning("SES_SENDER/SES_RECIPIENT not set; skipping email")
        return

    to_addrs = [a.strip() for a in recipients.split(",") if a.strip()]
    message: dict[str, Any] = {
        "Subject": {"Data": subject, "Charset": "UTF-8"},
        "Body": {"Text": {"Data": body_text, "Charset": "UTF-8"}},
    }
    if body_html:
        message["Body"]["Html"] = {"Data": body_html, "Charset": "UTF-8"}

    try:
        _ses.send_email(
            Source=sender,
            Destination={"ToAddresses": to_addrs},
            Message=message,
        )
        logger.info("SES email sent to %s", to_addrs)
    except Exception as e:
        # Don't fail the whole pipeline if email fails — just log
        logger.exception("Failed to send SES email: %s", e)


def _build_email(
    bucket: str, key: str, total: int, inserted: int,
    skipped: int, failed: int, status: str, error: str | None,
) -> tuple[str, str, str]:
    subject = f"[Trades Ingest] {status}: s3://{bucket}/{key}"
    text = (
        f"Stock trades ingestion {status}\n\n"
        f"Source: s3://{bucket}/{key}\n"
        f"Rows total:    {total}\n"
        f"Rows inserted: {inserted}\n"
        f"Rows skipped:  {skipped} (duplicates)\n"
        f"Rows failed:   {failed} (validation errors)\n"
    )
    if error:
        text += f"\nError: {error}\n"
    html = f"""
    <html><body style="font-family:system-ui,sans-serif">
      <h2>Stock trades ingestion: {status}</h2>
      <p><b>Source:</b> <code>s3://{bucket}/{key}</code></p>
      <table border="1" cellpadding="6" style="border-collapse:collapse">
        <tr><td>Rows total</td><td>{total}</td></tr>
        <tr><td>Rows inserted</td><td>{inserted}</td></tr>
        <tr><td>Rows skipped (duplicates)</td><td>{skipped}</td></tr>
        <tr><td>Rows failed (validation)</td><td>{failed}</td></tr>
      </table>
      {f'<p style="color:#b00"><b>Error:</b> {error}</p>' if error else ''}
    </body></html>
    """
    return subject, text, html


# ---------- Main handler ----------

def lambda_handler(event, context):
    """Process each S3 record in the event."""
    results = []
    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])
        results.append(_process_object(bucket, key))
    return {"statusCode": 200, "body": json.dumps(results)}


def _process_object(bucket: str, key: str) -> dict:
    started = datetime.utcnow()
    expected_prefix = os.environ.get("EXPECTED_PREFIX")
    if expected_prefix and not key.startswith(expected_prefix):
        logger.info("Skipping %s (does not match EXPECTED_PREFIX=%s)", key, expected_prefix)
        return {"key": key, "status": "skipped_prefix"}

    if not key.lower().endswith(".csv"):
        logger.info("Skipping non-CSV object: %s", key)
        return {"key": key, "status": "skipped_not_csv"}

    logger.info("Processing s3://%s/%s", bucket, key)
    total = inserted = skipped_dup = failed = 0
    status = "SUCCESS"
    error_msg: str | None = None

    try:
        # 1. Download
        obj = _s3.get_object(Bucket=bucket, Key=key)
        body = obj["Body"].read()
        logger.info("Downloaded %d bytes", len(body))

        # 2. Parse
        rows, total, failed = _parse_csv(body, key)
        logger.info("Parsed: total=%d valid=%d failed=%d", total, len(rows), failed)

        # 3. Connect + ensure schema
        conn = _get_conn()
        _ensure_schema(conn)

        # 4. Insert (chunked, in a single transaction)
        if rows:
            with conn.cursor() as cur:
                # rowcount after execute_values reflects how many rows were
                # actually inserted (ON CONFLICT skips count as 0).
                execute_values(cur, INSERT_SQL, rows, page_size=500)
                inserted = cur.rowcount if cur.rowcount >= 0 else 0
            skipped_dup = len(rows) - inserted
            conn.commit()
        logger.info("Inserted=%d Skipped(dup)=%d Failed=%d", inserted, skipped_dup, failed)

    except Exception as e:
        status = "FAILED"
        error_msg = f"{type(e).__name__}: {e}"
        logger.exception("Processing failed for s3://%s/%s", bucket, key)
        try:
            if _conn is not None:
                _conn.rollback()
        except Exception:
            pass

    finished = datetime.utcnow()

    # Best-effort: log the run to ingestion_log
    try:
        conn = _get_conn()
        _ensure_schema(conn)
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO ingestion_log
                   (s3_bucket, s3_key, rows_total, rows_inserted, rows_skipped,
                    rows_failed, status, error_message, started_at, finished_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (bucket, key, total, inserted, skipped_dup, failed,
                 status, error_msg, started, finished),
            )
        conn.commit()
    except Exception:
        logger.exception("Could not write ingestion_log entry")

    # Email summary
    subject, text, html = _build_email(
        bucket, key, total, inserted, skipped_dup, failed, status, error_msg,
    )
    _send_email(subject, text, html)

    return {
        "key": key, "status": status, "total": total,
        "inserted": inserted, "skipped": skipped_dup, "failed": failed,
        "error": error_msg,
    }
