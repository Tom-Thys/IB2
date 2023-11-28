import math
import time

import numpy as np
from Code_niet_langer_in_gebruik import pathfinding_gps

# from line_profiler_pycharm import profile
# from numba import njit
# from line_profiler_pycharm import profile

from sdl2 import *


class Sprite:
    def __init__(self, image, images, map_png, x, y, height, schaal=0.4):
        self.images = images
        self.image = image  # The image of the sprite
        self.map_png = map_png
        self.map_grootte = 9
        self.x = x  # The x-coordinate of the sprite
        self.y = y  # The y-coordinate of the sprite
        self.position = (x, y)
        self.breedte = image.size[0]
        self.hoogte = image.size[1]
        self.height = height
        self.afstand = 1
        self.schadelijk = True
        self.is_doos = False
        self.schaal = schaal

    def afstanden(self, player):
        """Berekend afstand ifv speler.
        :return: afstand tot speler"""
        self.afstand = ((self.x - player.p_x) ** 2 + (self.y - player.p_y) ** 2) ** (1 / 2)
        return self.afstand

    def update(self, *args):
        """Update elke sprite, wordt overschreven in onderliggende classes."""
        return False


class Doos_Sprite(Sprite):
    """Doos neemt alle functies met sprite over met een extra vector zodat hij gegooid kan worden"""

    def __init__(self, image, map_png, x, y, height, vector, deletable=True):
        super().__init__(image, [], map_png, x, y, height)
        self.deletable = deletable
        self.vector = vector
        self.map_grootte = 2
        self.tick = 1
        self.schadelijk = True
        self.is_doos = True

    def update(self, world_map):
        self.tick += 1
        if self.height < 800:
            time = self.tick / 50
            self.height -= (1 / 2) * (4 * time - time**2)
            x = self.x + 0.1 * self.vector[0]
            y = self.y + 0.1 * self.vector[1]
            atm = 0.3  # afstand_tot_muur zelfde bij auto
            x_2 = x + atm * self.vector[0]
            y_2 = y + atm * self.vector[1]
            if world_map[math.floor(y)][math.floor(x)] <= 0 and world_map[math.floor(y_2)][math.floor(x_2)] <= 0:
                self.x = x
                self.y = y
                self.position = (x, y)
            else:
                self.vector = (0,0)
                self.tick += 10
        else:
            self.height = 800
        if self.deletable and self.tick > 600:
            return True

        return False


