import math
import time
import random
import numpy as np



postkantoor = (434, 452)

# from line_profiler_pycharm import profile
# from numba import njit
# from line_profiler_pycharm import profile

from sdl2 import *


class Sprite:
    def __init__(self, image, images, map_png, x, y, height, soort, schaal=0.4, fall=0):
        """image, images (can be []), map_png, x, y, height, soort, schaal=0.4"""
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
        self.fall = fall

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

    def __init__(self, image, map_png, x, y, height, vector, deletable=True):
        super().__init__(image, [], map_png, x, y, height, "Doos")
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
                self.vector = (0, 0)
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
        self.oude_pos = (x, y)
        self.p_x = x
        self.p_y = y
        self.hoek = hoek
        self.r_speler = np.array([math.cos(hoek), math.sin(hoek)])
        self.r_camera = np.array([math.cos(self.hoek - math.pi / 2), math.sin(self.hoek - math.pi / 2)])
        self.breedte = breedte
        self.hoeken = np.zeros(self.breedte)
        self.r_stralen = np.zeros((self.breedte, 2))
        self.car = None
        self.in_auto = False
        self.aantal_hartjes = 5
        self.tile = math.floor(self.p_x / 9), math.floor(self.p_y / 9)  # Aanmaak autos rond speler
        self.initial = (x, y, hoek)  # Reset values
        self.laatste_doos = 0  # Time
        self.isWalking = False
        self.doos_vast = False
        self.hit = False
        self.in_kantoor = False
        aantal_deuren = 10
        self.kantoor_deuren = np.ones(aantal_deuren, dtype='float64')
        self.kantoor_open_deuren = np.full(aantal_deuren, False)
        self.kantoor_deuren_update = np.ones(aantal_deuren)
        self.messages = []
        self.delta_x = np.zeros(self.breedte)
        self.delta_y = np.zeros(self.breedte)
        self.aanmaak_r_stralen()
        self.draaien(0)

    def aanmaak_r_stralen(self, d_camera=1):
        """Gebruikt speler hoek, speler straal en gegeven camera afstand om r_stralen voor raycaster te berekenen"""
        self.r_speler = np.array([math.cos(self.hoek), math.sin(self.hoek)])
        self.r_camera = np.array([math.cos(self.hoek - math.pi / 2), math.sin(self.hoek - math.pi / 2)])

        for i in range(self.breedte):
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
                self.car.accelerate(self)
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
                if self.in_kantoor:
                    deur = world_map[math.floor(y_2)][math.floor(x_2)]
                    if deur < -2:
                        if not self.kantoor_open_deuren[deur]:
                            return
                self.p_x = x
                self.p_y = y
            if world_map[math.floor(y)][math.floor(self.p_x)] <= 0 and world_map[math.floor(y_2)][
                math.floor(self.p_x)] <= 0:
                if self.in_kantoor:
                    deur = world_map[math.floor(y_2)][math.floor(self.p_x)]
                    if deur < -2:
                        if not self.kantoor_open_deuren[deur]:
                            return
                self.p_y = y
            if world_map[math.floor(self.p_y)][math.floor(x)] <= 0 and world_map[math.floor(self.p_y)][
                math.floor(x_2)] <= 0:
                if self.in_kantoor:
                    deur = world_map[math.floor(self.p_y)][math.floor(x_2)]
                    if deur < -2:
                        if not self.kantoor_open_deuren[deur]:
                            return
                self.p_x = x
        self.position[:] = math.floor(self.p_x), math.floor(self.p_y)
        self.tile = math.floor(self.p_x / 9), math.floor(self.p_y / 9)

    def sideways_move(self, richting, stap, world_map):
        """Kijkt of speler naar voor kan bewegen zo niet of hij langs de muur kan schuiven"""
        y_dim, x_dim = np.shape(world_map)
        self.oude_pos = (self.p_x, self.p_y)
        if self.in_auto:
            self.car.stuurhoek = (stap * (richting * -1) * self.car.speed * self.car.turning_mult)
            if not -math.pi < self.car.stuurhoek < math.pi:
                self.car.stuurhoek = 0
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
                if self.in_kantoor:
                    deur = world_map[math.floor(y_2)][math.floor(x_2)]
                    if deur < -2:
                        if not self.kantoor_open_deuren[deur]:
                            return
                self.p_x = x
                self.p_y = y
            if world_map[math.floor(y)][math.floor(self.p_x)] <= 0 and world_map[math.floor(y_2)][
                math.floor(self.p_x)] <= 0:
                if self.in_kantoor:
                    deur = world_map[math.floor(y_2)][math.floor(self.p_x)]
                    if deur < -2:
                        if not self.kantoor_open_deuren[deur]:
                            return
                self.p_y = y
            if world_map[math.floor(self.p_y)][math.floor(x)] <= 0 and world_map[math.floor(self.p_y)][
                math.floor(x_2)] <= 0:
                if self.in_kantoor:
                    deur = world_map[math.floor(self.p_y)][math.floor(x_2)]
                    if deur < -2:
                        if not self.kantoor_open_deuren[deur]:
                            return
                self.p_x = x
        self.position[:] = math.floor(self.p_x), math.floor(self.p_y)
        self.tile = math.floor(self.p_x / 9), math.floor(self.p_y / 9)

    def idle(self):
        self.isWalking = False

    def draaien(self, hoek):
        """Via gegeven draaihoek alle stralen in van de speler (en auto) laten draaien"""
        self.hoek = (hoek + self.hoek)  # % (2 * math.pi)
        self.hoeken = (hoek + self.hoeken)  # % (2 * math.pi)

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
        sprite = Doos_Sprite(self.doos, self.map_doos, self.p_x, self.p_y, -600, self.r_speler / 5, )
        for i in range(51):
            sprite.update(world_map)
        return sprite

    def n_raycasting(self, world_map):
        """Gebruik maken van de numpy raycaster om de afstanden en kleuren van muren te bepalen
        Neemt world map in zodat er gemakkelijk van map kan gewisseld worden"""

        # variabelen
        y_max, x_max = np.shape(world_map)
        l = 80  # maximale lengte die geraycast wordt
        """AANPASSINGEN DOORTREKKEN NAAR SPRITES"""

        kleuren = np.zeros(self.breedte, dtype="int")

        # z_kleuren = np.zeros(self.breedte, dtype="int")
        z_d_muur = np.ones(self.breedte)
        z_d_muur_vlak = np.zeros(self.breedte)

        x = self.r_stralen[:, 0] != 0
        y = self.r_stralen[:, 1] != 0

        self.delta_x[~x] = 99999
        self.delta_y[~y] = 99999
        self.delta_x[x] = 1 / np.abs(self.r_stralen[x, 0])
        self.delta_y[y] = 1 / np.abs(self.r_stralen[y, 1])

        # Bij negatieve R_straal moeten we op de wereldmap 1 positie meer naar 0 toe schuiven.
        richting_x = np.where(self.r_stralen[:, 0] > 0, 0, 1)
        richting_y = np.where(self.r_stralen[:, 1] > 0, 0, 1)

        # initiele afstand berekenen
        d_v = np.where(self.r_stralen[:, 0] >= 0, (1 - (self.p_x - math.floor(self.p_x))) * self.delta_x,
                       (self.p_x - math.floor(self.p_x)) * self.delta_x)
        d_h = np.where(self.r_stralen[:, 1] >= 0, (1 - (self.p_y - math.floor(self.p_y))) * self.delta_y,
                       (self.p_y - math.floor(self.p_y)) * self.delta_y)

        z_buffer = np.full(self.breedte, False)
        checker = np.full(self.breedte, True)

        while True:

            # kijken of we d_v of d_h nodig hebben deze loop
            dist_cond = d_v < d_h
            least_distance = np.where(dist_cond, d_v, d_h)

            # Mogen enkel muren checken die nog niet geraakt zijn en binnen de afstand liggen
            break_1 = d_v < l
            break_2 = d_h < l

            break_cond = (dist_cond * break_1 + ~dist_cond * break_2) * checker
            # Break 1 enkel tellen als we met d_v werken en d_h enkel als we met d_h werken
            # Binair vermenigvuldigen als break3 = 0 dan wordt break_cond op die plek 0

            # Als op alle plekken break_cond == 0 return dan de bekomen waardes
            if not break_cond.any():
                break

            # x en y berekenen adhv gegeven d_v of d_h en afronden op 3-8 zodat astype(int) niet afrond naar beneden terwijl het naar boven zou moeten
            # AANPASSING: Zolang we geen modulo doen rond float 32 ook perfect af naar boven als het moet en is sneller
            """Neemt in totaal 18% van de raycast tijd in but the work around is nieuwe formules gebruiken"""
            x = (self.p_x + least_distance * self.r_stralen[:, 0]).astype("float32")
            y = (self.p_y + least_distance * self.r_stralen[:, 1]).astype("float32")

            # World map neemt enkel int dus afronden naar beneden via astype(int) enkel als d_v genomen is moet correctie toegevoegd worden bij x
            x_f = np.where(dist_cond, (x - richting_x).astype(int), x.astype(int))
            y_f = np.where(~dist_cond, (y - richting_y).astype(int), y.astype(int))

            # Logica: x_f moet tussen 0 en x_dim blijven en y_f tussen 0 en y_dim
            # Deze tellen ook enkel maar als de break conditie niet telt

            """Zou paar procentjes sparen als we enkel met break cond sparen but future error prevention"""
            valid_indices = np.logical_and.reduce((0 <= x_f, x_f < x_max, 0 <= y_f, y_f < y_max, break_cond))

            checker[valid_indices] = np.where(world_map[y_f[valid_indices], x_f[valid_indices]] > 0, False, True)
            if self.in_kantoor:
                """Logica voor deuren -- was vroeger klein beetje anders, deze is efficienter -> minder rendertijd"""

                z_buffer[valid_indices] = np.where(world_map[y_f[valid_indices], x_f[valid_indices]] < -2, True, False)

                if z_buffer.any():
                    z_kleuren = world_map[y_f[z_buffer], x_f[z_buffer]]
                    checker[z_buffer] = np.where(dist_cond[z_buffer],
                                                 np.where((y[z_buffer] % 1) < self.kantoor_deuren[z_kleuren], False,
                                                          True),
                                                 np.where((x[z_buffer] % 1) < self.kantoor_deuren[z_kleuren], False,
                                                          True))
                    z_buffer[:] = False

            # incrementeren, d_v als dist_cond True is, d_h als dist_cond False is
            d_v += dist_cond * self.delta_x * checker
            d_h += (~dist_cond) * self.delta_y * checker

        valid_indices = np.logical_and.reduce((0 <= x_f, x_f < x_max, y_f < y_max, ~checker))
        kleuren[valid_indices] = world_map[y_f[valid_indices], x_f[valid_indices]]
        d_muur_vlak = np.where(dist_cond, y, x)
        d_muur = np.where(valid_indices, least_distance * (
                self.r_stralen[:, 0] * self.r_speler[0] + self.r_stralen[:, 1] * self.r_speler[1]), 60)
        z_d_muur *= (self.r_stralen[:, 0] * self.r_speler[0] + self.r_stralen[:, 1] * self.r_speler[1])

        return (d_muur, d_muur_vlak, kleuren), dist_cond

    def reset(self):
        self.in_kantoor = False
        self.p_x = self.initial[0]
        self.p_y = self.initial[1]
        self.position[:] = math.floor(self.p_x), math.floor(self.p_y)
        self.hoek = self.initial[2]
        self.aanmaak_r_stralen()
        if self.in_auto:
            draaihoek = self.car.hoek - self.hoek
            self.car.draai_sprites(round(draaihoek * 180 / math.pi))
            self.car.hoek = self.hoek
            self.car.x = self.p_x
            self.car.y = self.p_y
            self.car.speed = 0

    def check_postition(self, game_state):
        if postkantoor[0] - 3 < self.p_y < postkantoor[0] and postkantoor[1] - 3 < self.p_x < postkantoor[1]:
            return 4
        elif postkantoor[0] - 3 < self.p_y < postkantoor[0] and postkantoor[1] + 8 > self.p_x > postkantoor[1] + 5:
            return 3
        else:
            return game_state


    def kantoor_set(self):
        self.in_kantoor = True
        self.p_x = 3
        self.p_y = 3
        self.position[:] = math.floor(self.p_x), math.floor(self.p_y)
        if self.in_auto:
            self.in_auto = False
            self.car.player_inside = False
            draaihoek = self.car.hoek - self.hoek
            self.car.draai_sprites(round(draaihoek * 180 / math.pi))
            self.car.hoek = self.hoek
            self.car.x = self.p_x
            self.car.y = self.p_y
            self.car.speed = 0

    def update_kantoor_deuren(self):
        if (self.kantoor_deuren_update != 0).any():
            self.kantoor_deuren += 0.004 * self.kantoor_deuren_update
            check1 = self.kantoor_deuren >= 1
            self.kantoor_deuren[check1] = 1
            self.kantoor_deuren_update[check1] = 0

            check2 = self.kantoor_deuren < 0
            self.kantoor_deuren[check2] = 0
            self.kantoor_deuren_update[check2] = 0
            self.kantoor_open_deuren[check2] = True

    def start_deur(self, deur):
        self.kantoor_open_deuren[deur] = False
        if self.kantoor_deuren_update[deur] != 0:
            self.kantoor_deuren_update[deur] *= -1
        elif self.kantoor_deuren[deur]:
            self.kantoor_deuren_update[deur] = -1
        else:
            self.kantoor_deuren_update[deur] = 1


