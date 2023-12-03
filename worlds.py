import math
import random

import numpy as np
import sdl2.ext
from sdl2 import *
from random import randint
from Classes import Deur, Sprite
from PIL import Image

random.seed(10)

# de "wereldkaart". Dit is een 2d matrix waarin elke cel een type van muur voorstelt
# Een 0 betekent dat op deze plaats in de game wereld geen muren aanwezig zijn
world_map = np.array([[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
                      [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                      [2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                      [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                      [2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                      [2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                      [2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                      [2, 0, 0, 0, -1000, 0, 0, 0, 0, 0, 0, 0, -1001, 0, 0, 0, 0, 0, 4],
                      [2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
                      [2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
                      [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
                      [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                      [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                      [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                      [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                      [2, 2, 2, 4, 2, 2, 1, 1, 1, 2, 2, 3, 2, 4, 2, 5, 2, 2, 2]])
world_map_2 = np.zeros((30, 5), dtype='int')
world_map_2[0, -2] = 3

deuren = {0: Deur(), -1000: Deur(), -1001: Deur()}

garage_map = [[10, 10, 10, 10, 10, 10, 10, 10],
              [10, 0, 0, 0, 0, 0, 0, 10],
              [10, 0, 0, 0, 0, 0, 0, 10],
              [10, 0, 0, 0, 0, 0, 0, 10],
              [10, 0, 0, 0, 0, 0, 0, 10],
              [10, 10, 10, 10, 10, 10, 10, 10]]

worldlijst = [world_map, world_map_2, garage_map]

kleuren = [
    sdl2.ext.Color(0, 0, 0, 0),  # 0 = Zwart
    sdl2.ext.Color(255, 0, 20, 0),  # 1 = Rood
    sdl2.ext.Color(0, 255, 0, 0),  # 2 = Groen
    sdl2.ext.Color(0, 0, 255, 100),  # 3 = Blauw
    sdl2.ext.Color(225, 165, 0, 0),  # 4 = oranje
    sdl2.ext.Color(64, 64, 64, 100),  # 5 = Donker grijs
    sdl2.ext.Color(128, 128, 128, 100),  # 6 = Grijs
    sdl2.ext.Color(192, 192, 192, 100),  # 7 = Licht grijs
    sdl2.ext.Color(255, 255, 255, 100),  # 8 = Wit
    sdl2.ext.Color(120, 200, 250, 100),  # 9 = Blauw_lucht
    sdl2.ext.Color(106, 13, 173, 100),  # 10 = Purple
    sdl2.ext.Color(255, 255, 0, 100),  # 11 = Yellow
]
colors = [0, 0, 0, 102, 102, 102, 176, 176, 176, 255, 255, 255]
kleur_dict = {0: (0, 0, 0), 25: (255, 0, 20), 50: (255, 0, 20), 75: (106, 13, 173), 100: (255, 255, 0),
              125: (128, 128, 128), 150: (0, 255, 0), 175: (255, 0, 20)}


def make_world_png(worldmap, unit_d=1):
    """
    Creëert een PNG die weer geeft, welk gebouw waar staat op de wereldmap
    Moet enkel gerunt worden als er een wijziging gebeurt aan de wereldmap
    Dit kan voornamelijk hier gerunt worden
    """

    y_nd, x_nd = np.shape(worldmap)
    window = SDL_CreateWindow(b"Wereld map", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, int(unit_d * x_nd),
                              int(unit_d * y_nd), SDL_WINDOW_SHOWN)
    windowsurface = SDL_GetWindowSurface(window)
    renderer = sdl2.ext.Renderer(windowsurface)
    # sdl2.SDL_CreateRGBSurface
    for j, row in enumerate(worldmap):
        if j % 3 != 0:
            continue
        for i, kleur in enumerate(row):
            if i % 3 != 0:
                continue
            kleur = kleur % len(kleuren)
            renderer.fill((i * unit_d, j * unit_d, (i + 3) * unit_d, (j + 3) * unit_d), kleuren[kleur])
    renderer.present()
    string = b"mappen\map" + str(0).encode('utf-8') + b".png"
    sdl2.sdlimage.IMG_SavePNG(windowsurface, string)
    SDL_DestroyWindow(window)


def main():
    # Initialiseer de SDL2 bibliotheek
    sdl2.ext.init()

    # Maak png van wereldmap
    make_world_png(worldlijst)


def aanmaken_sprites_bomen(speler_x, speler_y, HOOGTE, bomen, sprite_map_png, tree, worldmap, sprites, aantalbomen=1):
    x_max = speler_x + 100
    x_min = speler_x - 100
    y_max = speler_y + 100
    y_min = speler_y - 100
    # Checken of de coordinaten in het veld liggen
    if x_max >= 1000:
        x_max = 999
    if y_max >= 1000:
        y_max = 999
    if x_min <= 0:
        x_min = 1
    if y_min <= 0:
        y_min = 1
    for sprite in sprites:
        if sprite.afstand >= 80:
            sprites.remove(sprite)
    if len(sprites) >= 100:
        return sprites

    for teller in range(0, aantalbomen):
        while True:
            x = random.uniform(x_min, x_max)
            y = random.uniform(y_min, y_max)

            # print(math.floor(x))
            # print(math.floor(y))

            # print("de zak"  + str((speler_x - x)**2 + (speler_y - y)**2))
            if (worldmap[math.floor(y), math.floor(x)] <= 0
                    and worldmap[math.floor(y), math.floor(x+1)] <= 0
                    and worldmap[math.floor(y+1), math.floor(x)] <= 0
                    and worldmap[math.floor(y), math.floor(x-1)] <= 0
                    and worldmap[math.floor(y-1), math.floor(x)] <= 0
                    and (speler_x - x) ** 2 + (speler_y - y) ** 2 >= 100):
                sprites.append(Sprite(tree, bomen, sprite_map_png, x, y, HOOGTE, "Boom", schaal=0.2))
                break

    return sprites


def world_generation(openingen=[]):
    kaart = np.zeros((9, 9), dtype='int32')
    pakjes_plekken = [(1, 3), (3, 1), (7, 3), (3, 7), (1, 5), (5, 1), (7, 5), (5, 7)]
    for plekx, pleky in pakjes_plekken:
        kaart[plekx, pleky] = -1
    kleur = randint(2, 6)
    kaart[:3, :3] = kleur
    kleur = randint(2, 6)
    kaart[-3:, -3:] = kleur
    kleur = randint(2, 6)
    kaart[-3:, :3] = kleur
    kleur = randint(-1, 30)
    kaart[:3, -3:] = (kleur % 4) + 2
    if len(openingen) < 3:
        extra_openingen = randint(0, 3 - len(openingen))  # Extra openingen
        if extra_openingen == 0 and len(openingen) <= 1:
            extra_openingen = randint(1, 3)
        for i in range(extra_openingen):
            loops = 0
            while loops < 6:
                loops += 1
                opening = randint(1, 4)
                if opening not in openingen:
                    openingen.append(opening)
                    continue
    elif len(openingen) == 3:
        openingen.pop(randint(0, 2))
        if randint(0, 10) == 0:
            openingen.pop(randint(0, 1))
            if randint(0, 20) == 0:
                openingen.pop(0)
    else:
        openingen.pop(randint(0, 3))
        if randint(0, 2) == 0:
            openingen.pop(randint(0, 2))
            if randint(0, 6) == 6:
                openingen.pop(randint(0, 1))
    for i in range(1, 5):
        if i not in openingen:
            if i == 1:
                kaart[3:-3, :3] = 6
            elif i == 2:
                kaart[:3, 3:-3] = 6
            elif i == 3:
                kaart[3:-3, -3:] = 6
            else:
                kaart[-3:, 3:-3] = 6
    # print(kaart)
    return kaart, openingen


def converter(input_image):
    r_image_in, g_image_in, b_image_in, alfa = input_image.split()
    r_in = np.uint32(np.array(r_image_in))

    shape0 = r_in.shape[0]
    shape1 = r_in.shape[1]

    # hier komen de matrixbewerkingen
    r_out = np.zeros((shape0, shape1))
    g_out = np.zeros((shape0, shape1))
    b_out = np.zeros((shape0, shape1))

    for i in range(11):
        mask = r_in == (i * 25)

        if np.any(mask):
            r_out[mask] = kleur_dict[i * 25][0]
            g_out[mask] = kleur_dict[i * 25][1]
            b_out[mask] = kleur_dict[i * 25][2]
        """for j in range(shape1):
            gray = b_in[i][j]
            r_out[i][j] = kleur_dict[gray][0]
            g_out[i][j] = kleur_dict[gray][1]
            b_out[i][j] = kleur_dict[gray][2]"""

    # converteer drie matrices terug naar een afbeelding
    r_image_out = Image.fromarray(np.uint8(r_out))
    g_image_out = Image.fromarray(np.uint8(g_out))
    b_image_out = Image.fromarray(np.uint8(b_out))
    output_im = Image.merge("RGBA", (r_image_out, g_image_out, b_image_out, alfa))
    return output_im


class Tile():
    def __init__(self, generated, png=0):
        self.map = generated[0]
        self.png = png
        self.openingen = generated[1]


class Map():
    def __init__(self):
        self.tile_map = np.full((120, 120), Tile((0, 0)))
        self.tile_map[:, :] = 0
        self.tiles_size = np.shape(self.tile_map)
        y, x = self.tiles_size
        self.world_size = (y * 9, x * 9)
        self.world_map = np.zeros(self.world_size, dtype='int32')
        self.added = []

    def start(self):
        y, x = np.shape(self.tile_map)
        self.added = []
        # map = np.ones((9, 9), dtype='int32')
        map = np.full((9, 9), fill_value=7, dtype='int32')
        openingen = []
        surrounding_tiles = Tile((map, openingen))
        self.tile_map[0, :] = surrounding_tiles
        self.tile_map[:, 0] = surrounding_tiles
        self.tile_map[-1, :] = surrounding_tiles
        self.tile_map[:, -1] = surrounding_tiles

        for j in range(y):
            self.added.append((0, j))
            self.added.append((x - 1, j))
        for i in range(x):
            self.added.append((i, 0))
            self.added.append((i, y - 1))

        kaart = np.zeros((9, 9), dtype='int32')
        kaart[:, 4] = -2
        kaart[4, :] = -2
        intiele_tile = Tile((kaart, [1]))
        tile_2 = Tile((kaart, [1, 2, 3, 4]))
        tile_3 = Tile((kaart, [1, 2, 3, 4]))
        self.tile_map[48, 50] = tile_3
        self.tile_map[49, 50] = tile_2
        self.tile_map[49, 51] = tile_2
        self.tile_map[49, 49] = tile_2
        self.tile_map[50, 50] = intiele_tile
        if False:
            for i in range(5):
                x = randint(1, self.tiles_size[1] - 1)
                y = randint(1, self.tiles_size[0] - 1)
                print(x, y)
                self.tile_map[y, x] = Tile(world_generation([1, 2, 3, 4]))
        # self.world_map[450,450] = -5
        self.size = (np.shape(kaart))[0]
        for i in range(1, x - 1):
            for j in range(1, y - 1):
                self.direct_map_making(i, j)
                self.added.append((i, j))
        """for i in range(1, x - 1):
            for j in range(1, y - 1):
                self.drivable(i, j)"""
        self.update()

        if True:
            im = Image.fromarray(self.world_map * 25)
            rgbimg = Image.new("RGBA", im.size)
            rgbimg.paste(im)
            new_im = converter(rgbimg)
            new_im.save('mappen\map.png')

    def update(self):
        for x, y in self.added:
            self.world_map[x * self.size:(x + 1) * self.size, y * self.size:(y + 1) * self.size] = self.tile_map[
                x, y].map
        self.added = []
        self.mogelijke_bestemmingen = np.transpose((self.world_map == -1).nonzero()).tolist()

    def direct_map_making(self, x_pos, y_pos):
        if self.tile_map[x_pos, y_pos] == 0:
            if randint(0, 100) == 0:
                kaart = np.zeros((9, 9), dtype='int32')
                self.tile_map[x_pos, y_pos] = Tile((kaart, []))
                return

            openingen = []
            if self.tile_map[x_pos + 1, y_pos] != 0:
                if 3 in self.tile_map[x_pos + 1, y_pos].openingen:
                    openingen.append(1)
            if self.tile_map[x_pos - 1, y_pos] != 0:
                if 1 in self.tile_map[x_pos - 1, y_pos].openingen:
                    openingen.append(3)
            if self.tile_map[x_pos, y_pos + 1] != 0:
                if 2 in self.tile_map[x_pos, y_pos + 1].openingen:
                    openingen.append(4)
            if self.tile_map[x_pos, y_pos - 1] != 0:
                if 4 in self.tile_map[x_pos, y_pos - 1].openingen:
                    openingen.append(2)
            self.tile_map[x_pos, y_pos] = Tile(world_generation(openingen))

    def drivable(self, x_pos, y_pos):
        if self.tile_map[x_pos, y_pos] == 0:
            return
        kaart = self.tile_map[x_pos, y_pos].map
        openingen = self.tile_map[x_pos, y_pos].openingen
        drive = []
        if self.tile_map[x_pos, y_pos + 1] != 0 and 1 in openingen:
            if 3 in self.tile_map[x_pos, y_pos + 1].openingen:
                drive.append(1)
        if self.tile_map[x_pos, y_pos- 1] != 0 and 3 in openingen:
            if 1 in self.tile_map[x_pos, y_pos- 1].openingen:
                drive.append(3)
        if self.tile_map[x_pos + 1, y_pos] != 0 and 4 in openingen:
            if 2 in self.tile_map[x_pos + 1, y_pos].openingen:
                drive.append(4)
        if self.tile_map[x_pos- 1, y_pos] != 0 and 2 in openingen:
            if 4 in self.tile_map[x_pos- 1, y_pos].openingen:
                drive.append(2)

        for i in drive:
            kaart[4, 4] = -2
            # kleur = randint(2, 6)
            if i == 1:
                kaart[4, 3] = -2
            elif i == 2:
                kaart[3, 4] = -2
            elif i == 3:
                kaart[4, 5] = -2
            else:
                kaart[5, 4] = -2
        self.tile_map[x_pos, y_pos].map = kaart

    def map_making(self, speler):
        lengte = 7
        y, x = speler.tile
        if np.any(self.world_map[(x - lengte):x, y:(y + lengte)] == 0):  # bloking high end??
            for i in range(lengte):
                x_pos = x - i
                if x_pos - 1 < 0:
                    for i in range(3):
                        self.tile_map[x_pos, y + 1] = Tile((np.full((9, 9), 1), []))
                        self.added.append((x_pos, y + i))
                    break
                for j in range(lengte):
                    y_pos = y + j
                    if y_pos + 2 > self.tiles_size[0]:
                        self.tile_map[x_pos, y_pos] = Tile((np.full((9, 9), 1), []))
                        self.added.append((x_pos, y_pos))
                        break
                    if self.tile_map[x_pos, y_pos] == 0:
                        openingen = []
                        if self.tile_map[x_pos + 1, y_pos] != 0:
                            if 3 in self.tile_map[x_pos + 1, y_pos].openingen:
                                openingen.append(1)
                        if self.tile_map[x_pos - 1, y_pos] != 0:
                            if 1 in self.tile_map[x_pos - 1, y_pos].openingen:
                                openingen.append(3)
                        if self.tile_map[x_pos, y_pos + 1] != 0:
                            if 2 in self.tile_map[x_pos, y_pos + 1].openingen:
                                openingen.append(4)
                        if self.tile_map[x_pos, y_pos - 1] != 0:
                            if 4 in self.tile_map[x_pos, y_pos - 1].openingen:
                                openingen.append(2)
                        self.tile_map[x_pos, y_pos] = Tile(world_generation(openingen))
                        self.added.append((x_pos, y_pos))
        if np.any(self.world_map[(x - lengte):x, (y - lengte):y] == 0):
            for i in range(lengte):
                x_pos = x - i
                if x_pos - 1 < 0:
                    for i in range(3):
                        self.tile_map[x_pos, y + 1] = Tile((np.full((9, 9), 1), []))
                        self.added.append((x_pos, y + i))
                    break
                for j in range(lengte):
                    y_pos = y - j
                    if y_pos - 1 < 0:
                        self.tile_map[x_pos, y_pos] = Tile((np.full((9, 9), 1), []))
                        self.added.append((x_pos, y_pos))
                        break
                    if self.tile_map[x_pos, y_pos] == 0:
                        openingen = []
                        if self.tile_map[x_pos + 1, y_pos] != 0:
                            if 3 in self.tile_map[x_pos + 1, y_pos].openingen:
                                openingen.append(1)
                        if self.tile_map[x_pos - 1, y_pos] != 0:
                            if 1 in self.tile_map[x_pos - 1, y_pos].openingen:
                                openingen.append(3)
                        if self.tile_map[x_pos, y_pos + 1] != 0:
                            if 2 in self.tile_map[x_pos, y_pos + 1].openingen:
                                openingen.append(4)
                        if self.tile_map[x_pos, y_pos - 1] != 0:
                            if 4 in self.tile_map[x_pos, y_pos - 1].openingen:
                                openingen.append(2)
                        self.tile_map[x_pos, y_pos] = Tile(world_generation(openingen))
                        self.added.append((x_pos, y_pos))
        if np.any(self.world_map[x:(x + lengte), (y - lengte):y] == 0):
            for i in range(lengte):
                x_pos = x + i
                if x_pos + 2 > self.tiles_size[1]:
                    self.tile_map[x_pos, y] = Tile((np.full((9, 9), 1), []))
                    self.added.append((x_pos, y))
                    break
                for j in range(lengte):
                    y_pos = y - j
                    if y_pos - 1 < 0 or y_pos + 2 > self.tiles_size[0]:
                        self.tile_map[x_pos, y_pos] = Tile((np.full((9, 9), 1), []))
                        self.added.append((x_pos, y_pos))
                        break
                    if self.tile_map[x_pos, y_pos] == 0:
                        openingen = []
                        if self.tile_map[x_pos + 1, y_pos] != 0:
                            if 3 in self.tile_map[x_pos + 1, y_pos].openingen:
                                openingen.append(1)
                        if self.tile_map[x_pos - 1, y_pos] != 0:
                            if 1 in self.tile_map[x_pos - 1, y_pos].openingen:
                                openingen.append(3)
                        if self.tile_map[x_pos, y_pos + 1] != 0:
                            if 2 in self.tile_map[x_pos, y_pos + 1].openingen:
                                openingen.append(4)
                        if self.tile_map[x_pos, y_pos - 1] != 0:
                            if 4 in self.tile_map[x_pos, y_pos - 1].openingen:
                                openingen.append(2)
                        self.tile_map[x_pos, y_pos] = Tile(world_generation(openingen))
                        self.added.append((x_pos, y_pos))
        if np.any(self.world_map[x:(x + lengte), y:(y + lengte)] == 0):
            for i in range(lengte):
                x_pos = x + i
                if x_pos + 2 > self.tiles_size[1]:
                    self.tile_map[x_pos, y] = Tile((np.full((9, 9), 1), []))
                    self.added.append((x_pos, y))
                    break
                for j in range(lengte):
                    y_pos = y + j
                    if y_pos + 2 > self.tiles_size[0]:
                        self.tile_map[x_pos, y_pos] = Tile((np.full((9, 9), 1), []))
                        self.added.append((x_pos, y_pos))
                        break
                    if self.tile_map[x_pos, y_pos] == 0:
                        openingen = []
                        if self.tile_map[x_pos + 1, y_pos] != 0:
                            if 3 in self.tile_map[x_pos + 1, y_pos].openingen:
                                openingen.append(1)
                        if self.tile_map[x_pos - 1, y_pos] != 0:
                            if 1 in self.tile_map[x_pos - 1, y_pos].openingen:
                                openingen.append(3)
                        if self.tile_map[x_pos, y_pos + 1] != 0:
                            if 2 in self.tile_map[x_pos, y_pos + 1].openingen:
                                openingen.append(4)
                        if self.tile_map[x_pos, y_pos - 1] != 0:
                            if 4 in self.tile_map[x_pos, y_pos - 1].openingen:
                                openingen.append(2)
                        self.tile_map[x_pos, y_pos] = Tile(world_generation(openingen))
                        self.added.append((x_pos, y_pos))
        # looping
        self.update()


if __name__ == '__main__':
    pass
    # positie van de speler
    """p_speler_x, p_speler_y = 50.5 * 9, 49 * 9

    # richting waarin de speler kijkt
    r_speler_hoek = math.pi / 4
    # FOV
    d_camera = 1
    #
    # Speler aanmaken
    speler = Player(p_speler_x, p_speler_y, r_speler_hoek)
    inf_world = Map()
    inf_world.update()"""

    # main()
