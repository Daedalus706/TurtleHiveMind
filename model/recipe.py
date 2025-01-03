from __future__ import annotations

import zipfile
import json


class Recipe:

    @staticmethod
    def create_recipe(item_name: str) -> Recipe|None:
        """
        Create a crafting recipe of an item. Recipe data should be provided in the ./data/recipes/folder as {mod}.zip
        :param item_name: the name of the item
        :return: Recipe instance or None if the recipe cant be found or has an unknown crafting type
        """
        mod, item = item_name.split(':', 1)
        archive = zipfile.ZipFile(f"./data/recipes/{mod}.zip")
        data = json.loads(archive.read(f"{item}.json").decode("utf-8"))
        archive.close()

        pattern = ["" for _ in range(9)]
        items = {}
        count = 1

        match data['type']:
            case 'minecraft:crafting_shaped':
                for y, row in enumerate(data["pattern"]):
                    for x, key in enumerate(row):
                        if key == " ":
                            continue
                        if "tag" in data["key"][key]:
                            item = data["key"][key]["tag"]
                        elif "item" in data["key"][key]:
                            item = data["key"][key]["item"]
                        else:
                            raise KeyError(f"{data["key"][key]} not specified")
                        pattern[y*3+x] = item
                        if item not in items:
                            items[item] = 1
                        else:
                            items[item] += 1
                if "count" in data["result"]:
                    count = data["result"]["count"]
                return Recipe(item_name, pattern, items, count)

            case 'minecraft:crafting_shapeless':
                for i, ingredient in enumerate(data["ingredients"]):
                    if "tag" in ingredient:
                        item = ingredient["tag"]
                    elif "item" in ingredient:
                        item = ingredient["item"]
                    else:
                        raise KeyError(f"{ingredient} not specified")
                    pattern[i] = item
                    if item not in items:
                        items[item] = 1
                    else:
                        items[item] += 1
                if "count" in data["result"]:
                    count = data["result"]["count"]
                return Recipe(item_name, pattern, items, count)

            case _:
                return None

    def __init__(self, item_name:str, pattern:list, item_group_list, count:int):
        self.item_name = item_name
        self.pattern = pattern
        self.item_group_list = item_group_list
        self.count = count

    def to_dict(self):
        return {
            "item_name": self.item_name,
            "pattern": self.pattern,
            "item_group_list": self.item_group_list,
            "count": self.count,
        }

    def __repr__(self):
        return f"{self.to_dict()}"


