import numpy as np
import pygame as pg
from settings import WIN_WIDTH, WIN_HEIGHT
from level import Level


def main():
    # Initiation
    pg.init()

    # Window Settings
    screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))  # pg.FULLSCREEN
    pg.display.set_caption("A Lost Memory")
    pg.display.set_icon(pg.image.load("assets/game_icon.png").convert_alpha())
    pg.mouse.set_visible(False)
    pg.event.set_grab(True)
    clock = pg.time.Clock()

    # Level Instances
    level_1 = Level(screen)

    running = True
    while running:
        # Event Handler
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False

        dt = clock.tick(60) / 1000
        level_1.update(dt, events)
        pg.display.update()


if __name__ == '__main__':
    main()
    pg.quit()
