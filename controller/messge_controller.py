from queue import Queue


class MessageController:
    def __init__(self):
        self.event_queue = Queue()
        self.server = None

    def send_message(self, turtle_id:int, message_type:str, data:dict|None) -> bool:
        if turtle_id not in self.server.get_connection_keys():
            return False
        return self.server.get_connection(turtle_id).send_data(message_type, data)

    def broadcast_message(self, message_type:str, data:dict|None) -> set:
        message_sent = set()
        for turtle_id in self.server.get_connection_keys():
            if self.server.get_connection(turtle_id).send_data(message_type, data):
                message_sent.add(turtle_id)
        return message_sent

    def add_event(self, new_event):
        self.event_queue.put(new_event)

    def get_event(self, block=True, timeout=None):
        return self.event_queue.get(block, timeout)

    def has_event(self):
        return not self.event_queue.empty()