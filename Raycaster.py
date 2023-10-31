import math
import numpy as np
from Classes import Deur


def nr_rond(nr, tol=5):
    p = 10 ** tol
    if 0 < nr < 100:
        return math.ceil(nr * p) / p
    elif nr < 0:
        return -1
    elif nr == 0:
        return 0
    else:
        return math.inf


def sign(x):
    if x < 0:
        return -1
    else:
        return 1


def fish_eye_(d, r_straal, r_speler):
    hoek = np.dot(r_speler, r_straal) / (np.linalg.norm(r_speler) * np.linalg.norm(r_straal))
    return hoek * d


def cosinusregel(straal1, straal2, d1, d2):
    cos_alfa = np.dot(straal1, straal2)
    side = (d1 ** 2 + d2 ** 2 - 2 * d1 * d2 * cos_alfa) ** (1 / 2)
    return side


def raycast(p_speler_x, p_speler_y, r_straal, r_speler, world_map):
    y_dim, x_dim = np.shape(world_map)
    r_straal_x = (r_straal[0])
    r_straal_y = (r_straal[1])
    delta_v = (1 / np.abs(r_straal_x))
    delta_h = (1 / np.abs(r_straal_y))
    if r_straal_x > 0:
        if r_straal_y > 0:
            d_v = ((1 - (p_speler_x - math.floor(p_speler_x))) * delta_v)
            d_h = ((1 - (p_speler_y - math.floor(p_speler_y))) * delta_h)
            while True:
                if d_v < d_h:
                    x = math.floor(nr_rond(p_speler_x + d_v * r_straal_x))
                    y = nr_rond(p_speler_y + d_v * r_straal_y)
                    if y < y_dim and x < x_dim:
                        k = world_map[math.floor(y)][x]
                        if k != 0:
                            return fish_eye_(d_v, r_straal, r_speler), k, 'y', y
                        else:
                            d_v += delta_v
                    else:
                        return 10, 0, "b", 0
                else:
                    x = nr_rond(p_speler_x + d_h * r_straal_x)
                    y = math.floor(nr_rond(p_speler_y + d_h * r_straal_y))
                    if 0 < y < y_dim and 0 < x < x_dim:
                        k = world_map[y][math.floor(x)]
                        if k != 0:
                            return fish_eye_(d_h, r_straal, r_speler), k, 'x', x
                        else:
                            d_h += delta_h
                    else:
                        return 10, 0, "b", 0
    if r_straal_x > 0:
        if r_straal_y < 0:
            d_v = (1 - (p_speler_x - math.floor(p_speler_x))) * delta_v
            d_h = (p_speler_y - math.floor(p_speler_y)) * delta_h
            while True:
                if d_v < d_h:
                    x = math.floor(nr_rond(p_speler_x + d_v * r_straal_x))
                    y = nr_rond(p_speler_y + d_v * r_straal_y)
                    if 0 <= y < y_dim and 0 < x < x_dim:
                        k = world_map[math.floor(y)][x]
                        if k != 0:
                            return fish_eye_(d_v, r_straal, r_speler), k, 'y', y
                        else:
                            d_v += delta_v
                    else:
                        return 10, 0, "b", 0
                else:
                    x = nr_rond(p_speler_x + d_h * r_straal_x)
                    y = math.floor(nr_rond(p_speler_y + d_h * r_straal_y))
                    if 0 <= y and x < x_dim:
                        k = world_map[y - 1][math.floor(x)]
                        if k != 0:
                            return fish_eye_(d_h, r_straal, r_speler), k, 'x', x
                        else:
                            d_h += delta_h
                    else:
                        return 10, 0, "b", 0
    if r_straal_x < 0:
        if r_straal_y > 0:
            d_v = (p_speler_x - math.floor(p_speler_x)) * delta_v
            d_h = (1 - (p_speler_y - math.floor(p_speler_y))) * delta_h
            while True:
                if d_v < d_h:
                    x = math.floor(nr_rond(p_speler_x + d_v * r_straal_x))
                    y = nr_rond(p_speler_y + d_v * r_straal_y)
                    if y < y_dim and 0 <= x:
                        k = world_map[math.floor(y)][x - 1]
                        if k != 0:
                            return fish_eye_(d_v, r_straal, r_speler), k, 'y', y
                        else:
                            d_v += delta_v
                    else:
                        return 10, 0, "b", 0
                else:
                    x = nr_rond(p_speler_x + d_h * r_straal_x)
                    y = math.floor(nr_rond(p_speler_y + d_h * r_straal_y))
                    if y < y_dim and 0 <= x:
                        k = world_map[y][math.floor(x)]
                        if k != 0:
                            return fish_eye_(d_h, r_straal, r_speler), k, 'x', x
                        else:
                            d_h += delta_h
                    else:
                        return 10, 0, "b", 0
    if r_straal_x < 0:
        if r_straal_y < 0:
            d_v = (p_speler_x - math.floor(p_speler_x)) * delta_v
            d_h = (p_speler_y - math.floor(p_speler_y)) * delta_h
            while True:
                if d_v < d_h:
                    x = math.floor(nr_rond(p_speler_x + d_v * r_straal_x))
                    y = nr_rond(p_speler_y + d_v * r_straal_y)
                    if 0 <= y and 0 <= x:
                        k = world_map[math.floor(y)][math.floor(x - 1)]
                        if k != 0:
                            return fish_eye_(d_v, r_straal, r_speler), k, 'y', y
                        else:
                            d_v += delta_v
                    else:
                        return 10, 0, "b", 0
                else:
                    x = nr_rond(p_speler_x + d_h * r_straal_x)
                    y = math.floor(nr_rond(p_speler_y + d_h * r_straal_y))
                    if 0 <= y and 0 <= x:
                        k = world_map[math.floor(y - 1)][math.floor(x)]
                        if k != 0:
                            return fish_eye_(d_h, r_straal, r_speler), k, 'x', x
                        else:
                            d_h += delta_h
                    else:
                        return 10, 0, "b", 0
    if r_straal_y == 0:
        if r_straal_x < 0:
            d_v = (p_speler_x - math.floor(p_speler_x)) * delta_v
            while True:
                x = math.floor(nr_rond(p_speler_x + d_v * r_straal_x))
                y = nr_rond(p_speler_y)
                if 0 <= y and 0 <= x:
                    k = world_map[math.floor(y)][math.floor(x - 1)]
                    if k != 0:
                        return fish_eye_(d_v, r_straal, r_speler), k, 'y', y
                    else:
                        d_v += delta_v
                else:
                    return 10, 0, "b", 0
        if r_straal_x > 0:
            d_v = (1 - p_speler_x - math.floor(p_speler_x)) * delta_v
            while True:
                x = math.floor(nr_rond(p_speler_x + d_v * r_straal_x))
                y = nr_rond(p_speler_y)
                if y < y_dim and x < x_dim:
                    k = world_map[math.floor(y)][math.floor(x)]
                    if k != 0:
                        return fish_eye_(d_v, r_straal, r_speler), k, 'y', y
                    else:
                        d_v += delta_v
                else:
                    return 10, 0, "b", 0
    if r_straal_x == 0:
        if r_straal_y < 0:
            d_h = (p_speler_y - math.floor(p_speler_y)) * delta_h
            while True:
                y = math.floor(nr_rond(p_speler_x + d_h * r_straal_y))
                x = nr_rond(p_speler_y)
                if 0 <= y and 0 <= x:
                    k = world_map[math.floor(y - 1)][math.floor(x)]
                    if k != 0:
                        return fish_eye_(d_h, r_straal, r_speler), k, 'x', x
                    else:
                        d_h += delta_h
                else:
                    return 10, 0, "b", 0
        if r_straal_y > 0:
            d_h = (1 - p_speler_y - math.floor(p_speler_y)) * delta_h
            while True:
                y = math.floor(nr_rond(p_speler_x + d_h * r_straal_y))
                x = nr_rond(p_speler_y)
                if y < y_dim and x < x_dim:
                    k = world_map[math.floor(y)][math.floor(x)]
                    if k != 0:
                        return fish_eye_(d_h, r_straal, r_speler), k, 'x', x
                    else:
                        d_h += delta_h
                else:
                    return 10, 0, "b", 0

    return 1, 0, "b", 0


