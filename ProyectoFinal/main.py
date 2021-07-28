import pygame as pg
import os
import random
import csv
import json
import button
from pygame import mixer

pg.init()

GAMETITLE = "Graveyard Adventures"
gameRunning = True


# Loading score data from JSON file
with open("ProyectoFinal\\assets\\scores.json", "r") as scores_json:
    try:
        scores = json.load(scores_json)
    except json.decoder.JSONDecodeError:
        pass


# Init screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = int(SCREEN_WIDTH * 9 / 16)
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption(GAMETITLE)

# Set framerate
clock = pg.time.Clock()
FPS = 60

# Game variables
BACKGROUND = pg.image.load("ProyectoFinal\\assets\\maps\\bg.png").convert_alpha()
pumpkin_img = pg.image.load(
    f"ProyectoFinal\\assets\\maps\\items\\pumpkin.png"
).convert_alpha()


GRAVITY = 0.4
S = 0.23
ROWS = 9
COLS = 126
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = len(os.listdir("ProyectoFinal\\assets\\maps\\tiles"))
level = 0

img_list = []
for x in range(TILE_TYPES):
    img = pg.image.load(f"ProyectoFinal\\assets\\maps\\tiles\\tile{x}.png")
    img = pg.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)


# Player variables
moving_left = False
moving_right = False


font = pg.font.Font("ProyectoFinal\\assets\\maps\\BRLNSDB.TTF", 30)


def draw_text(text, font, color, xpos, ypos):
    text_img = font.render(text, True, color)
    screen.blit(text_img, (xpos, ypos))


def drawBG():
    screen.blit(BACKGROUND, (0, 0))


def ss(scale, c="z"):
    return scale * 0.60 if c == "p" else scale


