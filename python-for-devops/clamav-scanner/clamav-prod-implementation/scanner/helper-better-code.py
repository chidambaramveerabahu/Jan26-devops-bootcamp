import boto3
import json
import subprocess
import os
import logging
from typing import Tuple, List

# Initialize AWS clients for SQS, S3, and SES services

aws_region = os.getenv("AWS_REGION", "ap-south-1")  # Default to ap-south-1 if not set
sqs = boto3.client("sqs", region_name=aws_region)
s3 = boto3.client("s3", region_name=aws_region)
ses = boto3.client("ses", region_name=aws_region)

# Configure logging with timestamp, log level, and message format
# Log levels in order of severity: debug < info < warning < error < critical
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
# level Info, warning, error, critical
# logging.info("This is an info message")
# logging.warning("This is a warning message")
# logging.error("This is an error message")
# logging.critical("This is a critical message")

# Configure AWS credentials from environment variables



# Initialize logger
logger = logging.getLogger(__name__)

def read_sqs_queue(queue_url: str) -> Tuple[str, str, str, str]:
    """
    Polls a single message from the SQS queue and extracts S3 event details.

    Args:
        queue_url: The URL of the SQS queue to read from.

    Returns:
        Tuple of (bucket_name, object_key, s3_uri, receipt_handle).
        Returns (None, None, None, None) if no messages are available.
    """
    response = sqs.receive_message(
        QueueUrl=queue_url,
    )

    try:
        # Extract first message from the response (SQS returns a list)
        message = response.get("Messages", [])[0]

        # Parse the message body — S3 event notification is JSON inside SQS body
        body = json.loads(message.get("Body"))

        # Navigate the S3 event structure to get bucket name and object key
        bucket = body["Records"][0]["s3"]["bucket"]["name"]
        key = body["Records"][0]["s3"]["object"]["key"]

    except IndexError:
        # Raised when 'Messages' list is empty — queue has no messages
        logging.warning("No messages in the queue")

    try:
        # Return extracted details + receipt handle needed to delete the message later
        return bucket, key, f"s3://{bucket}/{key}", message.get("ReceiptHandle")
    except UnboundLocalError:
        # Raised if bucket/key were never assigned (IndexError hit above)
        logging.warning("No messages in the queue")
        return None, None, None, None


def delete_message_from_queue(queue_url: str, receipt_handle: str) -> None:
    """
    Deletes a processed message from the SQS queue using its receipt handle.
    This must be called after successful processing to prevent reprocessing.

    Args:
        queue_url: The URL of the SQS queue.
        receipt_handle: Unique identifier for the message received from SQS.
    """
    sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)


def download_file_from_landing_s3(
    landing_bucket: str, object_key: str, download_path: str
) -> None:
    """
    Downloads a file from the landing (untrusted/incoming) S3 bucket to local disk
    so it can be scanned by ClamAV.

    Args:
        landing_bucket: Source S3 bucket name (landing zone).
        object_key: S3 object key (file path within the bucket).
        download_path: Local filesystem path to save the downloaded file.
    """
    logging.info(f"Downloading s3://{landing_bucket}/{object_key} to {download_path}")
    try:
        s3.download_file(landing_bucket, object_key, download_path)
    except Exception as e:
        logging.error(f"Error downloading file from S3: {e}")
        # raise e  # Re-raise to let the caller handle or halt execution


def upload_file_to_clean_s3(clean_bucket: str, object_key: str, file_path: str) -> None:
    """
    Uploads a scanned-clean file to the clean (trusted) S3 bucket.
    Only called when ClamAV confirms the file has no threats.

    Args:
        clean_bucket: Destination S3 bucket name (clean/trusted zone).
        object_key: S3 object key to use for the uploaded file.
        file_path: Local path of the file to upload.
    """
    logging.info(f"Uploading {file_path} to s3://{clean_bucket}/{object_key}")
    try:
        s3.upload_file(file_path, clean_bucket, object_key)
    except Exception as e:
        logging.error(f"Error uploading file to S3: {e}")
        raise e  # Re-raise to let the caller handle or halt execution


def create_tags(scan_result: str) -> List[dict]:
    """
    Generates S3 object tags based on the antivirus scan result.
    Tags are used to mark files for downstream processing or auditing.

    Args:
        scan_result: Either 'Clean' or 'Infected' from the scan function.

    Returns:
        List of tag dicts with 'Key' and 'Value' pairs.
    """
    if scan_result == "Clean":
        return [
            {"Key": "Status", "Value": "Clean"},
            {
                "Key": "Scaned",
                "Value": "true",
            },  # Note: typo in key — should be 'Scanned'
        ]
    else:
        return [
            {"Key": "Status", "Value": "Infected"},
            {
                "Key": "Scaned",
                "Value": "true",
            },  # Note: typo in key — should be 'Scanned'
        ]


def tag_file_in_s3(bucket: str, key: str, tags: List[dict]) -> None:
    """
    Applies a list of tags to an existing S3 object.
    Used to mark files as Clean/Infected after antivirus scanning.

    Args:
        bucket: S3 bucket containing the object.
        key: S3 object key to tag.
        tags: List of tag dicts (from create_tags).
    """
    s3.put_object_tagging(
        Bucket=bucket,
        Key=key,
        Tagging={
            # Build the TagSet list from our tag dicts
            "TagSet": [{"Key": tag["Key"], "Value": tag["Value"]} for tag in tags]
        },
    )


def scan_file_with_antivirus(file_path: str) -> str:
    """
    Scans a local file using ClamAV (clamscan) and returns the scan result.
    ClamAV must be installed on the host — see `brew install clamav` on Mac.

    Return codes from clamscan:
        0 = No threats found (Clean)
        1 = Virus found (Infected)
        2 = Error during scan

    Args:
        file_path: Local path to the file to scan.

    Returns:
        'Clean' if no threats found, 'Infected' otherwise.

    Raises:
        FileNotFoundError: If the file doesn't exist at the given path.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Run clamscan as a subprocess and capture its output
    result = subprocess.run(["clamscan", file_path], capture_output=True)

    if result.returncode == 0:
        return "Clean"
    else:
        # Covers both returncode 1 (infected) and 2 (scan error)
        return "Infected"


def notify_email(file_path: str, from_email: str, to_email: List[str]) -> None:
    """
    Sends an email alert via AWS SES when an infected file is detected.
    The sender email (from_email) must be verified in SES.

    Args:
        file_path: Path/name of the infected file (used in email subject/body).
        from_email: SES-verified sender email address.
        to_email: List of recipient email addresses.
    """
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
                # Plain text fallback for email clients that don't render HTML
                "Text": {
                    "Data": f"File {file_path} has been scanned and found virus, please check the file and upload the clean file.",
                },
                # HTML version of the email body — currently a placeholder, needs proper template
                "Html": {
                    "Data": "<h1> Akhilesh Mishra </h1>",
                },
            },
        },
    )