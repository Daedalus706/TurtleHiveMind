import numpy as np
from event import TurtleInfoEvent


class Turtle:

    def __init__(self, turtle_id:int):
        self.turtle_id = turtle_id
        self.position:np.ndarray|None = None
        self.direction:int|None = None
        self.fuel:int|None = None
        self.inventory:dict|None = None

    def update_with_event(self, event:TurtleInfoEvent):
        if event.position is not None:
            self.position = event.position
        if event.direction is not None:
            self.direction = event.direction
        if event.fuel is not None:
            self.fuel = event.fuel
        if event.inventory is not None:
            self.inventory = event.inventory