def numpy_raycaster(p_x, p_y, r_stralen, r_speler, breedte, world_map):
    #variabelen
    y_dim, x_dim = np.shape(world_map)
    l = min(60, 3 * (x_dim ** 2 + y_dim ** 2) ** (1 / 2)) #maximale lengte die geraycast wordt

    #Aanmaak numpy arrays die terug gestuurd worden
    kleuren = np.zeros(breedte,dtype='int')
    d_muur = np.zeros(breedte)
    d_muur_vlak = np.zeros(breedte)

    z_kleuren = np.zeros(breedte, dtype='int')
    z_d_muur = np.zeros(breedte)
    z_d_muur_vlak = np.zeros(breedte)

    delta_x = 1 / np.abs(r_stralen[:, 0])
    delta_y = 1 / np.abs(r_stralen[:, 1])

    #Bij negatieve R_straal moeten we op de wereldmap 1 positie meer naar 0 toe schuiven.
    richting_x = np.where(r_stralen[:, 0] >= 0, 0, 1)
    richting_y = np.where(r_stralen[:, 1] >= 0, 0, 1)

    #initiele afstand berekenen
    d_v = np.where(r_stralen[:, 0] >= 0, (1 - (p_x - math.floor(p_x))) * delta_x, (p_x - math.floor(p_x)) * delta_x)
    d_h = np.where(r_stralen[:, 1] >= 0, (1 - (p_y - math.floor(p_y))) * delta_y, (p_y - math.floor(p_y)) * delta_y)

    while True:
        #reset van muren_check vormt plekken waarop we muren raken
        muren_check = np.full(breedte, False)
        z_buffer = np.full(breedte, False)

        #kijken of we d_v of d_h nodig hebben deze loop
        dist_cond = d_v < d_h
        least_distance = np.where(dist_cond, d_v, d_h)

        #Mogen enkel muren checken die nog niet geraakt zijn en binnen de afstand liggen
        break_1 = d_v < l
        break_2 = d_h < l
        break_3 = kleuren == 0
        break_z = z_kleuren == 0
        break_cond = (dist_cond * break_1 + ~dist_cond * break_2) * break_3
        #Break 1 enkel tellen als we met d_v werken en d_h enkel als we met d_h werken
        #Binair vermenigvuldigen als break3 = 0 dan wordt break_cond op die plek 0


        #Als op alle plekken break_cond == 0 return dan de bekomen waardes
        if np.all(~break_cond):
            return ((1 / d_muur), (d_muur_vlak % 1), (kleuren-1)),((1 / z_d_muur), (z_d_muur_vlak % 1), (z_kleuren))

        #x en y berekenen adhv gegeven d_v of d_h en afronden op 3-8 zodat astype(int) niet afrond naar beneden terwijl het naar boven zou moeten
        #AANPASSING: Zolang we geen modulo doen rond float 32 ook perfect af naar boven als het moet en is sneller
        x = (p_x + least_distance * r_stralen[:, 0]).astype('float32')
        y = (p_y + least_distance * r_stralen[:, 1]).astype('float32')

        #infinity world try-out
        """while np.any(np.logical_and.reduce((-4 * x_dim < x, x <= 0))):
            x = np.where(x <= 0, x + x_dim, x)
        while np.any(np.logical_and.reduce((-4 * y_dim <= y, y <= 0))):
            y = np.where(y <= 0, y + y_dim, y)
        while np.any(np.logical_and.reduce((y_dim <= y, y < 5*y_dim))):
            y = np.where(y >= y_dim, y - y_dim, y)

        while np.any(np.logical_and.reduce((x_dim < x, x < 5*x_dim))):
            x = np.where(x >= x_dim, x - x_dim, x)"""


        #World map neemt enkel int dus afronden naar beneden via astype(int) enkel als d_v genomen is moet correctie toegevoegd worden bij x
        x_f = np.where(dist_cond, (x - richting_x).astype(int), x.astype(int))
        y_f = np.where(~dist_cond, (y - richting_y).astype(int), y.astype(int))


        #Logica: x_f moet tussen 0 en x_dim blijven en y_f tussen 0 en y_dim
        #Deze tellen ook enkel maar als de break conditie niet telt
        valid_indices = np.logical_and.reduce((0 <= x_f, x_f < len(world_map[0]), 0 <= y_f, y_f < len(world_map),break_cond))
        """HIER LOGICA INVOEGEN VOOR ALS EEN RAY OUT OF BOUND GAAT --> Map herwerken"""

        muren_check[valid_indices] = np.where(world_map[y_f[valid_indices], x_f[valid_indices]], True, False)
        #op de plekken waar logica correct is kijken of we een muur raken
        z_buffer[muren_check] = np.where(world_map[y_f[muren_check], x_f[muren_check]]>0, True, False)




        #We raken op muren_check = True muren en we slaan die data op in de gecreeerde arrays
        kleuren[muren_check*z_buffer] += world_map[y_f[muren_check*z_buffer], x_f[muren_check*z_buffer]]
        #r_straal*r_speler voor fish eye eruit te halen
        d_muur += np.where(break_cond * muren_check*z_buffer, least_distance*(r_stralen[:,0]*r_speler[0]+r_stralen[:,1]*r_speler[1]), 0)
        #Als dist_cond dan raken we een muur langs de x kant dus is y de veranderlijke als we doorschuiven --> meegeven als var voor vaste textuur
        d_muur_vlak += np.where(muren_check*z_buffer * dist_cond, y, 0)
        d_muur_vlak += np.where(muren_check*z_buffer * ~dist_cond, x, 0)

        z_kleuren[muren_check * ~z_buffer*break_z] += world_map[y_f[muren_check * ~z_buffer*break_z], x_f[muren_check * ~z_buffer*break_z]]
        # r_straal*r_speler voor fish eye eruit te halen
        z_d_muur += np.where(break_cond * muren_check * ~z_buffer*break_z,
                           least_distance * (r_stralen[:, 0] * r_speler[0] + r_stralen[:, 1] * r_speler[1]), 0)
        # Als dist_cond dan raken we een muur langs de x kant dus is y de veranderlijke als we doorschuiven --> meegeven als var voor vaste textuur
        z_d_muur_vlak += np.where(muren_check * ~z_buffer * dist_cond*break_z, y, 0)
        z_d_muur_vlak += np.where(muren_check * ~z_buffer * ~dist_cond*break_z, x, 0)
        z_kleuren = np.where((z_d_muur_vlak%1) < deuren[z_kleuren].positie, 0, z_kleuren)




        # incrementeren, d_v als dist_cond True is, d_h als dist_cond False is
        d_v += dist_cond * delta_x
        d_h += (~dist_cond) * delta_y


deuren = {-1000: Deur(), -1001: Deur()}

class Deur():
    def __init__(self,kleur = 0):
        self.moving = False
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

    def moving(self):
        self.moving = True
        self.open = False
