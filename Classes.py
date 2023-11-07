import math
import numpy as np
from numba import njit
#from line_profiler_pycharm import profile

from sdl2 import *



class Sprite():
    def __init__(self, image, x, y, height):
        self.image = image  # The image of the sprite
        self.x = x  # The x-coordinate of the sprite
        self.y = y  # The y-coordinate of the sprite
        self.position = (x, y)
        self.breedte = image.size[0]
        self.hoogte = image.size[1]
        self.height = height
        self.updatebaar = False
        self.deletable = False
        self.vector = (1,0)
        self.tick = 0
        self.afstand = 1

    def afstanden(self, player):
        self.afstand = ((self.x - player.p_x) ** 2 + (self.y - player.p_y) ** 2)**(1/2)
        return self.afstand

    def update(self, world_map):
        if self.updatebaar:
            time = self.tick/50
            self.height -= (1/2)*(4*time-time**2)
            x = (self.x + 0.1 * self.vector[0])
            y = (self.y + 0.1 * self.vector[1])
            if world_map[math.floor(y)][math.floor(x)] == 0:
                self.x = x
                self.y = y
                self.position = (x, y)

            if world_map[math.floor(y)][math.floor(self.x)] == 0:
                self.y = y
                self.position = (self.x, y)
            if world_map[math.floor(self.y)][math.floor(x)] == 0:
                self.x = x
                self.position = (x, self.y)
            if self.height > 800:
                self.height = 800
                self.updatebaar = False

        self.tick += 1

        if self.deletable and self.tick > 500:
            return True
        return False


    def __delete__(self, instance):
        del self



