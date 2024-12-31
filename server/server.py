import functools
import threading
import json
from queue import Queue

from websockets.sync.server import ServerConnection, serve
from websockets.sync.server import Server as SocketServer

from controller import MessageController
from event import *
from server.client import ClientConnection


class Server:

    @staticmethod
    def server_worker(websocket: SocketServer):
        websocket.serve_forever()

    def __init__(self, message_controller:MessageController, host="localhost", port=5020):
        message_controller.server = self
        self.host = host
        self.port = port

        self.stop_event = threading.Event()

        self.connections:dict[int,ClientConnection] = {}

        bound_handler = functools.partial(self.websocket_handler, event_queue=message_controller.event_queue)
        self.websocket = serve(bound_handler, self.host, self.port)

        self.server_thread = threading.Thread(target=Server.server_worker, args=(self.websocket,), daemon=True)


    def add_connection(self, turtle_id, websocket, event_queue):
        new_connection = ClientConnection(turtle_id, websocket, event_queue)
        new_connection.start()
        self.connections[turtle_id] = new_connection


    def websocket_handler(self, websocket:ServerConnection, event_queue:Queue):
        handshake_data_dict =  json.loads(websocket.recv())

        turtle_id = handshake_data_dict["turtle_id"]
        position = handshake_data_dict["position"]
        direction = handshake_data_dict["direction"]

        self.add_connection(turtle_id, websocket, event_queue)

        new_event = NewTurtleEvent(turtle_id, position, direction)
        event_queue.put(new_event)

        print(f"New client connection with id {turtle_id}")
        self.connections[turtle_id].stop_event.wait()


    def start(self):
        self.server_thread.start()
        print("Server started")

    def stop(self):
        for client_id, connection in self.connections.items():
            connection.stop()
        self.stop_event.set()
        self.websocket.socket.close()
        self.server_thread.join()
