"""
Integrantes:
- Leonardo Candio
- Renzo Acervo
- Diego Diaz
- Alejandro Barturen
- Nicolas Arce

LINK VIDEO: https://drive.google.com/file/d/15z9m-ZPqr6t9TvO4jMjdmx9K3rCVQFCk/view?usp=sharing
"""

import pygame as pg
import os
import random
import csv
import json
import assets.button as button
from pathlib import Path


pg.mixer.init()
pg.init()

GAMETITLE = "Graveyard Adventures"
gameRunning = True
current_dir = os.path.dirname(__file__)


# Loading score data from JSON file
with open((Path(f"{current_dir}/assets/scores.json")), "r") as scores_json:
    try:
        scores = json.load(scores_json)
    except json.decoder.JSONDecodeError:
        scores = {}


# Init screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = int(SCREEN_WIDTH * 9 / 16)
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption(GAMETITLE)

# Set framerate
clock = pg.time.Clock()
FPS = 60

# Game variables
BACKGROUND = pg.image.load(
    Path(f"{current_dir}/assets/maps/bg.png")).convert_alpha()
pumpkin_img = pg.image.load(
    f"{current_dir}/assets/maps/items/pumpkin.png"
).convert_alpha()


GRAVITY = 0.4
S = 0.23
ROWS = 9
COLS = 126
TILE_SIZE = SCREEN_HEIGHT // ROWS
SCROLL_THRESH = 6 * TILE_SIZE
TILE_TYPES = len(os.listdir(f"{current_dir}/assets/maps/tiles"))
MAX_LEVELS = 5
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False
loop = 0
leaderboard_open = False
finish_game = False
global_score = 0

# Tiles
img_list = []
for x in range(TILE_TYPES):
    img = pg.image.load(f"{current_dir}/assets/maps/tiles/tile{x}.png")
    if x in range(17) or x in [20, 21, 28, 30]:
        img = pg.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# load music
# bg music
pg.mixer.music.load(f"{current_dir}/assets/audio/game.mp3")
pg.mixer.music.set_volume(0.1)
pg.mixer.music.play(-1, 0.0, 3000)

jump_fx = pg.mixer.Sound(f"{current_dir}/assets/audio/jump.wav")
death_fx = pg.mixer.Sound(f"{current_dir}/assets/audio/death.flac")
item_fx = pg.mixer.Sound(f"{current_dir}/assets/audio/item.mp3")
extralife_fx = pg.mixer.Sound(f"{current_dir}/assets/audio/extralife.wav")
jump_fx.set_volume(0.05)
death_fx.set_volume(0.05)
item_fx.set_volume(3)
extralife_fx.set_volume(0.5)

# Gui
start_img = pg.image.load(f"{current_dir}/assets/gui/start.png")
star_img = pg.image.load(f"{current_dir}/assets/gui/star.png")
exit_img = pg.image.load(f"{current_dir}/assets/gui/exit.png.")
restart_img = pg.image.load(f"{current_dir}/assets/gui/restart.png.")
leaderboard_img = pg.image.load(
    f"{current_dir}/assets/gui/leaderboard.png.")
leaderboard_panel_img = pg.image.load(
    f"{current_dir}/assets/gui/leaderboard_panel.png."
)
input_img = pg.image.load(f"{current_dir}/assets/gui/input.png.")
save_img = pg.image.load(f"{current_dir}/assets/gui/save.png.")


# Player variables
moving_left = False
moving_right = False


font = pg.font.Font(f"{current_dir}/assets/maps/BRLNSDB.TTF", 30)
font_title = pg.font.Font(f"{current_dir}/assets/maps/BRLNSDB.TTF", 50)
font_input = pg.font.Font(f"{current_dir}/assets/maps/BRLNSDB.TTF", 40)
user_text = ""


def draw_text(text, font, color, xpos, ypos):
    text_img = font.render(text, True, color)
    screen.blit(text_img, (xpos, ypos))


def drawBG():
    screen.blit(BACKGROUND, (0, 0))


def reset_level():
    zombie_group.empty()
    for group in groups:
        group.empty()

    return [[-1 for _ in range(COLS)] for __ in range(ROWS)]


def ss(scale, c="z"):
    return scale * 0.60 if c == "p" else scale