# Prijs, Pakjes, snelheid, optrek, hp, gears
auto_gegeven = [(0, 3, 10, 1, 6, 3), (20, 6, 20, 2, 8, 4), (100, 10, 30, 2, 10, 5)]


class PostBus(Sprite):

    def __init__(self, image, images, map_png, x, y, height, type=0, hp=20, schaal=0.2):
        super().__init__(image, images, map_png, x, y, height, "PostBus", schaal)
        self.schadelijk = False
        self.map_grootte = 6
        self.type = type
        self.speed = 0
        self.vector = np.array([1, 0])
        self.hoek = -math.pi / 2
        self.player_inside = False
        self.crashed = False
        self.turning_mult = 2
        self.stuurhoek = 0
        self.versnelling = 1
        self.versnellingen = ["R", "1", "2", "3", "4", "5", "6", "7"]
        self.input_delay = 0
        self.crash_time = time.time() + 2
        self.dozen = 5 # Start hoeveelheid dozen
        if not self.type:
            self.dozen = 3
        self.max_dozen = auto_gegeven[type][1]
        self.snelheid_incr = auto_gegeven[type][2] / 400
        self.optrek = auto_gegeven[type][3]/1000
        self.afrem = self.optrek * 2
        self.hp = auto_gegeven[type][4]
        self.max_versnelling = auto_gegeven[type][5]
        self.info = auto_gegeven[type]
        self.render_text = []

    def update(self, world_map, speler, delta):
        """Update positie auto"""
        self.speed_update()
        speed = self.speed * delta / 0.015
        if self.speed == 0:
            return
        elif self.speed < 0:
            self.turning_mult = 50
        else:
            self.turning_mult = (self.optrek / speed) ** 1.2 * 500
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
                        self.hoek = math.pi / 2
                    elif self.vector[1] != 0:
                        self.hoek = -math.pi / 2
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
                self.vector = (0, 0)
                self.speed = 0
                self.versnelling = 1
                self.hp -= 1
                if self.hp == 0:
                    speler.hit = True
                    self.player_leaving(world_map, speler)
                    self.hp = 9
                    speler.aantal_hartjes -= 1
                elif speler.in_auto:
                    self.crashed = True
                    self.crash_time = time.time()

    def brake(self):
        if self.speed > self.afrem:
            self.speed -= self.afrem
            if self.speed < (self.versnelling - 1.5) * self.snelheid_incr:
                self.versnelling -= 1
        else:
            self.speed = 0.0

    def accelerate(self, speler):
        if self.versnelling != 0:
            if self.speed < 0:
                self.speed = 0
            elif self.speed < self.snelheid_incr * self.versnelling:
                # Changing the 0.05 affects line 171 IB2 (sound) and the up and downshifting line 330 IB2
                # In class affects in speed_update and braking
                self.speed += self.optrek
            else:
                speler.messages.append(("Shift", time.time()))
                self.speed -= self.afrem
        else:
            if self.speed > 0:
                self.speed -= self.optrek
            elif self.speed > -0.01:
                self.speed -= self.optrek / 2

    def speed_update(self):
        if self.speed > self.snelheid_incr * self.versnelling:
            self.speed -= self.afrem / 2
            if self.speed > self.snelheid_incr * (self.versnelling + 1):
                self.speed -= self.afrem
            if self.speed < 0:
                self.speed = 0
        elif self.speed < 0 and self.versnelling:
            if self.speed > -self.optrek / 5:
                self.speed = 0
            else:
                self.speed += self.optrek / 5

    def draaien(self, hoek):
        self.hoek = (hoek + self.hoek) % (2 * math.pi)
        self.vector = np.array([math.cos(self.hoek), math.sin(self.hoek)])
        self.draai_sprites(round(-hoek * 180 / math.pi))

    def player_enter(self, speler):
        """Kijkt of speler dicht genoeg tegen auto staat om in te stappen.\n
        zet alle settings correct"""
        if self.afstanden(speler.p_x, speler.p_y) < 1.5:
            self.player_inside = True
            self.versnelling = 1
            speler.p_x = self.x
            speler.p_y = self.y
            speler.position[:] = math.floor(self.x), math.floor(self.y)
            hoek_diff = self.hoek - speler.hoek
            speler.draaien(hoek_diff)
            speler.hoek = self.hoek
            # speler.aanmaak_r_stralen()
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


