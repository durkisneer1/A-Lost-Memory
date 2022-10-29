import numpy as np
import pygame as pg
from numba import njit


class RayCastEngine:
    @staticmethod
    def movement(pos_x, pos_y, rot, map_h, dt, keys, rot_v, mouse_rel):
        # Navigation Normalization
        x, y, norm = pos_x, pos_y, 0

        # Horizontal Pan
        rot += np.clip((mouse_rel[0]) / 200, -0.2, 0.2)

        # Vertical Pan
        rot_v += np.clip((mouse_rel[1]) / 200, -0.2, 0.2)
        rot_v = np.clip(rot_v, -0.8, 0.8)

        # Forwards and Backwards
        if keys[pg.K_w]:
            x += dt * np.cos(rot)
            y += dt * np.sin(rot)
            norm = 1
        elif keys[pg.K_s]:
            x -= dt * np.cos(rot)
            y -= dt * np.sin(rot)
            norm = 1

        # Sidewards
        if keys[pg.K_a]:
            dt /= (norm + 1)
            x += dt * np.sin(rot)
            y -= dt * np.cos(rot)
        if keys[pg.K_d]:
            dt /= (norm + 1)
            x -= dt * np.sin(rot)
            y += dt * np.cos(rot)

        # Wall Collisions
        if not (map_h[int(x - 0.2)][int(y)] or map_h[int(x + 0.2)][int(y)] or
                map_h[int(x)][int(y - 0.2)] or map_h[int(x)][int(y + 0.2)]):
            pos_x, pos_y = x, y
        elif not (map_h[int(pos_x - 0.2)][int(y)] or map_h[int(pos_x + 0.2)][int(y)] or
                  map_h[int(pos_x)][int(y - 0.2)] or map_h[int(pos_x)][int(y + 0.2)]):
            pos_y = y
        elif not (map_h[int(x - 0.2)][int(pos_y)] or map_h[int(x + 0.2)][int(pos_y)] or
                  map_h[int(x)][int(pos_y - 0.2)] or map_h[int(x)][int(pos_y + 0.2)]):
            pos_x = x

        return pos_x, pos_y, rot, rot_v

    @staticmethod
    def gen_map(map_size):
        map_h = np.random.choice([0, 0, 0, 0, 1, 1], (map_size, map_size))
        map_h[0, :], map_h[map_size - 1, :], map_h[:, 0], map_h[:, map_size - 1] = (1, 1, 1, 1)

        pos_x, pos_y, rot = 1.5, np.random.randint(1, map_size - 1) + .5, np.pi / 4
        x, y = int(pos_x), int(pos_y)
        map_h[x][y] = 0
        count = 0
        while True:
            test_x, test_y = x, y
            if np.random.uniform() > 0.5:
                test_x = test_x + np.random.choice([-1, 1])
            else:
                test_y = test_y + np.random.choice([-1, 1])
            if 0 < test_x < map_size - 1 and 0 < test_y < map_size - 1:
                if map_h[test_x][test_y] == 0 or count > 5:
                    count = 0
                    x, y = test_x, test_y
                    map_h[x][y] = 0
                    if x == map_size - 2:
                        break
                else:
                    count += 1
        return pos_x, pos_y, rot, map_h

    @staticmethod
    @njit()  # Pre-Compile Optimization
    def new_frame(pos_x, pos_y, rot, frame, sky, floor, h_res, half_v_res, fov, map_h, map_size, wall, rot_v):
        # Vertical Pan Offset
        offset = -int(half_v_res * rot_v)
        sky_start = int(half_v_res * 0.8 - offset)

        for i in range(h_res):
            rot_i = rot + np.deg2rad(i / fov - 30)
            sin, cos, cos2 = np.sin(rot_i), np.cos(rot_i), np.cos(np.deg2rad(i / fov - 30))
            frame[i][:] = sky[int(np.rad2deg(rot_i) % 359)][sky_start:sky_start + 2 * half_v_res]

            x, y = pos_x, pos_y
            while map_h[int(x) % (map_size - 1)][int(y) % (map_size - 1)] == 0:
                x += 0.01 * cos
                y += 0.01 * sin

            n = abs((x - pos_x) / cos)
            h = int(half_v_res / (n * cos2 + 0.001))

            # Shading
            shade = 0.5 * (h / half_v_res)
            if shade > 1:
                shade = 1

            # Wall Textures
            xx = int(x * 4 % 1 * 99)
            if x % 1 < 0.02 or x % 1 > 0.98:
                xx = int(y * 4 % 1 * 99)
            yy = np.linspace(0, 3, h * 2) * 99 % 99

            # Wall Render
            for k in range(h * 2):
                if 0 <= half_v_res - h + k + offset < 2 * half_v_res:
                    frame[i][half_v_res - h + k + offset] = shade * wall[xx][int(yy[k])]

            # Floor Render
            for j in range(half_v_res - h - offset):
                n = (half_v_res / (half_v_res - j - offset)) / cos2
                x, y = pos_x + cos * n, pos_y + sin * n
                xx, yy = int(x * 4 % 1 * 99), int(y * 4 % 1 * 99)

                shade = min(0.5 / n, 1)

                frame[i][half_v_res * 2 - j - 1] = shade * floor[xx][yy]

        return frame
