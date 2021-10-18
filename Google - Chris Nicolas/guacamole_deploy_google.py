import argparse
import os
import time

from pprint import pprint

import googleapiclient.discovery
from six.moves import input

project='steady-bonsai-326707'
zone='europe-west6-a'

# [START list_instances]
def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else None
# [END list_instances]

# [START create_instance]
def create_instance(compute, project, zone, name, image, network, region, script, external_ip):
    # Find image
    if("ubuntu" in image):
       image_request = compute.images().get(project='ubuntu-os-cloud', image=image)
    else:
       image_request = compute.images().get(project=project, image=image)
    image_response = image_request.execute()
    source_disk_image = image_response['selfLink']

    #Find network
    network_request = compute.subnetworks().get(project=project, region=region, subnetwork=network)
    network_response = network_request.execute()
    network_instance = network_response['selfLink']

    # Configure the machine
    machine_type = "zones/%s/machineTypes/e2-micro" % zone
    
    if(script != '' and image == 'mysql'):
       startup_script = open(
        os.path.join(
            os.path.dirname(__file__), script), 'r').read()
       config = {
        'name': name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'subnetwork': network_instance
        }],

        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],

        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [{
                # Startup script is automatically executed by the
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script
            }]
        }
    }
    elif(external_ip == 'yes' and image=='guacamole'):
       startup_script = open(
        os.path.join(
            os.path.dirname(__file__), script), 'r').read()
       config = {
        'name': name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'subnetwork': network_instance,
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],
        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [{
                # Startup script is automatically executed by the
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script
            }]
        }

    }
 
    else:
        config = {
        'name': name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'subnetwork': network_instance
        }],

        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }]

    }



    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()
# [END create_instance]

# [START wait_for_operation]
def wait_for_operation(compute, project, zone, operation):
    print('Waiting for operation to finish...')
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)
# [END wait_for_operation]

compute = googleapiclient.discovery.build('compute', 'v1')


# deploy desktop
image = 'ubuntu-2004-focal-v20210927'
instance_name='desktop'
network='lan'
region='europe-west6'
script=''
external_ip='no'
operation = create_instance(compute, project, zone, instance_name, image, network, region, script, external_ip)
wait_for_operation(compute, project, zone, operation['name'])

request = compute.instances().get(project=project, zone=zone, instance=instance_name)
response = request.execute()

desktop_ip = response['networkInterfaces'][0]['networkIP']

# deploy mysql
image='mysql'
instance_name='mysql'
script='mysql.sh'
f = open(script, "w")
f.write("sudo mysql guacamole_db -e \"UPDATE guacamole_connection_parameter SET parameter_value ='" + desktop_ip + "' WHERE connection_id = 1 AND parameter_name = 'hostname';\"")
f.close()
operation = create_instance(compute, project, zone, instance_name, image, network, region, script, external_ip)
wait_for_operation(compute, project, zone, operation['name'])

request = compute.instances().get(project=project, zone=zone, instance=instance_name)
response = request.execute()

mysql_ip = response['networkInterfaces'][0]['networkIP']

# deploy guacamole
image='guacamole'
instance_name='guacamole'
script='guacamole.sh'
external_ip='yes'
f = open(script, "w")
f.write("sudo echo \"guacd-hostname: localhost \nguacd-port: 4822\nmysql-hostname: " + mysql_ip + "\nmysql-port: 3306\nmysql-database: guacamole_db\nmysql-username: guacamole_user\nmysql-password: heia\" > /etc/guacamole/guacamole.properties")
f.close()
operation = create_instance(compute, project, zone, instance_name, image, network, region, script, external_ip)
wait_for_operation(compute, project, zone, operation['name'])


request = compute.instances().get(project=project, zone=zone, instance=instance_name)
response = request.execute()

# set tag (firewall rule)
tags_body = {
    "fingerprint": response['tags']['fingerprint'],
    "items": ["guacamole-lan" ]
}

request = compute.instances().setTags(project=project, zone=zone, instance=instance_name, body=tags_body)
response = request.execute()

