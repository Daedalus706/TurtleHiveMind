import functools
import threading
import json

from websockets.sync.server import ServerConnection, serve
from websockets.sync.server import Server as SocketServer

from event import *
from controller import MessageController
from communication.client import ClientConnection


class Server:

    @staticmethod
    def server_worker(socket_server: SocketServer):
        socket_server.serve_forever()


    def __init__(self, message_controller:MessageController, host, port):
        message_controller.server = self
        self.host = host
        self.port = port

        self.stop_event = threading.Event()

        self.clients:dict[int,ClientConnection] = {}

        bound_handler = functools.partial(self.websocket_handler, message_controller=message_controller)
        self.socket_server = serve(bound_handler, self.host, self.port)

        self.server_thread = threading.Thread(target=Server.server_worker, args=(self.socket_server,), daemon=True)


    def add_connection(self, turtle_id, websocket, message_controller):
        new_connection = ClientConnection(turtle_id, websocket, message_controller)
        new_connection.start()
        self.clients[turtle_id] = new_connection
        new_connection.send_data("request_turtle_info", None)


    def websocket_handler(self, websocket:ServerConnection, message_controller:MessageController):
        handshake_data_dict = json.loads(websocket.recv())

        turtle_id = handshake_data_dict["payload"]
        self.add_connection(turtle_id, websocket, message_controller)

        new_event = NewTurtleConnectionEvent(turtle_id)
        message_controller.add_event(new_event)

        print(f"New client connection with id {turtle_id}")
        self.clients[turtle_id].stop_event.wait()


    def start(self):
        self.server_thread.start()
        print("Server started")


    def stop(self):
        self.stop_event.set()
        self.socket_server.socket.close()
        for client in set(self.clients.values()):
            client.stop()
        for client in set(self.clients.values()):
            client.join_threads()


    def get_active_client_keys(self) -> list[int]:
        return list(filter(lambda key: self.clients[key].active(), self.clients.keys()))


    def get_client(self, key):
        return self.clients[key]

