import json
import logging
import time
import threading

from controller import MessageController, CommandController
from util import const
from websockets import ConnectionClosed
from websockets.sync.server import ServerConnection


logger = logging.getLogger(__name__)

class BaseClient:
    def __init__(self, websocket:ServerConnection):
        self.websocket = websocket
        self.message_controller = MessageController()
        self.command_controller = CommandController()

        self.stop_event = threading.Event()
        self.last_received = time.time()

        self.input_thread = threading.Thread(target=self._base_input_handler, daemon=True)
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_worker, daemon=True)

        self.name = "BaseClient"

    def _heartbeat_worker(self):
        while self.active():
            if self.last_received + const.PING_INTERVAL < time.time():
                self.ping()
                time.sleep(1)
            if self.last_received + const.TIMEOUT_INTERVAL < time.time():
                logger.info(f"Timeout on client {self.name}")
                self.stop()

    def _base_input_handler(self):
        while self.active():
            data_dict = None
            try:
                data = self.websocket.recv()
                self.last_received = time.time()
                if type(data) == str:
                    data_dict = json.loads(data)
            except ConnectionClosed:
                if self.active():
                    logger.info(f"Connection to {self.name} closed")
                    self.stop()

            if data_dict is None:
                continue

            if data_dict["type"] == "pong":
                continue

            if data_dict["type"] == "ping":
                self.send_data("pong", None)
                continue

            self.data_handler(data_dict)

    def data_handler(self, data_dict):
        pass

    def start(self):
        self.input_thread.start()
        self.heartbeat_thread.start()

    def stop(self):
        if self.active():
            self.stop_event.set()
            self.websocket.close()
            self.websocket = None

    def join_threads(self):
        self.heartbeat_thread.join()
        self.input_thread.join()

    def ping(self):
        self.send_data("ping", None)

    def active(self) -> bool:
        return not self.stop_event.is_set()

    def send_data(self, message_type:str, payload:dict|None) -> bool:
        if self.stop_event.is_set():
            return False
        try:
            message = json.dumps({"payload": payload, "type": message_type})
            self.websocket.send(message, text=True)
            return True
        except ConnectionClosed:
            if self.active():
                logger.info(f"Connection to {self.name} closed")
                self.stop()
            return False