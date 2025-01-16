from queue import Queue
from event import *


class MessageController:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.event_queue = Queue()
        self.server = None

    def send_message(self, turtle_id:int, message_type:str, data:dict|None) -> bool:
        if self.server is None:
            return False
        if turtle_id not in self.server.get_active_client_keys():
            return False
        return self.server.get_client(turtle_id).send_data(message_type, data)

    def broadcast_message(self, message_type:str, data:dict|None) -> set:
        if self.server is None:
            return set()
        message_sent = set()
        for turtle_id in self.server.get_active_client_keys():
            if self.server.get_client(turtle_id).send_data(message_type, data):
                message_sent.add(turtle_id)
        return message_sent

    def add_event(self, new_event:BaseEvent):
        self.event_queue.put(new_event)

    def get_event(self, block=True, timeout:float|None=None) -> BaseEvent:
        return self.event_queue.get(block, timeout)

    def get_events(self) -> list[BaseEvent]:
        events = []
        while self.has_event():
            events.append(self.event_queue.get())
        return events

    def has_event(self):
        return not self.event_queue.empty()
