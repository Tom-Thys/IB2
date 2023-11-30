import math
import time
import random
import numpy as np
from Code_niet_langer_in_gebruik import pathfinding_gps

# from line_profiler_pycharm import profile
# from numba import njit
# from line_profiler_pycharm import profile

from sdl2 import *


class Sprite:
    def __init__(self, image, images, map_png, x, y, height, soort, schaal=0.4):
        self.images = images
        self.image = image  # The image of the sprite
        self.map_png = map_png
        self.map_grootte = 9
        self.x = x  # The x-coordinate of the sprite
        self.y = y  # The y-coordinate of the sprite
        self.position = [x, y]
        self.breedte = image.size[0]
        self.hoogte = image.size[1]
        self.height = height
        self.afstand = 1
        self.schadelijk = True
        self.soort = soort
        self.schaal = schaal

    def afstanden(self, x, y):
        """Berekend afstand ifv speler.
        :return: afstand tot speler"""
        self.afstand = ((self.x - x) ** 2 + (self.y - y) ** 2) ** (1 / 2)
        return self.afstand

    def draai_sprites(self, draai):
        aantal_te_verschuiven = draai
        laatste_items = self.images[-aantal_te_verschuiven:]
        rest_van_de_lijst = self.images[:-aantal_te_verschuiven]
        self.images = laatste_items + rest_van_de_lijst

    def kies_sprite_afbeelding(self, hoek_verschil, fout):
        index = 360 - round((hoek_verschil) / (math.pi * 2) * 360)
        if index == 0:
            index += 1
        if fout:
            # print("Fout")
            index = 360 - index
        # print (index)
        image = self.images[index]
        return image

    def update(self, *args):
        """Update elke sprite, wordt overschreven in onderliggende classes."""
        return False


