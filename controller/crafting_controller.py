import model
import zipfile
import json
import os


class CraftingController:
    _instance = None
    _init = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        self._init = True

        self.items = {}
        self.groups = map_groups()

    def add_item(self, item:model.Item):
        self.items[item.name] = item

    def get_item(self, name:str) -> model.Item|None:
        if name in self.items:
            return self.items[name]
        return None

def map_groups() -> dict[str: set]:
    groups = {}
    for zip_file in os.listdir("./data/recipes"):
        archive = zipfile.ZipFile(f"./data/recipes/{zip_file}")
        for file in archive.filelist:
            data = json.loads(archive.read(file).decode("utf-8"))
            if "group" not in data:
                continue
            if data["group"] not in groups:
                groups[data["group"]] = set()
            if type(data["result"]) == dict:
                item = data["result"]["item"]
            else:
                item = data["result"]
            groups[data["group"]].add(item)

        archive.close()
    return groups