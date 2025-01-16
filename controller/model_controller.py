import logging
import os

from util import const


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

    def purge(self):
        self.logger.info("Purge Model")
        for root, dirs, files in os.walk("./saves"):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                except Exception as e:
                    self.logger.error(f"Error while purging files {file_path}: {e}")