import logging
import os
import time
from typing import List

import yaml

from sqsalf.converters import message_to_event, event_to_content_obj, mapping_from_config
from sqsalf.models import Event, EventType
from sqsalf.services import Alfresco, SQS


class MapCreated:
    config = None
    acs: Alfresco = None
    sqs: SQS = None

    def __init__(self, config_file: str):
        if not os.path.exists(config_file):
            raise Exception("Config File {file} does not exist!".format(file=config_file))
        with open(config_file, "r") as yml_file:
            self.config = yaml.load(yml_file.read(), Loader=yaml.FullLoader)

        self.acs = Alfresco(connection_script=self.config.get("alfresco").get("connection_script"))
        self.sqs = SQS(queue_url=self.config.get("sqs_url"), max_batch=self.config.get("max_batch"),
                       event_structure=self.config.get("event"), import_event=self.config.get("import_event"),
                       drop_others=self.config.get("drop_other_events"))

    def map(self):
        batch_content_list = []
        batch_event_list = []
        sleep_seconds = float(self.config.get("sleep_seconds", 10))
        while True:
            messages = self.sqs.receive_message().get("Messages")
            if messages:
                event_structure = self.config.get("event")
                event_list: List[Event] = list(filter(lambda e: e,
                                                      map(lambda x: message_to_event(event_structure, x),
                                                          messages)))
                created_events = list(filter(lambda x: x.etype == EventType.CREATED and not x.directory, event_list))
                content_list = list(
                    map(lambda x: event_to_content_obj(x, mapping_from_config(self.config.get("mappings"))),
                        created_events))
                batch_content_list = batch_content_list + content_list
                batch_event_list = batch_event_list + event_list
                if len(batch_content_list) > 100:
                    self.save(batch_content_list, batch_event_list)
                    batch_content_list = []
                    batch_event_list = []
                    time.sleep(sleep_seconds)
            else:
                self.save(batch_content_list, batch_event_list)
                batch_content_list = []
                batch_event_list = []

    def save(self, batch_content_list, batch_event_list):
        try:
            if len(batch_content_list) > 0:
                self.acs.map_files(self.config.get("alfresco").get("root_noderef"), batch_content_list)
            if len(batch_event_list) > 0:
                self.sqs.delete_messages(batch_event_list)
        except Exception as e:
            logging.error("Couldn't map files")
            logging.error(e)