class Entity(pg.sprite.Sprite):  # Entity class for players and zombies
    def __init__(self, char_type, xpos, ypos, scale, speed_xpos):
        pg.sprite.Sprite.__init__(self)
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
                os.listdir(f"ProyectoFinal\\assets\\{self.char_type}\\{animation}")
            )
            for i in range(num_of_frames):
                image = pg.image.load(
                    f"ProyectoFinal\\assets\\{self.char_type}\\{animation}\\{animation}{i}.png"
                ).convert_alpha()
                image = pg.transform.scale(
                    image,
                    (int(scale * image.get_width()), int(scale * image.get_height())),
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

    def move(self, moving_left, moving_right):
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
            self.speed_ypos = -12
            self.jump = False
            self.isJumping = True

        # Gravity implementation
        self.speed_ypos += GRAVITY
        self.speed_ypos = min(self.speed_ypos, 10)
        dypos += self.speed_ypos

        for tile in world.obstacle_list:
            if tile[1].colliderect(
                self.rect.x + dxpos, self.rect.y, self.width, self.height
            ):
                dxpos = 0
            if tile[1].colliderect(
                self.rect.x, self.rect.y + dypos, self.width, self.height
            ):
                if self.speed_ypos < 0:
                    dypos = tile[1].bottom - self.rect.top
                else:
                    dypos = tile[1].top - self.rect.bottom
                self.speed_ypos = 0
                self.isJumping = False
        # Change movement speed
        self.rect.x += dxpos
        self.rect.y += dypos

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
        pg.draw.rect(screen, (255, 255, 255), self.rect, 1)

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
            self.extracted_from_ai()
            if random.randint(1, 300) == 1:
                self.idle(0, 50)
        if self.isAttacking:
            self.idle(3, 7)
        else:
            self.idling_counter -= 1
            if self.idling_counter <= 0:
                self.idling = False

    def idle(self, arg0, arg1):
        self.update_action(arg0)
        self.idling = True
        self.idling_counter = arg1

    def extracted_from_ai(self):
        ai_moving_right = self.direction == 1
        ai_moving_left = not ai_moving_right
        self.move(ai_moving_left, ai_moving_right)
        self.update_action(1)
        self.move_counter += 1
        if self.move_counter > TILE_SIZE:
            self.direction *= -1
            self.move_counter *= -1


class World:
    def __init__(self):
        self.obstacle_list = []

    def process_maindata(self, data):
        d = {25: "candy", 26: "cupcake", 27: "pumpkin", 28: "player", 29: "zombiemale"}
        # iterate trough tile values in data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile <= 15:  # blocks
                        self.obstacle_list.append(tile_data)
                    elif tile in [16, 30]:
                        collision_tile = CollisionTile(
                            img, x * TILE_SIZE, y * TILE_SIZE, "exit"
                        )
                        collision_tile_group.add(collision_tile)
                    elif tile in range(17, 25):  # decoration
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile in range(25, 28):  # items
                        item = Item(d[tile], x * TILE_SIZE, y * TILE_SIZE)
                        item_group.add(item)
                    elif tile in [28, 29]:
                        if tile == 28:
                            player = Entity(
                                d[tile], x * TILE_SIZE, y * TILE_SIZE, ss(S, "p"), 5
                            )
                        else:
                            zombie = Entity(
                                d[tile], x * TILE_SIZE, y * TILE_SIZE, ss(S), 3
                            )
                            zombie_group.add(zombie)

        return player

    def draw(self):
        for tile in self.obstacle_list:
            screen.blit(tile[0], tile[1])


class Decoration(pg.sprite.Sprite):
    def __init__(self, img, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (
            x + TILE_SIZE // 2,
            y + (TILE_SIZE - self.image.get_height()),
        )


class CollisionTile(pg.sprite.Sprite):
    def __init__(self, img, x, y, tile_type):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (
            x + TILE_SIZE // 2,
            y + (TILE_SIZE - self.image.get_height()),
        )


class Item(pg.sprite.Sprite):  # Entity class for players and zombies
    def __init__(self, item_type, xpos, ypos):
        pg.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = pg.image.load(
            f"ProyectoFinal\\assets\\maps\\items\\{self.item_type}.png"
        )
        self.rect = self.image.get_rect()
        self.rect.midtop = (
            xpos + TILE_SIZE // 2,
            ypos + (TILE_SIZE - self.image.get_height()),
        )

    def update(self):
        # check if pick up
        if pg.sprite.collide_rect(self, player):
            # check type of box
            if self.item_type == "pumpkin":
                player.health += 10
            elif self.item_type == "cupcake":
                player.score += 25
            else:
                player.score += 5

            # kill item
            self.kill()


zombie_group = pg.sprite.Group()
item_group = pg.sprite.Group()
decoration_group = pg.sprite.Group()
collision_tile_group = pg.sprite.Group()

groups = [item_group, decoration_group, collision_tile_group]


# Create empty tile list
world_data = [[-1 for __ in range(COLS)] for _ in range(ROWS)]

# load level data
with open(
    f"ProyectoFinal\\assets\\maps\\levels\\level{level}_data.csv", newline=""
) as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for y, row in enumerate(reader):
        for x, tile in enumerate(row):
            world_data[y][x] = int(tile)

world = World()
player = world.process_maindata(world_data)
world.draw()
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


while gameRunning:

    clock.tick(FPS)

    drawBG()
    world.draw()
    draw_text(f"Score: {player.score}", font, (255, 255, 255), SCREEN_WIDTH - 150, 20)
    draw_text("Health: ", font, (255, 255, 255), 15, 20)
    for i in range(player.health // 10):
        screen.blit(pumpkin_img, (120 + (i * pumpkin_img.get_width()), 0))

    for i in groups:
        i.update()
        i.draw(screen)

    for zombie_sprite in zombie_group:
        zombie_sprite.draw()
        zombie_sprite.update()
        zombie_sprite.ai()

    player.update()
    player.draw()

    if player.alive:
        if player.isJumping:
            player.update_action(2)  # update animation to jumping (index 2)
        elif moving_left or moving_right:
            player.update_action(1)  # update animation to walking (index 1)
        else:
            player.update_action(0)
        player.move(moving_left, moving_right)

    for event in pg.event.get():  # Event handler
        if event.type == pg.QUIT:  # Close game
            gameRunning = False

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
pg.quit()
