import numpy as np

from model.inventory import Inventory


class Chest(Inventory):
    def __init__(self, size:np.ndarray, position:np.ndarray):
        super().__init__(size)
        self.position = position