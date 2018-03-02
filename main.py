import pygame as pg
from pygame.locals import *
from Board import *
from typing import Tuple
from constants import *
import copy
import sys
update_frame = pg.display.update
KMOD_LCOMMAND = KMOD_LMETA
FPS = 20
_tempClock = pg.time.Clock()
clockClass = copy.deepcopy(_tempClock.__class__)
del _tempClock

def startScreen(mainSurface: pg.Surface, font: pg.font.Font) -> None:
    mainSurface.fill(C_LIME)
    text = font.render(GAME_NAME, True, C_LIME)
    mainSurface.blit(text, text.get_rect(center=(SCREEN_LENGTH//2, SCREEN_LENGTH//2)))


def init():
    pg.init()
    pg.display.set_caption(GAME_NAME)


def updateVars(clock: clockClass) -> None:
    clock.tick(20)
    update_frame()

def quitGame() -> None:
    pg.quit()
    sys.exit()

def processEvent(event: pg.event.Event) -> None:
    if event.type == QUIT:
        quitGame()
    elif event.type == KEYDOWN:
        # alt f4 on win&linux systems
        if (platform == OS.windows or platform == OS.linux) and event.mod == KMOD_ALT and event.key == K_F4:
            quitGame()
        # command q on mac systems
        elif (platform == OS.mac) and event.mod == KMOD_LCOMMAND and event.key == K_q:
            quitGame()




def loop(main: pg.Surface, clock: pg.time.Clock()) -> None:
    while True:
        for event in pg.event.get():
            processEvent(event)



        updateVars(clock)



def main():
    init()
    tickClock = pg.time.Clock()
    displayScreen = pg.display.set_mode((SCREEN_LENGTH,SCREEN_HEIGHT))
    defaultFont = pg.font.Font(None, 36)

    startScreen(displayScreen, defaultFont)

    loop(displayScreen, tickClock)



if __name__ == '__main__':
    main()

