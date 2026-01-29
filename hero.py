
from constants import *

class Hero(arcade.Sprite):
    def __init__(self):
        texture = arcade.make_soft_square_texture(40, arcade.color.BLUE)
        super().__init__(texture)
        self.scale = 1.0
        self.center_x = 100
        self.center_y = 300
        self.speed_x = 0
        self.speed_y = 0
        self.move_speed = HERO_SPEED
        self.jump_power = JUMP_POWER
        self.jumps_done = 0
        self.max_jumps = 2
        self.jump_buffer = 0
        self.health = START_HEALTH
        self.max_health = START_HEALTH
        self.lives = START_LIVES
        self.coins = 0
        self.score = 0
        self.invincible = 0

    def update(self, delta: float = 1 / 60):
        self.speed_y -= GRAVITY * delta * 60
        if self.speed_y < -MAX_FALL:
            self.speed_y = -MAX_FALL
        if self.jump_buffer > 0:
            self.jump_buffer -= delta
        if self.jumps_done > 0:
            self.speed_x *= 0.9
        else:
            self.speed_x *= 0.8
        if abs(self.speed_x) < 0.1:
            self.speed_x = 0
        if self.invincible > 0:
            self.invincible -= delta
            blink_time = int(self.invincible * 5)
            if blink_time % 2 == 0:
                self.alpha = 150
            else:
                self.alpha = 255
        else:
            self.alpha = 255

    def go_left(self):
        self.speed_x = -self.move_speed

    def go_right(self):
        self.speed_x = self.move_speed

    def jump(self):
        if self.jumps_done < self.max_jumps:
            self.speed_y = self.jump_power
            self.jumps_done += 1
            self.jump_buffer = 0
            return True
        self.jump_buffer = 0.15
        return False

    def get_hit(self, damage: int, push_x: float = 0, push_y: float = 8):
        self.health -= damage
        self.speed_x = push_x
        self.speed_y = push_y
        self.invincible = 1.5
        self.lives = self.health // 25
        if self.lives < 1:
            self.lives = 1
        if self.health <= 0:
            self.lives -= 1
            if self.lives > 0:
                self.respawn()
                return True
        return False

    def respawn(self):
        self.health = self.max_health
        self.center_x = 100
        self.center_y = 300
        self.speed_x = 0
        self.speed_y = 0
        self.jumps_done = 0
        self.jump_buffer = 0
        self.invincible = 2.0

    def add_coin(self, value: int = COIN_WORTH):
        self.coins += 1
        self.score += value

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)
        self.lives = max(1, (self.health + 24) // 25)
