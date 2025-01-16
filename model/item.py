import zipfile
import json

from model import Recipe, NoRecipe


class Item:
    def __init__(self, name):
        self.name = name
        self.group = None
        self.recipe = None

    def get_recipe(self) -> Recipe|None:
        if self.recipe is not None:
            return self.recipe
        self.recipe = Recipe.create_recipe(self.name)
        if isinstance(self.recipe, NoRecipe):
            return None
        return self.recipe

    def get_group(self):
        if self.group is not None:
            return self.group
        mod, item = self.name.split(':', 1)
        archive = zipfile.ZipFile(f"./data/recipes/{mod}.zip")
        data = json.loads(archive.read(f"{item}.json").decode("utf-8"))
        archive.close()
        if "group" in data:
            self.group = data["group"]
        else:
            self.group = ""
        return self.group