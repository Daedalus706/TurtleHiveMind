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
        self.last_received = time.time()

        self.input_thread = threading.Thread(target=self._input_handler, daemon=True)
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_worker, daemon=True)

    def _heartbeat_worker(self):
        while not self.stop_event.is_set():
            if self.last_received + const.PING_INTERVAL < time.time():
                self.ping()
                time.sleep(1)
            if self.last_received + const.TIMEOUT_INTERVAL < time.time():
                print(f"Timeout on client {self.turtle_id}")
                self.stop()

    def _input_handler(self):
        while not self.stop_event.is_set():
            data_dict = None
            try:
                data = self.websocket.recv()
                self.last_received = time.time()
                if type(data) == str:
                    data_dict = json.loads(data)
            except ConnectionClosed as e:
                print(f"Connection to turtle_{self.turtle_id} closed while awaiting input ", e.rcvd.code(), e.rcvd.reason())
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
        if self.active():
            self.stop_event.set()
            self.websocket.close()
            self.message_controller.close_connection(self.turtle_id)

    def join_threads(self):
        self.heartbeat_thread.join()
        self.input_thread.join()

    def ping(self):
        self.send_data("ping", None)

    def active(self) -> bool:
        return not self.stop_event.is_set()

    def send_data(self, message_type:str, payload:dict|None) -> bool:
        try:
            message = json.dumps({"payload": payload, "type": message_type})
            self.websocket.send(message)
            return True
        except ConnectionClosed as e:
            print(f"Connection to turtle_{self.turtle_id} closed while sending message", e.rcvd.code(), e.rcvd.reason())
            self.stop()
            return False
