import pygame as pg
from pygame import mixer
import os
import random
import csv
import json
import button

pg.init()

gametitle = "Zombie Rush"
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


# Player variables
moving_left = False
moving_right = False


def drawBG():
    screen.blit(background, (0, 0))


class Entity(pg.sprite.Sprite):  # Entity class for players and zombies
    def __init__(self, char_type, xpos, ypos, scale, speed):
        pg.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.flip = False
        avatar = pg.image.load(
            f"ProyectoFinal\\assets\\{self.char_type}\\Idle\\Idle (1).png"
        )
        self.avatar = pg.transform.scale(
            avatar, (int(scale * avatar.get_width()), int(scale * avatar.get_height()))
        )
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

    def draw(self):
        screen.blit(pg.transform.flip(self.avatar, self.flip, False), self.hitbox)


player = Entity("player", screen_width // 2, screen_height // 2, 0.10, 5)
zombiemale = Entity("zombiemale", screen_width // 4, screen_height // 2, 0.17, 5)

"""
===============
MAIN GAME LOOP
===============
"""
while gameRun:

    clock.tick(FPS)
    drawBG()
    zombiemale.draw()
    player.draw()

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
