import json
import logging
from communication.base_client import BaseClient
from event import *
from websockets.sync.server import ServerConnection



logger = logging.getLogger(__name__)

class TurtleConnection(BaseClient):

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

            case "block_info":
                new_event = BlockInfoEvent(
                    turtle_id=self.turtle_id,
                    position=payload["pos"] if "pos" in payload else None,
                    name=payload["name"] if "name" in payload else None,
                    tags=payload["tags"] if "tags" in payload else None,
                )
                self.command_controller.notify_as_turtle(self.turtle_id, json.dumps(payload))

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
        super().__init__(websocket)
        self.turtle_id = turtle_id
        self.name = f"turtle_{turtle_id}"


    def data_handler(self, data_dict:dict):
        new_event = self._create_event(data_dict["type"], data_dict["payload"])
        if new_event is None:
            return
        self.message_controller.add_event(new_event)
