import csv, boto3, os, random
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute.models import DiskCreateOption

# https://docs.microsoft.com/en-us/azure/virtual-machines/windows/python
# https://docs.microsoft.com/en-us/azure/virtual-machines/linux/create-vm-rest-api
# pip install azureml-sdk[notebooks]
# pip install azure.mgmt.compute

# fetch access id from OS environment variables to maintain security
ec2 = boto3.resource('ec2', aws_access_key_id=os.getenv('aws_access_key_id'), aws_secret_access_key=os.getenv('aws_secret_access_key'), aws_session_token=os.getenv('aws_session_token'), region_name='us-east-1')
SUBSCRIPTION_ID = os.getenv('subscription_id')
GROUP_NAME = 'setup'
LOCATION = 'eastus'

def get_credentials():
    credentials = ServicePrincipalCredentials(
        client_id = os.getenv('client_id'),
        secret = os.getenv('secret_id'), # be62a12b-2cad-49a1-a5fa-85f4f3156a7d
        tenant = os.getenv('tenant_id')
    )

    return credentials

def create_resource_group(resource_group_client):
    resource_group_params = { 'location':LOCATION }
    resource_group_result = resource_group_client.resource_groups.create_or_update(
        GROUP_NAME, 
        resource_group_params
    )

def create_availability_set(compute_client, av_name):
    avset_params = {
        'location': LOCATION,
        'sku': { 'name': 'Aligned' },
        'platform_fault_domain_count': 3
    }
    availability_set_result = compute_client.availability_sets.create_or_update(
        GROUP_NAME,
        av_name,
        avset_params
    )

def create_public_ip_address(network_client, ip_name):
    public_ip_addess_params = {
        'location': LOCATION,
        'public_ip_allocation_method': 'Dynamic'
    }
    creation_result = network_client.public_ip_addresses.create_or_update(
        GROUP_NAME,
        ip_name,
        public_ip_addess_params
    )

    return creation_result.result()

def create_vnet(network_client, vnet_name):
    vnet_params = {
        'location': LOCATION,
        'address_space': {
            'address_prefixes': ['10.0.0.0/16']
        }
    }
    creation_result = network_client.virtual_networks.create_or_update(
        GROUP_NAME,
        vnet_name,
        vnet_params
    )
    return creation_result.result()

def create_subnet(network_client, vnet_name, subnet_name):
    subnet_params = {
        'address_prefix': '10.0.0.0/24'
    }
    creation_result = network_client.subnets.create_or_update(
        GROUP_NAME,
        vnet_name,
        subnet_name,
        subnet_params
    )

    return creation_result.result()

def create_nic(network_client, nic_name, ip_name, vnet_name, subnet_name):
    subnet_info = network_client.subnets.get(
        GROUP_NAME, 
        vnet_name, 
        subnet_name
    )
    publicIPAddress = network_client.public_ip_addresses.get(
        GROUP_NAME,
        ip_name
    )
    nic_params = {
        'location': LOCATION,
        'ip_configurations': [{
            'name': 'myIPConfig',
            'public_ip_address': publicIPAddress,
            'subnet': {
                'id': subnet_info.id
            }
        }]
    }
    creation_result = network_client.network_interfaces.create_or_update(
        GROUP_NAME,
        nic_name,
        nic_params
    )

    return creation_result.result()

#Ubuntu Server 16.04 LTS, Red Hat Enterprise Linux 7.4, and Debian 10 "Buster".
def create_vm(network_client, compute_client, nic_name, vm_name, vm_size, av_name, vm_type, vm_pub, vm_offer):  
    nic = network_client.network_interfaces.get(
        GROUP_NAME, 
        nic_name
    )
    avset = compute_client.availability_sets.get(
        GROUP_NAME,
        av_name
    )
    vm_parameters = {
        'location': LOCATION,
        'os_profile': {
            'computer_name': vm_name,
            'admin_username': 'azureuser',
            'admin_password': 'Azure12345678'
        },
        'hardware_profile': {
            'vm_size': vm_size
        },
        'storage_profile': {
            'image_reference': {
                'publisher': vm_pub,
                'offer': vm_offer,
                'sku': vm_type,
                'version': 'latest'
            }
        },
        'network_profile': {
            'network_interfaces': [{
                'id': nic.id
            }]
        },
        'availability_set': {
            'id': avset.id
        }
    }
    creation_result = compute_client.virtual_machines.create_or_update(
        GROUP_NAME, 
        vm_name, 
        vm_parameters
    )

    return creation_result.result()

class instance_obj:
    def __init__(self,platform,i_name,v_name,v_size,s,s_type,s_size,ssh):
        self.platform = platform
        self.i_name = i_name
        self.v_name = v_name
        self.v_size = v_size
        self.s = s
        self.s_type = s_type
        self.s_size = s_size
        self.ssh = ssh
    def ins_print(self):
        print("Platform: "+ self.platform)
        print("Instance Name:" + self.i_name)
        print("VM Name: " + self.v_name)
        print("VM Size: " + self.v_size)
        print("Storage?: " + self.s)
        print("Storage Type: " + self.s_type)
        print("Storage Size: " + self.s_size)
        print("SSH key: " + self.ssh)

