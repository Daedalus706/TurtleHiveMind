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

    @staticmethod
    def from_dict(turtle_dict:dict) -> 'Turtle':
        turtle = Turtle(int(turtle_dict['turtle_id']))
        turtle.position = turtle_dict['position']
        turtle.direction = turtle_dict['direction']
        turtle.fuel = turtle_dict['fuel']
        turtle.inventory = turtle_dict['inventory']
        return turtle

    def to_dict(self):
        return {
            'turtle_id': self.turtle_id,
            'position': self.position,
            'direction': self.direction,
            'fuel': self.fuel,
            'inventory': self.inventory,
        }