class Player:
    def __init__(self, x, y, hoek, breedte=800):
        """Player is gedefinieerd door zijn start x-, y-coördinaten (floats), kijkhoek (rad) en
        de breedte (int) van het scherm dat hij opneemt"""
        self.position = [math.floor(x), math.floor(y)]
        self.p_x = x
        self.p_y = y
        self.hoek = hoek
        self.r_speler = np.array([math.cos(hoek), math.sin(hoek)])
        self.r_camera = np.array([math.cos(self.hoek - math.pi / 2), math.sin(self.hoek - math.pi / 2)])
        self.breedte = breedte
        self.hoeken = np.zeros(self.breedte)
        self.r_stralen = np.zeros((self.breedte, 2))
        self.car = 0
        self.in_auto = False
        self.aantal_hartjes = 5
        self.tile = math.floor(self.p_x / 9), math.floor(self.p_y / 9)
        self.initial = (x, y, hoek)
        self.laatste_doos = 0

    def aanmaak_r_stralen(self, d_camera=1):
        """Gebruikt speler hoek, speler straal en gegeven camera afstand om r_stralen voor raycaster te berekenen"""

        for i in range(self.breedte):
            r_straal_kolom = (d_camera * self.r_speler + (1 - (2 * i) / self.breedte) * self.r_camera)
            hoek = math.atan2(r_straal_kolom[0], r_straal_kolom[1])
            self.hoeken[i] = hoek

        self.r_stralen[:, 0] = np.cos(self.hoeken)
        self.r_stralen[:, 1] = np.sin(self.hoeken)

    def move(self, richting, stap, world_map):
        """Kijkt of speler naar voor kan bewegen zo niet of hij langs de muur kan schuiven"""
        y_dim, x_dim = np.shape(world_map)
        if self.in_auto:
            if richting == 1 and stap > 0:
                self.car.accelerate()
            else:
                self.car.brake()
        else:
            x = (self.p_x + richting * stap * self.r_speler[0]) % x_dim
            y = (self.p_y + richting * stap * self.r_speler[1]) % y_dim
            atm = 0.3  # afstand_tot_muur zelfde bij auto
            x_2 = (x + atm * richting * self.r_speler[0]) % x_dim
            y_2 = (y + atm * richting * self.r_speler[1]) % y_dim

            if world_map[math.floor(y)][math.floor(x)] <= 0 and world_map[math.floor(y_2)][math.floor(x_2)] <= 0:
                self.p_x = x
                self.p_y = y
            if world_map[math.floor(y)][math.floor(self.p_x)] <= 0 and world_map[math.floor(y_2)][math.floor(self.p_x)] <= 0:
                self.p_y = y
            if world_map[math.floor(self.p_y)][math.floor(x)] <= 0 and world_map[math.floor(self.p_y)][math.floor(x_2)] <= 0:
                self.p_x = x
        self.position[:] = math.floor(self.p_x), math.floor(self.p_y)
        self.tile = math.floor(self.p_x / 9), math.floor(self.p_y / 9)

    def sideways_move(self, richting, stap, world_map):
        """Kijkt of speler naar voor kan bewegen zo niet of hij langs de muur kan schuiven"""
        y_dim, x_dim = np.shape(world_map)
        if self.in_auto:
            self.car.stuurhoek = (stap * (richting * -1) * self.car.speed * self.car.turning_mult)
            self.draaien(self.car.stuurhoek)
            self.car.draaien(self.car.stuurhoek)
        else:
            x = (self.p_x + richting * stap * self.r_camera[0]) % x_dim
            y = (self.p_y + richting * stap * self.r_camera[1]) % y_dim
            atm = 0.3  # afstand_tot_muur zelfde bij auto
            x_2 = (x + atm * richting * self.r_camera[0]) % x_dim
            y_2 = (y + atm * richting * self.r_camera[1]) % y_dim

            if world_map[math.floor(y)][math.floor(x)] <= 0 and world_map[math.floor(y_2)][math.floor(x_2)] <= 0:
                self.p_x = x
                self.p_y = y
            if world_map[math.floor(y)][math.floor(self.p_x)] <= 0 and world_map[math.floor(y_2)][math.floor(self.p_x)] <= 0:
                self.p_y = y
            if world_map[math.floor(self.p_y)][math.floor(x)] <= 0 and world_map[math.floor(self.p_y)][math.floor(x_2)] <= 0:
                self.p_x = x
        self.position[:] = math.floor(self.p_x), math.floor(self.p_y)
        self.tile = math.floor(self.p_x / 9), math.floor(self.p_y / 9)

    def draaien(self, hoek):
        """Via gegeven draaihoek alle stralen in van de speler (en auto) laten draaien"""
        self.hoek = (hoek + self.hoek) % (2 * math.pi)
        self.hoeken = (hoek + self.hoeken) % (2 * math.pi)

        self.r_speler = np.array([math.cos(self.hoek), math.sin(self.hoek)])
        self.r_camera = np.array([math.cos(self.hoek - math.pi / 2), math.sin(self.hoek - math.pi / 2)])

        self.r_stralen[:, 0] = np.cos(self.hoeken)
        self.r_stralen[:, 1] = np.sin(self.hoeken)
        # print(self.hoeken)

    def trow(self, world_map):
        """Maakt Doos sprite aan en update deze zodat een paar keer voor betere visuals
        :return: Doos_Sprite"""
        self.laatste_doos = time.time()
        sprite = Doos_Sprite(self.doos, self.map_doos, self.p_x, self.p_y, 600, self.r_speler / 5)
        for i in range(51):
            sprite.update(world_map)
        return sprite

    def n_raycasting(self, world_map, deuren):
        """Gebruik maken van de numpy raycaster om de afstanden en kleuren van muren te bepalen
        Neemt world map in zodat er gemakkelijk van map kan gewisseld worden"""

        # variabelen
        l = 2000  # maximale lengte die geraycast wordt
        """AANPASSINGEN DOORTREKKEN NAAR SPRITES"""

        kleuren = np.zeros(self.breedte, dtype="int")

        z_kleuren = np.zeros(self.breedte, dtype="int")
        z_d_muur = np.ones(self.breedte)
        z_d_muur_vlak = np.zeros(self.breedte)

        delta_x = 1 / np.abs(self.r_stralen[:, 0])
        delta_y = 1 / np.abs(self.r_stralen[:, 1])

        # Bij negatieve R_straal moeten we op de wereldmap 1 positie meer naar 0 toe schuiven.
        richting_x = np.where(self.r_stralen[:, 0] >= 0, 0, 1)
        richting_y = np.where(self.r_stralen[:, 1] >= 0, 0, 1)

        # initiele afstand berekenen
        d_v = np.where(self.r_stralen[:, 0] >= 0,(1 - (self.p_x - math.floor(self.p_x))) * delta_x,(self.p_x - math.floor(self.p_x)) * delta_x)
        d_h = np.where( self.r_stralen[:, 1] >= 0,(1 - (self.p_y - math.floor(self.p_y))) * delta_y,(self.p_y - math.floor(self.p_y)) * delta_y)

        z_buffer = np.full(self.breedte, False)
        checker = np.full(self.breedte, True)

        while True:
            # reset van muren_check vormt plekken waarop we muren raken
            z_buffer[:] = False

            # kijken of we d_v of d_h nodig hebben deze loop
            dist_cond = d_v < d_h
            least_distance = np.where(dist_cond, d_v, d_h)

            # Mogen enkel muren checken die nog niet geraakt zijn en binnen de afstand liggen
            break_1 = d_v < l
            break_2 = d_h < l
            break_z = z_kleuren == 0
            break_cond = (dist_cond * break_1 + ~dist_cond * break_2) * checker
            # Break 1 enkel tellen als we met d_v werken en d_h enkel als we met d_h werken
            # Binair vermenigvuldigen als break3 = 0 dan wordt break_cond op die plek 0

            # Als op alle plekken break_cond == 0 return dan de bekomen waardes
            if not break_cond.any():
                break

            # x en y berekenen adhv gegeven d_v of d_h en afronden op 3-8 zodat astype(int) niet afrond naar beneden terwijl het naar boven zou moeten
            # AANPASSING: Zolang we geen modulo doen rond float 32 ook perfect af naar boven als het moet en is sneller
            x = (self.p_x + least_distance * self.r_stralen[:, 0]).astype("float32")
            y = (self.p_y + least_distance * self.r_stralen[:, 1]).astype("float32")

            """# infinity world try-out
            while np.any(np.logical_and.reduce((-4 * x_dim < x, x <= 0))):
                x = np.where(x <= 0, x + x_dim, x)
            while np.any(np.logical_and.reduce((-4 * y_dim <= y, y <= 0))):
                y = np.where(y <= 0, y + y_dim, y)
            while np.any(np.logical_and.reduce((y_dim <= y, y < 5*y_dim))):
                y = np.where(y >= y_dim, y - y_dim, y)

            while np.any(np.logical_and.reduce((x_dim < x, x < 5*x_dim))):
                x = np.where(x >= x_dim, x - x_dim, x)"""

            # World map neemt enkel int dus afronden naar beneden via astype(int) enkel als d_v genomen is moet correctie toegevoegd worden bij x
            x_f = np.where(dist_cond, (x - richting_x).astype(int), x.astype(int))
            y_f = np.where(~dist_cond, (y - richting_y).astype(int), y.astype(int))

            # Logica: x_f moet tussen 0 en x_dim blijven en y_f tussen 0 en y_dim
            # Deze tellen ook enkel maar als de break conditie niet telt
            valid_indices = np.logical_and.reduce((0 <= x_f, x_f < len(world_map[0]), 0 <= y_f, y_f < len(world_map), break_cond))
            z_valid = valid_indices * break_z
            """HIER LOGICA INVOEGEN VOOR ALS EEN RAY OUT OF BOUND GAAT --> Map herwerken"""

            # muren_check[valid_indices] = np.where(world_map[y_f[valid_indices], x_f[valid_indices]] > 0, True, False)
            checker[valid_indices] = np.where(world_map[y_f[valid_indices], x_f[valid_indices]] > 0, False, True)
            z_buffer[z_valid] = np.where(world_map[y_f[z_valid], x_f[z_valid]] < -2, True, False)

            # op de plekken waar logica correct is kijken of we een muur raken
            if z_buffer.any():
                z_kleuren[z_buffer] = world_map[y_f[z_buffer], x_f[z_buffer]]
                # r_straal*r_speler voor fish eye eruit te halen
                z_d_muur = np.where(z_buffer,least_distance* (self.r_stralen[:, 0] * self.r_speler[0]+ self.r_stralen[:, 1] * self.r_speler[1]), 0)
                # Als dist_cond dan raken we een muur langs de x kant dus is y de veranderlijke als we doorschuiven --> meegeven als var voor vaste textuur
                z_d_muur_vlak[z_buffer] = np.where(dist_cond[z_buffer], y[z_buffer], x[z_buffer])
                # z_kleuren = np.where((z_d_muur_vlak % 1) < deuren[z_kleuren].positie, 0, z_kleuren)

            # incrementeren, d_v als dist_cond True is, d_h als dist_cond False is
            d_v += dist_cond * delta_x * checker
            d_h += (~dist_cond) * delta_y * checker
        valid_indices = np.logical_and.reduce((0 <= x_f, x_f < len(world_map[0]), y_f < len(world_map), ~checker))
        kleuren[valid_indices] = world_map[y_f[valid_indices], x_f[valid_indices]]
        d_muur_vlak = np.where(dist_cond, y, x)
        d_muur = np.where(valid_indices, least_distance * (self.r_stralen[:, 0] * self.r_speler[0]+ self.r_stralen[:, 1] * self.r_speler[1]), 60)
        z_d_muur * ( self.r_stralen[:, 0] * self.r_speler[0]+ self.r_stralen[:, 1] * self.r_speler[1])
        return (d_muur, (d_muur_vlak % 1), (kleuren - 1)), ((1 / z_d_muur), (z_d_muur_vlak % 1), (z_kleuren))
        # print(self.r_speler)

    def reset(self):
        self.p_x = self.initial[0]
        self.p_y = self.initial[1]
        self.position[:] = math.floor(self.p_x),math.floor(self.p_y)
        self.hoek = self.initial[2]
        self.r_speler = np.array([math.cos(self.hoek), math.sin(self.hoek)])
        self.r_camera = np.array([math.cos(self.hoek - math.pi / 2), math.sin(self.hoek - math.pi / 2)])
        self.aanmaak_r_stralen()
        if self.in_auto:
            self.car.hoek = self.hoek
            self.car.x = self.p_x
            self.car.y = self.p_y

    def renderen(self, renderer, world_map):
        if self.in_auto:
            self.car.beweeg(world_map, self)
        else:
            pass