class Player():
    def __init__(self, x, y, hoek, breedte=800):
        """Player is gedefinieerd door zijn start x-, y-coördinaten (floats), kijkhoek (rad) en
         de breedte (int) van het scherm dat hij opneemt"""
        self.position = (math.floor(x), math.floor(y))
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
        self.tile = math.floor(self.p_x/9), math.floor(self.p_y/9)

    def aanmaak_r_stralen(self, d_camera=1):
        """Gebruikt speler hoek, speler straal en gegeven camera afstand om r_stralen voor raycaster te berekenen"""

        for i in range(self.breedte):
            r_straal_kolom = d_camera * self.r_speler + (1 - (2 * i) / self.breedte) * self.r_camera
            hoek = math.atan2(r_straal_kolom[0], r_straal_kolom[1])
            self.hoeken[i] = hoek

        self.r_stralen[:,0] = np.cos(self.hoeken)
        self.r_stralen[:,1] = np.sin(self.hoeken)

    def move(self, richting, stap, world_map):
        """Kijkt of speler naar voor kan bewegen zo niet of hij langs de muur kan schuiven"""
        y_dim, x_dim = np.shape(world_map)
        if type(self.car) != int:
            if richting == 1:
                self.car.accelerate(world_map)
            else:
                self.car.brake()
        else:
            x = (self.p_x + richting * stap * self.r_speler[0]) % x_dim
            y = (self.p_y + richting * stap * self.r_speler[1]) % y_dim
            atm = 0.3  # afstand_tot_muur zelfde bij auto
            x_2 = (x + atm * richting * self.r_speler[0]) % x_dim
            y_2 = (y + atm * richting * self.r_speler[1]) % y_dim

            if world_map[math.floor(y)][math.floor(x)] <= 0 and \
                    world_map[math.floor(y_2)][math.floor(x_2)] <= 0:
                self.p_x = x
                self.p_y = y
                self.position = (math.floor(x),math.floor(y))

            if world_map[math.floor(y)][math.floor(self.p_x)] <= 0 and \
                    world_map[math.floor(y_2)][math.floor(self.p_x)] <= 0:
                self.p_y = y
                self.position = (math.floor(self.p_x),math.floor(y))
            if world_map[math.floor(self.p_y)][math.floor(x)] <= 0 and \
                    world_map[math.floor(self.p_y)][math.floor(x_2)] <= 0:
                self.p_x = x
                self.position = (math.floor(x),math.floor(self.p_y))
        self.tile = math.floor(self.p_x/9),math.floor(self.p_y/9)

    def draaien(self, hoek):
        """Via gegeven draaihoek alle stralen in van de speler (en auto) laten draaien"""
        self.hoek = (hoek + self.hoek) % (2*math.pi)
        self.hoeken = (hoek + self.hoeken) % (2*math.pi)

        self.r_speler = np.array([math.cos(self.hoek), math.sin(self.hoek)])
        self.r_camera = np.array([math.cos(self.hoek - math.pi / 2), math.sin(self.hoek - math.pi / 2)])

        self.r_stralen[:, 0] = np.cos(self.hoeken)
        self.r_stralen[:, 1] = np.sin(self.hoeken)
        #print(self.hoeken)
        if self.car != 0:
            self.car.draaien(hoek)

    def trow(self, world_map):
        sprite = Sprite(self.doos, self.p_x, self.p_y, 600)
        sprite.updatebaar = True
        sprite.deletable = True
        sprite.vector = self.r_speler/5
        for i in range(51):
            sprite.update(world_map)
        return sprite


    def n_raycasting(self, world_map, deuren):
        """Gebruik maken van de numpy raycaster om de afstanden en kleuren van muren te bepalen
        Neemt world map in zodat er gemakkelijk van map kan gewisseld worden"""

        #Had circulaire import dus np raycaster in de class
        # print(self.r_speler)
        # variabelen
        y_dim, x_dim = np.shape(world_map)
        l = min(50, 3 * (x_dim ** 2 + y_dim ** 2) ** (1 / 2))  # maximale lengte die geraycast wordt

        # Aanmaak numpy arrays die terug gestuurd worden
        kleuren = np.zeros(self.breedte, dtype='int')
        d_muur = np.ones(self.breedte)*60
        d_muur_vlak = np.zeros(self.breedte)

        z_kleuren = np.zeros(self.breedte, dtype='int')
        z_d_muur = np.ones(self.breedte)
        z_d_muur_vlak = np.zeros(self.breedte)

        delta_x = 1 / np.abs(self.r_stralen[:, 0])
        delta_y = 1 / np.abs(self.r_stralen[:, 1])

        # Bij negatieve R_straal moeten we op de wereldmap 1 positie meer naar 0 toe schuiven.
        richting_x = np.where(self.r_stralen[:, 0] >= 0, 0, 1)
        richting_y = np.where(self.r_stralen[:, 1] >= 0, 0, 1)

        # initiele afstand berekenen
        d_v = np.where(self.r_stralen[:, 0] >= 0, (1 - (self.p_x - math.floor(self.p_x))) * delta_x,
                       (self.p_x - math.floor(self.p_x)) * delta_x)
        d_h = np.where(self.r_stralen[:, 1] >= 0, (1 - (self.p_y - math.floor(self.p_y))) * delta_y,
                       (self.p_y - math.floor(self.p_y)) * delta_y)

        muren_check = np.full(self.breedte, False)
        z_buffer = np.full(self.breedte, True)

        while True:
            # reset van muren_check vormt plekken waarop we muren raken
            muren_check[:] = False
            z_buffer[:] = True

            # kijken of we d_v of d_h nodig hebben deze loop
            dist_cond = d_v < d_h
            least_distance = np.where(dist_cond, d_v, d_h)

            # Mogen enkel muren checken die nog niet geraakt zijn en binnen de afstand liggen
            break_1 = d_v < l
            break_2 = d_h < l
            break_3 = kleuren == 0
            #break_z = z_kleuren == 0
            break_cond = (dist_cond * break_1 + ~dist_cond * break_2) * break_3
            # Break 1 enkel tellen als we met d_v werken en d_h enkel als we met d_h werken
            # Binair vermenigvuldigen als break3 = 0 dan wordt break_cond op die plek 0

            # Als op alle plekken break_cond == 0 return dan de bekomen waardes
            if (break_cond == False).all():
                return (d_muur, (d_muur_vlak % 1), (kleuren - 1)), (
                (1 / z_d_muur), (z_d_muur_vlak % 1), (z_kleuren))

            # x en y berekenen adhv gegeven d_v of d_h en afronden op 3-8 zodat astype(int) niet afrond naar beneden terwijl het naar boven zou moeten
            # AANPASSING: Zolang we geen modulo doen rond float 32 ook perfect af naar boven als het moet en is sneller
            x = (self.p_x + least_distance * self.r_stralen[:, 0])#.astype('float32')
            y = (self.p_y + least_distance * self.r_stralen[:, 1])#.astype('float32')

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
            #valid_indices = np.logical_and.reduce((0 <= x_f, x_f < len(world_map[0]), 0 <= y_f, y_f < len(world_map), break_cond))
            """HIER LOGICA INVOEGEN VOOR ALS EEN RAY OUT OF BOUND GAAT --> Map herwerken"""

            #muren_check[valid_indices] = np.where(world_map[y_f[valid_indices], x_f[valid_indices]] > 0, True, False)
            muren_check[break_cond] = np.where(world_map[y_f[break_cond], x_f[break_cond]] > 0, True, False)
            # op de plekken waar logica correct is kijken of we een muur raken
            if False:
                z_buffer[muren_check] = np.where(world_map[y_f[muren_check], x_f[muren_check]] < -10, True, False)
            if muren_check.any():
                # We raken op muren_check = True muren en we slaan die data op in de gecreeerde arrays
                kleuren[muren_check] = world_map[y_f[muren_check], x_f[muren_check]]
                    # r_straal*r_speler voor fish eye eruit te halen
                d_muur[muren_check] = least_distance[muren_check] * (self.r_stralen[muren_check, 0] * self.r_speler[0] + self.r_stralen[muren_check, 1] * self.r_speler[1])
                    # Als dist_cond dan raken we een muur langs de x kant dus is y de veranderlijke als we doorschuiven --> meegeven als var voor vaste textuur
                d_muur_vlak[muren_check] += np.where(dist_cond[muren_check], y[muren_check], x[muren_check])
                #d_muur_vlak += np.where(muren_check * ~dist_cond, x, 0)
            if False:
                z_kleuren[muren_check * ~z_buffer * break_z] += world_map[
                    y_f[muren_check * ~z_buffer * break_z], x_f[muren_check * ~z_buffer * break_z]]
                # r_straal*r_speler voor fish eye eruit te halen
                z_d_muur += np.where(break_cond * muren_check * ~z_buffer * break_z,
                                     least_distance * (self.r_stralen[:, 0] * self.r_speler[0] + self.r_stralen[:, 1] * self.r_speler[1]), 0)
                # Als dist_cond dan raken we een muur langs de x kant dus is y de veranderlijke als we doorschuiven --> meegeven als var voor vaste textuur
                z_d_muur_vlak += np.where(muren_check * ~z_buffer * dist_cond * break_z, y, 0)
                z_d_muur_vlak += np.where(muren_check * ~z_buffer * ~dist_cond * break_z, x, 0)
                #z_kleuren = np.where((z_d_muur_vlak % 1) < deuren[z_kleuren].positie, 0, z_kleuren)

            # incrementeren, d_v als dist_cond True is, d_h als dist_cond False is
            d_v += dist_cond * delta_x
            d_h += (~dist_cond) * delta_y
        #print(self.r_speler)
    def reset(self):
        self.p_x = 50.4*9
        self.p_y = 49*9
        self.hoek = math.pi / 4
        self.r_speler = np.array([math.cos(self.hoek), math.sin(self.hoek)])
        self.r_camera = np.array([math.cos(self.hoek - math.pi / 2), math.sin(self.hoek - math.pi / 2)])
        self.aanmaak_r_stralen(d_camera=1)


