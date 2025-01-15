import time

from controller import MessageController, CommandController


class Mind:

    def __init__(self, message_controller:MessageController, command_controller:CommandController) -> None:
        self.message_controller = message_controller

    def update(self):
        time.sleep(1)
        for event in self.message_controller.get_events():
            print(event)
        sent_to = self.message_controller.broadcast_message("empty", None)
