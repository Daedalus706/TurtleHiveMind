import json
import logging
import time
import threading
from asyncio import new_event_loop

from controller import MessageController, CommandController
from event import *
from util import const
from websockets import *
from websockets.sync.server import ServerConnection



logger = logging.getLogger(__name__)

class ClientConnection:

    def _create_event(self, event_type:str, payload:dict) -> ClientBaseEvent | None:
        match event_type:

            case 'error':
                new_event = TurtleError(
                    turtle_id=self.turtle_id,
                    message=payload['message'] if 'message' in payload else None,
                    command=payload['command'] if 'command' in payload else None
                )
                self.command_controller.notify_as_turtle(self.turtle_id, "Error: "+f"{new_event.message}")

            case 'info':
                new_event = TurtleNotifyMessage(
                    turtle_id=self.turtle_id,
                    message=payload['message'] if 'message' in payload else None,
                )
                self.command_controller.notify_as_turtle(self.turtle_id, new_event.message)

            case "turtle_info":
                new_event = TurtleInfoEvent(
                    turtle_id=self.turtle_id,
                    position=payload["position"] if "position" in payload else None,
                    direction=payload["direction"] if "direction" in payload else None,
                    fuel=payload["fuel"] if "fuel" in payload else None,
                    inventory=payload["inventory"] if "inventory" in payload else None
                )

            case "item_info":
                new_event = ItemInfoEvent(
                    turtle_id=self.turtle_id,
                    slot=payload["slot"] if "slot" in payload else None,
                    name=payload["name"] if "name" in payload else None,
                    count=payload["count"] if "count" in payload else None,
                    max_count=payload["max_count"] if "max_count" in payload else None,
                    tags=payload["tags"] if "tags" in payload else None
                )

            case "state_change":
                new_event = TurtleStateChangeEvent(
                    turtle_id=self.turtle_id,
                    name=payload["name"] if "name" in payload else None,
                    value=payload["value"] if "value" in payload else None,
                )

            case _:
                return None

        if self.command_controller.is_awaiting_answer(self.turtle_id):
            self.command_controller.answer(self.turtle_id, new_event)

        return new_event



    def __init__(self, turtle_id:int, websocket:ServerConnection):
        self.turtle_id = turtle_id
        self.websocket = websocket
        self.message_controller = MessageController()
        self.command_controller = CommandController()

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
                logger.info(f"Timeout on client {self.turtle_id}")
                self.stop()

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
                    logger.info(f"Connection to turtle_{self.turtle_id} closed")
                    self.stop()

            if data_dict is None:
                continue

            if data_dict["type"] == "pong":
                continue

            if data_dict["type"] == "ping":
                self.send_data("pong", None)
                continue

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
                logger.info(f"Connection to turtle_{self.turtle_id} closed")
                self.stop()
            return False
