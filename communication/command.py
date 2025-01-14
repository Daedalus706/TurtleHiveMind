import json
import time
import threading

from controller import MessageController
from event import *
from websockets import *
from websockets.sync.server import ServerConnection


class CommandConnection:

    def _create_event(self, event_type:str, payload:dict) -> ClientBaseEvent | None:
        print(event_type, payload)
        match event_type:
            case _:
                return None


    def __init__(self, websocket:ServerConnection, message_controller:MessageController, server):
        self.websocket = websocket
        self.message_controller = message_controller
        self.server = server

        self.stop_event = threading.Event()
        self.last_received = time.time()

        self.input_thread = threading.Thread(target=self._input_handler, daemon=True)


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

            new_event = self._create_event(data_dict["type"], data_dict["payload"])

            if new_event is None:
                continue

            self.message_controller.add_event(new_event)

    def start(self):
        self.input_thread.start()

    def stop(self):
        if self.active():
            self.stop_event.set()
            self.websocket.close()
            self.websocket = None
            self.server.command = None

    def join_threads(self):
        self.input_thread.join()

    def active(self) -> bool:
        return not self.stop_event.is_set()

    def send_data(self, message_type:str, payload:dict|None) -> bool:
        if self.stop_event.is_set():
            return False
        try:
            message = json.dumps({"payload": payload, "type": message_type})
            self.websocket.send(message)
            return True
        except ConnectionClosed:
            if self.active():
                print(f"Connection to command closed while sending message")
                self.stop()
            return False
