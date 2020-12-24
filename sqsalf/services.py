import json
import logging
import subprocess
from typing import List, Dict

import boto3
import requests

from sqsalf.models import Event


class Alfresco:
    connection_script = None
    mapping: List[Dict] = None

    def __init__(self, connection_script):
        self.connection_script = connection_script

    def test_service(self):
        pass

    def get_connection(self) -> Dict:
        result = subprocess.run([self.connection_script], stdout=subprocess.PIPE)
        return json.loads(result.stdout.decode("utf-8"))

    def map_files(self, root_noderef:str, files: List) -> Dict:
        connection = self.get_connection()
        url = connection.get("url") + "/s/bulkobj/mapobjects/{root}?autoCreate=y".format(root=root_noderef)
        logging.info(files)
        response = requests.post(url, json=files,
                                 auth=(connection.get("username"), connection.get("password")), verify=False)
        logging.info(response)
        logging.info(response.text)


class SQS:
    sqs = None
    queue_url = None
    max_batch = None
    drop_others = None
    import_event = None
    event_structure = None

    def __init__(self, queue_url, max_batch, event_structure: Dict, import_event, drop_others):
        self.sqs = boto3.client('sqs')
        self.queue_url = queue_url
        self.max_batch = max_batch
        self.event_structure = event_structure
        self.import_event = import_event
        self.drop_others = drop_others

    def test_service(self):
        pass

    def receive_message(self):
        return self.sqs.receive_message(
            QueueUrl=self.queue_url,
            WaitTimeSeconds=10,
            MaxNumberOfMessages=10,
            VisibilityTimeout=15
        )

    def delete_messages(self, event_list: List[Event]):
        for e in event_list:
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=e.receipt_handle
            )
