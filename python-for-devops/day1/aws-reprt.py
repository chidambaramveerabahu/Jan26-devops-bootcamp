# get the aws resoiurces in here
import boto3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--regions', nargs='+', type=str, help='List of items')
parser.add_argument("--services", nargs='+', type=str, help='List of items')


def list_ec2_instances(region):
    ec2 = boto3.client('ec2', region_name=region )
    ec2_data = ec2.describe_instances()["Reservations"]
    instances = []
    for items in ec2_data:
        instance_id = items["Instances"][0]["InstanceId"]
        state = items["Instances"][0]["State"]["Name"]
        instances.append([region, instance_id, state])
    return instances

args = parser.parse_args()
# region = args.region list type
# services = args.services


# if len(args.regions) > 0:
#     for region in args.regions:
#         print(f"EC2 instances in region {region}:")
#         print(list_ec2_instances(region))


def accumulate_ec2_data():
    ec2_data = []
    if len(args.regions) > 0:
        for region in args.regions:
            ec2_data.extend(list_ec2_instances(region))
    else:
        print("Provide regions ")

    return ec2_data
        
    
print(accumulate_ec2_data())