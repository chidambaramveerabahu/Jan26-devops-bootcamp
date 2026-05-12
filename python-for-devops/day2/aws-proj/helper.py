import boto3
from datetime import datetime, timezone

def list_ec2_instances(region):
    ec2 = boto3.client('ec2', region_name=region )
    ec2_data = ec2.describe_instances()["Reservations"]
    instances = []
    for items in ec2_data:
        instance_id = items["Instances"][0]["InstanceId"]
        state = items["Instances"][0]["State"]["Name"]
        instances.append([region, instance_id, state])
    return instances


def age_in_days(date):
    if date is None:
        return None
    return f'{(datetime.now(timezone.utc) - date).days}-days'

def list_secretmanegr_secrets(region):
    secretsmanager = boto3.client('secretsmanager', region_name=region )
    response = secretsmanager.list_secrets()

    # print(response.get("SecretList", [])[0].get('Name'))
    # print(len(response.get("SecretList", [])))
    secret_list_data = response.get("SecretList", [])
    for items in secret_list_data:
        name = items.get('Name')
        LastAccessedDate = items.get('LastAccessedDate')
        create_date = items.get('CreatedDate')

        print(name, age_in_days(LastAccessedDate), age_in_days(create_date))


def list_sqs_queues(region):
    sqs = boto3.client('sqs', region_name=region )
    response = sqs.list_queues()
    queue_urls = response.get('QueueUrls', [])
    print(queue_urls)
    
    
def get_queue_attributes(region, queue_url):
    sqs = boto3.client('sqs', region_name=region)
    response = sqs.get_queue_attributes(
        QueueUrl=queue_url,
         AttributeNames=[
        'KmsMasterKeyId'
         ])
    
    return response.get('Attributes', {}).get('KmsMasterKeyId', 'No KMS Key')

def get_sqs_with_kms_key(region):
    sqs = boto3.client('sqs', region_name=region)
    response = sqs.list_queues()
    queue_urls = response.get('QueueUrls', [])
    # queues_with_kms_key = []
    # # print(queue_urls)
    # for queue_url in queue_urls:
    #     # print(queue_url,get_queue_attributes(region, queue_url) )
    #     # print((queue_url, get_queue_attributes(region, queue_url)))

    #     queues_with_kms_key.append((queue_url, get_queue_attributes(region, queue_url)))

    # return queues_with_kms_key

    return [ (queue_url, get_queue_attributes(region, queue_url) ) for queue_url in queue_urls]
