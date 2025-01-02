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

    def remove_connection(self, turtle_id):
        print(f"removed client {turtle_id} from dict")
        if turtle_id not in self.clients:
            return
        if self.clients[turtle_id].active:
            self.clients[turtle_id].stop()
        del self.clients[turtle_id]


    def websocket_handler(self, websocket:ServerConnection, message_controller:MessageController):
        handshake_data_dict = json.loads(websocket.recv())

        turtle_id = handshake_data_dict["turtle_id"]
        payload = handshake_data_dict["payload"]
        position = payload["position"]
        direction = payload["direction"]

        self.add_connection(turtle_id, websocket, message_controller)
        print(f"{handshake_data_dict=}")

        new_event = NewTurtleEvent(turtle_id, position, direction)
        message_controller.add_event(new_event)

        print(f"New client connection with id {turtle_id}")
        self.clients[turtle_id].stop_event.wait()


    def start(self):
        self.server_thread.start()
        print("Server started")

    def stop(self):
        self.stop_event.set()
        self.socket_server.socket.close()
        for client in self.clients.values():
            client.stop()
        for client in self.clients.values():
            client.join_threads()

    def get_client_keys(self):
        return list(self.clients.keys())

    def get_client(self, key):
        return self.clients[key]

