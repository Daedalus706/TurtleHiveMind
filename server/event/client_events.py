from .base_event import BaseEvent
from dataclasses import dataclass

@dataclass
class ClientBaseEvent(BaseEvent):
    turtle_id: int


@dataclass
class NewTurtleEvent(ClientBaseEvent):
    position: dict
    direction: int