class Entity(pg.sprite.Sprite):  # Entity class for players and zombies
    def __init__(self, char_type, xpos, ypos, scale, speed_xpos):
        pg.sprite.Sprite.__init__(self)
        self.action = 0
        self.alive = True
        self.char_type = char_type
        self.speed_xpos = speed_xpos
        self.attack_cooldown = 0
        self.health = 30
        self.score = 0
        self.max_health = self.health
        self.direction = 1 if char_type == "player" else random.choice((-1, 1))
        self.move_counter = 0
        self.speed_ypos = 0
        self.jump = False
        self.isJumping = True
        self.isAttacking = False
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pg.time.get_ticks()
        self.idling = False
        self.idling_counter = 0
        """
        Animation indexes:
        - idle:0
        - walk:1
        - jump:2
        - attack:3
        - death:4
        """
        animation_types = ["idle", "walk", "jump", "attack", "death"]
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(
                os.listdir(
                    f"{current_dir}/assets/{self.char_type}/{animation}")
            )
            for i in range(num_of_frames):
                image = pg.image.load(
                    f"{current_dir}/assets/{self.char_type}/{animation}/{animation}{i}.png"
                ).convert_alpha()
                image = pg.transform.scale(
                    image,
                    (int(scale * image.get_width()),
                     int(scale * image.get_height())),
                )
                temp_list.append(image)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect(center=(xpos, ypos))
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.check_attack()
        self.update_animation()
        self.check_alive()
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def move(self, moving_left, moving_right):  # sourcery no-metrics

        screen_scroll = 0

        # Reset variables
        dxpos = 0
        dypos = 0

        # Movement variables
        if moving_left:  # left
            dxpos = -self.speed_xpos
            self.flip = True
            self.direction = -1
        if moving_right:  # right
            dxpos = self.speed_xpos
            self.flip = False
            self.direction = 1
        if self.jump and not self.isJumping:  # jump
            jump_fx.play()
            self.speed_ypos = -12
            self.jump = False
            self.isJumping = True

        # Gravity implementation
        self.speed_ypos += GRAVITY
        self.speed_ypos = min(self.speed_ypos, 10)
        dypos += self.speed_ypos

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dxpos, self.rect.y, self.width, self.height):
                dxpos = 0
                if "zombie" in self.char_type:
                    self.direction *= -1
                    self.move_counter = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dypos, self.width, self.height):
                if self.speed_ypos < 0:
                    dypos = tile[1].bottom - self.rect.top
                else:
                    dypos = tile[1].top - self.rect.bottom
                    self.isJumping = False
                self.speed_ypos = 0

        if pg.sprite.spritecollide(self, spikes_group, False) and self.char_type == 'player':
            self.health = 0

        level_complete = False
        if pg.sprite.spritecollide(self, exit_tile_group, False):
            level_complete = True

        if self.rect.top > SCREEN_HEIGHT:
            self.health = 0

        # check if going off edges
        if self.char_type == "player" and (
            self.rect.left + dxpos < 0 or self.rect.right + dxpos > SCREEN_WIDTH
        ):
            dxpos = 0

        # Change movement speed
        self.rect.x += dxpos
        self.rect.y += dypos

        # update scroll based on player position
        if (
            self.char_type == "player"
            and (
                self.rect.right > SCREEN_WIDTH - SCROLL_THRESH
                and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH
            )
            or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dxpos))
        ):
            self.rect.x -= dxpos
            screen_scroll = -dxpos

        return screen_scroll, level_complete

    def update_animation(self):
        cooldown = 80
        self.image = self.animation_list[self.action][self.frame_index]
        if pg.time.get_ticks() - self.update_time > cooldown:
            self.update_time = pg.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0
            if self.action == 4:
                self.frame_index = len(self.animation_list[self.action]) - 1
            self.isAttacking = False

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 1
            self.update_time = pg.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(4)

    def draw(self):
        screen.blit(pg.transform.flip(self.image, self.flip, False), self.rect)

    def check_attack(self):
        if (
            self.attack_cooldown == 0
            and player.alive
            and "zombie" in self.char_type
            and pg.sprite.collide_rect(self, player)
        ):
            self.attack_cooldown = 45
            self.attack()

    def attack(self):
        self.isAttacking = True
        player.health -= 10

    def ai(self):
        if not self.idling:
            self.move_ai()
            if random.randint(1, 300) == 1:
                self.idle(0, 50)
        if self.isAttacking:
            self.idle(3, 7)
        else:
            self.idling_counter -= 1
            if self.idling_counter <= 0:
                self.idling = False
        self.rect.x += screen_scroll

    def idle(self, arg0, arg1):
        self.update_action(arg0)
        self.idling = True
        self.idling_counter = arg1

    def move_ai(self):
        ai_moving_right = self.direction == 1
        ai_moving_left = not ai_moving_right
        self.move(ai_moving_left, ai_moving_right)
        self.update_action(1)
        self.move_counter += 1
        if self.move_counter > TILE_SIZE:
            self.direction *= -1
            self.move_counter *= -1


