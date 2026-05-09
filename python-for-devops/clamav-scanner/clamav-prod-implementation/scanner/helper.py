import boto3
import json
import subprocess
import os
import logging

aws_region = os.getenv("AWS_REGION", "ap-south-1")
sqs = boto3.client("sqs", region_name=aws_region)
s3 = boto3.client("s3", region_name=aws_region)
ses = boto3.client("ses", region_name=aws_region)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def read_sqs_queue(queue_url):
    response = sqs.receive_message(
        QueueUrl=queue_url,
    )

    try:
        message = response.get("Messages", [])[0]
        body = json.loads(message.get("Body"))
        bucket = body["Records"][0]["s3"]["bucket"]["name"]
        key = body["Records"][0]["s3"]["object"]["key"]

    except IndexError:
        logging.warning("No messages in the queue")

    try:
        return bucket, key, f"s3://{bucket}/{key}", message.get("ReceiptHandle")
    except UnboundLocalError:
        logging.warning("No messages in the queue")
        return None, None, None, None


def delete_message_from_queue(queue_url, receipt_handle):
    sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)


def download_file_from_landing_s3(landing_bucket, object_key, download_path):
    logging.info(f"Downloading s3://{landing_bucket}/{object_key} to {download_path}")
    try:
        s3.download_file(landing_bucket, object_key, download_path)
    except Exception as e:
        logging.error(f"Error downloading file from S3: {e}")


def upload_file_to_clean_s3(clean_bucket, object_key, file_path):
    logging.info(f"Uploading {file_path} to s3://{clean_bucket}/{object_key}")
    try:
        s3.upload_file(file_path, clean_bucket, object_key)
    except Exception as e:
        logging.error(f"Error uploading file to S3: {e}")
        raise e


def create_tags(scan_result):
    if scan_result == "Clean":
        return [
            {"Key": "Status", "Value": "Clean"},
            {"Key": "Scaned", "Value": "true"},
        ]
    else:
        return [
            {"Key": "Status", "Value": "Infected"},
            {"Key": "Scaned", "Value": "true"},
        ]


def tag_file_in_s3(bucket, key, tags):
    s3.put_object_tagging(
        Bucket=bucket,
        Key=key,
        Tagging={
            "TagSet": [{"Key": tag["Key"], "Value": tag["Value"]} for tag in tags]
        },
    )


def scan_file_with_antivirus(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    result = subprocess.run(["clamscan", file_path], capture_output=True)

    if result.returncode == 0:
        return "Clean"
    else:
        return "Infected"


def notify_email(file_path, from_email, to_email):
    ses.send_email(
        Source=from_email,
        Destination={
            "ToAddresses": to_email,
        },
        Message={
            "Subject": {
                "Data": f"File {file_path} has been scanned",
            },
            "Body": {
                "Text": {
                    "Data": f"File {file_path} has been scanned and found virus, please check the file and upload the clean file.",
                },
                "Html": {
                    "Data": f"<h1> {file_path} file is infected </h1>",
                },
            },
        },
    )