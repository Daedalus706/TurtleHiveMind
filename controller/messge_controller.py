from queue import Queue


class MessageController:
    def __init__(self):
        self.event_queue = Queue()
        self.server = None

    def send_message(self, turtle_id:int, message_type:str, data:dict|None) -> bool:
        if turtle_id not in self.server.connections.keys():
            return False
        return self.server.connections[turtle_id].send_data(message_type, data)

    def broadcast_message(self, message_type:str, data:dict|None) -> bool:
        message_sent = False
        for turtle_id, client in self.server.connections.items():
            message_sent = message_sent or client.send_data(message_type, data)
        return message_sent