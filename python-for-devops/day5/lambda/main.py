"""
Lambda: S3 CSV -> RDS Postgres -> SES email
Dumb version with verbose logging.
"""
import csv
import io
import os
import boto3
import psycopg2

print("=== Lambda cold start ===")
print(f"AWS_REGION       = {os.environ.get('AWS_REGION')}")
print(f"DB_HOST          = {os.environ.get('DB_HOST')}")
print(f"DB_NAME          = {os.environ.get('DB_NAME')}")
print(f"DB_USER          = {os.environ.get('DB_USER')}")
print(f"DB_PASSWORD set? = {bool(os.environ.get('DB_PASSWORD'))}")
print(f"SES_SENDER       = {os.environ.get('SES_SENDER')}")
print(f"SES_RECIPIENT    = {os.environ.get('SES_RECIPIENT')}")

s3 = boto3.client("s3")
ses = boto3.client("ses")
print("Boto3 clients created")


def lambda_handler(event, context):
    print("=" * 60)
    print(">>> lambda_handler START")
    print(f"Event: {event}")

    # 1. Get the file info from the S3 event
    print("\n--- Step 1: Read S3 event ---")
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    print(f"Bucket: {bucket}")
    print(f"Key:    {key}")
    print(f"Source: s3://{bucket}/{key}")

    # 2. Download the CSV from S3
    print("\n--- Step 2: Download CSV from S3 ---")
    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj["Body"].read().decode("utf-8")
    print(f"Downloaded {len(body)} bytes")
    print(f"First 200 chars: {body[:200]!r}")

    # 3. Parse the CSV into a list of rows
    print("\n--- Step 3: Parse CSV ---")
    reader = csv.DictReader(io.StringIO(body))
    print(f"CSV columns: {reader.fieldnames}")
    rows = []
    for row in reader:
        parsed = (
            row["trade_id"],
            row["trade_timestamp"],
            row["ticker"],
            row["side"],
            int(row["quantity"]),
            float(row["price"]),
            row["trader_id"],
            row["exchange"],
            float(row["commission"]),
            float(row["trade_value"]),
        )
        rows.append(parsed)
        print(f"  Parsed row {len(rows)}: {parsed}")
    print(f"Total parsed rows: {len(rows)}")

    # 4. Connect to Postgres
    print("\n--- Step 4: Connect to Postgres ---")
    print(f"Connecting to {os.environ['DB_HOST']}:5432 db={os.environ['DB_NAME']} user={os.environ['DB_USER']}")
    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=5432,
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )
    cur = conn.cursor()
    print("Connection established")

    # 5. Create the table if it doesn't exist
    print("\n--- Step 5: Create table if not exists ---")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_trades (
            trade_id VARCHAR(64) PRIMARY KEY,
            trade_timestamp TIMESTAMP,
            ticker VARCHAR(16),
            side VARCHAR(8),
            quantity INTEGER,
            price NUMERIC,
            trader_id VARCHAR(32),
            exchange VARCHAR(16),
            commission NUMERIC,
            trade_value NUMERIC
        );
    """)
    print("CREATE TABLE executed")

    # 6. Insert the rows
    print("\n--- Step 6: Insert rows ---")
    for i, row in enumerate(rows, 1):
        cur.execute("""
            INSERT INTO stock_trades
            (trade_id, trade_timestamp, ticker, side, quantity, price,
             trader_id, exchange, commission, trade_value)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (trade_id) DO NOTHING;
        """, row)
        print(f"  Inserted row {i}/{len(rows)} (trade_id={row[0]}, rowcount={cur.rowcount})")

    conn.commit()
    print(f"Committed {len(rows)} insert statements")

    # 7. Read back from the table to include in email
    print("\n--- Step 7: SELECT * from stock_trades ---")
    cur.execute("SELECT * FROM stock_trades ORDER BY trade_timestamp DESC;")
    db_rows = cur.fetchall()
    col_names = [desc[0] for desc in cur.description]
    print(f"SELECT returned {len(db_rows)} rows")
    print(f"Columns: {col_names}")

    # Build a plain-text table for the email
    header_line = " | ".join(col_names)
    separator = "-" * len(header_line)
    body_lines = [header_line, separator]
    for r in db_rows:
        body_lines.append(" | ".join(str(c) for c in r))
    table_text = "\n".join(body_lines)
    print("--- Table preview (first 500 chars) ---")
    print(table_text[:500])
    print("--- end preview ---")

    cur.close()
    conn.close()
    print("DB connection closed")

    # 8. Send an email with the SELECT result
    print("\n--- Step 8: Send SES email ---")
    email_body = (
        f"Loaded {len(rows)} rows from {key} into stock_trades.\n\n"
        f"Current contents of stock_trades ({len(db_rows)} rows):\n\n"
        f"{table_text}\n"
    )
    print(f"Email body length: {len(email_body)} chars")
    print(f"Sending from {os.environ['SES_SENDER']} to {os.environ['SES_RECIPIENT']}")
    resp = ses.send_email(
        Source=os.environ["SES_SENDER"],
        Destination={"ToAddresses": [os.environ["SES_RECIPIENT"]]},
        Message={
            "Subject": {"Data": f"Trades loaded: {key}"},
            "Body": {"Text": {"Data": email_body}},
        },
    )
    print(f"SES MessageId: {resp.get('MessageId')}")

    print("\n>>> lambda_handler DONE")
    print("=" * 60)
    return {"status": "ok", "inserted_rows": len(rows), "table_rows": len(db_rows)}



event= {'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'ap-south-1', 'eventTime': '2026-04-30T18:22:05.035Z', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'A168SSCSJWRKEO'}, 'requestParameters': {'sourceIPAddress': '122.161.53.4'}, 'responseElements': {'x-amz-request-id': 'Z55ZJRXM1TJRM2GN', 'x-amz-id-2': 'BRZlNCSD73h2mB94beb5cI5InWf77jG+sF4EELFjVSURBd2BMQJ2dYUxQh9HBJKaMNerbtjnpK0Er5ZnWmiWhg1642XiGL2294iqH+A2D2g='}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': 'c5754f5f-fe0a-4e8d-a3c7-9a5a4812ec9c', 'bucket': {'name': 'clean-bucket-879381241087', 'ownerIdentity': {'principalId': 'A168SSCSJWRKEO'}, 'arn': 'arn:aws:s3:::clean-bucket-879381241087'}, 'object': {'key': 'stock_trades_2026-04-30.csv', 'size': 4318, 'eTag': '9139a00c633d4fe1278e87815a9e9b60', 'sequencer': '0069F39DCD03DD7028'}}}]}
lambda_handler(event, "context")