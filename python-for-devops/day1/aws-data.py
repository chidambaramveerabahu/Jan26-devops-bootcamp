# get the aws resoiurces in here
import boto3

# s3 = boto3.resource('s3')  # specify your region

# # Print out bucket names
# for bucket in s3.buckets.all():
#     print(bucket.name)


# ec2 = boto3.client('ec2')


# response = ec2.describe_instances()


# print(response["Reservations"][0]["Instances"][0]["InstanceId"])
# print(response["Reservations"][0]["Instances"][0]["State"]["Name"])

# print(response["Reservations"][1]["Instances"][0]["InstanceId"])
# print(response["Reservations"][1]["Instances"][0]["State"]["Name"])

# for reservation in response["Reservations"]:
#     print(reservation["Instances"][0]["InstanceId"])
#     print(reservation["Instances"][0]["State"]["Name"])



# data in this format
# [[instance_id, state], [instance_id, state], ...]


def list_ec2_instances(region):
    ec2 = boto3.client('ec2', region_name=region )
    ec2_data = ec2.describe_instances()["Reservations"]
    instances = []
    # print(f" before loop:   {instances}")  # this will print an empty list before the loop starts
    for items in ec2_data:
        instance_id = items["Instances"][0]["InstanceId"]
        state = items["Instances"][0]["State"]["Name"]
        # print(f'{instance_id} -> {state}')  # this will print the instance id and state in the format instance_id -> state
        instances.append([instance_id, state])
        # print(instances)  # this will print the list of instances with their state in the format [[instance_id, state], [instance_id, state], ...]
    # print(instances)
    return instances

print(list_ec2_instances("us-east-1"))  # this will print the list of instances with their state in the format [[instance_id, state], [instance_id, state], ...] for the specified region


