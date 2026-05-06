from helper import delete_ec2_instance  
from helper import get_ec2_instance_id



def lambda_handler(event, context):
    print(f"Event: {event}")
    print(f"Context: {context}")

    instance_name = event['instance_name']  
    print(f"Terminating EC2 instance {instance_name}")
    response = delete_ec2_instance(get_ec2_instance_id(instance_name))
    print(f"Response: {response}")
    return {
        'statusCode': 200,
        'body': f"EC2 instance {instance_name} terminated successfully"
    }

# format of the event
# {
#     "instance_name": "test-instance"
# }