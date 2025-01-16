import json
import time
import threading

from controller import MessageController, CommandController
from event import *
from websockets import *
from websockets.sync.server import ServerConnection

from util import const


class CommandConnection:

    def _create_event(self, event_type:str, payload:dict) -> ClientBaseEvent | None:
        match event_type:
            case _:
                return None


    def __init__(self, websocket:ServerConnection, server):
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
                print(f"Timeout on command")
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
                    print(f"Connection to command closed while awaiting input")
                    self.stop()

            if data_dict is None:
                continue

            if data_dict["type"] == "command":
                command = data_dict["payload"]["text"].split(" ")[0]

                if self.await_confirm_function is not None:
                    if command == "confirm":
                        self.await_confirm_function()
                    else:
                        self.await_confirm_function = None

                if command == "echo":
                    self.send_data("info", {"text":data_dict["payload"]["text"]})
                    continue

                if command == "purge":
                    self.send_data("info", {"text": "Do you really want to purge? Please 'confirm'"})
                    self.await_confirm_function = self.command_controller.purge

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
            message = json.dumps({"payload": payload, "type": message_type})
            self.websocket.send(message)#, text=True)
            return True
        except ConnectionClosed:
            if self.active():
                print(f"Connection to command closed while sending message")
                self.stop()
            return False

    def notify(self, text):
        self.send_data("info", {"text": text})
