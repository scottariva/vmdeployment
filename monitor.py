import csv, boto3, os
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute.models import DiskCreateOption

SUBSCRIPTION_ID = os.getenv('subscription_id')
GROUP_NAME = 'setup'
LOCATION = 'eastus'
VM_NAME = 'myVM-test1'
ec2 = boto3.client('ec2', aws_access_key_id=os.getenv('aws_access_key_id'), aws_secret_access_key=os.getenv('aws_secret_access_key'), aws_session_token=os.getenv('aws_session_token'), region_name='us-east-1')

def main():
    print ("AWS Instances running and pending")
    # https://www.slsmk.com/how-to-use-python-boto3-to-list-instances-in-amazon-aws/

    # fetch appropriate VM instances from retruned reservations from ec2
    response = ec2.describe_instances()
    for instances in response["Reservations"]:
        for instance in instances["Instances"]:
            # only display running or pending VMs
            if instance["State"]["Name"] == 'running' or instance["State"]["Name"] == 'pending':
                # print appropriate VM OS based on the Image ID
                if instance["ImageId"] == 'ami-07ebfd5b3428b6f4d':
                    print ('Ubuntu server 18.04 LTS, InstanceID: '+instance["InstanceId"])
                elif instance["ImageId"] == 'ami-0df6cfabfbe4385b7':
                    print ('Suse Linux Enterprise Server 15 SP1, InstanceID: '+instance["InstanceId"])
                elif instance["ImageId"] == 'ami-0c322300a1dd5dc79':
                    print ('Red Hat Enterprise Linux 8, InstanceID: '+instance["InstanceId"])
                elif instance["ImageId"] == 'ami-0e2ff28bfb72a4e45':
                    print ('Amazon Linux AMI 2018.03.0, InstanceID: '+instance["InstanceId"])
                elif instance["ImageId"] == 'ami-0a887e401f7654935':
                    print ('Amazon Linux 2 AMI, InstanceID: '+instance["InstanceId"])


if __name__ == "__main__":
    main()