import json
import boto3

sqs_queue_url = "https://sqs.ap-south-1.amazonaws.com/879381241087/clamav-scanner-queue"

sqs = boto3.client('sqs', region_name='ap-south-1')
s3 = boto3.client('s3', region_name='ap-south-1')
bucket_name = 'landing-bucket-879381241087'

def read_messages_from_sqs(sqs_queue_url ):
    response = sqs.receive_message(
        QueueUrl=sqs_queue_url,
    )
    return response.get('Messages', [])

def write_messages_to_sqs(messages):
    if isinstance(messages, dict):
        bodies = [json.dumps(messages)]
    else:
        bodies = [m['Body'] for m in messages if isinstance(m, dict) and 'Body' in m]
    for body in bodies:
        response = sqs.send_message(
            QueueUrl=sqs_queue_url,
            MessageBody=body,
        )
        print(response)

def get_object_key_from_message(message):
    return json.loads(message.get("Body")).get("Records")[0].get("s3").get("object").get("key")

def delete_message_from_queue(message):
    sqs.delete_message(
        QueueUrl=sqs_queue_url,
        ReceiptHandle=message['ReceiptHandle']
    )

def download_object_from_s3(object_key):
    s3.download_file(bucket_name, object_key, "file_to_scan")
    

# message = read_messages_from_sqs(sqs_queue_url )
# object_key = get_object_key_from_message(message)
# print(object_key)
# downloaded_file = download_object_from_s3(object_key)
# delete_message_from_queue(message)



if __name__ == "__main__":
    # messages = {'file_path': 'test.txt', 'file_name': 'test.txt'}
    # write_messages_to_sqs(messages)

    messages = read_messages_from_sqs(sqs_queue_url)
    # print(messages)
    # delete the message from the queue
    for message in messages:
        delete_message_from_queue(message)


    # message = read_messages_from_sqs()[0]
    # print(json.loads(message.get("Body")).get("Records")[0].get("s3").get("object").get("key"))
    