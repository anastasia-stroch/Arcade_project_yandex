import arcade
import random
import math
from constants import *

class Gold(arcade.Sprite):
    def __init__(self, x: float, y: float, value: int = COIN_WORTH):
        texture = arcade.make_circle_texture(30, arcade.color.YELLOW)
        super().__init__(texture)
        self.scale = 0.8
        self.center_x = x
        self.center_y = y
        self.value = value
        self.timer = random.randint(0, 100)
        self.start_y = y
        self.rotate_speed = random.uniform(2, 4)

    def update(self, delta: float = 1 / 60):
        self.timer += delta * 60
        self.center_y = self.start_y + math.sin(self.timer * 0.1) * 15
        self.angle += self.rotate_speed * delta * 60

class Heart(arcade.Sprite):
    def __init__(self, x: float, y: float, value: int = POTION_HEAL):
        texture = arcade.make_soft_square_texture(40, arcade.color.RED)
        super().__init__(texture)
        self.scale = 0.8
        self.center_x = x
        self.center_y = y
        self.value = value
        self.timer = random.randint(0, 100)
        self.start_y = y

    def update(self, delta: float = 1 / 60):
        self.timer += delta * 60
        self.center_y = self.start_y + math.sin(self.timer * 0.08) * 8
        pulse = 0.08 * math.sin(self.timer * 0.1)
        self.scale = 0.8 + pulse

class ExitFlag(arcade.Sprite):
    def __init__(self, x: float, y: float):
        texture = arcade.make_soft_square_texture(80, arcade.color.GREEN)
        super().__init__(texture)
        self.scale = 1.0
        self.center_x = x
        self.center_y = y
        self.timer = random.randint(0, 100)
        self.start_y = y
        self.should_move = True

    def update(self, delta: float = 1 / 60):
        if not self.should_move:
            return
        self.timer += delta * 60
        self.center_y = self.start_y + math.sin(self.timer * 0.05) * 10
