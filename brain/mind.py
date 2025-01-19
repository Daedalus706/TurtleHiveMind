import logging
import time

from event import *
from controller import MessageController, CommandController, CraftingController


class Mind:

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.message_controller = MessageController()
        self.command_controller = CommandController()
        self.crafting_controller = CraftingController()

    def update(self):
        for event in self.message_controller.get_events():
            self.logger.debug(f"Handle Event of type: {type(event)}")
            match event.__class__.__name__:
                case 'NewTurtleConnectionEvent':
                    print('New Turtle Connection Event')
