from .base_event import BaseEvent
from dataclasses import dataclass

@dataclass
class CommandDisconnected(BaseEvent):
    pass