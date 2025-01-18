import logging

from communication.base_client import BaseClient
from event import *
from websockets.sync.server import ServerConnection


class CommandConnection(BaseClient):

    def _create_event(self, event_type:str, payload:dict) -> ClientBaseEvent|None:
        match event_type:
            case _:
                return None

    def parse_turtle_command(self, command: str, arguments: list[str]) -> dict|None:
        match command:
            case "request_turtle_info":
                return {}

            case "request_item_info":
                if len(arguments) == 0:
                    self.command_controller.notify("error: missing argument 'slot'")
                    return None
                return {'slot': int(arguments[0])}

            case "inspect_block":
                turtle_arguments = {}
                if len(arguments) == 1:
                    turtle_arguments["direction"] = arguments[0]
                return turtle_arguments

            case "update":
                turtle_arguments = {}
                if len(arguments) == 1:
                    turtle_arguments["no_reboot"] = arguments[0]
                return turtle_arguments

            case "reboot":
                return {}

            case _:
                self.send_error("unknown command '{}'".format(command))
                return None


    def __init__(self, websocket:ServerConnection, server):
        super().__init__(websocket)
        self.logger = logging.getLogger(__name__)
        self.server = server
        self.await_confirm_function = None
        self.name = "Command"


    def data_handler(self, data_dict):
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
                    self.notify("confirmation aborted")
                    self.await_confirm_function = None

            if command == "echo":
                self.logger.debug(f'Command echo {" ".join(arguments)}')
                self.notify(" ".join(arguments))

            elif command == "purge":
                self.notify("Do you really want to purge? Please 'confirm'")
                self.await_confirm_function = self.command_controller.purge

            elif "turtle_" in command:
                self.logger.debug("received turtle command")
                turtle_id = command.split("turtle_")[1]
                turtle_command = arguments[0]
                turtle_arguments = arguments[1:]
                send_command_arguments = self.parse_turtle_command(turtle_command, turtle_arguments)
                if send_command_arguments is None:
                    return
                if turtle_id == "all":
                    self.message_controller.broadcast_command(turtle_command, send_command_arguments)
                else:
                    if not turtle_id.isdigit():
                        self.send_error(f"{turtle_id} is not a valid turtle id")
                        return
                    turtle_id = int(turtle_id)
                    if turtle_id not in self.server.get_active_client_keys():
                        self.send_error(f"Turtle {turtle_id} not online")
                        return
                    self.message_controller.send_command(turtle_id, turtle_command, send_command_arguments)
                    self.command_controller.await_answer(turtle_id)

            else:
                new_event = self._create_event(data_dict["type"], data_dict["payload"])

                if new_event is None:
                    return

                self.message_controller.add_event(new_event)

    def stop(self):
        super().stop()
        self.server.command = None


    def notify(self, text:str):
        self.logger.debug("server notify")
        self.send_data("info", {"text": text})

    def notify_as_turtle(self, turtle_id:int, text:str):
        self.logger.debug("turtle notify")
        self.send_data(f"turtle_{turtle_id}", {"text": text})

    def turtle_answer(self, turtle_id:int, text):
        self.logger.debug("turtle_answer")
        self.send_data(f"turtle_{turtle_id}", {"text": text})

    def send_error(self, message:str):
        self.send_data("error", {"text": message})