class Voertuig(Sprite):
    def __init__(self, image, images, map_png, x, y, height, world_map, schaal=0.2):
        super().__init__(image, images, map_png, int(x) + 0.5, int(y) + 0.5, height, "Auto", schaal)
        self.speed = 0.05
        self.vector = [1, 0]
        self.hoek = 0
        self.nieuwe_pos = [0, 0]  # pos op wereldmap
        self.position = [math.floor(x), math.floor(y)]
        self.select_new_dir(world_map, initial=True)
        self.map_grootte = 6

    def crashing(self):
        self.draai_sprites(180)
        self.nieuwe_pos = [self.nieuwe_pos[0] - 9 * self.vector[0], self.nieuwe_pos[1] - 9 * self.vector[1]]
        self.vector = [v * -1 for v in self.vector]

    def collision(self, sprites):
        for sprite in sprites:
            if sprite == self:
                continue
            print(abs(self.x - sprite.x + self.y - sprite.y))
            if abs(self.x - sprite.x + self.y - sprite.y) <= 0.5:
                return sprite
        return 0

    def update(self, world_map, speler, delta, *args):
        if self.position != self.nieuwe_pos:
            self.x += self.speed * self.vector[0]
            self.y += self.speed * self.vector[1]
            self.position = [math.floor(self.x), math.floor(self.y)]

            return

        self.select_new_dir(world_map)

    def select_new_dir(self, world_map, initial=None):
        nieuwe_richting = []
        i = 0
        vectors = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        for vx, vy in vectors:
            if self.vector == [(vx * -1), (vy * -1)]: continue;
            pos = (self.position[1] + 3 * vy, self.position[0] + 3 * vx)
            pos2 = (self.position[1] + 5 * vy, self.position[0] + 5 * vx)
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
            plek = random.randint(0, len(nieuwe_richting) - 1)
            self.vector = nieuwe_richting[plek][0]
            self.nieuwe_pos = nieuwe_richting[plek][1]
        if self.position[0] == self.nieuwe_pos[0]:
            x = self.position[1] - self.nieuwe_pos[1]
            if x >= 0:
                x = 130
            else:
                x = 310

        if self.position[1] == self.nieuwe_pos[1]:
            x = self.position[0] - self.nieuwe_pos[0]
            if x >= 0:
                x = 220
            else:
                x = 40
        self.draai_sprites(x - self.hoek)
        self.hoek = x

        self.update(world_map, None, 0.1)


