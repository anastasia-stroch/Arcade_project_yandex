import arcade
import random
import math
from constants import *

class Particle(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.texture = arcade.load_texture("particles/particle_1.png")
        except:
            color = random.choice([
                arcade.color.YELLOW,
                arcade.color.ORANGE,
                arcade.color.RED,
                arcade.color.WHITE
            ])
            self.texture = arcade.make_circle_texture(8, color)
        self.scale = random.uniform(0.5, 1.5)
        self.center_x = x
        self.center_y = y
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.life = random.uniform(0.5, 2.0)
        self.timer = 0
        self.alpha = 255
        self.gravity = 0.5

    def update(self, delta: float):
        self.timer += delta
        self.center_x += self.speed_x
        self.center_y += self.speed_y
        self.speed_y -= self.gravity
        if self.timer > self.life * 0.7:
            self.alpha = int(255 * (1 - (self.timer - self.life * 0.7) / (self.life * 0.3)))
        if self.timer >= self.life:
            self.remove_from_sprite_lists()

class ParticleSystem:
    def __init__(self):
        self.particles = arcade.SpriteList()

    def make_explosion(self, x, y, count=20):
        for _ in range(count):
            p = Particle(x, y)
            self.particles.append(p)

    def make_coin_effect(self, x, y):
        for _ in range(10):
            p = Particle(x, y)
            p.texture = arcade.make_circle_texture(6, arcade.color.YELLOW)
            self.particles.append(p)

    def make_blood(self, x, y):
        for _ in range(15):
            p = Particle(x, y)
            p.texture = arcade.make_circle_texture(6, arcade.color.RED)
            p.life = random.uniform(1.0, 3.0)
            self.particles.append(p)

    def update(self, delta: float):
        self.particles.update()
        self.particles.update_animation(delta)

    def draw(self):
        self.particles.draw()
