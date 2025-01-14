import logging

from controller import MessageController
from communication import Server
from brain import Mind


def register_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s[%(levelname)s] %(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]",
        handlers=[
            logging.FileHandler("server.log"),
            logging.StreamHandler()
        ]
    )



if __name__ == '__main__':
    register_logger()

    message_controller = MessageController()
    server = Server(message_controller, host='10.147.18.240', port=5020)
    mind = Mind(message_controller)

    try:
        server.start()

        while True:
            mind.update()

    except KeyboardInterrupt:
        print("Stop signal received, exiting...")
        server.stop()

    print("Server stopped")