class Doos_Sprite(Sprite):
    """Doos neemt alle functies met sprite over met een extra vector zodat hij gegooid kan worden"""

    def __init__(self, image, map_png, x, y, height, is_boom,vector, deletable=True):
        super().__init__(image, [], map_png, x, y, height,"Doos")
        self.deletable = deletable
        self.vector = vector
        self.map_grootte = 2
        self.tick = 1
        self.schadelijk = True

    def update(self, world_map, *args):
        self.tick += 1
        if self.height < 800:
            time = self.tick / 50
            self.height += 4 * time
            x = self.x + 0.1 * self.vector[0]
            y = self.y + 0.1 * self.vector[1]
            atm = 0.3  # afstand_tot_muur zelfde bij auto
            x_2 = x + atm * self.vector[0]
            y_2 = y + atm * self.vector[1]
            if world_map[math.floor(y)][math.floor(x)] <= 0 and world_map[math.floor(y_2)][math.floor(x_2)] <= 0:
                self.x = x
                self.y = y
                self.position = [math.floor(x), math.floor(y)]
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
        self.oude_pos = (x,y)
        self.p_x = x
        self.p_y = y
        self.hoek = hoek
        self.r_speler = np.array([math.cos(hoek), math.sin(hoek)])
        self.r_camera = np.array([math.cos(self.hoek - math.pi / 2), math.sin(self.hoek - math.pi / 2)])
        self.breedte = breedte + 100
        self.hoeken = np.zeros(self.breedte)
        self.r_stralen = np.zeros((self.breedte, 2))
        self.car = 0
        self.in_auto = False
        self.aantal_hartjes = 5
        self.tile = math.floor(self.p_x / 9), math.floor(self.p_y / 9)
        self.initial = (x, y, hoek)
        self.laatste_doos = 0
        self.isWalking = False
        self.delta_x = np.zeros(self.breedte)
        self.delta_y = np.zeros(self.breedte)

    def aanmaak_r_stralen(self, d_camera=1):
        """Gebruikt speler hoek, speler straal en gegeven camera afstand om r_stralen voor raycaster te berekenen"""
        self.r_speler = np.array([math.cos(self.hoek), math.sin(self.hoek)])
        self.r_camera = np.array([math.cos(self.hoek - math.pi / 2), math.sin(self.hoek - math.pi / 2)])


        for i in range(-50,self.breedte-50):
            r_straal_kolom = (d_camera * self.r_speler + (1 - (2 * i) / self.breedte) * self.r_camera)
            hoek = math.atan2(r_straal_kolom[0], r_straal_kolom[1])
            self.hoeken[i] = hoek


        self.r_stralen[:, 0] = np.cos(self.hoeken)
        self.r_stralen[:, 1] = np.sin(self.hoeken)

    def move(self, richting, stap, world_map):
        """Kijkt of speler naar voor kan bewegen zo niet of hij langs de muur kan schuiven"""
        y_dim, x_dim = np.shape(world_map)
        self.oude_pos = (self.p_x, self.p_y)
        if self.in_auto:
            if richting == 1 and stap > 0:
                self.car.accelerate()
            else:
                self.car.brake()
        else:
            self.isWalking = True
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
        self.oude_pos = (self.p_x, self.p_y)
        if self.in_auto:
            self.car.stuurhoek = (stap * (richting * -1) * self.car.speed * self.car.turning_mult)
            self.draaien(self.car.stuurhoek)
            self.car.draaien(self.car.stuurhoek)
        else:
            self.isWalking = True
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


    def idle(self):
        self.isWalking = False

    def draaien(self, hoek):
        """Via gegeven draaihoek alle stralen in van de speler (en auto) laten draaien"""
        self.hoek = (hoek + self.hoek)# % (2 * math.pi)
        self.hoeken = (hoek + self.hoeken)# % (2 * math.pi)

        self.r_speler = np.array([math.cos(self.hoek), math.sin(self.hoek)])
        self.r_camera = np.array([math.cos(self.hoek - math.pi / 2), math.sin(self.hoek - math.pi / 2)])

        self.r_stralen[:, 0] = np.cos(self.hoeken)
        self.r_stralen[:, 1] = np.sin(self.hoeken)

        self.hoek = self.hoek % (2 * math.pi)
        self.hoeken = self.hoeken % (2 * math.pi)

    def trow(self, world_map):
        """Maakt Doos sprite aan en update deze zodat een paar keer voor betere visuals
        :return: Doos_Sprite"""
        self.laatste_doos = time.time()
        sprite = Doos_Sprite(self.doos, self.map_doos, self.p_x, self.p_y, -600,False ,self.r_speler / 5,)
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

        x = self.r_stralen[:, 0] != 0
        y = self.r_stralen[:, 1] != 0
        if not x.all() or not y.all():
            print("straight on")

        self.delta_x[~x] = 999
        self.delta_y[~y] = 999
        self.delta_x[x] = 1 / np.abs(self.r_stralen[x, 0])
        self.delta_y[y] = 1 / np.abs(self.r_stralen[y, 1])


        # Bij negatieve R_straal moeten we op de wereldmap 1 positie meer naar 0 toe schuiven.
        richting_x = np.where(self.r_stralen[:, 0] >= 0, 0, 1)
        richting_y = np.where(self.r_stralen[:, 1] >= 0, 0, 1)

        # initiele afstand berekenen
        d_v = np.where(self.r_stralen[:, 0] >= 0,(1 - (self.p_x - math.floor(self.p_x))) * self.delta_x,(self.p_x - math.floor(self.p_x)) * self.delta_x)
        d_h = np.where( self.r_stralen[:, 1] >= 0,(1 - (self.p_y - math.floor(self.p_y))) * self.delta_y,(self.p_y - math.floor(self.p_y)) * self.delta_y)

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
            d_v += dist_cond * self.delta_x * checker
            d_h += (~dist_cond) * self.delta_y * checker
        valid_indices = np.logical_and.reduce((0 <= x_f, x_f < len(world_map[0]), y_f < len(world_map), ~checker))
        kleuren[valid_indices] = world_map[y_f[valid_indices], x_f[valid_indices]]
        d_muur_vlak = np.where(dist_cond, y, x)
        d_muur = np.where(valid_indices, least_distance * (self.r_stralen[:, 0] * self.r_speler[0] + self.r_stralen[:, 1] * self.r_speler[1]), 60)
        z_d_muur * (self.r_stralen[:, 0] * self.r_speler[0] + self.r_stralen[:, 1] * self.r_speler[1])
        return (d_muur, (d_muur_vlak % 1), (kleuren - 1)), ((1 / z_d_muur), (z_d_muur_vlak % 1), (z_kleuren))

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


