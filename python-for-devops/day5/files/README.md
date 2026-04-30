# Stock Trades Ingestion: S3 → Lambda → RDS Postgres → SES

Drop a CSV in S3, Lambda parses it, writes to Postgres, emails a summary.

## Files

| File | Purpose |
|---|---|
| `lambda_function.py` | Lambda handler |
| `requirements.txt` | Python deps (psycopg2-binary) |
| `stock_trades_2026-04-30.csv` | Sample 50-row CSV for testing |
| `generate_csv.py` | Regenerate the sample CSV |

## CSV schema

```
trade_id, trade_timestamp, ticker, side, quantity, price,
trader_id, exchange, commission, trade_value
```

- `side` must be `BUY` or `SELL`
- `trade_timestamp` format: `YYYY-MM-DD HH:MM:SS`
- `trade_id` is the natural key (deduplication via `ON CONFLICT DO NOTHING`)

## DB schema (auto-created on first run)

- `stock_trades` — one row per trade, PK on `trade_id`
- `ingestion_log` — one row per S3 file processed (audit trail)
- Indexes: `(ticker, trade_timestamp)`, `trader_id`, daily date index

## Deployment

### 1. Package

```bash
mkdir package
pip install -r requirements.txt -t package/
cp lambda_function.py package/
cd package && zip -r ../lambda.zip . && cd ..
```

Upload `lambda.zip` to your Lambda. Runtime: **Python 3.12**, handler: `lambda_function.lambda_handler`.

> **Note on `psycopg2-binary` and Lambda:** the wheel from PyPI is built for the
> platform you `pip install` from. If you install on macOS and deploy to Lambda
> (Linux x86_64), it will fail at import. Use one of:
> - `pip install --platform manylinux2014_x86_64 --target package --only-binary=:all: -r requirements.txt`
> - Or build inside a Linux container / CodeBuild
> - Or use the [AWS-maintained psycopg2 layer](https://github.com/jkehler/awslambda-psycopg2)

### 2. Networking (this trips most people up)

- Lambda **must** be in the same VPC as RDS (or a peered one)
- Attach Lambda to **private subnets** (it needs a NAT for S3/SES, OR add S3/Secrets Manager/SES VPC endpoints)
- RDS security group: allow inbound **5432 from the Lambda security group**
- Lambda security group: allow outbound 443 (S3, SES, Secrets) and 5432 (RDS)

### 3. IAM role

Attach to the Lambda execution role:

- `AWSLambdaVPCAccessExecutionRole` (managed)
- Inline policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::YOUR_BUCKET/trades/*"
    },
    {
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue"],
      "Resource": "arn:aws:secretsmanager:ap-south-1:ACCOUNT:secret:rds-trades-*"
    },
    {
      "Effect": "Allow",
      "Action": ["ses:SendEmail", "ses:SendRawEmail"],
      "Resource": "*"
    }
  ]
}
```

### 4. Environment variables

| Key | Example | Required |
|---|---|---|
| `DB_HOST` | `trades.xxxx.ap-south-1.rds.amazonaws.com` | yes |
| `DB_PORT` | `5432` | no |
| `DB_NAME` | `trades` | yes |
| `DB_USER` | `trades_app` | yes |
| `DB_SECRET_ARN` | `arn:aws:secretsmanager:...:secret:rds-trades-AbCdEf` | yes (or `DB_PASSWORD`) |
| `DB_SSLMODE` | `require` | no (default `require`) |
| `SES_SENDER` | `noreply@livingdevops.com` (must be verified) | yes |
| `SES_RECIPIENT` | `you@livingdevops.com,ops@livingdevops.com` | yes |
| `SES_REGION` | `ap-south-1` | no (defaults to Lambda region) |
| `EXPECTED_PREFIX` | `trades/` | no (extra safety check) |

Tune Lambda config:
- **Memory**: 512 MB (1024 if files are large)
- **Timeout**: 60s (more if your CSVs are big)
- **VPC**: yes, attach private subnets

### 5. S3 trigger

On the bucket → Properties → Event notifications → Create event:
- Event types: `s3:ObjectCreated:*`
- Prefix: `trades/`
- Suffix: `.csv`
- Destination: this Lambda

### 6. Test locally with the sample CSV

```bash
aws s3 cp stock_trades_2026-04-30.csv s3://YOUR_BUCKET/trades/
# Watch CloudWatch Logs, check Postgres:
#   SELECT COUNT(*) FROM stock_trades;
#   SELECT * FROM ingestion_log ORDER BY id DESC LIMIT 5;
```

## Design notes

- **Idempotent**: re-uploading the same CSV is safe — `ON CONFLICT (trade_id) DO NOTHING`.
  The email will show `inserted=0, skipped=N`.
- **Row-level fault tolerance**: a single bad row is logged and counted as `failed`,
  the rest of the file still loads. Schema-level errors (missing columns, etc.) abort the file.
- **Connection reuse**: the Postgres connection and Secrets Manager password are
  cached at module scope, so warm invocations skip those round-trips.
- **No RDS Proxy**: for higher concurrency or many small files,
  put RDS Proxy in front of the DB so you don't exhaust connections.
- **Email failures don't fail the pipeline** — they're logged but the function still returns success.

## Common gotchas

1. **Lambda hangs / times out** → almost always VPC/SG issue. Check the SG inbound rule on RDS.
2. **`No module named 'psycopg2._psycopg'`** → wrong-platform wheel. See packaging note above.
3. **SES `MessageRejected: Email address is not verified`** → in SES sandbox, both sender AND recipient must be verified, or move out of sandbox.
4. **Lambda can't reach S3 from VPC** → add a NAT gateway, or (cheaper) an S3 Gateway endpoint on the VPC.
