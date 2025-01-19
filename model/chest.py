import numpy as np
from pip._internal.utils.retry import retry

from model.inventory import Inventory


class Chest(Inventory):
    def __init__(self, size:int, position:np.ndarray):
        super().__init__(size)
        self.position = position

    def to_dict(self):
        super_dict = super().to_dict()
        super_dict['position'] = self.position
        return super_dict

    @staticmethod
    def from_dict(chest_dict):
        position = (int(chest_dict["position"][0]), int(chest_dict["position"][1]), int(chest_dict["position"][2]))
        chest = Chest(int(chest_dict['size']), position)
        chest.content = chest_dict['content']
        return chest