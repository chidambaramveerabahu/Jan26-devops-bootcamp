from helper import delete_ec2_instance  
from helper import get_ec2_instance_id


instance_data = {
    'instance_name': "test-instance"
}

def lambda_handler(event, context):
    instance_name = instance_data['instance_name']
    delete_ec2_instance(get_ec2_instance_id(instance_name))
    return {
        'statusCode': 200,
        'body': f"EC2 instance {instance_name} terminated successfully"
    }
