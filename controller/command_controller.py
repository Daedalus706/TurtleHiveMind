import logging

from .model_controller import ModelController

class CommandController:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.server = None

    def purge(self):
        ModelController().purge()
        self.notify("Server purged!")

    def notify(self, message):
        self.logger.debug(f"notify command: {message}")
        self.logger.debug(f"{self.server=}")
        self.logger.debug(f"{self.server.command=}")
        if self.server is not None and self.server.command is not None:
            self.server.command.notify(message)

    def set_server(self, server):
        self.server = server
        self.logger.debug(f"set_server command: {self.server=}")