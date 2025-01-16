import json
import logging
from dataclasses import asdict

from .model_controller import ModelController
from event import *

class CommandController:
    _instance = None
    _init = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        self._init = True

        self.logger = logging.getLogger(__name__)
        self.server = None
        self.awaiting_answer = {}

    def purge(self):
        ModelController().purge()
        self.notify("Server purged!")

    def notify(self, message):
        if self.server is not None and self.server.command is not None:
            self.server.command.notify(message)

    def set_server(self, server):
        self.server = server
        self.logger.debug(f"set_server command: {self.server=}")

    def connect_turtle(self, turtle_id):
        self.notify(f"turtle_{turtle_id} connected")

    def disconnect_turtle(self, turtle_id):
        self.notify(f"turtle_{turtle_id} disconnected")
        if turtle_id in self.awaiting_answer:
            del self.awaiting_answer[turtle_id]

    def await_answer(self, turtle_id):
        self.awaiting_answer[turtle_id] = True

    def is_awaiting_answer(self, turtle_id):
        if turtle_id in self.awaiting_answer:
            return self.awaiting_answer[turtle_id]

    def answer(self, turtle_id, event):
        if turtle_id in self.awaiting_answer:
            event_data = asdict(event)
            self.notify(f"turtle_{turtle_id} {json.dumps(event_data, indent=4)}")
            del self.awaiting_answer[turtle_id]