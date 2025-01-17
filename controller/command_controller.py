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

    def notify(self, message:str):
        if self.server is not None and self.server.command is not None:
            self.server.command.notify(message)

    def set_server(self, server):
        self.server = server

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
        if self.server is None or self.server.command is None:
            return
        if turtle_id in self.awaiting_answer:
            self.logger.debug("received turtle answer")
            event_data = asdict(event)
            self.server.command.turtle_answer(turtle_id, json.dumps(event_data))
            del self.awaiting_answer[turtle_id]

    def notify_as_turtle(self, turtle_id:int, message:str):
        if self.server is not None and self.server.command is not None:
            self.server.command.notify_as_turtle(turtle_id, message)