from .base_event import BaseEvent
from dataclasses import dataclass

@dataclass
class ClientBaseEvent(BaseEvent):
    turtle_id: int


@dataclass
class NewTurtleConnectionEvent(ClientBaseEvent):
    pass

@dataclass
class TurtleInfoEvent(ClientBaseEvent):
    position: None|dict
    direction: None|int
    fuel: None|int
    inventory: None|dict

@dataclass
class ItemInfoEvent(ClientBaseEvent):
    slot: None|int
    name: None|str
    count: None|int
    max_count: None|int
    tags: None|dict