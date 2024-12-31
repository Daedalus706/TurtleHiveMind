from queue import Queue


class MessageController:
    def __init__(self):
        self.event_queue = Queue()
        self.server = None

    def send_message(self, turtle_id: int, message_type: str, data: dict | None) -> bool:
        if turtle_id not in self.server.connections.keys():
            return False
        return self.server.connections[turtle_id].send_data(message_type, data)
