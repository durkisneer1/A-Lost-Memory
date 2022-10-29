import pygame as pg
from settings import WIN_WIDTH, WIN_HEIGHT


class LoadUp:
    def __init__(self, screen):
        self.screen = screen
        self.surf = pg.image.load("assets/logo.png").convert_alpha()
        self.rect = self.surf.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2))

        self.alpha_value = 255

    def update(self, dt):
        self.alpha_value -= 1 / (dt * 20)
        self.surf.set_alpha(self.alpha_value)

        self.screen.fill("black")
        self.screen.blit(self.surf, self.rect)


class MenuScreen:
    def __init__(self, screen):
        self.screen = screen

        # Title Render
        self.title_text = pg.image.load("assets/title.png").convert_alpha()
        self.title_text.set_colorkey("white")
        self.title_rect = self.title_text.get_rect(center=(WIN_WIDTH / 2, 100))

        # Background Render
        bg_surf = pg.image.load("assets/wall.jpg").convert()
        self.bg_surf = pg.transform.scale(bg_surf, (WIN_WIDTH, WIN_HEIGHT))
        self.bg_pos = pg.Vector2(0, 0)

        # Instructions Render
        instruct_text = pg.image.load("assets/instruct.png").convert_alpha()
        instruct_text.set_colorkey("white")
        self.instruct_text = pg.transform.scale(instruct_text, (WIN_WIDTH - 30, 45))
        self.instruct_rect = self.instruct_text.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT - 200))

    def scroll(self, dt):
        self.bg_pos.x -= 1 / (dt * 30)
        pos_x = (self.bg_pos.x % WIN_WIDTH)

        # Looping Logic
        for i in range(-2, 3):
            self.screen.blit(self.bg_surf, ((pos_x + WIN_WIDTH * i), self.bg_pos.y))

    def update(self, dt):
        self.scroll(dt)
        self.screen.blit(self.title_text, self.title_rect)
        self.screen.blit(self.instruct_text, self.instruct_rect)
