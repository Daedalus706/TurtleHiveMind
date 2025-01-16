import functools
import logging
import threading
import json

from websockets import ConnectionClosed
from websockets.sync.server import ServerConnection, serve
from websockets.sync.server import Server as SocketServer

from event import *
from controller import MessageController, CommandController
from communication.client import ClientConnection
from communication.command import CommandConnection


class Server:

    @staticmethod
    def server_worker(socket_server: SocketServer):
        socket_server.serve_forever()


    def __init__(self, host, port):
        self.logger = logging.getLogger(__name__)
        self.command_controller = CommandController()
        message_controller = MessageController()
        message_controller.server = self
        self.command_controller = CommandController()
        self.command_controller.set_server(self)
        self.host = host
        self.port = port

        self.stop_event = threading.Event()

        self.clients:dict[int,ClientConnection] = {}
        self.command:CommandConnection|None = None

        bound_handler = functools.partial(self.websocket_handler, message_controller=message_controller)
        self.socket_server = serve(bound_handler, self.host, self.port)

        self.server_thread = threading.Thread(target=Server.server_worker, args=(self.socket_server,), daemon=True)


    def add_connection(self, turtle_id, websocket):
        new_connection = ClientConnection(turtle_id, websocket)
        new_connection.start()
        self.clients[turtle_id] = new_connection
        new_connection.send_data("request_turtle_info", None)


    def websocket_handler(self, websocket:ServerConnection, message_controller:MessageController):
        client_ip, client_port = websocket.remote_address
        try:
            handshake_data_dict = json.loads(websocket.recv())
        except ConnectionClosed:
            self.logger.error(f"New connection failed to handshake. {client_ip=}")
            return

        match handshake_data_dict["type"]:
            case "turtle_handshake":
                turtle_id = handshake_data_dict["payload"]
                self.add_connection(turtle_id, websocket)

                new_event = NewTurtleConnectionEvent(turtle_id)
                message_controller.add_event(new_event)

                self.logger.info(f"New turtle connection with id {turtle_id}")
                self.command_controller.notify(f"turtle_{turtle_id} connected")
                self.clients[turtle_id].stop_event.wait()

            case "command_handshake":
                if self.command is None:
                    self.command = CommandConnection(websocket, self)
                    self.command.start()
                    self.command.send_data("info", {"text": "connected"})
                    self.logger.info(f"New command connection")
                    self.command.stop_event.wait()

            case _:
                pass


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

