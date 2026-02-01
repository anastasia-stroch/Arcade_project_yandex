import arcade
from constants import *
from hero import Hero
from world import World
import random
from database import db


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Рыцарь в замке")
        self.screen = "menu"
        self.level = 1
        self.max_levels = 10
        self.hero = None
        self.world = None
        self.coins = 0
        self.score = 0
        self.camera_x = 0
        self.camera_y = 0
        self.key_left = False
        self.key_right = False
        self.key_up = False
        self.can_move = True
        self.blink = 0
        self.menu_selected = 0
        self.menu_options = ["НАЧАТЬ", "РЕКОРДЫ", "СТАТИСТИКА", "ВЫЙТИ"]

        self.show_scores = False
        self.show_stats = False
        self.enter_name = False
        self.player_name = "ИГРОК"
        self.letters = list("АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ1234567890 ")
        self.letter_index = 0

        try:
            self.music = arcade.load_sound("music.mp3")
            arcade.play_sound(self.music, volume=0.2, loop=True)
            self.hit_sound = arcade.load_sound("hit.mp3")
        except:
            ...

        stats = db.get_my_stats()
        if stats:
            self.max_levels = max(10, stats['best_level'])

    def start_game(self):
        self.key_left = False
        self.key_right = False
        self.key_up = False
        self.hero = Hero()
        self.hero.coins = self.coins
        self.hero.score = self.score
        self.world = World(self.level)
        self.screen = "game"
        self.can_move = True
        self.hero.center_x = 100
        self.hero.center_y = 300
        self.camera_x = 0
        self.camera_y = 0
        self.backgrounds = arcade.SpriteList()

        bg_choice = random.choice(["tileset1", "tileset"])
        try:
            bg = arcade.load_texture(f"textures/{bg_choice}.png")
        except:
            try:
                bg = arcade.load_texture(f"{bg_choice}.png")
            except:
                bg = arcade.make_soft_square_texture(64, arcade.color.DARK_BROWN)

        w = bg.width
        h = bg.height
        tiles_x = int(WORLD_WIDTH / w) + 2
        tiles_y = int(WORLD_HEIGHT / h) + 2

        for x in range(tiles_x):
            for y in range(tiles_y):
                tile = arcade.Sprite()
                tile.texture = bg
                tile.center_x = x * w + w / 2
                tile.center_y = y * h + h / 2
                self.backgrounds.append(tile)

    def move_camera(self):
        target_x = self.hero.center_x - SCREEN_WIDTH / 2
        target_y = self.hero.center_y - SCREEN_HEIGHT / 2
        target_x = max(0, min(target_x, WORLD_WIDTH - SCREEN_WIDTH))
        target_y = max(0, min(target_y, WORLD_HEIGHT - SCREEN_HEIGHT))
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1

    def on_draw(self):
        self.clear()

        if self.screen == "menu":
            if self.show_scores:
                self.draw_scores()
            elif self.show_stats:
                self.draw_stats()
            elif self.enter_name:
                self.draw_name_input()
            else:
                self.draw_menu()
            return
        elif self.screen == "choose_level":
            self.draw_levels()
            return

        if self.backgrounds:
            self.backgrounds.draw()

        def draw_list(sprites):
            for s in sprites:
                s.center_x -= self.camera_x
                s.center_y -= self.camera_y
            sprites.draw()
            for s in sprites:
                s.center_x += self.camera_x
                s.center_y += self.camera_y

        draw_list(self.world.ground)
        draw_list(self.world.traps)
        draw_list(self.world.monsters)
        draw_list(self.world.treasure)
        draw_list(self.world.potions)

        if self.world.exit:
            flag = self.world.exit
            flag.center_x -= self.camera_x
            flag.center_y -= self.camera_y
            arcade.SpriteList().append(flag).draw()
            flag.center_x += self.camera_x
            flag.center_y += self.camera_y

        self.hero.center_x -= self.camera_x
        self.hero.center_y -= self.camera_y
        arcade.SpriteList().append(self.hero).draw()
        self.hero.center_x += self.camera_x
        self.hero.center_y += self.camera_y

        self.draw_info()

        if self.screen == "lose":
            self.draw_lose()
        elif self.screen == "win":
            self.draw_win()

    def draw_menu(self):
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.DARK_PASTEL_PURPLE)

        castle_x = SCREEN_WIDTH // 2 - 200
        castle_y = SCREEN_HEIGHT // 2 - 50
        arcade.draw_lrbt_rectangle_filled(castle_x, castle_x + 400, castle_y, castle_y + 200, arcade.color.DARK_YELLOW)

        tower_y = castle_y + 125
        arcade.draw_lrbt_rectangle_filled(castle_x - 40, castle_x, tower_y - 125, tower_y + 125, arcade.color.GRAY)
        arcade.draw_lrbt_rectangle_filled(castle_x + 400, castle_x + 440, tower_y - 125, tower_y + 125,
                                          arcade.color.GRAY)

        for i in range(4):
            window_x = castle_x + (i + 1) * 80 + 20
            window_y = castle_y + 100
            arcade.draw_lrbt_rectangle_filled(window_x, window_x + 30, window_y - 20, window_y + 20,
                                              arcade.color.YELLOW)

        arcade.Text("ЗАМОК САМУРАЯ", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150, arcade.color.GOLD, 64, bold=True,
                    anchor_x="center").draw()
        arcade.Text("Начни свое приключение!", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 220, arcade.color.LIGHT_GRAY, 28,
                    anchor_x="center").draw()

        for i, item in enumerate(self.menu_options):
            color = arcade.color.GOLD if i == self.menu_selected else arcade.color.WHITE
            size = 48 if i == self.menu_selected else 36
            bold = i == self.menu_selected
            arcade.Text(item, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - i * 60, color, size, bold=bold,
                        anchor_x="center").draw()

        if int(self.blink * 2) % 2 == 0:
            arcade.Text("Стрелки ВВЕРХ/ВНИЗ для выбора, ENTER для подтверждения", SCREEN_WIDTH // 2, 100,
                        arcade.color.LIGHT_GRAY, 22, anchor_x="center").draw()

        arcade.Text("В игре: <- -> движение, SPACE прыжок", SCREEN_WIDTH // 2, 60, arcade.color.LIGHT_GRAY, 20,
                    anchor_x="center").draw()

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
        if bottom < top:
            arcade.draw_lrbt_rectangle_outline(SCREEN_WIDTH // 2 - 250, SCREEN_WIDTH // 2 + 250, bottom, top,
                                               arcade.color.WHITE, 3)

        arcade.Text(self.player_name, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, arcade.color.WHITE, 42,
                    anchor_x="center").draw()

        if int(self.blink * 2) % 2 == 0:
            x = SCREEN_WIDTH // 2 - 100 + (len(self.player_name) * 18)
            arcade.draw_line(x, SCREEN_HEIGHT // 2 - 25, x, SCREEN_HEIGHT // 2 + 25, arcade.color.YELLOW, 3)

        letter = self.letters[self.letter_index]
        arcade.Text(f"Выбранная буква: {letter}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100, arcade.color.YELLOW, 28,
                    anchor_x="center").draw()

        arcade.Text("← → - выбор буквы | SPACE - добавить букву", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150,
                    arcade.color.LIGHT_GRAY, 22, anchor_x="center").draw()
        arcade.Text("BACKSPACE - удалить | ENTER - сохранить", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 180,
                    arcade.color.LIGHT_GRAY, 22, anchor_x="center").draw()
        arcade.Text(f"Ваш результат: {self.score} очков", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120,
                    arcade.color.GREEN, 28, anchor_x="center").draw()

    def draw_levels(self):
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.DARK_SLATE_GRAY)
        arcade.Text("ВЫБЕРИ УРОВЕНЬ", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, arcade.color.GOLD, 48, bold=True,
                    anchor_x="center").draw()

        stats = db.get_my_stats()
        max_open = stats['best_level'] if stats else 1

        for i in range(1, self.max_levels + 1):
            x = SCREEN_WIDTH // 2 + (i - 5) * 100
            y = SCREEN_HEIGHT // 2

            if i <= max_open:
                color = arcade.color.GREEN if i <= self.level else arcade.color.YELLOW
                border = arcade.color.GOLD if i == self.level else arcade.color.WHITE
                arcade.draw_lrbt_rectangle_filled(x - 30, x + 30, y - 20, y + 20, color)
                arcade.draw_lrbt_rectangle_outline(x - 30, x + 30, y - 20, y + 20, border, 3)
                arcade.Text(str(i), x, y, arcade.color.WHITE, 24, bold=True, anchor_x="center").draw()
            else:
                arcade.draw_lrbt_rectangle_filled(x - 30, x + 30, y - 20, y + 20, arcade.color.DARK_GRAY)
                arcade.draw_lrbt_rectangle_outline(x - 30, x + 30, y - 20, y + 20, arcade.color.GRAY, 2)
                arcade.Text("✗", x, y, arcade.color.GRAY, 24, anchor_x="center").draw()

        arcade.Text(f"Максимальный пройденный: {max_open}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100,
                    arcade.color.LIGHT_GRAY, 28, anchor_x="center").draw()

        if int(self.blink * 2) % 2 == 0:
            arcade.Text("Цифры 1-10 для выбора уровня или ESC для возврата", SCREEN_WIDTH // 2, 100,
                        arcade.color.LIGHT_GRAY, 22, anchor_x="center").draw()

    def draw_info(self):
        arcade.Text(f"ЖИЗНИ: {self.hero.lives}", 20, SCREEN_HEIGHT - 40, arcade.color.RED, 28, bold=True).draw()
        arcade.Text(f"МОНЕТЫ: {self.hero.coins}", 20, SCREEN_HEIGHT - 80, arcade.color.YELLOW, 24).draw()
        arcade.Text(f"ОЧКИ: {self.hero.score}", SCREEN_WIDTH - 200, SCREEN_HEIGHT - 40, arcade.color.WHITE, 28).draw()
        arcade.Text(f"УРОВЕНЬ: {self.level}", SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80, arcade.color.GREEN, 24).draw()

    def draw_lose(self):
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (0, 0, 0, 180))
        arcade.Text("ПОРАЖЕНИЕ", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, arcade.color.RED, 48, bold=True,
                    anchor_x="center").draw()
        arcade.Text(f"Очки: {self.hero.score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, arcade.color.YELLOW, 32,
                    anchor_x="center").draw()
        arcade.Text(f"Монет: {self.hero.coins}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30, arcade.color.YELLOW, 28,
                    anchor_x="center").draw()
        arcade.Text("R - начать заново", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80, arcade.color.WHITE, 24,
                    anchor_x="center").draw()
        arcade.Text("ESC - в меню", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120, arcade.color.LIGHT_GRAY, 20,
                    anchor_x="center").draw()

    def draw_win(self):
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (0, 50, 0, 150))
        arcade.Text(f"УРОВЕНЬ {self.level} ПРОЙДЕН!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, arcade.color.GOLD, 48,
                    bold=True, anchor_x="center").draw()
        arcade.Text(f"Очки: {self.hero.score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30, arcade.color.YELLOW, 32,
                    anchor_x="center").draw()
        arcade.Text(f"Монет: {self.hero.coins}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10, arcade.color.YELLOW, 28,
                    anchor_x="center").draw()
        arcade.Text("SPACE - следующий уровень", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60, arcade.color.WHITE, 24,
                    anchor_x="center").draw()
        arcade.Text("ESC - в меню", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100, arcade.color.LIGHT_GRAY, 20,
                    anchor_x="center").draw()

    def check_ground(self):
        old_x = self.hero.center_x
        old_y = self.hero.center_y
        self.hero.center_x += self.hero.speed_x
        if arcade.check_for_collision_with_list(self.hero, self.world.ground):
            self.hero.center_x = old_x
            self.hero.speed_x = 0

        self.hero.center_y += self.hero.speed_y
        hit = arcade.check_for_collision_with_list(self.hero, self.world.ground)
        on_ground = False

        for p in hit:
            if self.hero.speed_y <= 0 and self.hero.bottom <= p.top + 5:
                if abs(self.hero.bottom - p.top) < 15:
                    self.hero.bottom = p.top + 1
                    self.hero.speed_y = 0
                    self.hero.jumps_done = 0
                    on_ground = True
                    if self.world.moving_platform and p == self.world.moving_platform:
                        move = self.world.moving_platform.move_speed * self.world.moving_platform.direction
                        self.hero.center_x += move
                        self.camera_x += move * 0.05
                    break
            elif self.hero.speed_y > 0 and self.hero.top >= p.bottom - 5:
                self.hero.top = p.bottom - 1
                self.hero.speed_y = 0
                break

        if arcade.check_for_collision_with_list(self.hero, self.world.ground) and not on_ground:
            self.hero.center_y = old_y
            self.hero.speed_y = 0

    def on_update(self, delta):
        self.blink += delta
        if self.screen != "game":
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

        self.check_collisions()
        self.move_camera()
        self.check_game_state()

    def check_collisions(self):
        coins_hit = arcade.check_for_collision_with_list(self.hero, self.world.treasure)
        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            self.hero.add_coin()
            self.coins = self.hero.coins
            self.score = self.hero.score

        hearts_hit = arcade.check_for_collision_with_list(self.hero, self.world.potions)
        for heart in hearts_hit:
            heart.remove_from_sprite_lists()
            self.hero.heal(heart.value)

        monsters_hit = arcade.check_for_collision_with_list(self.hero, self.world.monsters)
        for monster in monsters_hit:
            if self.hero.invincible <= 0:
                push = 15 if monster.center_x < self.hero.center_x else -15
                self.hero.get_hit(monster.damage, push)
                try:
                    arcade.play_sound(self.hit_sound)
                except:
                    ...

        traps_hit = arcade.check_for_collision_with_list(self.hero, self.world.traps)
        for trap in traps_hit:
            if self.hero.invincible <= 0:
                push_x = -10 if self.hero.center_x < trap.center_x else 10
                push_y = 5 if self.hero.center_y < trap.center_y else -5
                self.hero.get_hit(trap.damage, push_x, push_y)
                try:
                    arcade.play_sound(self.hit_sound)
                except:
                    ...

        for monster in self.world.monsters:
            if arcade.check_for_collision_with_list(monster, self.world.traps):
                monster.remove_from_sprite_lists()

        if self.world.exit:
            if arcade.check_for_collision(self.hero, self.world.exit):
                self.screen = "win"
                self.can_move = False
                self.hero.speed_x = 0
                self.coins = self.hero.coins
                self.score = self.hero.score

                db.save_game_result(self.level, self.hero.coins, self.hero.score)
                if self.hero.score > 0:
                    db.add_score("ИГРОК", self.hero.score, self.level, self.hero.coins)

    def check_game_state(self):
        if self.hero.lives <= 0:
            self.coins = self.hero.coins
            self.score = self.hero.score
            self.screen = "lose"

            db.save_game_result(self.level, self.hero.coins, self.hero.score)
            if self.hero.score > 0:
                db.add_score("ИГРОК", self.hero.score, self.level, self.hero.coins)

        if self.hero.center_y < -100:
            self.hero.get_hit(999)

    def on_key_press(self, key, mod):
        if self.screen == "menu":
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
                        db.add_score(self.player_name, self.score, self.level, self.coins)
                        self.enter_name = False
                        self.show_scores = True
                elif key == arcade.key.ESCAPE:
                    self.enter_name = False
                return

            if key == arcade.key.UP:
                self.menu_selected = (self.menu_selected - 1) % len(self.menu_options)
            elif key == arcade.key.DOWN:
                self.menu_selected = (self.menu_selected + 1) % len(self.menu_options)
            elif key == arcade.key.ENTER:
                if self.menu_selected == 0:
                    self.screen = "choose_level"
                elif self.menu_selected == 1:
                    self.show_scores = True
                elif self.menu_selected == 2:
                    self.show_stats = True
                elif self.menu_selected == 3:
                    arcade.close_window()
            elif key == arcade.key.ESCAPE:
                arcade.close_window()
            return

        elif self.screen == "choose_level":
            if key == arcade.key.ESCAPE:
                self.screen = "menu"
            elif key in [arcade.key.KEY_1, arcade.key.KEY_2, arcade.key.KEY_3,
                         arcade.key.KEY_4, arcade.key.KEY_5, arcade.key.KEY_6,
                         arcade.key.KEY_7, arcade.key.KEY_8, arcade.key.KEY_9]:
                lvl = key - arcade.key.KEY_0
                stats = db.get_my_stats()
                max_open = stats['best_level'] if stats else 1
                if lvl <= max_open:
                    self.level = lvl
                    self.start_game()
                    self.screen = "game"
            elif key == arcade.key.KEY_0 or key == arcade.key.NUM_0:
                self.level = 10
                stats = db.get_my_stats()
                max_open = stats['best_level'] if stats else 1
                if 10 <= max_open:
                    self.start_game()
                    self.screen = "game"
            return

        elif self.screen == "game":
            if key == arcade.key.LEFT or key == arcade.key.A:
                self.key_left = True
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.key_right = True
            elif key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
                if self.hero.jump():
                    self.key_up = True
            elif key == arcade.key.ESCAPE:
                self.screen = "menu"
            elif key == arcade.key.R:
                self.start_game()

        elif self.screen == "lose":
            if key == arcade.key.R:
                self.start_game()
            elif key == arcade.key.ESCAPE:
                self.screen = "menu"

        elif self.screen == "win":
            if key == arcade.key.SPACE:
                if self.level < self.max_levels:
                    self.level += 1
                self.start_game()
            elif key == arcade.key.ESCAPE:
                self.screen = "menu"

    def on_key_release(self, key, mod):
        if self.screen == "game":
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