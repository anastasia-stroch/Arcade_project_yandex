import arcade
import random
import math
from constants import *
from enemies import Monster, Spike
from items import Gold, Heart, ExitFlag

class World:
    def __init__(self, level_num: int = 1):
        self.level_num = level_num
        self.ground = arcade.SpriteList()
        self.treasure = arcade.SpriteList()
        self.potions = arcade.SpriteList()
        self.monsters = arcade.SpriteList()
        self.traps = arcade.SpriteList()
        self.exit = None
        self.bg_color = self.get_bg_color(level_num)
        self.moving_platform = None
        self.seed = random.randint(1, 10000)
        random.seed(self.seed + level_num * 1000)
        self.level_style = self.get_level_style(level_num)
        self.create()

    def get_bg_color(self, num):
        colors = [
            arcade.color.DARK_SLATE_GRAY,
            arcade.color.DARK_BLUE_GRAY,
            arcade.color.DARK_GREEN,
            arcade.color.DARK_VIOLET,
            arcade.color.DARK_BROWN,
            arcade.color.DARK_CYAN,
            arcade.color.DARK_RED,
            arcade.color.DARK_ORANGE,
            arcade.color.DARK_MAGENTA,
            arcade.color.DARK_GOLDENROD,
        ]
        return colors[(num - 1) % len(colors)]

    def get_level_style(self, num):
        styles = ["normal", "cave", "castle", "forest", "ice"]
        return styles[(num - 1) % len(styles)]

    def get_ground_color(self):
        if self.level_style == "cave":
            return arcade.color.SIENNA
        elif self.level_style == "castle":
            return arcade.color.GRAY
        elif self.level_style == "forest":
            return arcade.color.DARK_GREEN
        elif self.level_style == "ice":
            return arcade.color.LIGHT_BLUE
        else:
            return arcade.color.WOOD_BROWN

    def position_free(self, x, y, taken, w=30, h=30, margin=10):
        for px, py, pw, ph in taken:
            if (abs(x - px) < (w / 2 + pw / 2 + margin) and
                    abs(y - py) < (h / 2 + ph / 2 + margin)):
                return False
        return True

    def create(self):
        if self.level_style == "cave":
            self.create_cave()
        elif self.level_style == "castle":
            self.create_castle()
        elif self.level_style == "forest":
            self.create_forest()
        elif self.level_style == "ice":
            self.create_ice()
        else:
            self.create_normal()

    def create_normal(self):
        random.seed(self.seed + self.level_num * 1000)
        floor_color = self.get_ground_color()
        for x in range(0, WORLD_WIDTH, TILE_SIZE):
            tile = arcade.Sprite()
            tile.texture = arcade.make_soft_square_texture(TILE_SIZE, floor_color)
            tile.center_x = x + TILE_SIZE // 2
            tile.center_y = TILE_SIZE // 2
            self.ground.append(tile)
        taken = []
        for tile in self.ground:
            taken.append((tile.center_x, tile.center_y, TILE_SIZE, TILE_SIZE))
        platform_spots = []
        sections = 8 + min(self.level_num, 4)
        cur_x = 200
        cur_y = 180
        ground_color = self.get_ground_color()
        for section in range(sections):
            if cur_x > WORLD_WIDTH - 600:
                break
            width_tiles = random.choice([3, 4, 5])
            width = width_tiles * TILE_SIZE
            parts = []
            for i in range(width_tiles):
                x_pos = cur_x + (i * TILE_SIZE)
                tile = arcade.Sprite()
                tile.texture = arcade.make_soft_square_texture(TILE_SIZE, ground_color)
                tile.center_x = x_pos
                tile.center_y = cur_y
                self.ground.append(tile)
                parts.append(tile)
            center_x = cur_x + (width_tiles / 2) * TILE_SIZE
            platform_spots.append((center_x, cur_y, parts))
            for i in range(width_tiles):
                x_pos = cur_x + (i * TILE_SIZE)
                taken.append((x_pos, cur_y, TILE_SIZE, TILE_SIZE))
            coin_count = random.randint(1, 3)
            for _ in range(coin_count):
                coin_x = center_x + random.randint(-width // 4, width // 4)
                coin_y = cur_y + 45
                if self.position_free(coin_x, coin_y, taken, 30, 30, 20):
                    coin = Gold(coin_x, coin_y)
                    self.treasure.append(coin)
                    taken.append((coin_x, coin_y, 30, 30))
            distance = random.randint(150, 300)
            if section % 3 == 0:
                distance = random.randint(300, 400)
            cur_x += width + distance
            height_change = random.randint(-80, 100)
            if self.level_num > 5:
                height_change = random.randint(-100, 120)
            cur_y = max(120, min(350, cur_y + height_change))
        if len(platform_spots) > 2:
            monster_chance = 0.3 + min(self.level_num * 0.05, 0.6)
            max_monsters = min(2 + self.level_num // 2, 8)
            monsters_placed = 0
            for center_x, spot_y, parts in platform_spots[2:]:
                if monsters_placed >= max_monsters:
                    break
                if random.random() < monster_chance:
                    monsters_on_spot = 1
                    if self.level_num > 5 and random.random() < 0.3:
                        monsters_on_spot = 2
                    for _ in range(monsters_on_spot):
                        if monsters_placed >= max_monsters:
                            break
                        monster_x = center_x + random.randint(-width//3, width//3)
                        monster_y = spot_y + 30
                        if self.position_free(monster_x, monster_y, taken, 40, 40, 20):
                            monster = Monster(monster_x, monster_y)
                            monster.platform_parts = parts
                            monster.platform_width = len(parts) * TILE_SIZE
                            monster.start_x = center_x
                            monster.speed = 1.0 + random.random() * 1.0 + (self.level_num * 0.15)
                            monster.direction = 1 if random.random() > 0.5 else -1
                            self.monsters.append(monster)
                            taken.append((monster_x, monster_y, 40, 40))
                            monsters_placed += 1
        gap_pos = random.uniform(0.4, 0.7)
        gap_start = int(WORLD_WIDTH * gap_pos) - 300
        gap_width = 400 + self.level_num * 50
        clear_left = gap_start - 200
        clear_right = gap_start + gap_width + 200
        to_remove = []
        for tile in self.ground:
            if (clear_left < tile.center_x < clear_right and
                    tile.center_y > 100 and tile.center_y < 250):
                to_remove.append(tile)
        for tile in to_remove:
            tile.remove_from_sprite_lists()
        spike_space = max(40, 60 - self.level_num * 2)
        for x in range(int(gap_start), int(gap_start + gap_width), spike_space):
            spike_y = 40 + random.randint(0, 15)
            spike = Spike(x, spike_y)
            self.traps.append(spike)
        move_width = TILE_SIZE * max(2, 4 - self.level_num // 4)
        move_height = TILE_SIZE // 2
        self.moving_platform = arcade.SpriteSolidColor(
            move_width,
            move_height,
            arcade.color.DARK_GRAY
        )
        self.moving_platform.center_x = gap_start + gap_width // 2
        self.moving_platform.center_y = 180
        self.moving_platform.move_speed = 2.5 + self.level_num * 0.2
        self.moving_platform.direction = 1
        self.moving_platform.left_bound = gap_start + 100
        self.moving_platform.right_bound = gap_start + gap_width - 100
        self.ground.append(self.moving_platform)
        coin_x = self.moving_platform.center_x
        coin_y = self.moving_platform.center_y + 45
        if self.position_free(coin_x, coin_y, taken, 30, 30, 15):
            coin = Gold(coin_x, coin_y)
            self.treasure.append(coin)
        final_x = max(clear_right + 100, WORLD_WIDTH - 500)
        final_y = random.choice([120, 150, 180])
        if random.random() > 0.5:
            steps = random.randint(2, 4)
            for i in range(steps):
                step_tiles = random.randint(2, 4)
                for j in range(step_tiles):
                    tile = arcade.Sprite()
                    tile.texture = arcade.make_soft_square_texture(TILE_SIZE, ground_color)
                    tile.center_x = final_x + (i * TILE_SIZE * 2) + (j * TILE_SIZE)
                    tile.center_y = final_y - (i * 40)
                    self.ground.append(tile)
                coin_x = final_x + (i * TILE_SIZE * 2) + (step_tiles * TILE_SIZE) / 2
                coin_y = final_y - (i * 40) + 45
                coin = Gold(coin_x, coin_y)
                self.treasure.append(coin)
        else:
            pyramid = random.randint(2, 3)
            for i in range(pyramid):
                width = pyramid - i
                for j in range(width):
                    tile = arcade.Sprite()
                    tile.texture = arcade.make_soft_square_texture(TILE_SIZE, ground_color)
                    tile.center_x = final_x + (j * TILE_SIZE * 2) - (width * TILE_SIZE)
                    tile.center_y = final_y + (i * TILE_SIZE)
                    self.ground.append(tile)
        exit_x = WORLD_WIDTH - 200
        exit_y = 180
        self.exit = ExitFlag(exit_x, exit_y)
        for tile in self.ground:
            if (abs(tile.center_x - exit_x) < 150 and
                tile.center_y > 100 and
                tile.center_y < 250):
                tile.remove_from_sprite_lists()
        num_spikes = 3 + self.level_num
        for _ in range(num_spikes):
            x = random.randint(300, clear_left - 50)
            if x < 300:
                x = random.randint(clear_right + 50, WORLD_WIDTH - 400)
            y = 40 + random.randint(0, 15)
            spike = Spike(x, y)
            self.traps.append(spike)
        if random.random() < 0.3:
            safe = []
            for center_x, spot_y, _ in platform_spots:
                if abs(center_x - (gap_start + gap_width // 2)) > 500:
                    safe.append((center_x, spot_y))
            if safe:
                heart_spot = random.choice(safe)
                heart_x = heart_spot[0]
                heart_y = heart_spot[1] + 55
                heart = Heart(heart_x, heart_y)
                self.potions.append(heart)

    def create_cave(self):
        self.create_normal()
        for x in range(400, WORLD_WIDTH - 400, 200):
            if random.random() < 0.4:
                spike = Spike(x, SCREEN_HEIGHT - 50)
                spike.texture = arcade.make_soft_square_texture(40, arcade.color.DARK_GRAY)
                self.traps.append(spike)
        self.bg_color = arcade.color.DARK_SLATE_BLUE

    def create_castle(self):
        random.seed(self.seed + self.level_num * 1000)
        for x in range(0, WORLD_WIDTH, TILE_SIZE):
            floor = arcade.Sprite()
            floor.texture = arcade.make_soft_square_texture(TILE_SIZE, arcade.color.DARK_GRAY)
            floor.center_x = x + TILE_SIZE // 2
            floor.center_y = TILE_SIZE // 2
            self.ground.append(floor)
        wall_spots = []
        wall_heights = []
        wall_xs = []
        for i, x in enumerate(range(300, WORLD_WIDTH - 300, 250)):
            if i > 4:
                break
            height = random.randint(2, min(4, 2 + self.level_num // 3))
            wall_xs.append(x)
            wall_heights.append(height)
            wall_parts = []
            for y in range(1, height + 1):
                wall = arcade.Sprite()
                wall.texture = arcade.make_soft_square_texture(TILE_SIZE, arcade.color.GRAY)
                wall.center_x = x
                wall.center_y = TILE_SIZE // 2 + y * TILE_SIZE
                self.ground.append(wall)
                wall_parts.append(wall)
                if y == height and random.random() < 0.4:
                    monster = Monster(x, wall.center_y + 30)
                    monster.platform_parts = wall_parts
                    monster.platform_width = TILE_SIZE
                    monster.start_x = x
                    monster.speed = 0.8 + random.random() * 0.8
                    monster.direction = 1
                    self.monsters.append(monster)
            wall_spots.append((x, TILE_SIZE // 2 + height * TILE_SIZE))
        for i, (x, height_y) in enumerate(wall_spots):
            if i > 0:
                prev_x, prev_height_y = wall_spots[i-1]
                platform_x = x - 100
                platform_y = TILE_SIZE * 2
                step_count = wall_heights[i]
                for step in range(step_count):
                    step_y = platform_y + step * TILE_SIZE
                    for j in range(3):
                        tile = arcade.Sprite()
                        tile.texture = arcade.make_soft_square_texture(TILE_SIZE, arcade.color.WOOD_BROWN)
                        tile.center_x = platform_x + j * TILE_SIZE
                        tile.center_y = step_y
                        self.ground.append(tile)
                        if j == 1 and random.random() < 0.5:
                            coin = Gold(tile.center_x, tile.center_y + 45)
                            self.treasure.append(coin)
        for i in range(len(wall_spots) - 1):
            x1, y1 = wall_spots[i]
            x2, y2 = wall_spots[i + 1]
            if abs(y1 - y2) < TILE_SIZE * 1.5:
                bridge_y = (y1 + y2) // 2
                bridge_len = int(abs(x2 - x1) // TILE_SIZE)
                for j in range(bridge_len):
                    tile = arcade.Sprite()
                    tile.texture = arcade.make_soft_square_texture(TILE_SIZE, arcade.color.WOOD_BROWN)
                    tile.center_x = min(x1, x2) + j * TILE_SIZE + TILE_SIZE // 2
                    tile.center_y = bridge_y
                    self.ground.append(tile)
                    if j % 2 == 0:
                        coin = Gold(tile.center_x, tile.center_y + 45)
                        self.treasure.append(coin)
                        if random.random() < 0.3:
                            monster = Monster(tile.center_x, tile.center_y + 30)
                            monster.platform_parts = [tile]
                            monster.platform_width = TILE_SIZE
                            monster.start_x = tile.center_x
                            monster.speed = 1.0 + random.random() * 0.8
                            monster.direction = 1 if random.random() > 0.5 else -1
                            self.monsters.append(monster)
        exit_x = WORLD_WIDTH - 200
        exit_y = 180
        self.exit = ExitFlag(exit_x, exit_y)

    def create_forest(self):
        self.create_normal()
        for tile in self.ground:
            if tile.center_y > 100:
                tile.texture = arcade.make_soft_square_texture(TILE_SIZE, arcade.color.DARK_GREEN)
        if random.random() < 0.5:
            heart = Heart(WORLD_WIDTH // 2, 200)
            self.potions.append(heart)

    def create_ice(self):
        self.create_normal()
        for tile in self.ground:
            if tile.center_y > 100:
                tile.texture = arcade.make_soft_square_texture(TILE_SIZE, arcade.color.LIGHT_BLUE)

    def update_moving(self, delta):
        if self.moving_platform:
            self.moving_platform.center_x += self.moving_platform.direction * self.moving_platform.move_speed
            if self.moving_platform.center_x >= self.moving_platform.right_bound:
                self.moving_platform.center_x = self.moving_platform.right_bound
                self.moving_platform.direction = -1
            elif self.moving_platform.center_x <= self.moving_platform.left_bound:
                self.moving_platform.center_x = self.moving_platform.left_bound
                self.moving_platform.direction = 1
        for monster in self.monsters:
            if hasattr(monster, 'platform_parts') and monster.platform_parts:
                left = min(p.center_x for p in monster.platform_parts) - monster.platform_parts[0].width / 2 + 30
                right = max(p.center_x for p in monster.platform_parts) + monster.platform_parts[0].width / 2 - 30
                monster.center_x += monster.speed * monster.direction
                if monster.center_x <= left:
                    monster.center_x = left
                    monster.direction = 1
                elif monster.center_x >= right:
                    monster.center_x = right
                    monster.direction = -1
