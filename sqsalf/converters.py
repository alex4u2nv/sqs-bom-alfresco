import json
from typing import Dict, List
import re

from sqsalf.models import Event, EventType, MappedAttributes, Mapping


def message_to_event(structure: Dict, message: Dict) -> Event:
    try:
        message_body = message.get("Body")
        message_json = json.loads(message_body)
        src_path = message_json.get(structure.get("path"))
        path_split = src_path.split("contentstore/")
        path = path_split[1] if len(path_split) == 2 else structure.get("path")
        return Event(
            etype=EventType(message_json.get(structure.get("type"))),
            directory=message_json.get(structure.get("directory")),
            path=path,
            receipt_handle=message.get("ReceiptHandle")
        )
    except Exception as e:
        return Event(
            etype=None,
            directory=False,
            path=None,
            receipt_handle=message.get("ReceiptHandle")
        )


def mapping_from_config(mapping: List[Dict]) -> List[Mapping]:
    return list(
        map(lambda x: Mapping(x.get("physical"), x.get("logical"), x.get("content_type")), mapping))


def get_mapping(event: Event, mappings: List[Mapping]) -> MappedAttributes:
    if event.path:
        for item in mappings:
            if event.path.startswith(item.physical):
                attr: MappedAttributes = MappedAttributes()
                attr.content_type = item.content_type
                attr.relative_physical_path = event.path.lstrip("/")
                attr.logical_path = re.sub("/+", "/", item.logical + "/" + event.path[len(item.physical):].lstrip("/"))
                return attr
    raise Exception("Path not found in  Not Specified")


def event_to_content_obj(event: Event, mappings: List[Mapping]) -> Dict:
    mapping = get_mapping(event, mappings)
    filename = mapping.logical_path.split("/")[-1:][0]
    path = "/".join(mapping.logical_path.split("/")[:-1])
    title = "".join(" ".join(filename.split("-")).split(".")[:-1]).title()
    return {
        "type": mapping.content_type,
        "path": path,
        "properties": {
            "cm:name": filename,
            "cm:title": title
        },
        "contentUrls": {
            "cm:content": "store://" + mapping.relative_physical_path
        }
    }