class PostBus(Sprite):
    def __init__(self, image, images, map_png, x, y, height, type=0, hp=20, schaal=0.2):
        super().__init__(image, images, map_png, x, y, height, "PostBus", schaal)
        self.schadelijk = False
        self.map_grootte = 6
        self.type = type
        self.hp = hp
        self.speed = 0
        self.vector = np.array([1, 0])
        self.afrem = 0.002
        self.optrek = 0.001
        self.hoek = -math.pi/2
        self.player_inside = False
        self.crashed = False
        self.turning_mult = 2
        self.stuurhoek = 0
        self.versnelling = "1"
        self.input_delay = 0
        self.crash_time = 0

    def update(self, world_map, speler, delta):
        """Update positie auto"""


        speed = self.speed * delta / 0.015
        if self.speed == 0:
            return
        elif self.speed < 0:
            self.turning_mult = 40
        else:
            self.turning_mult = (self.optrek/speed)**1.2 * 500
        if self.player_inside == False:
            self.brake()
            self.brake()

        y_dim, x_dim = np.shape(world_map)
        x = self.x + speed * self.vector[0]
        y = self.y + speed * self.vector[1]
        atm = 0.3  # afstand_tot_muur
        x_2 = x + atm * self.vector[0]
        x_2_f = math.floor(x_2)
        y_2 = y + atm * self.vector[1]
        y_2_f = math.floor(y_2)
        if x_2_f == math.floor(self.x) and y_2_f == math.floor(self.y):
            self.x = x
            self.y = y
            if self.player_inside:
                speler.p_x = x
                speler.p_y = y
                speler.position[:] = math.floor(x), math.floor(y)
            return
        if x < 0:
            x += x_dim
        elif x > x_dim:
            x -= x_dim
        if y < 0:
            y += y_dim
        elif y > y_dim:
            y -= y_dim
        if world_map[math.floor(y)][math.floor(x)] <= 0 and world_map[y_2_f][x_2_f] <= 0:
            self.x = x
            self.y = y
            if self.player_inside:
                speler.p_x = x
                speler.p_y = y
                speler.position[:] = math.floor(x), math.floor(y)
        else:
            if not self.crash_time < time.time() - 0.2:
                if world_map[math.floor(y)][math.floor(self.x)] <= 0 and world_map[y_2_f][math.floor(self.x)] <= 0:
                    if self.vector[1] > 0:
                        self.hoek = math.pi/2
                    elif self.vector[1] != 0:
                        self.hoek = -math.pi/2
                    veranderingshoek = self.hoek - speler.hoek
                    speler.draaien(veranderingshoek)
                if world_map[math.floor(self.y)][math.floor(x)] <= 0 and world_map[math.floor(self.y)][x_2_f] <= 0:
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
                    speler.aantal_hartjes -= 1

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
        self.draai_sprites(round(hoek*180/math.pi))

    def player_enter(self, speler):
        """Kijkt of speler dicht genoeg tegen auto staat om in te stappen.\n
        zet alle settings correct"""
        if self.afstanden(speler.p_x, speler.p_y) < 1.5:
            self.player_inside = True
            speler.p_x = self.x
            speler.p_y = self.y
            speler.position[:] = math.floor(self.x), math.floor(self.y)
            hoek_diff = self.hoek - speler.hoek
            speler.draaien(hoek_diff)
            speler.hoek = self.hoek
            #speler.aanmaak_r_stralen()
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


class Voertuig(Sprite):
    def __init__(self, image, images, map_png, x, y, height, world_map, schaal=0.2):
        super().__init__(image, images, map_png, int(x)+0.5, int(y)+0.5, height, "Auto", schaal)
        self.speed = 0.05
        self.vector = [1, 0]
        self.hoek = 0
        self.nieuwe_pos = [0,0] #pos op wereldmap
        self.position = [math.floor(x), math.floor(y)]
        self.crash = False
        self.select_new_dir(world_map,initial=True)
        self.last_car = self

    def crashing(self,autos):
        if self.crash:
            return True
        for auto in autos:
            if auto == self and auto == self.last_car: continue;

            afstand = ((self.x - auto.x) ** 2 + (self.y - auto.y) ** 2) ** (1 / 2)
            if afstand < 0.5:
                self.crash = True
                auto.crash = True
                self.last_car = auto
        return self.crash


    def update(self, world_map, delta, auto_sprites):
        if self.position != self.nieuwe_pos:
            self.x += self.speed * self.vector[0]
            self.y += self.speed * self.vector[1]
            self.position = [math.floor(self.x), math.floor(self.y)]
            if self.crashing(auto_sprites):
                self.hoek = (math.pi + self.hoek) % (2 * math.pi)
                self.draai_sprites(180)
                self.crash = False
                self.nieuwe_pos = [self.nieuwe_pos[0] - 9 * self.vector[0], self.nieuwe_pos[1] - 9 * self.vector[1]]
                self.vector = [v * -1 for v in self.vector]
            return

        self.select_new_dir(world_map)

    def select_new_dir(self,world_map, initial=None):
        nieuwe_richting = []
        i = 0
        vectors = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        for vx, vy in vectors:
            if self.vector == [(vx*-1), (vy*-1)]: continue;
            pos = (self.position[1] + 3 * vy, self.position[0] + 3 * vx)
            pos2 = (self.position[1] + 5 * vy, self.position[0] + 5 * vx)
            v1, v2 = (world_map[pos],world_map[pos2])
            if world_map[pos] <= 0 and world_map[pos2] <= 0:
                 i += 1
                 nieuwe_richting.append(([vx, vy], [self.position[0] + 9 * vx, self.position[1] + 9 * vy]))
        if i == 0:
            if initial:
                self.vector = []
                return
            self.nieuwe_pos = [self.nieuwe_pos[0] - 9 * self.vector[0], self.nieuwe_pos[1] - 9 * self.vector[1]]
            self.vector = [v * -1 for v in self.vector]
        else:
            plek = random.randint(0, len(nieuwe_richting)-1)
            self.vector = nieuwe_richting[plek][0]
            self.nieuwe_pos = nieuwe_richting[plek][1]




class Politie(Sprite):
    def __init__(self, image, images, map_png, x, y, height, speler, schaal=0.2):
        super().__init__(image, images, map_png, x, y, height, "Politie", schaal)
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