class Politie(Sprite):
    def __init__(self, image, images, map_png, x, y, height, speler, politie_pad, schaal=0.2):
        super().__init__(image, images, map_png, x, y, height, "Politie", schaal)
        self.pad = []
        self.prev_playerpos = [-1, -1]
        self.achtervolgen = True
        self.hoek = 0  # set to initial of 3D SPRITE
        self.speed = 0.05
        self.politie_pad = self.pad
        self.position = [math.floor(self.x), math.floor(self.y)]

    def update(self, world_map, speler, *args):
        self.politie_pad = self.pad
        if self.politie_pad:
            if self.achtervolgen:
                if speler.in_auto:
                    speed = max(speler.car.speed, self.speed)
                else:
                    speed = self.speed

                if len(self.politie_pad) > 1:

                    vector = (self.politie_pad[0][1] - self.politie_pad[1][1],
                            self.politie_pad[0][0] - self.politie_pad[1][0])  # Pad uses inverse x/y from normal so reverting here
                    self.x -= speed * vector[1]
                    self.y -= speed * vector[0]

                else:
                    if self.afstand <= 2:
                        self.x = speler.p_x
                        self.y = speler.p_y


            if self.afstand <= 2:
                self.x = speler.p_x
                self.y = speler.p_y
            else:
                oude_position = self.position
                self.position = [math.floor(self.x), math.floor(self.y)]
                if self.position != oude_position:
                    x = 0

                    if oude_position[0] == self.position[0]:
                        x = oude_position[1] - self.position[1]
                        if x >= 0:
                            x = 130
                        else:
                            x = 310

                    if oude_position[1] == self.position[1]:
                        x = oude_position[0] - self.position[0]
                        if x >= 0:
                            x = 220
                        else:
                            x = 40
                    self.draai_sprites(x - self.hoek)
                    self.hoek = x
                    #print(self.hoek)



