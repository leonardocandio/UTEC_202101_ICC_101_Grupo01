import pygame as pg
from pygame import mixer
import os
import random
import csv
import json
import button

pg.init()

GAMETITLE = "Graveyard Adventures"
gameRunning = True


# Loading score data from JSON file
with open("ProyectoFinal\\assets\\scores.json", "a+") as scores_json:
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
    f"ProyectoFinal\\assets\\maps\\ico\\pumpkin.png"
).convert_alpha()
GRAVITY = 0.4
TILE_SIZE = 80
S = 0.23

# Player variables
moving_left = False
moving_right = False


font = pg.font.Font("ProyectoFinal\\assets\\maps\\BRLNSDB.TTF", 30)


def draw_text(text, font, color, xpos, ypos):
    text_img = font.render(text, True, color)
    screen.blit(text_img, (xpos, ypos))


def drawBG():
    screen.blit(BACKGROUND, (0, 0))
    pg.draw.line(screen, (255, 255, 255), (0, 550), (SCREEN_WIDTH, 550))


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
        self.direction = 1
        self.speed_ypos = 0
        self.jump = False
        self.isJumping = True
        self.isAttacking = False
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pg.time.get_ticks()
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
                avatar = pg.image.load(
                    f"ProyectoFinal\\assets\\{self.char_type}\\{animation}\\{animation}{i}.png"
                ).convert_alpha()
                avatar = pg.transform.scale(
                    avatar,
                    (int(scale * avatar.get_width()), int(scale * avatar.get_height())),
                )
                temp_list.append(avatar)
            self.animation_list.append(temp_list)
        self.avatar = self.animation_list[self.action][self.frame_index]
        self.rect = self.avatar.get_rect()
        self.rect.center = (xpos, ypos)

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
            self.direction = 1
        if moving_right:  # right
            dxpos = self.speed_xpos
            self.flip = False
            self.direction = -1
        if self.jump and not self.isJumping:  # jump
            self.speed_ypos = -11
            self.jump = False
            self.isJumping = True

        # Gravity implementation
        self.speed_ypos += GRAVITY
        self.speed_ypos = min(self.speed_ypos, 10)
        dypos += self.speed_ypos

        if self.rect.bottom + dypos > 550:
            dypos = 550 - self.rect.bottom
            self.isJumping = False

        # Change movement speed
        self.rect.x += dxpos
        self.rect.y += dypos

    def update_animation(self):
        cooldown = 80
        self.avatar = self.animation_list[self.action][self.frame_index]
        if pg.time.get_ticks() - self.update_time > cooldown:
            self.update_time = pg.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0
            if self.action == 4:
                self.frame_index = len(self.animation_list[self.action]) - 1
            if "zombie" in self.char_type and self.isAttacking:
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
        screen.blit(pg.transform.flip(self.avatar, self.flip, False), self.rect)
        pg.draw.rect(screen, (255, 255, 255), self.rect, 1)

    def check_attack(self):
        if (
            self.attack_cooldown == 0
            and player.alive
            and "zombie" in self.char_type
            and pg.sprite.collide_rect(self, player)
        ):
            self.attack_cooldown = 90
            self.attack()

    def attack(self):
        self.isAttacking = True
        player.health -= 10


class Item(pg.sprite.Sprite):  # Entity class for players and zombies
    def __init__(self, item_type, xpos, ypos):
        self.item_type = item_type
        pg.sprite.Sprite.__init__(self)
        self.image = pg.image.load(
            f"ProyectoFinal\\assets\\maps\\ico\\{self.item_type}.png"
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

# temporary

item0 = Item("candy", 100, 300)
item_group.add(item0)
item1 = Item("pumpkin", 400, 300)
item_group.add(item1)
item2 = Item("cupcake", 500, 300)
item_group.add(item2)


player = Entity("player", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, ss(S, c="p"), 5)
zombie = Entity(
    "zombiemale",
    SCREEN_WIDTH // 4,
    SCREEN_HEIGHT // 2,
    ss(S),
    5,
)
zombie_group.add(zombie)
zombie1 = Entity(
    "zombiemale",
    SCREEN_WIDTH,
    SCREEN_HEIGHT // 3,
    ss(S),
    5,
)
zombie_group.add(zombie1)
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
    draw_text(f"Score: {player.score}", font, (255, 255, 255), SCREEN_WIDTH - 150, 20)
    draw_text("Health: ", font, (255, 255, 255), 15, 20)
    for i in range(player.health // 10):
        screen.blit(pumpkin_img, (120 + (i * pumpkin_img.get_width()), 0))

    for zombie in zombie_group:
        zombie.move(False, False)
        zombie.draw()
        zombie.update()
        if zombie.isAttacking:
            zombie.update_action(3)
        else:
            zombie.update_action(0)

    player.update()
    player.draw()
    item_group.update()
    item_group.draw(screen)

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
