import functools
import logging
import threading
import json

from websockets import ConnectionClosed
from websockets.sync.server import ServerConnection, serve
from websockets.sync.server import Server as SocketServer

from event import *
from controller import MessageController, CommandController
from communication.turtle_client import TurtleConnection
from communication.command import CommandConnection


class Server:

    @staticmethod
    def server_worker(socket_server: SocketServer):
        socket_server.serve_forever()


    def __init__(self, host, port, minecraft_ip):
        self.logger = logging.getLogger(__name__)
        self.command_controller = CommandController()
        self.command_controller.set_server(self)
        message_controller = MessageController()
        message_controller.server = self
        self.host = host
        self.port = port
        self.minecraft_ip = minecraft_ip

        self.stop_event = threading.Event()

        self.clients:dict[int,TurtleConnection] = {}
        self.command:CommandConnection|None = None

        bound_handler = functools.partial(self.websocket_handler, message_controller=message_controller)
        self.socket_server = serve(bound_handler, self.host, self.port)

        self.server_thread = threading.Thread(target=Server.server_worker, args=(self.socket_server,), daemon=True)


    def add_connection(self, turtle_id, websocket):
        new_connection = TurtleConnection(turtle_id, websocket)
        new_connection.start()
        new_connection.send_data("request_turtle_info", None)
        self.clients[turtle_id] = new_connection


    def websocket_handler(self, websocket:ServerConnection, message_controller:MessageController):
        headers = websocket.request.headers
        client_ip = headers.get("X-Forwarded-For", None)
        self.logger.debug(f"New client ip: {client_ip}")
        try:
            handshake_data_dict = json.loads(websocket.recv())
        except ConnectionClosed:
            self.logger.error(f"New connection failed to handshake")
            return

        match handshake_data_dict["type"]:
            case "turtle_handshake":
                if client_ip != self.minecraft_ip:
                    logging.info(f"Refused turtle connection from unknown host: {client_ip}")
                    websocket.send(json.dumps({"type": "refuse_connection"}), text=True)
                    return
                turtle_id = int(handshake_data_dict["payload"])
                self.add_connection(turtle_id, websocket)

                new_event = NewTurtleConnectionEvent(turtle_id)
                message_controller.add_event(new_event)

                self.logger.info(f"New connection with turtle_{turtle_id}")
                self.command_controller.connect_turtle(turtle_id)
                self.clients[turtle_id].stop_event.wait()
                self.command_controller.disconnect_turtle(turtle_id)

                new_event = TurtleDisconnectEvent(turtle_id)
                message_controller.add_event(new_event)

            case "command_handshake":
                if self.command is None:
                    self.command = CommandConnection(websocket, self)
                    self.command.start()
                    self.logger.info(f"New command connection")
                    self.command.stop_event.wait()

            case _:
                self.logger.error(f"Unknown handshake type: {handshake_data_dict['type']}")


    def start(self):
        self.server_thread.start()
        self.logger.info("Server started")


    def stop(self):
        self.stop_event.set()
        self.socket_server.socket.close()
        for client in set(self.clients.values()):
            client.stop()
        for client in set(self.clients.values()):
            client.join_threads()
        if self.command is not None:
            self.command.stop()


    def get_active_client_keys(self) -> list[int]:
        return list(filter(lambda key: self.clients[key].active(), self.clients.keys()))


    def get_client(self, key):
        return self.clients[key]

