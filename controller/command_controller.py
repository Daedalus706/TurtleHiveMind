import logging

from .model_controller import ModelController

class CommandController:
    _instance = None
    _init = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if CommandController._init:
            return
        print("init")
        self.logger = logging.getLogger(__name__)
        self.server = None
        CommandController._init = True

    def purge(self):
        ModelController().purge()
        self.notify("Server purged!")

    def notify(self, message):
        if self.server is not None and self.server.command is not None:
            self.server.command.notify(message)

    def set_server(self, server):
        self.server = server
        self.logger.debug(f"set_server command: {self.server=}")