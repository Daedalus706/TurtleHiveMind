import logging

from event import *
from controller import *


class Mind:

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.message_controller = MessageController()
        self.command_controller = CommandController()
        self.model_controller = ModelController()
        self.crafting_controller = CraftingController()

    def update(self):
        for e in self.message_controller.get_events():
            self.logger.debug(f"Handle Event of type: {type(e)}")

            if type(e) is NewTurtleConnectionEvent:
                self.model_controller.connect_turtle(e)

            elif type(e) is TurtleDisconnectEvent:
                self.model_controller.disconnect_turtle(e)

            elif type(e) is BlockInfoEvent:
                self.model_controller.update_block_with_event(e)

            elif type(e) is TurtleInfoEvent:
                self.model_controller.update_turtle_with_event(e)