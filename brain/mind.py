import logging
import time

from controller import MessageController, CommandController, CraftingController


class Mind:

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.message_controller = MessageController()
        self.command_controller = CommandController()
        self.crafting_controller = CraftingController()

    def update(self):
        time.sleep(1)
        for event in self.message_controller.get_events():
            self.logger.debug(f"Handle Event of type: {type(event)}")
        sent_to = self.message_controller.broadcast_message("empty", None)
