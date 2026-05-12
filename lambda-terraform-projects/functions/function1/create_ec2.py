from helper import create_ec2

instance_data = {
    'instance_type': "t2.micro",
    'instance_name': "test-instance"
}

def lambda_handler(event, context):
    instance_type = instance_data['instance_type']
    instance_name = instance_data['instance_name']
    create_ec2(instance_type, instance_name)
    return {
        'statusCode': 200,
        'body': f"EC2 instance {instance_name} created successfully"
    }

# format of the event
# {
#     "instance_type": "t2.micro",
#     "instance_name": "test-instance"
# }