import json
import time
from queue import Queue
import threading

from controller import MessageController
from event import *
from util import const
from websockets import *
from websockets.sync.server import ServerConnection


class ClientConnection:

    @staticmethod
    def _create_event(data:dict) -> ClientBaseEvent | None:
        match data["type"]:

            case "pong":
                return ClientBaseEvent(turtle_id=data["turtle_id"])

            case _:
                return None



    def __init__(self, turtle_id:int, websocket:ServerConnection, message_controller:MessageController):
        self.turtle_id = turtle_id
        self.websocket = websocket
        self.message_controller = message_controller
        self.stop_event = threading.Event()
        self.active = True
        self.last_received = time.time()

        self.input_thread = threading.Thread(target=self._input_handler, daemon=True)
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_worker, daemon=True)

    def _heartbeat_worker(self):
        current_time = time.time()
        if self.last_received + const.PING_INTERVAL < current_time:
            self.ping()
            time.sleep(1)
        if self.last_received + const.TIMEOUT_INTERVAL < current_time:
            print(f"Timeout on client {self.turtle_id}")
            self.stop()

    def _input_handler(self):
        print(f"Started Client id {self.turtle_id}")
        while not self.stop_event.is_set():
            data_dict = None
            try:
                data = self.websocket.recv()
                self.last_received = time.time()
                if type(data) == str:
                    data_dict = json.loads(data)
            except ConnectionClosed:
                self.stop()

            if data_dict is None:
                continue

            if data_dict["type"] == "pong":
                continue

            if data_dict["type"] == "ping":
                self.send_data("pong", None)
                continue

            new_event = self._create_event(data_dict)

            if new_event is None:
                continue

            self.message_controller.add_event(new_event)

    def start(self):
        self.input_thread.start()
        self.heartbeat_thread.start()

    def stop(self):
        self.active = False
        self.stop_event.set()
        self.input_thread.join()
        self.heartbeat_thread.join()
        self.websocket.close()
        print(f"Closed Client connection {self.turtle_id}")

    def ping(self):
        self.send_data("ping", None)

    def send_data(self, message_type:str, payload:dict|None) -> bool:
        try:
            message = json.dumps({"payload": payload, "type": message_type})
            self.websocket.send(message)
            return True
        except ConnectionClosed:
            self.stop()
            return False
