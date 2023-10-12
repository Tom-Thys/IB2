import math
import time
import random
import numpy as np

import sdl2.ext





# de "wereldkaart". Dit is een 2d matrix waarin elke cel een type van muur voorstelt
# Een 0 betekent dat op deze plaats in de game wereld geen muren aanwezig zijn
world_map = [[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
             [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
             [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
             [2, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 2],
             [2, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 2],
             [2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 2],
             [0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0],
             [2, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 2],
             [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
             [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
             [2, 2, 2, 4, 2, 3, 2, 4, 2, 5, 2, 2, 2]]
worldlijst = [world_map]




def make_world_png(maplijst,unit_d=10):
    """
    Creëert een PNG die weer geeft, welk gebouw waar staat op de wereldmap
    Moet enkel gerunt worden als er een wijziging gebeurt aan de wereldmap
    Dit kan voornamelijk hier gerunt worden
    """
    for id,map in enumerate(maplijst):
        y_nd, x_nd = np.shape(map)
        window = SDL_CreateWindow(b"Wereld map", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, int(unit_d*x_nd), int(unit_d*y_nd),SDL_WINDOW_SHOWN)
        windowsurface = SDL_GetWindowSurface(window)
        renderer = sdl2.ext.Renderer(windowsurface)
        # sdl2.SDL_CreateRGBSurface
        for j, row in enumerate(map):
            for i, kleur in enumerate(row):
                renderer.fill((i*unit_d,j*unit_d,(i+1)*unit_d,(j+1)*unit_d),kleuren[kleur])
        #renderer.present()
        string = b"mappen\map"+str(id).encode('utf-8')+b".png"
        sdl2.sdlimage.IMG_SavePNG(windowsurface,string)
        SDL_DestroyWindow(window)

def main():
    # Initialiseer de SDL2 bibliotheek
    sdl2.ext.init()

    # Maak png van wereldmap
    make_world_png(maplijst)
    time.sleep(0.002)



if __name__ == '__main__':
    main()
