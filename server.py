from controller import MessageController
from server import Server
from brain import Mind


if __name__ == '__main__':
    message_controller = MessageController()
    server = Server(message_controller, host='10.147.18.135', port=5020, )
    mind = Mind(message_controller)

    try:
        server.start()

        while True:
            mind.update()

    except KeyboardInterrupt:
        print("Stop signal received, exiting...")
        server.stop()

    print("Server stopped")