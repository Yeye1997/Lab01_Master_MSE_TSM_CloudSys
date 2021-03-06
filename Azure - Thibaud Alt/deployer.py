"""A deployer class to deploy a template on Azure"""

import base64
import os.path
import json
from haikunator import Haikunator
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
# from azure.mgmt.resource.resources.models import DebugSetting

class Deployer(object):
    """ Initialize the deployer class with subscription, resource group and public key.

    :raises IOError: If the public key path cannot be read (access or not exists)
    :raises KeyError: If AZURE_CLIENT_ID, AZURE_CLIENT_SECRET or AZURE_TENANT_ID env
        variables or not defined
    """
    name_generator = Haikunator()

    def __init__(self, subscription_id, resource_group, pub_ssh_key_path='~/.ssh/id_rsa.pub'):
        self.subscription_id = subscription_id
        self.resource_group = resource_group

        pub_ssh_key_path = os.path.expanduser(pub_ssh_key_path)
        # Will raise if file not exists or not enough permission
        with open(pub_ssh_key_path, 'r') as pub_ssh_file_fd:
            self.pub_ssh_key = pub_ssh_file_fd.read()

        self.credentials = ServicePrincipalCredentials(
            client_id=os.environ['AZURE_CLIENT_ID'],
            secret=os.environ['AZURE_CLIENT_SECRET'],
            tenant=os.environ['AZURE_TENANT_ID']
        )
        self.client = ResourceManagementClient(self.credentials, self.subscription_id)

        # DebugSetting("requestContent, responseContent")

    def deploy(self, template_path, name, publicIp = False):
        """Deploy the template to a resource group."""
        self.dns_label_prefix = self.name_generator.haikunate()
        self.client.resource_groups.create_or_update(
            self.resource_group,
            {
                'location': 'switzerlandnorth'
            }
        )

        with open(template_path, 'r') as template_file_fd:
            template = json.load(template_file_fd)

        if publicIp :
            parameters = {
                'sshKeyData': self.pub_ssh_key,
                'dnsLabelPrefix': self.dns_label_prefix
            }
        else :
            parameters = {}

        parameters = {k: {'value': v} for k, v in parameters.items()}

        deployment_properties = {
            'mode': DeploymentMode.incremental,
            'template': template,
            'parameters': parameters
        }

        if name == "guacapache" :
            with open("config/guac-init.txt", "rb") as cloud_init:
                deployment_properties["customData"] = base64.b64encode(cloud_init.read())

        deployment_async_operation = self.client.deployments.create_or_update(
            self.resource_group,
            'azure-' + name,
            deployment_properties
        )
        deployment_async_operation.wait()

    def destroy(self):
        """Destroy the given resource group"""
        self.client.resource_groups.delete(self.resource_group)
