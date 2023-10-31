import math
import time
import random
import numpy as np
import sdl2.ext
from sdl2 import *
from random import randint
from Classes import Deur


from Classes import Player

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
world_map_2 = np.zeros((30,5),dtype='int')
world_map_2[0,-2] = 3

deuren = {0: Deur(), -1000: Deur(),-1001: Deur()}


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
    sdl2.ext.Color(64, 64, 64, 100),  # 4 = Donker grijs
    sdl2.ext.Color(128, 128, 128, 100),  # 5 = Grijs
    sdl2.ext.Color(192, 192, 192, 100),  # 6 = Licht grijs
    sdl2.ext.Color(255, 255, 255, 100),  # 7 = Wit
    sdl2.ext.Color(120, 200, 250, 100),  # 8 = Blauw_lucht
    sdl2.ext.Color(106, 13, 173)  # 9 = Purple
]


def make_world_png(worldlijst, unit_d=30):
    """
    Creëert een PNG die weer geeft, welk gebouw waar staat op de wereldmap
    Moet enkel gerunt worden als er een wijziging gebeurt aan de wereldmap
    Dit kan voornamelijk hier gerunt worden
    """
    for id, map in enumerate(worldlijst):
        y_nd, x_nd = np.shape(map)
        window = SDL_CreateWindow(b"Wereld map", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, int(unit_d * x_nd),
                                  int(unit_d * y_nd), SDL_WINDOW_SHOWN)
        windowsurface = SDL_GetWindowSurface(window)
        renderer = sdl2.ext.Renderer(windowsurface)
        # sdl2.SDL_CreateRGBSurface
        for j, row in enumerate(map):
            for i, kleur in enumerate(row):
                kleur = kleur % len(kleuren)
                renderer.fill((i * unit_d, j * unit_d, (i + 1) * unit_d, (j + 1) * unit_d), kleuren[kleur])
        renderer.present()
        string = b"mappen\map" + str(id).encode('utf-8') + b".png"
        sdl2.sdlimage.IMG_SavePNG(windowsurface, string)
        SDL_DestroyWindow(window)


def main():
    # Initialiseer de SDL2 bibliotheek
    sdl2.ext.init()

    # Maak png van wereldmap
    make_world_png(worldlijst)


def world_generation(openingen=[]):
    z = {1: (2, -3, 0, 2), 2: (0, 2, 2, -3), 3: (2, -3, -3, -1),
         4: (-3, -1, 2, -3)}  # KANTEN voor map locaties invullen gaten
    kaart = np.zeros((9, 9), dtype='int32')
    kleur = randint(2, 5)
    kaart[:3, :3] = kleur
    kleur = randint(2, 5)
    kaart[-3:, -3:] = kleur
    kleur = randint(2, 5)
    kaart[-3:, :3] = kleur
    kleur = randint(2, 5)
    kaart[:3, -3:] = kleur
    if len(openingen) == 4:
        return kaart, openingen
    else:
        extra_openingen = randint(0, 4 - len(openingen))  # Extra openingen
        #print(extra_openingen)
        for i in range(extra_openingen):
            loops = 0
            while loops < 5:
                loops += 1
                opening = randint(1, 4)
                if opening not in openingen:
                    openingen.append(opening)
                    continue
        for i in range(1, 5):
            if i not in openingen:
                kleur = randint(2, 5)
                kaart[z[i][0]:z[i][1], z[i][2]:z[i][3]] = kleur
    #print(kaart)
    return kaart, openingen


class Tile():
    def __init__(self, generated, png=0):
        self.map = generated[0]
        self.png = png
        self.openingen = generated[1]
        self.surrounding = []