class container_obj:
    def __init__(self,i_name,d_name,registry,background):
        self.i_name = i_name
        self.d_name = d_name
        self.registry = registry
        self.background = background
    def con_print(self):
        print("Instance Name: " + self.i_name)
        print("Docker Image Name: " + self.d_name)
        print("Registry: " + self.registry)
        print("Background: " + self.background)

def main():
    print ("Parsing preconditions...\n")

    # parse defined instances based on instance input file
    with open('instances.csv') as csv_file:
        instances = []
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_num = 0
        for row in csv_reader:
            if line_num != 0: # do not parse first line, as this will include subtitles
                new_instance = instance_obj(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                instances.append(new_instance)
            line_num = line_num + 1

    # parse defined containers based on instance input file
    with open('containers.csv') as csv_file:
        containers = []
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_num = 0
        for row in csv_reader:
            if line_num != 0: # parse defined instances based on instance input file
                new_container = container_obj(row[0], row[1], row[2], row[3])
                containers.append(new_container)
            line_num = line_num + 1       

    credentials = get_credentials()
    
    for i in range(0, len(instances)):

        print (str(i) + ": "+instances[i].i_name.lower())
        imageID = 'empty'
        # determine imageID based on parsed instance type
        if '2018' in instances[i].i_name.lower():
            imageID = 'ami-0e2ff28bfb72a4e45'
        elif 'hat' in instances[i].i_name.lower():
            imageID = 'ami-0c322300a1dd5dc79'
        if 'sus' in instances[i].i_name.lower():
            imageID = 'ami-0df6cfabfbe4385b7'
        elif 'ubuntu' in instances[i].i_name.lower():
            imageID = 'ami-07ebfd5b3428b6f4d'
        else:
            imageID = 'ami-0a887e401f7654935'

        # logic for AWS deployment of a given instance
        if instances[i].platform.lower() == "aws":
            # https://blog.ipswitch.com/how-to-create-an-ec2-instance-with-python


            # create a file to store the key locally
            outfile = open(instances[i].ssh,'w')
            sshkey = instances[i].ssh.split(".")[0]

            # call the boto ec2 function to create a key pair
            key_pair = ec2.create_key_pair(KeyName=sshkey)

            # capture the key and store it in a file
            KeyPairOut = str(key_pair.key_material)
            outfile.write(KeyPairOut)

            # create appropriate chmod command for the given instance
            chmodcommand = "chmod 400 " + instances[i].ssh
           
            # print to console the creation of the AWS instance
            print("Creating VM " + instances[i].v_name + " on AWS...")
            print(imageID)
            
            # create the AWS instance in the cloud
            ec2.create_instances(
                ImageId=imageID,
                MinCount=1,
                MaxCount=1,
                InstanceType=instances[i].v_size,
                KeyName=sshkey
            )
            
            #randhex = ""
            #for r in range(0,17):
            #    randhex = randhex + random.choice('0123456789abcdef')

            #command = "aws ec2 create-instance --image-id "+ imageID + " --count 1 --instance-type " + instances[i].v_size + " --key-name "+ sshkey + " --name \"" + instances[i].v_name +"\" --instance-id i-" + randhex
            #os.system(command)

        # logic for Azure deployment of a given instance
        elif instances[i].platform.lower() == "azure":

            #define associated resources
            resource_group_client = ResourceManagementClient(
                credentials,
                SUBSCRIPTION_ID
            )

            network_client = NetworkManagementClient(
                credentials,
                SUBSCRIPTION_ID
            )
            compute_client = ComputeManagementClient(
                credentials,
                SUBSCRIPTION_ID
            )

            # define instance variables with appropriate prefix
            vm_name = instances[i].v_name
            ip_name = "ip-"+vm_name
            nic_name = "nic-"+vm_name
            vnet_name = "vnet-"+vm_name
            subnet_name = "subnet-"+vm_name
            av_name = "av-"+vm_name

            # define additional constatns for Ubuntu OS
            if instances[i].i_name.lower() == 'ubuntu' or instances[i].i_name.lower() == 'ubuntu server 16.04 lts' or instances[i].i_name.lower() == '16.04-lts':
                vm_type = '16.04-LTS'
                vm_pub = 'Canonical'
                vm_offer = 'UbuntuServer'

            # print to console the creation of the Azure VM instance and its associated resource as each is created

            print("Fetching Resource group for " + vm_name + " on azure...")
            creation_result = create_resource_group(resource_group_client)

            print("Creating availability set for " + vm_name + " on azure...")
            creation_result2 = create_availability_set(compute_client, av_name)

            print("Creating public ip address for " + vm_name  + " on azure...")
            creation_result3 = create_public_ip_address(network_client, ip_name)

            print("Creating pvirtual network for " + vm_name + " on azure...")
            creation_result4 = create_vnet(network_client, vnet_name)

            print("Creating subnet for " + vm_name + " on azure...")
            creation_result5 = create_subnet(network_client, vnet_name, subnet_name)

            print("Creating network interface for " + vm_name + " on azure...")
            creation_result6 = create_nic(network_client, nic_name, ip_name, vnet_name, subnet_name)

            print("Creating virtual machine " + vm_name + " on azure...")
            vm = create_vm(network_client, compute_client, nic_name, vm_name, instances[i].v_size, av_name, vm_type, vm_pub, vm_offer)

if __name__ == "__main__":
    main()