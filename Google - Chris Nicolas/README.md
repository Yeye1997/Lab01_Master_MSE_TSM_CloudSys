# Guacamole - Google Cloud Deploy
## Configuration

You will need to set an environment variable :

- GOOGLE_APPLICATION_CREDENTIALS
- For that you will need to create an API key and save it in JSON File

More instructions here : https://cloud.google.com/docs/authentication/getting-started

On the script "guacamole_deploy_google.py" you will need to set following variables:
- project='_project_' example: steady-bonsai-326707
- zone='_zone_'
- region='_region_'
 

## Run
To run, you need python (and install requirements) and then execute :

`python guacamole_deploy_google.py`

## Problèmes rencontrés
- L'interface et l'API de Google n'étaient pas très "user-friendly". J'ai donc perdu du temps à me familiariser avec.
- La documentation manquait parfois de précision concernant certains paramètres nécessaires et j'ai donc aussi perdu du temps.
- Pour passer les networks tags, il est nécessaire de passer le fingerprint précédant en paramètre. Comme l'API Google retournait plusieurs fingerprints, il m'a fallu trouvé le bon.
###### Inspired from :
https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/compute/api
