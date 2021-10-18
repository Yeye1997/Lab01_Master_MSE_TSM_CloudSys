# Guacamole - SwitchEngine OpenStack Deploy
## Configuration

You will need :

- The OpenStack SDK : pip install openstacksdk
- Check installed version : python -m openstack version
- Adapt the clouds.yaml from your provider

More instructions here : https://docs.openstack.org/openstacksdk/xena/user/guides/intro.html
And here ... : https://docs.openstack.org/openstacksdk/xena/user/config/configuration.html

## Run
To run, you need python and then execute :

`python DaaS.py`

You can now enter some information if you want.

## Problèmes rencontrés
- Quelques limitation au niveau du support et des forums. Je n'ai pas trouver beaucoup d'information à part dans la documentation officielle d'OpenStack. 
- Les exemples donnés ne sont pas très complet et peu suffisant pour le travail demandé
- La gestion des cloud init n'est pas super bien intégrée avec OpenStackSDK

