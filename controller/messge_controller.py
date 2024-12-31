from queue import Queue


class MessageController:
    def __init__(self):
        self.event_queue = Queue()
        self.server = None

    def send_message(self, turtle_id:int, message_type:str, data:dict|None) -> bool:
        if turtle_id not in self.server.connections.keys():
            return False
        return self.server.connections[turtle_id].send_data(message_type, data)

    def broadcast_message(self, message_type:str, data:dict|None) -> set:
        message_sent = set()
        for turtle_id, client in self.server.connections.items():
            if client.send_data(message_type, data):
                message_sent.add(turtle_id)
        return message_sent