class World:  # World class for world creation
    def __init__(self):
        self.obstacle_list = []

    def process_maindata(self, data):
        self.level_length = len(data[0])
        d = {25: "candy", 26: "cupcake", 27: "pumpkin",
             28: "player", 29: "zombiemale"}
        # iterate trough tile values in data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile <= 15 or tile == 20:  # blocks
                        self.obstacle_list.append(tile_data)
                    elif tile == 16:
                        spikes = Spikes(img, x * TILE_SIZE, y * TILE_SIZE)
                        spikes_group.add(spikes)
                    elif tile in range(17, 25):  # decoration
                        decoration = Decoration(
                            img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile in range(25, 28):  # items
                        item = Item(d[tile], x * TILE_SIZE, y * TILE_SIZE)
                        item_group.add(item)
                    elif tile in [28, 29]:
                        if tile == 28:
                            player = Entity(
                                d[tile], x * TILE_SIZE, y *
                                TILE_SIZE, ss(S, "p"), 5
                            )
                        else:
                            zombie = Entity(
                                d[tile], x * TILE_SIZE, y * TILE_SIZE, ss(S), 3
                            )
                            zombie_group.add(zombie)
                    else:
                        exit_tile = Exit_tile(
                            img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_tile_group.add(exit_tile)
        return player

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(*tile)


class Decoration(pg.sprite.Sprite):  # Decoration class for level decoration
    def __init__(self, img, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (
            x + TILE_SIZE // 2,
            y + (TILE_SIZE - self.image.get_height()),
        )

    def update(self):
        self.rect.x += screen_scroll


class Spikes(pg.sprite.Sprite):  # Spikes class for insta-kill tile
    def __init__(self, img, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (
            x + TILE_SIZE // 2,
            y + (TILE_SIZE - self.image.get_height()),
        )

    def update(self):
        self.rect.x += screen_scroll


class Exit_tile(pg.sprite.Sprite):  # Exit tile class for next level sign
    def __init__(self, img, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (
            x + TILE_SIZE // 2,
            y + (TILE_SIZE - self.image.get_height()),
        )

    def update(self):
        self.rect.x += screen_scroll


class Item(pg.sprite.Sprite):  # Item class for collectible items
    def __init__(self, item_type, xpos, ypos):
        pg.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = pg.image.load(
            f"{current_dir}/assets/maps/items/{self.item_type}.png"
        )
        self.rect = self.image.get_rect()
        self.rect.midtop = (
            xpos + TILE_SIZE // 2,
            ypos + (TILE_SIZE - self.image.get_height()),
        )

    def update(self):
        self.rect.x += screen_scroll

        # check if pick up
        if pg.sprite.collide_rect(self, player):
            # check type of box
            if self.item_type == "pumpkin":
                player.health += 10
                extralife_fx.play()
            elif self.item_type == "cupcake":
                player.score += 25
                item_fx.play()
            else:
                player.score += 5
                item_fx.play()

            # kill item
            self.kill()


class Panel:  # Panel class for leaderboard
    def __init__(self, x, y, image):
        width = image.get_width()
        height = image.get_height()
        self.image = pg.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False

        # get mouse position
        pos = pg.mouse.get_pos()
        # check mouseover and clicked conditions
        if (
            self.rect.collidepoint(pos)
            and pg.mouse.get_pressed()[0] == 1
            and self.clicked == False
        ):
            action = True
            self.clicked = True

        if pg.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))
        draw_text(
            "LEADERBOARD",
            font_title,
            (0, 0, 0),
            SCREEN_WIDTH // 2 - 180,
            self.rect.top + 40,
        )

        for row, (holder, score) in enumerate(scores.items()):
            self.draw_table(holder, score, row)
        return action

    def draw_table(self, holder, score, row):
        if row < 8:
            draw_text(
                holder,
                font,
                (0, 0, 0),
                self.rect.left + 180,
                (self.rect.top + 200) + (row * 50),
            )
            draw_text(
                str(score),
                font,
                (0, 0, 0),
                self.rect.left + 380,
                (self.rect.top + 200) + (row * 50),
            )
        elif row < 16:
            draw_text(
                holder,
                font,
                (0, 0, 0),
                self.rect.centerx - 150,
                (self.rect.top + 200) + ((row - 8) * 50),
            )
            draw_text(
                str(score),
                font,
                (0, 0, 0),
                self.rect.centerx + 50,
                (self.rect.top + 200) + ((row - 8) * 50),
            )
        else:
            draw_text(
                holder,
                font,
                (0, 0, 0),
                self.rect.right - 450,
                (self.rect.top + 200) + ((row - 16) * 50),
            )
            draw_text(
                str(score),
                font,
                (0, 0, 0),
                self.rect.right - 250,
                (self.rect.top + 200) + ((row - 16) * 50),
            )


class Transition:  # Transition class for transition screens
    def __init__(self, direction, color, speed, img=star_img):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0

    def fade(self, img=star_img):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:
            pg.draw.rect(
                screen,
                self.color,
                (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT),
            )
            pg.draw.rect(
                screen,
                self.color,
                (SCREEN_WIDTH // 2 + self.fade_counter,
                 0, SCREEN_WIDTH, SCREEN_HEIGHT),
            )
            pg.draw.rect(
                screen,
                self.color,
                (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2),
            )
            pg.draw.rect(
                screen,
                self.color,
                (
                    0,
                    SCREEN_HEIGHT // 2 + self.fade_counter,
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT,
                ),
            )
        elif self.direction == 2:
            pg.draw.rect(
                screen, self.color, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter)
            )
        else:
            pg.draw.rect(
                screen,
                (255, 255, 0),
                (
                    0,
                    SCREEN_HEIGHT - self.fade_counter,
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT + self.fade_counter,
                ),
            )
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True
        return fade_complete


# Gui buttons
start_button = button.Button(
    SCREEN_WIDTH // 2,
    SCREEN_HEIGHT // 2,
    start_img,
)
exit_button = button.Button(
    SCREEN_WIDTH // 2 - start_img.get_width() - 50,
    SCREEN_HEIGHT // 2,
    exit_img,
)
leaderboard_button = button.Button(
    SCREEN_WIDTH // 2 + start_img.get_width() + 50,
    SCREEN_HEIGHT // 2,
    leaderboard_img,
)
restart_button = button.Button(
    SCREEN_WIDTH // 2,
    SCREEN_HEIGHT // 2,
    restart_img,
)

save_button = button.Button(
    SCREEN_WIDTH - 150, SCREEN_HEIGHT - 270, save_img, 0.85)

leaderboard_panel = Panel(
    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, leaderboard_panel_img)
# Screen transition
death_transition = Transition(2, (26, 37, 39), 10)
level_transition = Transition(1, (0, 0, 0), 10)
endgame_transition = Transition(3, (255, 255, 0), 15)

# Sprite groups
zombie_group = pg.sprite.Group()
item_group = pg.sprite.Group()
decoration_group = pg.sprite.Group()
spikes_group = pg.sprite.Group()
exit_tile_group = pg.sprite.Group()

groups = [decoration_group, item_group, exit_tile_group, spikes_group]


# Create empty tile list
world_data = [[-1 for __ in range(COLS)] for _ in range(ROWS)]

# load level data
with open(
    f"{current_dir}/assets/maps/levels/level{level}_data.csv", newline=""
) as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for y, row in enumerate(reader):
        for x, tile in enumerate(row):
            world_data[y][x] = int(tile)

world = World()
player = world.process_maindata(world_data)
"""
===============
MAIN GAME LOOP
===============

Animation indexes:
- idle:0
- walk:1
- jump:2
- attack:3
- death:4
"""


def draw_endscreen():
    screen.blit(
        input_img,
        (
            SCREEN_WIDTH // 2 - input_img.get_width() // 2,
            SCREEN_HEIGHT // 2 - input_img.get_height() // 2,
        ),
    )
    draw_text(
        user_text,
        font_input,
        (255, 255, 255),
        SCREEN_WIDTH // 2 - 300,
        SCREEN_HEIGHT // 2 + 65,
    )
    draw_text(
        "Enter your name",
        font_input,
        (0, 0, 0),
        SCREEN_WIDTH // 2 - 160,
        SCREEN_HEIGHT // 2 - 140,
    )
    draw_text(
        f"Final Score: {global_score}",
        font_input,
        (0, 0, 0),
        SCREEN_WIDTH // 2 - 180,
        SCREEN_HEIGHT - 100,
    )


while gameRunning:

    clock.tick(FPS)

    if not start_game:
        screen.blit(BACKGROUND, (0, 0))
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        elif exit_button.draw(screen):
            gameRunning = False
        elif leaderboard_button.draw(screen):
            leaderboard_open = True

    if leaderboard_open and leaderboard_panel.draw(screen):
        leaderboard_open = False
    if start_game:
        drawBG()
        world.draw()
        draw_text(
            f"Score: {player.score}", font, (255,
                                             255, 255), SCREEN_WIDTH - 150, 20
        )
        draw_text("Health: ", font, (255, 255, 255), 15, 20)
        for i in range(player.health // 10):
            screen.blit(pumpkin_img, (120 + (i * pumpkin_img.get_width()), 0))

        for group in groups:
            group.update()
            group.draw(screen)

        for zombie_sprite in zombie_group:
            zombie_sprite.draw()
            zombie_sprite.update()
            zombie_sprite.ai()

        player.update()
        player.draw()

        # play intro
        if start_intro and level_transition.fade():
            start_intro = False
            level_transition.fade_counter = 0

        if player.alive and not finish_game:
            if player.isJumping:
                # update animation to jumping (index 2)
                player.update_action(2)
            elif moving_left or moving_right:
                # update animation to walking (index 1)
                player.update_action(1)
            else:
                player.update_action(0)
            screen_scroll, level_complete = player.move(
                moving_left, moving_right)
            bg_scroll -= screen_scroll
            # Check if level complete
            if level_complete:
                global_score += player.score
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    # load in level data and create world
                    with open(
                        f"{current_dir}/assets/maps/levels/level{level}_data.csv",
                        newline="",
                    ) as csvfile:
                        reader = csv.reader(csvfile, delimiter=",")
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player = world.process_maindata(world_data)
                else:
                    finish_game = True
        elif finish_game:
            if endgame_transition.fade():
                draw_endscreen()
                if save_button.draw(screen):
                    gameRunning = False
        else:

            if loop < 1:
                death_fx.play()
                loop += 1
            screen_scroll = 0
            if death_transition.fade() and restart_button.draw(screen):
                loop = 0
                death_transition.fade_counter = 0
                bg_scroll = 0
                world_data = reset_level()
                # load in level data and create world
                with open(
                    f"{current_dir}/assets/maps/levels/level{level}_data.csv",
                    newline="",
                ) as csvfile:
                    reader = csv.reader(csvfile, delimiter=",")
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player = world.process_maindata(world_data)

    for event in pg.event.get():  # Event handler
        if event.type == pg.QUIT:  # Close game
            gameRunning = False

        if event.type == pg.KEYDOWN and finish_game:
            if event.key == pg.K_BACKSPACE:
                user_text = user_text[:-1]
            else:
                user_text += event.unicode

        if event.type == pg.KEYDOWN and player.alive:
            if event.key == pg.K_a:
                moving_left = True
            if event.key == pg.K_d:
                moving_right = True
            if event.key == pg.K_w:
                player.jump = True
            if event.key == pg.K_ESCAPE:
                gameRunning = False

        if event.type == pg.KEYUP:
            if event.key == pg.K_a:
                moving_left = False
            if event.key == pg.K_d:
                moving_right = False

    pg.display.update()
if user_text:
    scores[user_text] = global_score

scores_sorted = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
with open(f"{current_dir}/assets/scores.json", "w") as scores_json:
    json.dump(scores_sorted, scores_json)
pg.quit()


"""
Integrantes:
- Leonardo Candio
- Renzo Acervo
- Diego Diaz
- Alejandro Barturen
- Nicolas Arce

LINK VIDEO: https://drive.google.com/file/d/15z9m-ZPqr6t9TvO4jMjdmx9K3rCVQFCk/view?usp=sharing
"""
