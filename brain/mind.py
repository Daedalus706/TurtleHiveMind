import time
from controller import MessageController

class Mind:

    def __init__(self, message_controller:MessageController) -> None:
        self.event_queue = message_controller.event_queue
        self.message_controller = message_controller

    def update(self):
        time.sleep(1)
        sent_to = self.message_controller.broadcast_message("empty", None)
        print("broadcast message to", sent_to)