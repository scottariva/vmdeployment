# vmdeployment
VM Deployment and Monitoring

CIS 4010 - Cloud Computing
By Scott Riva

This assignment is tasked with the monitoring and deployment of cloud based VMs via Microsoft Azure and AWS.
Utilizing CSV files as input, the system will be able to dynamic deploy VMs to Azure or AWS based on user credentials
The program will create the VM itself as well as any other resource dependencies for the appropriate OS and hosting service
The progrma can also be used to monitor the existing VMs on your cloud subscriptions directly from the terminal

Access Tokens

In order to utilize these scripts, you will need to input your cloud credentials in your Operating System Environment Variables. This is done to ensure privacy and security of data, and not requiring the credentials to be directly included in the code.

You will want to set: 
- AWS access key as "aws_access_key_id"
- AWS secret key as "aws_secret_access_key"
- AWS session token as "aws_session_token"
- Azure secret key as "azure_secret_id"
- Azure client key as "azure_client_id"
- Azure tenant key as "azure_tenant_id"

In addition you will need to input your desired containers and instances within containers.csv and instances.csv

Containers.csv

Each container will include 4 variables as defined by the included sample file
Instance Name - the defined name for your instance
Docker image Name - the name of your docker image
Registry - Your VM defined container registry
Background (Y or N) - Input "Y" or "N" to have your container run in the background or not

Instances.csv

Each instance will include 8 variables as defined by the included sample file
Platform - input "Azure" or "AWS" for the respective cloud service
Instance Name - input the instance operating system name. Supports "Ubuntu server 18.04 LTS", "Suse Linux Enterprise Server 15 SP1", "Red Hat Enterprise Linux 8", "Amazon Linux AMI 2018.03.0", and "Amazon Linux 2 AMI"
VM Name - will be your defined name for the virtual machine
Storage (Y or N) - input "Y" or "N" to include additional storage
Storage type - input a defined storage type as defined by the cloud service
Storage size - input a defined storage size as defined by the cloud service
SSH Key file name - input a file name to store the ssh key for this vm, the file will be created and does not need to exist prior

Deploy.py

Running deploy.py will automatically trigger its logic to create and deploy the appropriate containers and instances based on the input provided in containers.csv and instances.csv

Monitor.py

Running mointor.py will automatically trigger its logic to display existing VMs to the terminal based on the cloud credentials