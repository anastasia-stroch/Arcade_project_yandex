import arcade
import random
from constants import *

class Monster(arcade.Sprite):
    def __init__(self, x: float, y: float):
        texture = arcade.make_soft_square_texture(35, arcade.color.RED)
        super().__init__(texture)
        self.scale = 1.0
        self.center_x = x
        self.center_y = y
        self.health = 25
        self.damage = MONSTER_DAMAGE
        self.speed = 1.0 + random.random() * 0.8
        self.direction = 1 if random.random() > 0.5 else -1
        self.platform_parts = None
        self.platform_width = 0

    def update(self, delta: float = 1 / 60):
        pass

class Spike(arcade.Sprite):
    def __init__(self, x: float, y: float):
        texture = arcade.make_soft_square_texture(40, arcade.color.DARK_RED)
        super().__init__(texture)
        self.scale = 0.8
        self.center_x = x
        self.center_y = y + 10
        self.damage = TRAP_DAMAGE

    def update(self, delta: float = 1 / 60):
        pass
