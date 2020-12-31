# Description
This service listens in on an Amazon SQS queue for filesystem events,
and acts upon the CREATE events, while discarding the others.

The create events will then be used to invoke the Alfresco Professional Services Bulk File System Importer
for asynchronous ingestion.


# Pre-Requisites
* Python 3.8
* SQS Queue where events are published in the following format
```json
{
  "event_type": "modified|created|deleted|moved",
  "is_directory": true,
  "src_path": "/path/to/stuff/teststuff"
}
```

# Installation
* Create a Python Virtual Environment for execution
* Install install into virtual environment
```shell
python3 -m venv myenv
source myenv/bin/activate
cd sqs-bom-alfresco
pip3 install .
# verify that it works
sqs-alfresco -h
```


# Configure
Create a configuration file based on the config-example.yaml
## Yaml Config
```yaml
---
sqs_url: https://sqs.us-east-1.amazonaws.com/accountid/queue

  # unmarshalling the json event from SQS
  # Example would be an event created from in this format:
  # {
  #  "event_type": "modified",
#  "is_directory": false,
#  "src_path": "/path/to/alf_data/contentstore/inplace/CCF11162015.pdf"
#}
event:
  type: event_type
  directory: is_directory
  path: src_path

import_event: created
drop_other_events: true # clean up the queue for other events like modified, etc. (since inplace import. it's important there are no deletes, etc.)
max_batch: 100
sleep_seconds: 10

alfresco:
  url: https://your.alfresco.com/alfresco
  # Return a json username and password statically, or from vault
  # example: echo '{ "username": "user", "password": "passwd" }'
  username_password_script: ./example-vault.sh

```
## Create an executable shell script to get the username and password
`example-vault.sh`
```shell
#!/usr/bin/env bash
VAULT_ADDR=http://localhost:9400
vault kv get -format json alfresco/env1  |jq ".data.data"

# Produces output similar to the following, providing the following data was stored in a hashicorp vault KV engine
# {
#  "password": "alskj230984213jwlspassword",
#  "url": "https://localhost:8443/alfresco",
#  "username": "myuser"
#}
```

# Invoke
`sqs-alfresco -c config-example.yaml`
Logging will be found in a file `sqs-alfresco.log`