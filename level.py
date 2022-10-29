import numpy as np
import pygame as pg
import random
from raycaster import RayCastEngine
from screens import LoadUp, MenuScreen


class Level:
    def __init__(self, screen):
        self.screen = screen
        self.play_game = False

        # Engine Instance
        self.engine = RayCastEngine()
        self.loading_screen = LoadUp(screen)
        self.menu_screen = MenuScreen(screen)

        # Render Resolution
        self.h_res = 200
        self.half_v_res = 150
        self.frame = np.random.uniform(0, 1, (self.h_res, self.half_v_res * 2, 3))

        # FOV Scaling
        self.fov = self.h_res / 60

        # Map Settings
        self.map_size = 40
        self.pos_x, self.pos_y, self.rot, self.map_h = self.engine.gen_map(self.map_size)

        # Vertical Pan
        self.rot_v = 0
        self.offset = int(0.8 * self.half_v_res) * 2

        # Texture Loading
        sky = pg.image.load("assets/environment.png").convert()
        self.sky = pg.surfarray.array3d(pg.transform.scale(sky, (360, self.half_v_res * 2 + self.offset))) / 255
        self.floor = pg.surfarray.array3d(pg.image.load("assets/floor.png").convert()) / 255
        self.wall = pg.surfarray.array3d(pg.image.load("assets/wall.jpg").convert()) / 255

        # Sound Effects
        self.ambience = pg.mixer.Sound("sounds/ambient.mp3")
        self.game_music = pg.mixer.Sound("sounds/game_music.mp3")
        self.menu_music = pg.mixer.Sound("sounds/menu_music.mp3")
        self.feet1 = pg.mixer.Sound("sounds/footsteps.mp3")
        self.feet2 = pg.mixer.Sound("sounds/footsteps2.mp3")
        self.ambience.set_volume(0.8)
        self.game_music.set_volume(0.1)
        self.menu_music.set_volume(0.35)
        self.feet1.set_volume(0.7)
        self.feet2.set_volume(0.4)
        self.menu_music.play(-1)

        # Custom Events
        self.PLAY_STEPS = pg.USEREVENT + 1

    def update(self, dt, events):
        # Getting New Frame Render
        self.frame = self.engine.new_frame(self.pos_x, self.pos_y, self.rot, self.frame, self.sky, self.floor,
                                           self.h_res, self.half_v_res, self.fov, self.map_h, self.map_size,
                                           self.wall, self.rot_v)

        # Inputs
        keys = pg.key.get_pressed()
        mouse_rel = pg.mouse.get_rel()

        # Scale Frame To Window map_size
        surf = pg.surfarray.make_surface(self.frame * 255)
        scaled_frame = pg.transform.scale(surf, (800, 600))

        # Blit Frame On Screen
        self.screen.blit(scaled_frame, (0, 0))

        # Manage Movements
        speed = 1 if keys[pg.K_LSHIFT] else 0.5
        self.pos_x, self.pos_y, self.rot, self.rot_v = self.engine.movement(self.pos_x, self.pos_y, self.rot,
                                                                            self.map_h, dt * speed,
                                                                            keys, self.rot_v, mouse_rel)

        # Startup
        if self.loading_screen.alpha_value > 0:
            self.loading_screen.update(dt)
        else:
            # Menu Screen
            if not self.play_game:
                self.menu_screen.update(dt)
                if keys[pg.K_RETURN]:
                    self.menu_music.fadeout(1500)
                    self.ambience.play(-1)
                    self.game_music.play(-1)
                    pg.time.set_timer(self.PLAY_STEPS, 10000)
                    self.play_game = True
            else:
                # Cue Footstep Sounds
                for ev in events:
                    if ev.type == self.PLAY_STEPS:
                        random_sound = random.randint(1, 2)
                        if random_sound == 1:
                            self.feet1.play()
                        elif random_sound == 2:
                            self.feet2.play()

                        # Reschedule Steps At Random Time Interval
                        random_play = random.randint(10000, 20000)
                        pg.time.set_timer(self.PLAY_STEPS, random_play)
