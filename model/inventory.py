from model.item import Item


class Inventory:
    def __init__(self, size:int):
        self.size = size
        self.content:dict[Item, int] = {}

    def get_content(self):
        return self.content

    def get_item_count(self, item:Item):
        if item in self.content:
            return self.content[item]
        else:
            return 0

    def remove_item(self, item:Item, count:int):
        if item in self.content:
            self.content[item] -= count
        if self.content[item] <= 0:
            del self.content[item]

    def add_item(self, item:Item, count:int):
        if item not in self.content:
            self.content[item] = 0
        self.content[item] += count

    def to_dict(self):
        return {
            "size": self.size,
            "content": self.content,
        }