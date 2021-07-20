# sourcery skip: ensure-file-closed
import pygame as pg
from pygame.locals import *
import json

pg.init()

gametitle = ""
screen_width = 900
screen_heigth = 900

screen = pg.display.set_mode((screen_width, screen_heigth))
pg.display.set_caption(gametitle)

gameRun = True

scores_json = open("scores.json", "a+")

try:
    scores = json.load(scores_json)
except json.decoder.JSONDecodeError:
    pass


while gameRun:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            gameRun = False

pg.quit()


scores_json.close()
