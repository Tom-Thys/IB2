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
world_map_2 = np.zeros((30,5),dtype='int')
world_map_2[0,-2] = 3


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
    sdl2.ext.Color(106, 13, 173)    #9 = Purple
]

def make_world_png(worldlijst,unit_d=30):
    """
    Creëert een PNG die weer geeft, welk gebouw waar staat op de wereldmap
    Moet enkel gerunt worden als er een wijziging gebeurt aan de wereldmap
    Dit kan voornamelijk hier gerunt worden
    """
    for id,map in enumerate(worldlijst):
        y_nd, x_nd = np.shape(map)
        window = SDL_CreateWindow(b"Wereld map", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, int(unit_d*x_nd), int(unit_d*y_nd),SDL_WINDOW_SHOWN)
        windowsurface = SDL_GetWindowSurface(window)
        renderer = sdl2.ext.Renderer(windowsurface)
        # sdl2.SDL_CreateRGBSurface
        for j, row in enumerate(map):
            for i, kleur in enumerate(row):
                kleur = kleur % len(kleuren)
                renderer.fill((i*unit_d,j*unit_d,(i+1)*unit_d,(j+1)*unit_d),kleuren[kleur])
        renderer.present()
        string = b"mappen\map"+str(id).encode('utf-8')+b".png"
        sdl2.sdlimage.IMG_SavePNG(windowsurface,string)
        SDL_DestroyWindow(window)

def main():
    # Initialiseer de SDL2 bibliotheek
    sdl2.ext.init()

    # Maak png van wereldmap
    make_world_png(worldlijst)

def world_generation(openingen = []):
    z = {1:(2,-4,0,2), 2: (0,2,2,-4), 3:(2,-4,-4,-1), 4:(-4,-1,2,-4)} #KANTEN voor map locaties invullen gaten
    openingen = []
    map = np.zeros((9, 9),dtype='int32')
    kleur = randint(2,5)
    map[:2,:2] = kleur
    kleur = randint(2,5)
    map[-4:-1,-4:-1] = kleur
    kleur = randint(2,5)
    map[-4:-1,:2] = kleur
    kleur = randint(2,5)
    map[:2,-4:-1] = kleur
    if len(openingen) == 4:
        return map
    else:
        extra_openingen = randint(0, 4-len(openingen)) #Extra openingen
        for i in range(extra_openingen):
            while True:
                opening = randint(1,5)
                if opening not in openingen:
                    openingen.append(opening)
                    break
        for i in range(1,5):
            if i not in openingen:
                kleur = randint(2, 5)
                map[z[i][0]:z[i][1],z[i][2]:z[i][3]] = kleur
    return map
    kleur = randint(2, 5)




class Tiles():
    def __init__(self, map, openingen, png=0):
        self.map = map
        self.png = png
        self.openingen = openingen
        self.surrounding = []
        self.full = False












if __name__ == '__main__':
    main()