class Auto(Sprite):
    def __init__(self, image, images, map_png, x, y, height, type=0, hp=20, schaal=0.2):
        super().__init__(image, images, map_png, x, y, height, schaal)
        self.schadelijk = False

        self.type = type
        self.hp = hp
        self.speed = 0
        self.vector = np.array([1, 0])
        self.afrem = 0.002
        self.optrek = 0.001
        self.hoek = math.sqrt(2)
        self.player_inside = False
        self.crashed = False
        self.turning_mult = 2
        self.stuurhoek = 0
        self.versnelling = "1"
        self.input_delay = 0
        self.crash_time = 0

    def beweeg(self, world_map, speler):
        """Update positie auto"""
        """print(self.hoek, speler.hoek)
        print(self.vector, speler.r_speler)
        print('\n\n')"""
        if self.speed == 0:
            self.turning_mult = 0
        elif self.speed < 0:
            self.turning_mult = 40
        else:
            self.turning_mult = (self.optrek/self.speed)**1.2 * 500
        if self.player_inside == False:
            self.brake()

        y_dim, x_dim = np.shape(world_map)
        x = self.x + self.speed * self.vector[0]
        y = self.y + self.speed * self.vector[1]
        atm = 0.3  # afstand_tot_muur
        x_2 = x + atm * self.vector[0]
        y_2 = y + atm * self.vector[1]
        if x < 0:
            x += x_dim
        elif x > x_dim:
            x -= x_dim
        if y < 0:
            y += y_dim
        elif y > y_dim:
            y -= y_dim
        if world_map[math.floor(y)][math.floor(x)] <= 0 and world_map[math.floor(y_2)][math.floor(x_2)] <= 0:
            self.x = x
            self.y = y
            if self.player_inside:
                speler.p_x = x
                speler.p_y = y
                speler.position[:] = math.floor(x), math.floor(y)
        else:
            if not self.crash_time < time.time() - 0.2:
                if world_map[math.floor(y)][math.floor(self.x)] <= 0 and world_map[math.floor(y_2)][math.floor(self.x)] <= 0:
                    if self.vector[1] > 0:
                        self.hoek = math.pi/2
                    elif self.vector[1] != 0:
                        self.hoek = -math.pi/2
                    veranderingshoek = self.hoek - speler.hoek
                    speler.draaien(veranderingshoek)
                if world_map[math.floor(self.y)][math.floor(x)] <= 0 and world_map[math.floor(self.y)][math.floor(x_2)] <= 0:
                    if self.vector[0] > 0:
                        self.hoek = 0
                    elif self.vector[1] != 0:
                        self.hoek = math.pi
                    veranderingshoek = self.hoek - speler.hoek
                    speler.draaien(veranderingshoek)
            if self.crash_time < time.time() - 0.01:
                self.vector = (0,0)
                self.crashed = True
                self.crash_time = time.time()
                self.speed = 0
                self.hp -= 1
                if self.hp == 0:
                    self.player_leaving(world_map, speler)
                    self.hp = 9

    def brake(self):
        if self.speed > self.afrem:
            self.speed -= self.afrem
        else:
            self.speed = 0.0

    def accelerate(self):
        if self.versnelling == "1":
            if self.speed < 0:
                self.speed = 0
            elif self.speed < 1:
                self.speed += self.optrek
        elif self.versnelling == "R":
            if self.speed > 0:
                self.speed -= self.optrek
            elif self.speed > -0.01:
                self.speed -= self.optrek/2
            """
            if 0.2 > self.speed > 0.1:
                self.turning_mult = 1
            elif 0.3 > self.speed > 0.2:
                self.turning_mult = 0.1
            elif self.speed > 0.3:
                self.turning_mult = 0.02"""

    def draaien(self, hoek):
        self.hoek = (hoek + self.hoek) % (2 * math.pi)
        self.vector = np.array([math.cos(self.hoek), math.sin(self.hoek)])

    def player_enter(self, speler):
        """Kijkt of speler dicht genoeg tegen auto staat om in te stappen.\n
        zet alle settings correct"""
        if self.afstanden(speler) < 1.5:
            self.player_inside = True
            speler.p_x = self.x
            speler.p_y = self.y
            speler.position[:] = math.floor(self.x), math.floor(self.y)
            hoek_diff = self.hoek - speler.hoek
            speler.draaien(hoek_diff)
            speler.hoek = self.hoek
            self.vector = np.array([math.cos(self.hoek), math.sin(self.hoek)])
            speler.in_auto = True
            return False
        else:
            return True
            # render text ofz

    def player_leaving(self, world_map, speler):
        # y_dim, x_dim = np.shape(world_map)
        self.player_inside = False
        speler.in_auto = False
        self.speed = 0
        if 0 < self.x - 0.5 and 0 < self.y - 0.5:
            if world_map[math.floor(self.y - 0.5)][math.floor(self.x - 0.5)] == 0:
                speler.p_x = self.x - 0.5
                speler.p_y = self.y - 0.5
                speler.position[:] = math.floor(speler.p_x), math.floor(speler.p_y)

    def hitting(self, object):
        self.hp -= 1


