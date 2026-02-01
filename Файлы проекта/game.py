import random
import arcade
from constants import *
from hero import Hero
from world import World
from database import db


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Рыцарь в замке")

        self.current_screen = "menu"
        self.current_level = 1
        self.max_levels = 10

        self.hero = None
        self.hero_group = None
        self.world = None

        self.coins_saved = 0
        self.score_saved = 0
        self.camera_x = 0
        self.camera_y = 0
        self.key_left = False
        self.key_right = False
        self.key_up = False
        self.can_move = True
        self.blink_timer = 0

        self.menu_choice = 0
        self.menu_items = ["НАЧАТЬ", "РЕКОРДЫ", "СТАТИСТИКА", "ВЫЙТИ"]

        self.show_scores = False
        self.show_stats = False
        self.enter_name = False
        self.player_name = "ИГРОК"
        self.letters = list("АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ1234567890 ")
        self.letter_index = 0

        self.background_list = None
        self.music = None
        self.hit_sound = None

        try:
            self.music = arcade.load_sound("music.mp3")
            arcade.play_sound(self.music, volume=0.2, loop=True)
            self.hit_sound = arcade.load_sound("hit.mp3")
        except:
            pass

        stats = db.get_my_stats()
        if stats and stats['best_level'] > self.max_levels:
            self.max_levels = stats['best_level']

    def init_game(self):
        self.key_left = False
        self.key_right = False
        self.key_up = False
        self.hero = Hero()
        self.hero.coins = self.coins_saved
        self.hero.score = self.score_saved
        self.hero_group = arcade.SpriteList()
        self.hero_group.append(self.hero)
        self.world = World(self.current_level)
        self.current_screen = "game"
        self.can_move = True
        self.hero.center_x = 100
        self.hero.center_y = 300
        self.camera_x = 0
        self.camera_y = 0

        self.background_list = arcade.SpriteList()
        random_num = random.randint(0, 3)
        try:
            if random_num == 0:
                bg_texture = arcade.load_texture("tileset.png")
            elif random_num == 1:
                bg_texture = arcade.load_texture("tileset1.png")
            elif random_num == 2:
                bg_texture = arcade.load_texture("tileset2.png")
            elif random_num == 3:
                bg_texture = arcade.load_texture("tileset3.png")
        except:
            bg_texture = arcade.make_soft_square_texture(64, arcade.color.DARK_BROWN)

        texture_width = bg_texture.width
        texture_height = bg_texture.height
        tiles_x = int(WORLD_WIDTH / texture_width) + 2
        tiles_y = int(WORLD_HEIGHT / texture_height) + 2
        for x in range(tiles_x):
            for y in range(tiles_y):
                bg_tile = arcade.Sprite()
                bg_tile.texture = bg_texture
                bg_tile.center_x = x * texture_width + texture_width / 2
                bg_tile.center_y = y * texture_height + texture_height / 2
                bg_tile.scale = 1.0
                self.background_list.append(bg_tile)

    def move_camera(self):
        target_x = self.hero.center_x - SCREEN_WIDTH / 2
        target_y = self.hero.center_y - SCREEN_HEIGHT / 2
        target_x = max(0, min(target_x, WORLD_WIDTH - SCREEN_WIDTH))
        target_y = max(0, min(target_y, WORLD_HEIGHT - SCREEN_HEIGHT))
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1

    def on_draw(self):
        self.clear()

        if self.current_screen == "menu":
            if self.show_scores:
                self.draw_scores()
            elif self.show_stats:
                self.draw_stats()
            elif self.enter_name:
                self.draw_name_input()
            else:
                self.draw_menu()
            return
        elif self.current_screen == "choose_level":
            self.draw_level_choice()
            return

        if self.background_list:
            self.background_list.draw()

        def draw_sprites(sprite_list):
            for sprite in sprite_list:
                sprite.center_x -= self.camera_x
                sprite.center_y -= self.camera_y
            sprite_list.draw()
            for sprite in sprite_list:
                sprite.center_x += self.camera_x
                sprite.center_y += self.camera_y

        if self.world:
            draw_sprites(self.world.ground)
            draw_sprites(self.world.traps)
            draw_sprites(self.world.monsters)
            draw_sprites(self.world.treasure)
            draw_sprites(self.world.potions)
            if self.world.exit:
                flag = self.world.exit
                flag.center_x -= self.camera_x
                flag.center_y -= self.camera_y
                temp_list = arcade.SpriteList()
                temp_list.append(flag)
                temp_list.draw()
                flag.center_x += self.camera_x
                flag.center_y += self.camera_y

        if self.hero:
            self.hero.center_x -= self.camera_x
            self.hero.center_y -= self.camera_y
            if self.hero_group:
                self.hero_group.draw()
            else:
                hero_list = arcade.SpriteList()
                hero_list.append(self.hero)
                hero_list.draw()
            self.hero.center_x += self.camera_x
            self.hero.center_y += self.camera_y

            self.draw_stats_info()

        if self.current_screen == "lose":
            self.draw_lose_screen()
        elif self.current_screen == "win":
            self.draw_win_screen()

    def draw_menu(self):
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH,
            0, SCREEN_HEIGHT,
            arcade.color.DARK_PASTEL_PURPLE
        )
        castle_w = 400
        castle_h = 200
        castle_x = SCREEN_WIDTH // 2 - castle_w // 2
        castle_y = SCREEN_HEIGHT // 2 - castle_h // 2 + 100
        arcade.draw_lrbt_rectangle_filled(
            left=castle_x,
            right=castle_x + castle_w,
            bottom=castle_y,
            top=castle_y + castle_h,
            color=arcade.color.DARK_YELLOW
        )
        tower_w = 80
        tower_h = 250
        left_tower_x = castle_x - tower_w // 2
        left_tower_y = castle_y + tower_h // 2
        arcade.draw_lrbt_rectangle_filled(
            left=left_tower_x - tower_w // 2,
            right=left_tower_x + tower_w // 2,
            bottom=left_tower_y - tower_h // 2,
            top=left_tower_y + tower_h // 2,
            color=arcade.color.GRAY
        )
        right_tower_x = castle_x + castle_w + tower_w // 2
        arcade.draw_lrbt_rectangle_filled(
            left=right_tower_x - tower_w // 2,
            right=right_tower_x + tower_w // 2,
            bottom=left_tower_y - tower_h // 2,
            top=left_tower_y + tower_h // 2,
            color=arcade.color.GRAY
        )
        window_w = 30
        window_h = 40
        for i in range(4):
            window_x = castle_x + (i + 1) * (castle_w // 5) - window_w // 2
            window_y = castle_y + castle_h // 2 - window_h // 2
            arcade.draw_lrbt_rectangle_filled(
                left=window_x,
                right=window_x + window_w,
                bottom=window_y,
                top=window_y + window_h,
                color=arcade.color.YELLOW
            )
        title = arcade.Text(
            "ЗАМОК САМУРАЯ",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 150,
            arcade.color.GOLD,
            64,
            align="center",
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
        subtitle = arcade.Text(
            "Начни свое приключение!",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 220,
            arcade.color.LIGHT_GRAY,
            28,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )
        for i, item in enumerate(self.menu_items):
            if i == self.menu_choice:
                color = arcade.color.GOLD
            else:
                color = arcade.color.WHITE
            size = 48 if i == self.menu_choice else 36
            text = arcade.Text(
                item,
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - i * 60,
                color,
                size,
                align="center",
                anchor_x="center",
                anchor_y="center",
                bold=(i == self.menu_choice)
            )
            text.draw()
        if int(self.blink_timer * 2) % 2 == 0:
            hint = arcade.Text(
                "Стрелки ВВЕРХ/ВНИЗ для выбора, ENTER для подтверждения",
                SCREEN_WIDTH // 2,
                100,
                arcade.color.LIGHT_GRAY,
                22,
                align="center",
                anchor_x="center",
                anchor_y="center"
            )
            hint.draw()
        controls = arcade.Text(
            "В игре: <- -> движение, SPACE прыжок",
            SCREEN_WIDTH // 2,
            60,
            arcade.color.LIGHT_GRAY,
            20,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )
        title.draw()
        subtitle.draw()
        controls.draw()

    def draw_scores(self):
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.DARK_SLATE_BLUE)
        arcade.Text("ТАБЛИЦА РЕКОРДОВ", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80, arcade.color.GOLD, 48, bold=True,
                    anchor_x="center").draw()

        scores = db.get_top_scores()
        y_pos = SCREEN_HEIGHT - 140

        arcade.Text("№", 100, y_pos, arcade.color.YELLOW, 24, anchor_x="center").draw()
        arcade.Text("ИМЯ", 300, y_pos, arcade.color.YELLOW, 24, anchor_x="center").draw()
        arcade.Text("ОЧКИ", 500, y_pos, arcade.color.YELLOW, 24, anchor_x="center").draw()
        arcade.Text("УРОВЕНЬ", 700, y_pos, arcade.color.YELLOW, 24, anchor_x="center").draw()
        arcade.Text("МОНЕТЫ", 900, y_pos, arcade.color.YELLOW, 24, anchor_x="center").draw()

        if scores:
            for i, score in enumerate(scores):
                y = y_pos - 40 - (i * 40)
                if i == 0:
                    color = arcade.color.GOLD
                elif i == 1:
                    color = arcade.color.SILVER
                elif i == 2:
                    color = arcade.color.BRONZE
                else:
                    color = arcade.color.WHITE

                arcade.Text(f"{i + 1}.", 100, y, color, 22, anchor_x="center").draw()
                arcade.Text(score['name'][:10], 300, y, color, 22, anchor_x="center").draw()
                arcade.Text(f"{score['score']}", 500, y, color, 22, anchor_x="center").draw()
                arcade.Text(f"{score['level']}", 700, y, color, 22, anchor_x="center").draw()
                arcade.Text(f"{score['coins']}", 900, y, color, 22, anchor_x="center").draw()
        else:
            arcade.Text("Пока нет рекордов!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, arcade.color.LIGHT_GRAY, 36,
                        anchor_x="center").draw()

        arcade.Text("ESC - вернуться в меню", SCREEN_WIDTH // 2, 80, arcade.color.LIGHT_GRAY, 24,
                    anchor_x="center").draw()

    def draw_stats(self):
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.DARK_SLATE_GRAY)
        arcade.Text("ВАША СТАТИСТИКА", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80, arcade.color.GOLD, 48, bold=True,
                    anchor_x="center").draw()

        stats = db.get_my_stats()
        if stats:
            y = SCREEN_HEIGHT - 180
            arcade.Text(f"Максимальный уровень:", 300, y, arcade.color.WHITE, 28).draw()
            arcade.Text(f"{stats['best_level']}", 850, y, arcade.color.GREEN, 32, bold=True).draw()

            arcade.Text(f"Всего монет:", 300, y - 60, arcade.color.WHITE, 28).draw()
            arcade.Text(f"{stats['total_coins']}", 850, y - 60, arcade.color.YELLOW, 32, bold=True).draw()

            arcade.Text(f"Всего очков:", 300, y - 120, arcade.color.WHITE, 28).draw()
            arcade.Text(f"{stats['total_score']}", 850, y - 120, arcade.color.CYAN, 32, bold=True).draw()

            arcade.Text(f"Сыграно игр:", 300, y - 180, arcade.color.WHITE, 28).draw()
            arcade.Text(f"{stats['games_count']}", 850, y - 180, arcade.color.ORANGE, 32, bold=True).draw()

        button_y = 150
        arcade.draw_lrbt_rectangle_filled(SCREEN_WIDTH // 2 - 150, SCREEN_WIDTH // 2 + 150, button_y - 25,
                                          button_y + 25, arcade.color.DARK_RED)
        arcade.Text("СБРОСИТЬ ПРОГРЕСС", SCREEN_WIDTH // 2, button_y, arcade.color.WHITE, 24, anchor_x="center").draw()

        arcade.Text("ESC - вернуться в меню | ENTER - сбросить прогресс", SCREEN_WIDTH // 2, button_y + 60,
                    arcade.color.LIGHT_GRAY, 22, anchor_x="center").draw()

    def draw_name_input(self):
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.DARK_BLUE)
        arcade.Text("ВВЕДИТЕ ВАШЕ ИМЯ", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150, arcade.color.GOLD, 48, bold=True,
                    anchor_x="center").draw()

        top = SCREEN_HEIGHT // 2 + 50
        bottom = SCREEN_HEIGHT // 2 - 50
        arcade.draw_lrbt_rectangle_outline(SCREEN_WIDTH // 2 - 250, SCREEN_WIDTH // 2 + 250, bottom, top,
                                           arcade.color.WHITE, 3)

        arcade.Text(self.player_name, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, arcade.color.WHITE, 42,
                    anchor_x="center").draw()

        if int(self.blink_timer * 2) % 2 == 0:
            x = SCREEN_WIDTH // 2 - 100 + (len(self.player_name) * 18)
            arcade.draw_line(x, SCREEN_HEIGHT // 2 - 25, x, SCREEN_HEIGHT // 2 + 25, arcade.color.YELLOW, 3)

        letter = self.letters[self.letter_index]
        arcade.Text(f"Выбранная буква: {letter}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100, arcade.color.YELLOW, 28,
                    anchor_x="center").draw()

        arcade.Text("← → - выбор буквы | SPACE - добавить букву", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150,
                    arcade.color.LIGHT_GRAY, 22, anchor_x="center").draw()
        arcade.Text("BACKSPACE - удалить | ENTER - сохранить", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 180,
                    arcade.color.LIGHT_GRAY, 22, anchor_x="center").draw()
        arcade.Text(f"Ваш результат: {self.score_saved} очков", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120,
                    arcade.color.GREEN, 28, anchor_x="center").draw()

    def draw_level_choice(self):
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH,
            0, SCREEN_HEIGHT,
            arcade.color.DARK_SLATE_GRAY
        )
        title = arcade.Text(
            "ВЫБЕРИ УРОВЕНЬ",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            arcade.color.GOLD,
            48,
            align="center",
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
        stats = db.get_my_stats()
        max_open = stats['best_level'] if stats else self.current_level

        for i in range(1, self.max_levels + 1):
            x = SCREEN_WIDTH // 2 + (i - 5) * 100
            y = SCREEN_HEIGHT // 2
            if i <= max_open:
                color = arcade.color.GREEN if i <= self.current_level else arcade.color.YELLOW
                border = arcade.color.GOLD if i == self.current_level else arcade.color.WHITE
                arcade.draw_lrbt_rectangle_filled(
                    left=x - 30,
                    right=x + 30,
                    bottom=y - 20,
                    top=y + 20,
                    color=color
                )
                arcade.draw_lrbt_rectangle_outline(
                    left=x - 30,
                    right=x + 30,
                    bottom=y - 20,
                    top=y + 20,
                    color=border,
                    border_width=3
                )
                num = arcade.Text(
                    str(i),
                    x,
                    y,
                    arcade.color.WHITE,
                    24,
                    align="center",
                    anchor_x="center",
                    anchor_y="center",
                    bold=True
                )
                num.draw()
            else:
                arcade.draw_lrbt_rectangle_filled(
                    left=x - 30,
                    right=x + 30,
                    bottom=y - 20,
                    top=y + 20,
                    color=arcade.color.DARK_GRAY
                )
                arcade.draw_lrbt_rectangle_outline(
                    left=x - 30,
                    right=x + 30,
                    bottom=y - 20,
                    top=y + 20,
                    color=arcade.color.GRAY,
                    border_width=2
                )
                lock = arcade.Text(
                    "✗",
                    x,
                    y,
                    arcade.color.GRAY,
                    24,
                    align="center",
                    anchor_x="center",
                    anchor_y="center"
                )
                lock.draw()

        arcade.Text(f"Максимальный пройденный: {max_open}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100,
                    arcade.color.LIGHT_GRAY, 28, anchor_x="center").draw()

        if int(self.blink_timer * 2) % 2 == 0:
            hint = arcade.Text(
                "Цифры 1-10 для выбора уровня или ESC для возврата",
                SCREEN_WIDTH // 2,
                100,
                arcade.color.LIGHT_GRAY,
                22,
                align="center",
                anchor_x="center",
                anchor_y="center"
            )
            hint.draw()
        title.draw()

    def draw_stats_info(self):
        lives = arcade.Text(
            f"ЖИЗНИ: {self.hero.lives}",
            20,
            SCREEN_HEIGHT - 40,
            arcade.color.RED,
            28,
            bold=True
        )
        coins = arcade.Text(
            f"МОНЕТЫ: {self.hero.coins}",
            20,
            SCREEN_HEIGHT - 80,
            arcade.color.YELLOW,
            24
        )
        score = arcade.Text(
            f"ОЧКИ: {self.hero.score}",
            SCREEN_WIDTH - 200,
            SCREEN_HEIGHT - 40,
            arcade.color.WHITE,
            28
        )
        level = arcade.Text(
            f"УРОВЕНЬ: {self.current_level}",
            SCREEN_WIDTH - 200,
            SCREEN_HEIGHT - 80,
            arcade.color.GREEN,
            24
        )
        lives.draw()
        coins.draw()
        score.draw()
        level.draw()

    def draw_lose_screen(self):
        arcade.draw_lrbt_rectangle_filled(
            left=0,
            right=SCREEN_WIDTH,
            bottom=0,
            top=SCREEN_HEIGHT,
            color=(0, 0, 0, 180)
        )
        lose = arcade.Text(
            "ПОРАЖЕНИЕ",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 50,
            arcade.color.RED,
            48,
            align="center",
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
        score = arcade.Text(
            f"Очки: {self.hero.score}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            arcade.color.YELLOW,
            32,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )
        coins_text = arcade.Text(
            f"Монет: {self.hero.coins}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 30,
            arcade.color.YELLOW,
            28,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )
        restart = arcade.Text(
            "R - начать заново",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 80,
            arcade.color.WHITE,
            24,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )
        menu = arcade.Text(
            "ESC - в меню",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 120,
            arcade.color.LIGHT_GRAY,
            20,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )
        lose.draw()
        score.draw()
        coins_text.draw()
        restart.draw()
        menu.draw()

    def draw_win_screen(self):
        arcade.draw_lrbt_rectangle_filled(
            left=0,
            right=SCREEN_WIDTH,
            bottom=0,
            top=SCREEN_HEIGHT,
            color=(0, 50, 0, 150)
        )
        win = arcade.Text(
            f"УРОВЕНЬ {self.current_level} ПРОЙДЕН!",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 80,
            arcade.color.GOLD,
            48,
            align="center",
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
        score = arcade.Text(
            f"Очки: {self.hero.score}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 + 30,
            arcade.color.YELLOW,
            32,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )
        coins = arcade.Text(
            f"Монет: {self.hero.coins}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 10,
            arcade.color.YELLOW,
            28,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )
        next_level = arcade.Text(
            "SPACE - следующий уровень",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 60,
            arcade.color.WHITE,
            24,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )
        menu = arcade.Text(
            "ESC - в меню",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2 - 100,
            arcade.color.LIGHT_GRAY,
            20,
            align="center",
            anchor_x="center",
            anchor_y="center"
        )
        win.draw()
        score.draw()
        coins.draw()
        next_level.draw()
        menu.draw()

    def check_ground(self):
        old_x = self.hero.center_x
        old_y = self.hero.center_y
        self.hero.center_x += self.hero.speed_x
        hit_x = arcade.check_for_collision_with_list(self.hero, self.world.ground)
        if hit_x:
            self.hero.center_x = old_x
            self.hero.speed_x = 0
        self.hero.center_y += self.hero.speed_y
        hit_y = arcade.check_for_collision_with_list(self.hero, self.world.ground)
        on_floor = False
        on_moving = False
        for platform in hit_y:
            if self.hero.speed_y <= 0 and self.hero.bottom <= platform.top + 5:
                if abs(self.hero.bottom - platform.top) < 15:
                    self.hero.bottom = platform.top + 1
                    self.hero.speed_y = 0
                    self.hero.jumps_done = 0
                    on_floor = True
                    if (self.world.moving_platform and
                            platform == self.world.moving_platform):
                        on_moving = True
                    break
            elif self.hero.speed_y > 0 and self.hero.top >= platform.bottom - 5:
                self.hero.top = platform.bottom - 1
                self.hero.speed_y = 0
                break
        if on_moving and on_floor and self.world.moving_platform:
            plat = self.world.moving_platform
            move = plat.move_speed * plat.direction
            self.hero.center_x += move
            self.camera_x += move * 0.05
        if arcade.check_for_collision_with_list(self.hero, self.world.ground) and not on_floor:
            self.hero.center_y = old_y
            self.hero.speed_y = 0

    def on_update(self, delta):
        self.blink_timer += delta
        if self.current_screen != "game":
            return
        if self.can_move:
            if self.key_left and not self.key_right:
                self.hero.go_left()
            elif self.key_right and not self.key_left:
                self.hero.go_right()
            else:
                self.hero.speed_x *= 0.8
                if abs(self.hero.speed_x) < 0.5:
                    self.hero.speed_x = 0
        self.hero.update(delta)
        if self.world:
            self.world.update_moving(delta)
        self.check_ground()
        if self.hero.jump_buffer > 0 and self.hero.jumps_done == 0:
            self.hero.jump()
        self.world.monsters.update(delta)
        self.world.treasure.update(delta)
        self.world.potions.update(delta)
        if self.world.exit:
            self.world.exit.update(delta)
        self.check_hits()
        self.move_camera()
        self.check_state()

    def check_traps(self):
        trap_hit = arcade.check_for_collision_with_list(self.hero, self.world.traps)
        for trap in trap_hit:
            if self.hero.invincible <= 0:
                if self.hero.center_x < trap.center_x:
                    push_x = -10
                else:
                    push_x = 10
                if self.hero.center_y < trap.center_y:
                    push_y = 5
                else:
                    push_y = -5
                self.hero.get_hit(trap.damage, push_x, push_y)
                if self.hit_sound:
                    arcade.play_sound(self.hit_sound)
                return

    def check_hits(self):
        coins_hit = arcade.check_for_collision_with_list(
            self.hero, self.world.treasure
        )
        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            self.hero.add_coin()
            self.coins_saved = self.hero.coins
            self.score_saved = self.hero.score
        potions_hit = arcade.check_for_collision_with_list(
            self.hero, self.world.potions
        )
        for potion in potions_hit:
            potion.remove_from_sprite_lists()
            self.hero.heal(potion.value)
        monsters_hit = arcade.check_for_collision_with_list(
            self.hero, self.world.monsters
        )
        for monster in monsters_hit:
            if self.hero.invincible <= 0:
                push = 15 if monster.center_x < self.hero.center_x else -15
                self.hero.get_hit(monster.damage, push)
                if self.hit_sound:
                    arcade.play_sound(self.hit_sound)
        self.check_traps()
        for monster in self.world.monsters:
            monster_traps = arcade.check_for_collision_with_list(monster, self.world.traps)
            if monster_traps:
                monster.remove_from_sprite_lists()
        if self.world.exit:
            if arcade.check_for_collision(self.hero, self.world.exit):
                self.current_screen = "win"
                self.can_move = False
                self.hero.speed_x = 0
                self.coins_saved = self.hero.coins
                self.score_saved = self.hero.score

                db.save_game_result(self.current_level, self.hero.coins, self.hero.score)
                if self.hero.score > 0 and not self.enter_name:
                    self.enter_name = True

    def check_state(self):
        if self.hero.lives <= 0:
            self.coins_saved = self.hero.coins
            self.score_saved = self.hero.score
            self.current_screen = "lose"

            db.save_game_result(self.current_level, self.hero.coins, self.hero.score)
            if self.hero.score > 0 and not self.enter_name:
                self.enter_name = True

        if self.hero.center_y < -100:
            self.hero.get_hit(999)

    def on_key_press(self, key, mod):
        if self.current_screen == "menu":
            if self.show_scores:
                if key == arcade.key.ESCAPE:
                    self.show_scores = False
                return
            elif self.show_stats:
                if key == arcade.key.ESCAPE:
                    self.show_stats = False
                elif key == arcade.key.ENTER:
                    db.clear_all()
                return
            elif self.enter_name:
                if key == arcade.key.LEFT:
                    self.letter_index = (self.letter_index - 1) % len(self.letters)
                elif key == arcade.key.RIGHT:
                    self.letter_index = (self.letter_index + 1) % len(self.letters)
                elif key == arcade.key.SPACE:
                    self.player_name += self.letters[self.letter_index]
                elif key == arcade.key.BACKSPACE:
                    if len(self.player_name) > 0:
                        self.player_name = self.player_name[:-1]
                elif key == arcade.key.ENTER:
                    if self.player_name.strip():
                        db.add_score(self.player_name, self.score_saved, self.current_level, self.coins_saved)
                        self.enter_name = False
                        self.show_scores = True
                elif key == arcade.key.ESCAPE:
                    self.enter_name = False
                return

            if key == arcade.key.UP:
                self.menu_choice = (self.menu_choice - 1) % len(self.menu_items)
            elif key == arcade.key.DOWN:
                self.menu_choice = (self.menu_choice + 1) % len(self.menu_items)
            elif key == arcade.key.ENTER:
                if self.menu_choice == 0:
                    self.current_screen = "choose_level"
                elif self.menu_choice == 1:
                    self.show_scores = True
                elif self.menu_choice == 2:
                    self.show_stats = True
                elif self.menu_choice == 3:
                    arcade.close_window()
            elif key == arcade.key.ESCAPE:
                arcade.close_window()
            return

        elif self.current_screen == "choose_level":
            if key == arcade.key.ESCAPE:
                self.current_screen = "menu"
            elif key in [arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3,
                         arcade.key.KEY_4, arcade.key.KEY_5, arcade.key.KEY_6,
                         arcade.key.KEY_7, arcade.key.KEY_8, arcade.key.KEY_9]:
                level = key - arcade.key.KEY_0
                stats = db.get_my_stats()
                max_open = stats['best_level'] if stats else self.current_level
                if level <= max_open:
                    self.current_level = level
                    self.init_game()
                    self.current_screen = "game"
            elif key == arcade.key.KEY_0 or key == arcade.key.NUM_0:
                self.current_level = 10
                stats = db.get_my_stats()
                max_open = stats['best_level'] if stats else self.current_level
                if 10 <= max_open:
                    self.init_game()
                    self.current_screen = "game"
            return

        elif self.current_screen == "game":
            if key == arcade.key.LEFT or key == arcade.key.A:
                self.key_left = True
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.key_right = True
            elif key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
                if self.hero.jump():
                    self.key_up = True
            elif key == arcade.key.ESCAPE:
                self.current_screen = "menu"
            elif key == arcade.key.R:
                self.init_game()

        elif self.current_screen == "lose":
            if key == arcade.key.R:
                self.init_game()
            elif key == arcade.key.ESCAPE:
                self.current_screen = "menu"

        elif self.current_screen == "win":
            if key == arcade.key.SPACE:
                if self.current_level < self.max_levels:
                    self.current_level += 1
                self.init_game()
            elif key == arcade.key.ESCAPE:
                self.current_screen = "menu"

    def on_key_release(self, key, mod):
        if self.current_screen == "game":
            if key == arcade.key.LEFT or key == arcade.key.A:
                self.key_left = False
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.key_right = False
            elif key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
                self.key_up = False


def start_game():
    game = MyGame()
    arcade.run()


if __name__ == "__main__":
    start_game()
