from .base_event import BaseEvent
from dataclasses import dataclass

@dataclass
class TurtleBaseEvent(BaseEvent):
    turtle_id: int


@dataclass
class NewTurtleConnectionEvent(TurtleBaseEvent):
    pass

@dataclass
class TurtleError(TurtleBaseEvent):
    message: None|str
    command: None|str

@dataclass
class TurtleNotifyMessage(TurtleBaseEvent):
    message: None|str

@dataclass
class TurtleInfoEvent(TurtleBaseEvent):
    position: None|dict
    direction: None|int
    fuel: None|int
    inventory: None|dict

@dataclass
class ItemInfoEvent(TurtleBaseEvent):
    slot: None|int
    name: None|str
    count: None|int
    max_count: None|int
    tags: None|dict

@dataclass
class BlockInfoEvent(TurtleBaseEvent):
    position: None|dict
    name: None|str
    tags: None|dict

@dataclass
class TurtleStateChangeEvent(TurtleBaseEvent):
    name: None|str
    value: None|str