class Deur:
    def __init__(self, kleur=0):
        self.moving = True
        self.open = False
        self.richting = 1
        self.positie = 0
        self.kleur = kleur

    def update(self):
        if self.moving:
            self.positie += self.richting / 500
            if self.positie >= 1:
                self.moving = False
                self.open = True
                self.richting = -1
                self.positie = 1
            elif self.positie <= 0:
                self.moving = False
                self.richting = 1
                self.positie = 0

    def start(self):
        if self.moving:
            self.richting *= -1
        self.moving = True
        self.open = False


class Politie(Sprite):
    def __init__(self, image, images, map_png, x, y, height, speler, schaal=0.2):
        super().__init__(image, images, map_png, x, y, height, schaal)
        self.pad = (0, 0)
        self.speler = speler
        self.achtervolgen = False
        self.hoek = 0  # set to initial of 3D SPRITE

    def update(self, *args):
        self.padfind()
        if self.achtervolgen:
            if len(self.pad) > 2:
                self.hoek = math.atan2(self.pad[-2][1], self.pad[-2][0])
            else:
                self.hoek = math.atan2(self.y - self.speler.p_y, self.x - self.speler.p_x)

            if self.speler.in_auto:
                speed = abs(self.speler.car.speed - 0.002)
            else:
                speed = 0.05

            vector = (self.pad[-1][1] - self.pad[-2][1],self.pad[-1][0] - self.pad[-2][0])  # Pad uses inverse x/y from normal so reverting here

            self.x += speed * vector[0]
            self.y += speed * vector[1]

    def padfind(self):
        if self.afstand < 25 and self.achtervolgen:
            self.pad = pathfinding_gps((self.x,self.y))
        else:
            self.achtervolgen = False

