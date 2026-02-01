import arcade
from constants import *


class Hero(arcade.Sprite):
    def __init__(self, skin_selected=0):
        self.skin_selected = skin_selected
        self.textures_list = []
        self.flipped_textures = []
        if self.skin_selected == 1:
            print("scin selected")
            for i in range(1, 7):
                texture_path = f"textures/Running_hero{i}b.png"
                texture = arcade.load_texture(texture_path)
                self.textures_list.append(texture)
                texture_path = f"textures/Running_hero{i}b (1).png"
                texture = arcade.load_texture(texture_path)
                self.flipped_textures.append(texture)
        else:
            for i in range(1, 7):
                texture_path = f"textures/Running_hero{i}.png"
                texture = arcade.load_texture(texture_path)
                self.textures_list.append(texture)
                texture_path = f"textures/Running_hero{i} (1).png"
                texture = arcade.load_texture(texture_path)
                self.flipped_textures.append(texture)
        super().__init__(self.textures_list[0])
        self.base_width = 100
        self.base_height = 100

        self.width = self.base_width
        self.height = self.base_height

        self.anchor_x = 0.5
        self.anchor_y = 0.5

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

        self.facing_right = True
        self.animation_frame = 1
        self.animation_timer = 0
        self.frame_duration = 0.12

        self.current_state = "idle"
        self.is_moving = False

    def update(self, delta: float = 1 / 60):
        self.speed_y -= GRAVITY * delta * 60
        if self.speed_y < -MAX_FALL:
            self.speed_y = -MAX_FALL

        if self.jump_buffer > 0:
            self.jump_buffer -= delta

        if self.jumps_done > 0:
            self.speed_x *= 0.95
        else:
            self.speed_x *= 0.85

        if abs(self.speed_x) < 0.1:
            self.speed_x = 0

        on_ground = self.jumps_done == 0
        self.is_moving = abs(self.speed_x) > 0.5

        old_state = self.current_state

        if not on_ground:
            if self.speed_y > 0:
                self.current_state = "jumping"
            else:
                self.current_state = "falling"
        elif self.is_moving:
            self.current_state = "running"
        else:
            self.current_state = "idle"

        if self.speed_x > 0.5:
            self.facing_right = True
        elif self.speed_x < -0.5:
            self.facing_right = False

        if old_state != "running" and self.current_state == "running":
            self.animation_frame = 1
            self.animation_timer = 0
        elif old_state == "running" and self.current_state == "idle":
            self.animation_frame = 0
            self.animation_timer = 0

        self.update_animation(delta)

        if self.invincible > 0:
            self.invincible -= delta
            blink_time = int(self.invincible * 5)
            self.alpha = 150 if blink_time % 2 == 0 else 255
        else:
            self.alpha = 255

    def update_animation(self, delta: float):
        if self.current_state == "idle":
            self.set_texture_simple(0)

        elif self.current_state == "running":
            self.animation_timer += delta

            if self.animation_timer >= self.frame_duration:
                self.animation_timer = 0
                self.animation_frame += 1

                if self.animation_frame > 5:
                    self.animation_frame = 1

                if self.animation_frame < 1:
                    self.animation_frame = 1

            self.set_texture_simple(self.animation_frame)

        elif self.current_state == "jumping":
            self.set_texture_simple(2)

        elif self.current_state == "falling":
            self.set_texture_simple(2)

    def set_texture_simple(self, frame_index: int):
        old_center_x = self.center_x
        old_center_y = self.center_y

        texture = self.get_texture_by_frame(frame_index)
        if texture:
            self.texture = texture

        self.center_x = old_center_x
        self.center_y = old_center_y

    def get_texture_by_frame(self, frame_index: int):
        if 0 <= frame_index < len(self.textures_list):
            if self.facing_right:
                return self.textures_list[frame_index]
            else:
                if frame_index < len(self.flipped_textures):
                    return self.flipped_textures[frame_index]
                else:
                    return self.textures_list[frame_index]
        return self.textures_list[0]

    def go_left(self):
        self.speed_x = -self.move_speed
        self.facing_right = False

    def go_right(self):
        self.speed_x = self.move_speed
        self.facing_right = True

    def jump(self):
        if self.jumps_done < self.max_jumps:
            self.speed_y = self.jump_power
            self.jumps_done += 1
            self.jump_buffer = 0
            self.current_state = "jumping"
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
        self.current_state = "idle"
        self.animation_frame = 1
        self.animation_timer = 0
        self.is_moving = False
        self.set_texture_simple(0)

    def add_coin(self, value: int = COIN_WORTH):
        self.coins += 1
        self.score += value

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)
        self.lives = max(1, (self.health + 24) // 25)
