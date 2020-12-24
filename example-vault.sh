#!/usr/bin/env bash

vault kv get -format json alfresco/env1  |jq ".data.data"

# Produces output similar to the following, providing the following data was stored in a hashicorp vault KV engine
# {
#  "password": "alskj230984213jwlspassword",
#  "url": "https://localhost:8443/alfresco",
#  "username": "myuser"
#}