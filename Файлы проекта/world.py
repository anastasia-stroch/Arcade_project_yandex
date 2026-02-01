import arcade
import random
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
        self.background_decor = arcade.SpriteList()
        self.exit = None
        self.moving_platform = None
        self.seed = random.randint(1, 10000)
        random.seed(self.seed + level_num * 1000)
        self.level_style = self.get_level_style(level_num)
        self.create()

    def get_level_style(self, num):
        styles = ["normal", "cave", "castle"]
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
        for pos in taken:
            px, py, pw, ph = pos
            if abs(x - px) < 100 and abs(y - py) < 100:
                return False
        return True

    def create(self):
        if self.level_style == "cave":
            self.create_cave()
        elif self.level_style == "castle":
            self.create_castle()
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

        current_x = 200
        current_y = 150

        for i in range(3):
            tile = arcade.Sprite()
            tile.texture = arcade.make_soft_square_texture(TILE_SIZE, arcade.color.GRAY)
            tile.center_x = current_x + i * TILE_SIZE
            tile.center_y = current_y
            self.ground.append(tile)

        coin = Gold(current_x + TILE_SIZE, current_y + 45)
        self.treasure.append(coin)

        platforms_created = 0
        max_platforms = 8 + self.level_num

        while current_x < WORLD_WIDTH - 500 and platforms_created < max_platforms:
            gap_width = random.randint(100, 200)
            current_x += gap_width

            height_change = random.choice([-TILE_SIZE, 0, TILE_SIZE, TILE_SIZE * 2])
            if platforms_created % 3 == 0:
                height_change = TILE_SIZE * 2
            current_y = max(150, min(400, current_y + height_change))

            platform_length = random.randint(2, 4)

            for i in range(platform_length):
                tile = arcade.Sprite()
                tile.texture = arcade.make_soft_square_texture(TILE_SIZE, arcade.color.GRAY)
                tile.center_x = current_x + i * TILE_SIZE
                tile.center_y = current_y
                self.ground.append(tile)
                if i == platform_length // 2 and random.random() < 0.5:
                    coin = Gold(tile.center_x, tile.center_y + 45)
                    self.treasure.append(coin)

            platforms_created += 1

            if platforms_created > 2 and random.random() < 0.4:
                monster_x = current_x + (platform_length * TILE_SIZE) // 2
                monster_y = current_y + 30
                monster = Monster(monster_x, monster_y)
                monster.platform_parts = []
                for i in range(platform_length):
                    for tile in self.ground:
                        if (abs(tile.center_x - (current_x + i * TILE_SIZE)) < 5 and
                                abs(tile.center_y - current_y) < 5):
                            monster.platform_parts.append(tile)
                if monster.platform_parts:
                    monster.platform_width = len(monster.platform_parts) * TILE_SIZE
                    monster.start_x = current_x + (platform_length * TILE_SIZE) // 2
                    monster.speed = 1.0 + random.random() * 0.8
                    monster.direction = 1 if random.random() > 0.5 else -1
                    self.monsters.append(monster)

            current_x += platform_length * TILE_SIZE + random.randint(50, 100)

        for i in range(random.randint(2, 3)):
            fly_x = 500 + i * 300
            fly_y = 250 + random.randint(-50, 50)
            fly_length = random.randint(2, 3)

            if i == 1:
                self.moving_platform = arcade.SpriteSolidColor(
                    fly_length * TILE_SIZE,
                    TILE_SIZE // 2,
                    arcade.color.DARK_GRAY
                )
                self.moving_platform.center_x = fly_x
                self.moving_platform.center_y = fly_y
                self.moving_platform.move_speed = 2.0
                self.moving_platform.direction = 1
                self.moving_platform.left_bound = fly_x - 100
                self.moving_platform.right_bound = fly_x + 100
                self.ground.append(self.moving_platform)

                coin = Gold(fly_x, fly_y + 45)
                self.treasure.append(coin)
            else:
                for j in range(fly_length):
                    tile = arcade.Sprite()
                    tile.texture = arcade.make_soft_square_texture(TILE_SIZE, arcade.color.LIGHT_GRAY)
                    tile.center_x = fly_x + j * TILE_SIZE
                    tile.center_y = fly_y
                    self.ground.append(tile)

                if random.random() < 0.7:
                    coin = Gold(fly_x + (fly_length * TILE_SIZE) // 2, fly_y + 45)
                    self.treasure.append(coin)

        for i in range(3 + self.level_num):
            spike_x = random.randint(300, WORLD_WIDTH - 400)
            on_floor = False
            for tile in self.ground:
                if abs(tile.center_x - spike_x) < 50 and tile.center_y < 100:
                    on_floor = True
                    break
            if on_floor:
                spike = Spike(spike_x, 40)
                self.traps.append(spike)

        heart_x = WORLD_WIDTH // 2
        heart_y = 200
        heart = Heart(heart_x, heart_y)
        self.potions.append(heart)

        exit_platform_length = 4
        exit_x = WORLD_WIDTH - 300
        exit_y = 180

        for i in range(exit_platform_length):
            tile = arcade.Sprite()
            tile.texture = arcade.make_soft_square_texture(TILE_SIZE, arcade.color.GOLD)
            tile.center_x = exit_x + i * TILE_SIZE
            tile.center_y = exit_y
            self.ground.append(tile)

        final_coin = Gold(exit_x + (exit_platform_length * TILE_SIZE) // 2, exit_y + 60)
        self.treasure.append(final_coin)

        self.exit = ExitFlag(exit_x + (exit_platform_length * TILE_SIZE) // 2, exit_y + 120)

        last_platform_end = current_x
        last_platform_y = current_y

        if last_platform_end < exit_x - 200:
            steps = 3
            for step in range(steps):
                step_x = last_platform_end + step * 150
                step_y = last_platform_y - step * 40

                for i in range(2):
                    tile = arcade.Sprite()
                    tile.texture = arcade.make_soft_square_texture(TILE_SIZE, arcade.color.GRAY)
                    tile.center_x = step_x + i * TILE_SIZE
                    tile.center_y = step_y
                    self.ground.append(tile)

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
            left = min(p.center_x for p in monster.platform_parts) - monster.platform_parts[0].width / 2 + 30
            right = max(p.center_x for p in monster.platform_parts) + monster.platform_parts[0].width / 2 - 30
            monster.center_x += monster.speed * monster.direction
            if monster.center_x <= left:
                monster.center_x = left
                monster.direction = 1
            elif monster.center_x >= right:
                monster.center_x = right
                monster.direction = -1