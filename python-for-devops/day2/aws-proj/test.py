import boto3

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

    
# tupe_1 =('asd', 'dfg')
# print(tupe_1[0])




# list_sqs_queues("ap-south-1")

# ['https://sqs.ap-south-1.amazonaws.com/879381241087/clamav-notify', 'https://sqs.ap-south-1.amazonaws.com/879381241087/queue-with-customerkms', 'https://sqs.ap-south-1.amazonaws.com/879381241087/sqs-without-customer-kms']


region = "ap-south-1"
# queue_url = "https://sqs.ap-south-1.amazonaws.com/879381241087/clamav-notify"

# print(get_queue_attributes(region, queue_url))
print(get_sqs_with_kms_key(region))