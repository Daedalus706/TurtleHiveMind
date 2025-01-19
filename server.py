import logging
import os
from datetime import datetime
import configparser

from controller import *
from communication import Server
from brain import Mind
from util import const


def register_logger(log_level):
    if "logs" not in os.listdir():
        os.mkdir(const.LOG_FOLDER_PATH)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s[%(levelname)s] %(message)s",
        datefmt="[%Y-%m-%d %H:%M:%S]",
        handlers=[
            logging.FileHandler(f"{const.LOG_FOLDER_PATH}/server{datetime.now().strftime('%Y-%m-%d')}.log"),
            logging.StreamHandler()
        ]
    )
    logging.getLogger("websockets").setLevel(logging.CRITICAL)

def load_config() -> configparser.ConfigParser:
    config_parser = configparser.ConfigParser()
    if const.CONFIG_FILE_PATH not in os.listdir():
        config_parser["Server"] = {
            "ip": "127.0.0.1",
            "port": "5020"
        }
        config_parser["Logger"] = {
            "level": "INFO",
        }
        with open(const.CONFIG_FILE_PATH, "w") as configfile:
            config_parser.write(configfile)
    else:
        config_parser.read(const.CONFIG_FILE_PATH)
    return config_parser


if __name__ == '__main__':
    config = load_config()
    register_logger(config.get("Logger", "level"))

    ## init controllers
    MessageController()
    CommandController()
    model_controller = ModelController()
    CraftingController()

    server = Server(host=config.get("Server", "ip"), port=config.getint("Server", "port"))
    mind = Mind()

    try:
        server.start()

        while True:
            mind.update()

    except KeyboardInterrupt:
        print("Stop signal received, exiting...")
        server.stop()
        model_controller.save()


    print("Server stopped")