import boto3

# from helper import *
import helper
import os

# clean-bucket-879381241087 /tmp livingdevops@gmail.com ['abubaker.dev417@gmail.com', 'shivamshekhar960@gmail.com', 'aditiyamishranit@gmail.com'] https://sqs.ap-south-1.amazonaws.com/879381241087/clamav-notify

Queue_url = os.getenv("QUEUE_URL")
clean_bucket = os.getenv("CLEAN_BUCKET")
locals_path = os.getenv("LOCAL_PATH", "/tmp")
from_email = os.getenv("FROM_EMAIL")
to_email = os.getenv("TO_EMAIL").split(",") if os.getenv("TO_EMAIL") else []
aws_region = os.getenv("AWS_REGION", "ap-south-1")


def main(Queue_url):
    bucket, key, s3_path, receipt_handle = helper.read_sqs_queue(Queue_url)

    helper.download_file_from_landing_s3(bucket, key, f"{locals_path}/{key}")

    scan_result = helper.scan_file_with_antivirus(f"{locals_path}/{key}")
    if scan_result == "Clean":
        helper.tag_file_in_s3(bucket, key, helper.create_tags(scan_result))
        helper.upload_file_to_clean_s3(clean_bucket, key, f"{locals_path}/{key}")
    else:
        helper.tag_file_in_s3(bucket, key, helper.create_tags(scan_result))
        helper.notify_email(s3_path, from_email, to_email)

    helper.delete_message_from_queue(Queue_url, receipt_handle)


if __name__ == "__main__":
    main(Queue_url)