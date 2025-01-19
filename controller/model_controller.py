import json
import logging
import os

import numpy as np
from bidict import bidict

from util import const
from model import Chest, Turtle
from event import *


class ModelController:
    _instance = None
    _init = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def create_save_folder(base_path, structure):
        for folder, subfolders in structure.items():
            current_path = os.path.join(base_path, folder)
            if not os.path.exists(current_path):
                os.makedirs(current_path)
            if isinstance(subfolders, dict):
                ModelController.create_save_folder(current_path, subfolders)

    def __init__(self):
        if self._init:
            return
        self._init = True

        self.logger = logging.getLogger(__name__)
        ModelController.create_save_folder('./', const.SAVES_STRUCTURE)

        self.chunks:dict[tuple[int, int], np.ndarray] = {}
        self.chests:dict[tuple[int, int, int], Chest] = {}
        self.turtles:dict[int:Turtle] = {}
        self.block_lookup:bidict[np.uint16, str] = bidict()
        self.load_chunks()
        self.load_chests()
        self.load_turtles()

    def save_chunks(self):
        self.logger.info("Saving chunks")
        for key, chunk in self.chunks.items():
            np.save(os.path.join(const.SAVE_PATH_CHUNKS, f"chunk_{key[0]}_{key[1]}.npy"), chunk)
        json.dump(dict(self.block_lookup), open(os.path.join(const.SAVE_PATH_CHUNKS, "blocks.json"), "w"), indent=4)

    def save_chests(self):
        self.logger.info("Saving chests")
        path = os.path.join(const.SAVE_PATH_CHESTS, "chests.json")
        chest_dicts = [c.to_dict() for c in self.chests.values()]
        json.dump(chest_dicts, open(path, "w"), indent=4)

    def save_turtles(self):
        self.logger.info("Saving turtles")
        path = os.path.join(const.SAVE_PATH_TURTLES, "turtles.json")
        turtle_dicts = [t.to_dict() for t in self.turtles.values()]
        json.dump(turtle_dicts, open(path, "w"), indent=4)

    def save(self):
        self.save_chunks()
        self.save_chests()
        self.save_turtles()

    def load_chunks(self):
        files = os.listdir(const.SAVE_PATH_CHUNKS)
        for file in files:
            if "chunk" in file:
                parts = file[6:-4].split('_')
                self.chunks[(int(parts[0]), int(parts[1]))] = np.load(os.path.join(const.SAVE_PATH_CHUNKS, file))
            elif "blocks" in file:
                block_dict = json.load(open(os.path.join(const.SAVE_PATH_CHUNKS, file), "r"))
                self.block_lookup = bidict({np.uint16(k): v for k, v in block_dict})

    def load_chests(self):
        path = os.path.join(const.SAVE_PATH_CHESTS, "chests.json")
        if os.path.exists(path):
            for chest_dict in json.load(open(path, "r")):
                position = (int(chest_dict["position"][0]), int(chest_dict["position"][1]), int(chest_dict["position"][2]))
                self.chests[position] = Chest.from_dict(chest_dict)

    def load_turtles(self):
        path = os.path.join(const.SAVE_PATH_TURTLES, "turtles.json")
        if os.path.exists(path):
            for turtle_dict in json.load(open(path, "r")):
                self.turtles[int(turtle_dict["turtle_id"])] = Turtle.from_dict(turtle_dict)

    def get_chunk(self, pos:tuple[int, int]) -> np.ndarray:
        if pos not in self.chunks:
            self.chunks[pos] = np.zeros((16, 384, 16), dtype=np.uint16)
        return self.chunks[pos]

    def get_block_id_at(self, pos:tuple[int, int, int]) -> np.uint16:
        return self.get_chunk((pos[0] // 16, pos[2] // 16))[pos[0], pos[1]+64, pos[2]]

    def purge(self):
        self.logger.info("Purge Model")
        tree = list(os.walk("./saves"))
        for root, dirs, files in tree:
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    self.logger.debug("Delete {}".format(file_path))
                    os.remove(file_path)
                except Exception as e:
                    self.logger.error(f"Error while purging files {file_path}: {e}")
        self.block_lookup = bidict()
        self.chunks = {}
        self.chests = {}

    def get_block_name_at(self, pos:tuple[int, int, int]) -> str|None:
        block_id = self.get_block_id_at(pos)
        if block_id == 0:
            return None
        return self.block_lookup[block_id]

    def set_block_at(self, pos:tuple[int, int, int], block_name:str):
        if block_name not in self.block_lookup.inv:
            self.block_lookup[np.uint16(max(self.block_lookup)+1)] = block_name
        self.get_chunk((pos[0]//16, pos[2]//16))[pos[0], pos[1]+64, pos[2]] = self.block_lookup.inv[block_name]

    def connect_turtle(self, event:NewTurtleConnectionEvent):
        if event.turtle_id not in self.turtles.keys():
            new_turtle = Turtle(event.turtle_id)
            self.turtles[event.turtle_id] = new_turtle
        self.turtles[event.turtle_id].set_connected(True)

    def disconnect_turtle(self, event:TurtleDisconnectEvent):
        if event.turtle_id in self.turtles.keys():
            self.turtles[event.turtle_id].set_connected(False)









