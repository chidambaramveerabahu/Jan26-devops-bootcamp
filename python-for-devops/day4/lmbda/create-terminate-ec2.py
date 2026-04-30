import boto3

ec2 = boto3.client('ec2')

def create_ec2(instance_type, instance_name):
    response = ec2.run_instances(
        InstanceType=instance_type,
        ImageId='ami-0e12ffc2dd465f6e4',
    )
    return response

def terminate_ec2(instance_id):
    response = ec2.terminate_instances(
        InstanceIds=[instance_id]
    )
    return response