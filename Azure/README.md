# Guacamole - Azure Deploy
## Configuration

You will need to copy the .env.sample file to .env file and complete the following variables :

- AZURE_TENANT_ID = _Your tenant id_
- AZURE_CLIENT_ID = _Your client id_
- AZURE_CLIENT_SECRET = _Your client secret_
- AZURE_SUBSCRIPTION_ID = _Your subscription id_

More instructions here : https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal#get-application-id-and-authentication-key

## Run
To run, you need python (and install requirements) and then execute :

`python guacamole_deploy.py`

## Problèmes rencontrés
- J'ai passé plusieurs heures à chercher pourquoi 2 de mes machines étaient déployées mais pas la 3e ... pour enfin trouver l'erreur suivante : "operation could not be completed as it results in exceeding approved standardbsfamily cores quota". J'ai finalement pu résoudre l'erreur en modifiant le "vmSize" d'une de mes machines.
- Bien que la doc de Microsoft soit clair, le débuggage et notamment la recherche d'erreur est très peu explicite.
- La définiiton des templates JSON devient très vite indigeste, j'ai passé beaucoup de temps à formatter, debugguer, paramétrer...

###### Inspired from :
https://docs.microsoft.com/en-us/samples/azure-samples/resource-manager-python-template-deployment/resource-manager-python-template-deployment/
