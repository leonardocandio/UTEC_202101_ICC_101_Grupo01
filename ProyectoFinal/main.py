import pygame as pg
from pygame.locals import *

pg.init()

gametitle = ""
screen_width = 1000
screen_heigth = 1000

screen = pg.display.set_mode((screen_width, screen_heigth))
pg.display.set_caption(gametitle)

gameRun = True

while gameRun:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = FALSE

pg.quit()