class Auto():
    def __init__(self, p_x, p_y, type=0, hp=20, Player=0):
        self.position = (p_x, p_y)
        self.p_x = p_x
        self.p_y = p_y
        self.type = type
        self.hp = hp
        self.speed = 0
        self.vector = np.array([1, 0])
        self.afrem = 0.1
        self.optrek = 0.1
        self.hoek = 0
        self.Player = Player
        self.player_inside = False

    def update(self, world_map):
        y_dim, x_dim = np.shape(world_map)
        x = self.p_x + self.speed * self.vector[0]
        y = self.p_x + self.speed * self.vector[1]
        atm = 0.3  # afstand_tot_muur
        if x < 0:
            x += x_dim
        elif x > x_dim:
            x -= x_dim
        if y < 0:
            y += y_dim
        elif y > y_dim:
            y -= y_dim
        if world_map[math.floor(y)][math.floor(x)] == 0 and world_map[math.floor(y + atm)][math.floor(x + atm)] == 0:
            self.p_x = x
            self.p_y = y
            if self.player_inside:
                self.Player.p_x = x
                self.Player.p_y = y
                self.Player.position = (x, y)

    def brake(self):
        if self.speed > self.afrem:
            self.speed -= self.afrem
        else:
            self.speed = 0

    def accelerate(self):
        if self.speed < 5:
            self.speed += self.optrek

    def turning(self, hoek):
        self.hoek += hoek
        self.vector = np.array([math.cos(self.hoek), math.sin(self.hoek)])

    def player_enter(self):
        self.player_inside = True
        self.Player.p_x = self.p_x
        self.Player.p_y = self.p_y

    def player_leaving(self, world_map):
        y_dim, x_dim = np.shape(world_map)
        self.player_inside = False
        self.speed = 0
        if 0 < self.p_x - 0.5 and 0 < self.p_y - 0.5:
            if world_map[math.floor(self.p_y - 0.5)][math.floor(self.p_x - 0.5)] == 0:
                self.Player.p_x = self.p_x - 0.5
                self.Player.p_y = self.p_y - 0.5

    def hitting(self, object):
        self.hp -= 1


class Node:  # A* algoritme
    def __init__(self, parent=None, positie=None):
        self.parent = parent
        self.positie = positie
        self.g = 0  # g_cost: afstand van beginnende node
        self.h = 0  # h_cost: afstand van eind node
        self.f = 0  # f_cost: g_cost + h_cost = totale cost
    def __eq__(self, other):
        return self.positie == other.positie

class Deur():
    def __init__(self,kleur = 0):
        self.moving = True
        self.open = False
        self.richting = 1
        self.positie = 0
        self.kleur = kleur

    def update(self):
        if self.moving:
            self.positie += self.richting/500
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

