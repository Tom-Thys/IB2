import math
import numpy as np
from sdl2 import *
from Raycaster import *


class Player():
    def __init__(self, x, y, hoek, breedte=800):
        """Player is gedefinieerd door zijn start x-, y-coördinaten (floats), kijkhoek (rad) en
         de breedte (int) van het scherm dat hij opneemt"""
        self.p_x = x
        self.p_y = y
        self.hoek = hoek
        self.r_speler = np.array([math.cos(hoek), math.sin(hoek)])
        self.r_stralen = np.zeros((breedte, 2))
        self.breedte = breedte
        self.car = 0

    def aanmaak_r_stralen(self, d_camera=1):
        """Gebruikt speler hoek, speler straal en gegeven camera afstand om r_stralen voor raycaster te berekenen"""
        cameravlak = np.array([math.cos(self.hoek - math.pi / 2), math.sin(self.hoek - math.pi / 2)])
        for i in range(self.breedte):  # +1 anders mis je buitenste waarde op renderer
            r_straal_kolom = d_camera * self.r_speler + (1 - (2 * i) / self.breedte) * cameravlak
            self.r_stralen[i] = (np.divide(r_straal_kolom, np.linalg.norm(r_straal_kolom)))

    def move(self, richting, stap, world_map):
        """Kijkt of speler naar voor kan bewegen zo niet of hij langs de muur kan schuiven"""
        y_dim, x_dim = np.shape(world_map)
        # print(self.r_speler,[self.p_x,self.p_y])
        if type(self.car) != int:
            if richting == 1:
                self.car.accelerate(world_map)
            else:
                self.car.brake()
        else:
            x = (self.p_x + richting * stap * self.r_speler[0])%x_dim
            y = (self.p_y + richting * stap * self.r_speler[1])%y_dim
            atm = 0.3  # afstand_tot_muur zelfde bij auto
            x_2 = (x + atm * richting * self.r_speler[0])%x_dim
            y_2 = (y + atm * richting * self.r_speler[1])%y_dim



            if world_map[math.floor(y)][math.floor(x)] == 0 and \
                    world_map[math.floor(y_2)][math.floor(x_2)] == 0:
                self.p_x = x
                self.p_y = y

            if world_map[math.floor(y)][math.floor(self.p_x)] == 0 and \
                    world_map[math.floor(y_2)][math.floor(self.p_x)] == 0:
                self.p_y = y
            if world_map[math.floor(self.p_y)][math.floor(x)] == 0 and \
                    world_map[math.floor(self.p_y)][math.floor(x_2)] == 0:
                self.p_x = x

    def draaien(self, hoek):
        """Via gegeven draaihoek alle stralen in van de speler (en auto) laten draaien"""
        self.hoek += hoek
        draai_matrix = np.array([[math.cos(hoek), -math.sin(hoek)],
                                 [math.sin(hoek), math.cos(hoek)]])

        self.r_speler = np.array([math.cos(self.hoek), math.sin(self.hoek)])

        for i, straal in enumerate(self.r_stralen):
            self.r_stralen[i] = np.matmul(draai_matrix, straal)
        if self.car != 0:
            self.car.draaien(hoek, draai_matrix)

    def n_raycasting(self, world_map):
        """Gebruik maken van de numpy raycaster om de afstanden en kleuren van muren te bepalen
        Neemt world map in zodat er gemakkelijk van map kan gewisseld worden"""
        kolom = np.arange(self.breedte)
        d, v, kl = numpy_raycaster(self.p_x, self.p_y, self.r_stralen, self.r_speler, self.breedte, world_map)
        return kolom, d, v, kl


class Auto():
    def __init__(self, p_x, p_y, type=0, hp=20, Player=0):
        self.p_x = p_x
        self.p_y = p_y
        self.type = type
        self.hp = hp
        self.speed = 0
        self.vector = np.array([0, 0])
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
                self.Player.changes = True

    def brake(self):
        if self.speed > self.afrem:
            self.speed -= self.afrem
        else:
            self.speed = 0

    def accelerate(self):
        if self.speed < 5:
            self.speed += self.optrek

    def turning(self, hoek, draai_matrix=0):
        if not draai_matrix.any():
            draai_matrix = np.array([[math.cos(hoek), -math.sin(hoek)],
                                     [math.sin(hoek), math.cos(hoek)]])
        self.vector = np.matmul(draai_matrix, self.vector)
        self.hoek += hoek

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
        self.hitpoints -= 1
