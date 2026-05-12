import boto3

# job is to fetch the sqs queue and kms data
# import helper

# region = "ap-south-1"

# queue_data = helper.get_sqs_with_kms_key(region)


from helper import get_sqs_with_kms_key

region = "ap-south-1"
queue_data = get_sqs_with_kms_key(region)
print(queue_data)