import pygame as pg
from pygame import mixer
import os
import random
import csv
import json
import button

pg.init()

gametitle = "Graveyard Adventures"
gameRun = True


# Loading score data from JSON file
with open("ProyectoFinal\\assets\\scores.json", "a+") as scores_json:
    try:
        scores = json.load(scores_json)
    except json.decoder.JSONDecodeError:
        pass


# Init screen
screen_width = 1280
screen_height = int(screen_width * 9 / 16)
screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption(gametitle)

# Set framerate
clock = pg.time.Clock()
FPS = 60

# Game variables
background = pg.image.load("ProyectoFinal\\assets\\maps\\bg.png")
gravity = 0.75
tile_size = 50

# Player variables
moving_left = False
moving_right = False


def drawBG():
    screen.blit(background, (0, 0))


class Entity(pg.sprite.Sprite):  # Entity class for players and zombies
    def __init__(self, char_type, xpos, ypos, scale, speed):
        pg.sprite.Sprite.__init__(self)
        self.alive = False
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.isJumping = False
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
        - dead:3
        """
        animation_types = ["idle", "walk", "jump"]
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(
                os.listdir(f"ProyectoFinal\\assets\\{self.char_type}\\{animation}")
            )
            for i in range(num_of_frames):
                avatar = pg.image.load(
                    f"ProyectoFinal\\assets\\{self.char_type}\\{animation}\\{animation}{i}.png"
                )
                avatar = pg.transform.scale(
                    avatar,
                    (int(scale * avatar.get_width()), int(scale * avatar.get_height())),
                )
                temp_list.append(avatar)
            self.animation_list.append(temp_list)
        self.avatar = self.animation_list[self.action][self.frame_index]
        self.hitbox = self.avatar.get_rect()
        self.hitbox.center = (xpos, ypos)

    def move(self, moving_left, moving_right):
        # Reset variables
        dxpos = 0
        dypos = 0

        # Assing variables
        if moving_left:
            dxpos = -self.speed
            self.flip = True
            self.direction = 1
        if moving_right:
            dxpos = self.speed
            self.flip = False
            self.direction = -1

        # Change movement speed
        self.hitbox.x += dxpos
        self.hitbox.y += dypos

    def update_animation(self):
        cooldown = 80
        self.avatar = self.animation_list[self.action][self.frame_index]
        if pg.time.get_ticks() - self.update_time > cooldown:
            self.update_time = pg.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 1
            self.update_time = pg.time.get_ticks()

    def draw(self):
        screen.blit(pg.transform.flip(self.avatar, self.flip, False), self.hitbox)


player = Entity("player", screen_width // 2, screen_height // 2, 0.2, 5)
zombie = Entity("zombiemale", screen_width // 4, screen_height // 2, 0.3, 5)

"""
===============
MAIN GAME LOOP
===============
"""
while gameRun:

    clock.tick(FPS)
    drawBG()
    zombie.update_animation()
    player.update_animation()
    zombie.draw()
    player.draw()

    if moving_left or moving_right:
        player.update_action(1)  # update animation to running (1)
    else:
        player.update_action(0)
    player.move(moving_left, moving_right)

    for event in pg.event.get():  # Event handler
        if event.type == pg.QUIT:  # Close game
            gameRun = False

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_a:
                moving_left = True
            if event.key == pg.K_d:
                moving_right = True
            if event.key == pg.K_ESCAPE:
                gameRun = False

        if event.type == pg.KEYUP:
            if event.key == pg.K_a:
                moving_left = False
            if event.key == pg.K_d:
                moving_right = False

    pg.display.update()
pg.quit()
