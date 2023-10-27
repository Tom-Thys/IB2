import math
import time
import random
import numpy as np
import sdl2.ext
from sdl2 import *
from random import randint

# de "wereldkaart". Dit is een 2d matrix waarin elke cel een type van muur voorstelt
# Een 0 betekent dat op deze plaats in de game wereld geen muren aanwezig zijn
world_map = np.array([[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
                      [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                      [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                      [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 2],
                      [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 2],
                      [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                      [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                      [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
                      [2, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
                      [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
                      [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
                      [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 2],
                      [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 2],
                      [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                      [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
                      [2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 3, 2, 4, 2, 5, 2, 2, 2]])
world_map_2 = np.zeros((30, 5), dtype='int')
world_map_2[0, -2] = 3

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
        extra_openingen = 0 #randint(0, 4 - len(openingen))  # Extra openingen
        print(extra_openingen)
        for i in range(extra_openingen):
            while True:
                opening = randint(1, 5)
                if opening not in openingen:
                    openingen.append(opening)
                    break
        for i in range(1, 5):
            if i not in openingen:
                kleur = randint(2, 5)
                kaart[z[i][0]:z[i][1], z[i][2]:z[i][3]] = kleur
    print(kaart)
    return kaart, openingen
    kleur = randint(2, 5)


class Tile():
    def __init__(self, generated, png=0,ok = True):
        self.map = generated[0]
        self.png = png
        self.openingen = generated[1]
        self.surrounding = []
        self.ok = ok


class Map():
    def __init__(self):
        self.world_map = np.array(0,dtype='int32')
        self.tile_map = np.full((100,101),Tile((0,0),ok=False))
        self.start()
    def start(self):
        map_initieel = np.full((9, 9), 2, dtype='int32')
        map_initieel[0:-3, 3:-3] = 0
        intiele_tile = Tile((map_initieel, [1]))
        tile_2 = Tile(world_generation([1, 2, 3, 4]))
        self.tile_map[49,50] = tile_2
        self.tile_map[50,50] = intiele_tile
        self.size = (np.shape(map_initieel))[0]

    def update(self):
        y, x = np.shape(self.tile_map)
        self.world_map = np.zeros((y*self.size,x*self.size,),dtype='int32')
        for i, rij in enumerate(self.tile_map):
            for j, element in enumerate(rij):
                if element != 0:
                    self.world_map[i*self.size:(i+1)*self.size,j*self.size:(j+1)*self.size] = element.map
        print(self.world_map)



if __name__ == '__main__':
    inf_world = Map()
    inf_world.update()

    #main()
