from enum import Enum


class EventType(Enum):
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


class Event:
    etype: EventType
    directory: bool
    path: str
    receipt_handle: str

    def __init__(self, etype: EventType, directory: bool, path: str, receipt_handle: str):
        self.etype = etype
        self.path = path
        self.directory = directory
        self.receipt_handle = receipt_handle


class MappedAttributes:
    logical_path: str
    content_type: str
    relative_physical_path: str


class Mapping:
    physical: str
    logical: str
    content_type: str

    def __init__(self, physical, logical, content_type):
        self.physical = physical
        self.logical = logical
        self.content_type = content_type
