import numpy as np
import sdl2.ext
from sdl2 import *
from random import randint
from Classes import Deur
from PIL import Image

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
    sdl2.ext.Color(64, 64, 64, 100),  # 4 = Donker grijs
    sdl2.ext.Color(128, 128, 128, 100),  # 5 = Grijs
    sdl2.ext.Color(192, 192, 192, 100),  # 6 = Licht grijs
    sdl2.ext.Color(255, 255, 255, 100),  # 7 = Wit
    sdl2.ext.Color(120, 200, 250, 100),  # 8 = Blauw_lucht
    sdl2.ext.Color(106, 13, 173, 0)  # 9 = Purple
]
colors = [0, 0, 0, 102, 102, 102, 176, 176, 176, 255, 255, 255]
kleur_dict = {0: [0, 0, 0, 0], 25: [255, 0, 20, 0], 50: [0, 255, 0, 0], 75: [0, 0, 255, 100], 100: [225, 165, 0, 0], 125: [64, 64, 64, 100], 150: [128, 128, 128, 100], 175: [192, 192, 192, 100], 200: [255, 255, 255, 100], 225: [120, 200, 250, 100], 250: [106, 13, 173, 0]}

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


def world_generation(openingen=[]):
    kaart = np.zeros((9, 9), dtype='int32')
    kleur = randint(2, 6)
    kaart[:3, :3] = kleur
    kleur = randint(2, 6)
    kaart[-3:, -3:] = kleur
    kleur = randint(2, 6)
    kaart[-3:, :3] = kleur
    kleur = randint(-1, 30)
    kaart[:3, -3:] = (kleur % 4) + 2
    if len(openingen) < 4:
        extra_openingen = randint(0, 4 - len(openingen))  # Extra openingen
        # print(extra_openingen)
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
                kleur = randint(2, 6)
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
    g_in = np.uint32(np.array(g_image_in))
    b_in = np.uint32(np.array(b_image_in))

    shape0 = r_in.shape[0]
    shape1 = r_in.shape[1]

    # hier komen de matrixbewerkingen
    r_out = np.zeros((shape0,shape1))
    g_out = np.zeros((shape0,shape1))
    b_out = np.zeros((shape0,shape1))

    for i in range(11):
        mask = r_in == (i*25)
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
    output_im = Image.merge("RGBA", (r_image_out, g_image_out, b_image_out,alfa))
    return output_im


class Tile():
    def __init__(self, generated, png=0):
        self.map = generated[0]
        self.png = png
        self.openingen = generated[1]


class Map():
    def __init__(self):
        self.tile_map = np.full((111, 111), Tile((0, 0)))
        self.tile_map[:, :] = 0
        self.tiles_size = np.shape(self.tile_map)
        y, x = self.tiles_size
        self.world_size = (y * 9, x * 9)
        self.world_map = np.zeros(self.world_size, dtype='int32')
        self.added = []

    def start(self):
        y, x = np.shape(self.tile_map)
        self.added = []
        map = np.ones((9, 9), dtype='int32')
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

        map_initieel = np.full((9, 9), 2)
        map_initieel[0:-3, 3:-3] = 0
        intiele_tile = Tile((map_initieel, [1]))
        tile_2 = Tile(world_generation([1, 2, 3, 4]))
        tile_3 = Tile(world_generation([1, 2, 3, 4]))
        self.tile_map[48, 50] = tile_3
        self.tile_map[49, 50] = tile_2
        self.tile_map[50, 50] = intiele_tile
        self.size = (np.shape(map_initieel))[0]
        for i in range(1, x - 1):
            for j in range(1, y - 1):
                self.direct_map_making(i, j)
        self.update()

        im = Image.fromarray(self.world_map * 25)
        rgbimg = Image.new("RGBA", im.size)
        rgbimg.paste(im)
        new_im = converter(rgbimg)
        new_im.save('map.png')

    def update(self):
        for x, y in self.added:
            self.world_map[x * self.size:(x + 1) * self.size, y * self.size:(y + 1) * self.size] = self.tile_map[
                x, y].map
        self.added = []

    def direct_map_making(self, x_pos, y_pos):
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
