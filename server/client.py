import json
from queue import Queue
import threading

from event import *

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



    def __init__(self, turtle_id:int, websocket:ServerConnection, event_queue:Queue):
        self.id = turtle_id
        self.websocket = websocket
        self.event_queue = event_queue
        self.stop_event = threading.Event()
        self.active = True

        self.input_thread = threading.Thread(target=self._input_handler, daemon=True)

    def _input_handler(self):
        print(f"Started Client id {self.id}")
        while not self.stop_event.is_set():
            data_dict = None
            try:
                data = self.websocket.recv()
                if type(data) == str:
                    data_dict = json.loads(data)
            except ConnectionClosed:
                self.active = False
                self.stop_event.set()

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

            self.event_queue.put(new_event)

    def start(self):
        self.input_thread.start()

    def stop(self):
        self.stop_event.set()
        self.input_thread.join()
        self.websocket.close()
        print(f"Closed Client connection {self.id}")

    def send_data(self, message_type:str, payload:dict|None) -> bool:
        try:
            message = json.dumps({"payload": payload, "type": message_type})
            self.websocket.send(message)
            return True
        except ConnectionClosed:
            self.active = False
            self.stop_event.set()
            return False
