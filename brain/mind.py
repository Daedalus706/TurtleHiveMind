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
                event:NewTurtleConnectionEvent = e
                self.model_controller.connect_turtle(event)

            elif type(e) is TurtleDisconnectEvent:
                event: TurtleDisconnectEvent = e
                self.model_controller.disconnect_turtle(event)

            elif type(e) is BlockInfoEvent:
                event: BlockInfoEvent = e
                self.model_controller.update_block_with_event(event)

            elif type(e) is TurtleInfoEvent:
                event: TurtleInfoEvent = e
                self.model_controller.update_turtle_with_event(event)