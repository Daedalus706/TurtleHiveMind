import json
import logging
import time
import threading

from controller import MessageController, CommandController
from event import *
from websockets import *
from websockets.sync.server import ServerConnection

from util import const


def parse_turtle_command(command:str, arguments:list[str]) -> dict:
    match command:
        case "request_turtle_info":
            return {}

        case "request_item_info":
            return {'slot': int(arguments[0])}


class CommandConnection:

    def _create_event(self, event_type:str, payload:dict) -> ClientBaseEvent | None:
        match event_type:
            case _:
                return None


    def __init__(self, websocket:ServerConnection, server):
        self.logger = logging.getLogger(__name__)

        self.websocket = websocket
        self.message_controller = MessageController()
        self.command_controller = CommandController()
        self.server = server

        self.await_confirm_function = None

        self.stop_event = threading.Event()
        self.last_received = time.time()

        self.input_thread = threading.Thread(target=self._input_handler, daemon=True)
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_worker, daemon=True)

    def _heartbeat_worker(self):
        while self.active():
            if self.last_received + const.PING_INTERVAL < time.time():
                self.ping()
                time.sleep(1)
            if self.last_received + const.TIMEOUT_INTERVAL < time.time():
                self.logger.info("Command Timeout")
                self.stop()

    def ping(self):
        self.send_data("ping", None)

    def pong(self):
        self.send_data("pong", None)

    def _input_handler(self):
        while self.active():
            data_dict = None
            try:
                data = self.websocket.recv()
                self.last_received = time.time()
                if type(data) == str:
                    data_dict = json.loads(data)
            except ConnectionClosed:
                if self.active():
                    self.logger.info(f"Connection to command closed")
                    self.stop()

            if data_dict is None:
                continue

            if data_dict["type"] == "command":
                command = data_dict["payload"]["command"]
                arguments = data_dict["payload"]["arguments"]

                if self.await_confirm_function is not None:
                    if command == "confirm":
                        self.logger.debug('Command received confirmation')
                        self.await_confirm_function()
                        self.await_confirm_function = None
                    else:
                        self.logger.debug('Command confirmation aborted')
                        self.send_data("info", {"text": "confirmation aborted"})
                        self.await_confirm_function = None

                if command == "echo":
                    self.logger.debug(f'Command echo {" ".join(arguments)}')
                    self.send_data("info", {"text":" ".join(arguments)})

                elif command == "purge":
                    self.send_data("info", {"text": "Do you really want to purge? Please 'confirm'"})
                    self.await_confirm_function = self.command_controller.purge

                elif "turtle_" in command:
                    turtle_id = int(command.split("turtle_")[1])
                    turtle_command = arguments[0]
                    turtle_arguments = arguments[1:]
                    self.message_controller.send_command(turtle_id, turtle_command, parse_turtle_command(turtle_command, turtle_arguments))
                    self.command_controller.await_answer(turtle_id)
                    self.logger.debug("received turtle command")

                else:
                    new_event = self._create_event(data_dict["type"], data_dict["payload"])

                    if new_event is None:
                        continue

                    self.message_controller.add_event(new_event)

    def start(self):
        self.input_thread.start()
        self.heartbeat_thread.start()

    def stop(self):
        if self.active():
            self.stop_event.set()
            self.websocket.close()
            self.websocket = None
            self.server.command = None

    def join_threads(self):
        self.input_thread.join()
        self.heartbeat_thread.join()

    def active(self) -> bool:
        return not self.stop_event.is_set()

    def send_data(self, message_type:str, payload:dict|None) -> bool:
        if self.stop_event.is_set():
            return False
        try:
            message = json.dumps({"type": message_type, "payload": payload})
            self.websocket.send(message, text=True)
            return True
        except ConnectionClosed:
            if self.active():
                self.logger.info(f"Connection to command closed")
                self.stop()
            return False

    def notify(self, text):
        self.send_data("info", {"text": text})

    def turtle_answer(self, turtle_id:int, text):
        self.send_data(f"turtle_{turtle_id}", {"text": text})