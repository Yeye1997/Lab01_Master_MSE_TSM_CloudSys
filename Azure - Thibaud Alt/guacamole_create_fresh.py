import os.path
from deployer import Deployer
from dotenv import load_dotenv

# This script expects that the following environment vars are setted in .env file
#
# - AZURE_TENANT_ID: with your Azure Active Directory tenant id or domain
# - AZURE_CLIENT_ID: with your Azure Active Directory Application Client ID
# - AZURE_CLIENT_SECRET: with your Azure Active Directory Application Secret

load_dotenv() # Load the environment variables from the .env file

my_subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID')
my_resource_group = 'TSM-CloudSys-Labo01-New' # the resource group for deployment
my_pub_ssh_key_path = os.path.expanduser('~/.ssh/id_rsa.pub') # the path to your rsa public key file

msg = "\nInitializing the Deployer class with subscription id: {}, resource group: {} \nand public key located at: {}...\n\n"
msg = msg.format(my_subscription_id, my_resource_group, my_pub_ssh_key_path)
print(msg)

# Initialize the deployer class
deployer = Deployer(my_subscription_id, my_resource_group, my_pub_ssh_key_path)

try:

    print("Beginning deployments: \n")

    parameters = {
        'sshKeyData': self.pub_ssh_key,
        'dnsLabelPrefix': self.dns_label_prefix
    }

    # Deploy Guacamole Desktop
    print(" - Deploying Guacamole Desktop...")
    guacamole_template_path = os.path.join(os.path.dirname(__file__), 'templates/new', 'guacamole.json')
    guacamole_deployment = deployer.deploy(guacamole_template_path, 'guacamole', parameters)
    print("   => Done deploying Guacamole! You can connect via: `ssh guacamole@{}.switzerlandnorth.cloudapp.azure.com`\n".format(deployer.dns_label_prefix))

    # Deploy GuacApache
    print(" - Deploying Guacamole Apache...")
    apache_template_path = os.path.join(os.path.dirname(__file__), 'templates/new', 'apache.json')
    apache_deployment = deployer.deploy(apache_template_path, 'guacapache', parameters)
    print("   => Done deploying Guacamole Apache! You can connect via: `ssh guacamole@{}.switzerlandnorth.cloudapp.azure.com`\n".format(deployer.dns_label_prefix))

    # Deploy GuacMySQL
    print(" - Deploying Guacamole MySQL...")
    mysql_template_path = os.path.join(os.path.dirname(__file__), 'templates/new', 'mysql.json')
    mysql_deployment = deployer.deploy(mysql_template_path, 'guacmysql', parameters)
    print("   => Done deploying Guacamole MySQL! You can connect via: `ssh guacamole@{}.switzerlandnorth.cloudapp.azure.com`\n".format(deployer.dns_label_prefix))

    print("All deployements finished. \n\n")

except Exception as e:
    print(e)
    deployer.destroy() # On fail, destroy the resource group which contains the deployment