class Map():
    def __init__(self):
        self.tile_map = np.full((500, 600), Tile((0, 0)))
        y, x = np.shape(self.tile_map)
        self.world_map = np.zeros((y * 9, x * 9), dtype='int32')
        self.tiles_size = np.shape(self.tile_map)
        self.start()
        self.added = []

    def start(self):
        map_initieel = np.full((9, 9), 2)
        map_initieel[0:-3, 3:-3] = 0
        intiele_tile = Tile((map_initieel, [1]))
        tile_2 = Tile(world_generation([1, 2, 3, 4]))
        tile_3 = Tile(world_generation([1, 2, 3, 4]))
        self.tile_map[:, :] = 0
        self.tile_map[48, 50] = tile_3
        self.tile_map[49, 50] = tile_2
        self.tile_map[50, 50] = intiele_tile
        self.size = (np.shape(map_initieel))[0]

    def update(self):
        for x, y in self.added:
            self.world_map[x * self.size:(x + 1) * self.size, y * self.size:(y + 1) * self.size] = self.tile_map[x,y].map
        self.added = []
        #print(self.world_map)

    def map_making(self, speler):
        lengte = 7
        y, x = speler.tile
        if np.any(self.world_map[(x - lengte):x, y:(y + lengte)] == 0):  # bloking high end??
            for i in range(lengte):
                x_pos = x - i
                if x_pos - 1 < 0:
                    for i in range(3):
                        self.tile_map[x_pos, y+1] = Tile((np.full((9, 9), 1), []))
                        self.added.append((x_pos, y+i))
                    break
                for j in range(lengte):
                    y_pos = y+j
                    if y_pos + 2 > self.tiles_size[0]:
                        self.tile_map[x_pos, y_pos] = Tile((np.full((9, 9), 1), []))
                        self.added.append((x_pos, y_pos))
                        break
                    if self.tile_map[x_pos,y_pos] == 0:
                        openingen = []
                        if self.tile_map[x_pos+1,y_pos] != 0:
                            if 3 in self.tile_map[x_pos+1,y_pos].openingen:
                                openingen.append(1)
                        if self.tile_map[x_pos-1,y_pos] != 0:
                            if 1 in self.tile_map[x_pos-1,y_pos].openingen:
                                openingen.append(3)
                        if self.tile_map[x_pos,y_pos+1] != 0:
                            if 2 in self.tile_map[x_pos,y_pos+1].openingen:
                                openingen.append(4)
                        if self.tile_map[x_pos,y_pos-1] != 0:
                            if 4 in self.tile_map[x_pos,y_pos-1].openingen:
                                openingen.append(2)
                        self.tile_map[x_pos,y_pos] = Tile(world_generation(openingen))
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
                    y_pos = y-j
                    if y_pos - 1 < 0:
                        self.tile_map[x_pos, y_pos] = Tile((np.full((9, 9), 1), []))
                        self.added.append((x_pos, y_pos))
                        break
                    if self.tile_map[x_pos,y_pos] == 0:
                        openingen = []
                        if self.tile_map[x_pos+1,y_pos] != 0:
                            if 3 in self.tile_map[x_pos+1,y_pos].openingen:
                                openingen.append(1)
                        if self.tile_map[x_pos-1,y_pos] != 0:
                            if 1 in self.tile_map[x_pos-1,y_pos].openingen:
                                openingen.append(3)
                        if self.tile_map[x_pos,y_pos+1] != 0:
                            if 2 in self.tile_map[x_pos,y_pos+1].openingen:
                                openingen.append(4)
                        if self.tile_map[x_pos,y_pos-1] != 0:
                            if 4 in self.tile_map[x_pos,y_pos-1].openingen:
                                openingen.append(2)
                        self.tile_map[x_pos,y_pos] = Tile(world_generation(openingen))
                        self.added.append((x_pos, y_pos))
        if np.any(self.world_map[x:(x + lengte), (y - lengte):y] == 0):
            for i in range(lengte):
                x_pos = x + i
                if x_pos + 2 > self.tiles_size[1]:
                    self.tile_map[x_pos, y] = Tile((np.full((9, 9), 1), []))
                    self.added.append((x_pos, y))
                    break
                for j in range(lengte):
                    y_pos = y-j
                    if y_pos - 1 < 0 or y_pos + 2 > self.tiles_size[0]:
                        self.tile_map[x_pos, y_pos] = Tile((np.full((9, 9), 1), []))
                        self.added.append((x_pos, y_pos))
                        break
                    if self.tile_map[x_pos,y_pos] == 0:
                        openingen = []
                        if self.tile_map[x_pos+1,y_pos] != 0:
                            if 3 in self.tile_map[x_pos+1,y_pos].openingen:
                                openingen.append(1)
                        if self.tile_map[x_pos-1,y_pos] != 0:
                            if 1 in self.tile_map[x_pos-1,y_pos].openingen:
                                openingen.append(3)
                        if self.tile_map[x_pos,y_pos+1] != 0:
                            if 2 in self.tile_map[x_pos,y_pos+1].openingen:
                                openingen.append(4)
                        if self.tile_map[x_pos,y_pos-1] != 0:
                            if 4 in self.tile_map[x_pos,y_pos-1].openingen:
                                openingen.append(2)
                        self.tile_map[x_pos,y_pos] = Tile(world_generation(openingen))
                        self.added.append((x_pos, y_pos))
        if np.any(self.world_map[x:(x + lengte), y:(y + lengte)] == 0):
            for i in range(lengte):
                x_pos = x + i
                if x_pos + 2 > self.tiles_size[1]:
                    self.tile_map[x_pos, y] = Tile((np.full((9, 9), 1),[]))
                    self.added.append((x_pos, y))
                    break
                for j in range(lengte):
                    y_pos = y+j
                    if y_pos + 2 > self.tiles_size[0]:
                        self.tile_map[x_pos, y_pos] = Tile((np.full((9, 9), 1), []))
                        self.added.append((x_pos, y_pos))
                        break
                    if self.tile_map[x_pos,y_pos] == 0:
                        openingen = []
                        if self.tile_map[x_pos+1,y_pos] != 0:
                            if 3 in self.tile_map[x_pos+1,y_pos].openingen:
                                openingen.append(1)
                        if self.tile_map[x_pos-1,y_pos] != 0:
                            if 1 in self.tile_map[x_pos-1,y_pos].openingen:
                                openingen.append(3)
                        if self.tile_map[x_pos,y_pos+1] != 0:
                            if 2 in self.tile_map[x_pos,y_pos+1].openingen:
                                openingen.append(4)
                        if self.tile_map[x_pos,y_pos-1] != 0:
                            if 4 in self.tile_map[x_pos,y_pos-1].openingen:
                                openingen.append(2)
                        self.tile_map[x_pos,y_pos] = Tile(world_generation(openingen))
                        self.added.append((x_pos,y_pos))
        # looping
        self.update()


if __name__ == '__main__':
    # positie van de speler
    p_speler_x, p_speler_y = 50.5 * 9, 49 * 9

    # richting waarin de speler kijkt
    r_speler_hoek = math.pi / 4
    # FOV
    d_camera = 1
    #
    # Speler aanmaken
    speler = Player(p_speler_x, p_speler_y, r_speler_hoek)
    inf_world = Map()
    inf_world.update()

    # main()
