---
title: "Logs on Azure Storage"
meta_title: "Azure Storage"
meta_description: "Using Azure Storage to organize your jobs, builds, and experiment logs. Polyaxon allows users to manage all logs generated by jobs, builds, and experiments containers in Azure Storage."
custom_excerpt: "Azure Storage is Microsoft's cloud storage solution. Azure Storage provides storage for data objects that is highly available, secure, durable, massively scalable cloud storage solution."
image: "../../content/images/integrations/azure-storage.png"
author:
  name: "Polyaxon"
  slug: "Polyaxon"
  website: "https://polyaxon.com"
  twitter: "polyaxonAI"
  github: "polyaxon"
tags: 
  - logging
  - storage
featured: false
visibility: public
status: published
---

## Create an Azure Storage account

You should create a storage account (e.g. plx-storage) and a blob (e.g. logs). 
You should then create a file with your access information json object, e.g. `az-key.json`. 
This file should include the following information:

```json
{ 
  "AZURE_ACCOUNT_NAME": "plx-storage",
  "AZURE_ACCOUNT_KEY": "your key",
  "AZURE_CONNECTION_STRING": "your connection string",
}
```

## Create a secret on Kubernetes

You should then create a secret with this access keys information on Kubernetes on the same namespace as Polyaxon deployment:

`kubectl create secret generic az-secret --from-file=az-secret.json=path/to/az-key.json -n polyaxon`

## Use the secret name and secret in your logs persistence definition

```yaml
persistence:
  logs:
    store: azure
    bucket: wasbs://[CONTAINER-NAME]@[ACCOUNT-NAME].blob.core.windows.net/
    secret: [SECRET-NAME]
    secretKey: [SECRET-KEY]
```

e.g.

```yaml
persistence:
  logs:
    store: azure
    bucket: wasbs://logs@account.blob.core.windows.net/
    secret: az-secret
    secretKey: az-secret.json
```
