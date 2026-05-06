import boto3

ec2 = boto3.client('ec2', region_name="ap-south-1")
ami_id = 'ami-0e12ffc2dd465f6e4'
# crete ec2 instance with a certain name and type
def create_ec2(instance_type, instance_name):
    response = ec2.run_instances(
        InstanceType=instance_type,
        ImageId=ami_id,
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': instance_name}]
            }
        ]
    )
    return response 


# create_ec2("t2.micro", "test-instance")


# function to get ec2 instance id with a certain instance name (tag name)
def get_ec2_instance_id(instance_name):
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Name', 'Values': [instance_name]}
        ]
    )
    return response.get('Reservations', [])[0].get('Instances', [])[0].get('InstanceId')
   

# print(get_ec2_instance_id("test-instance"))

# delete ec2 instance with a certain instance id
def delete_ec2_instance(instance_id):
    response = ec2.terminate_instances(
        InstanceIds=[instance_id]
    )
    return response

# print(delete_ec2_instance(get_ec2_instance_id("test-instance")))

