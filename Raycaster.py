import math
import numpy as np

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
    side = (d1 ** 2 + d2 ** 2 - 2 * d1 * d2 * cos_alfa)**(1/2)
    return side



def raycast(p_speler_x, p_speler_y, r_straal,r_speler,world_map):
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
                    if 0< y < y_dim and 0 < x < x_dim:
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
                    if 0 <= y < y_dim and 0< x < x_dim:
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
            d_v = (1-p_speler_x - math.floor(p_speler_x)) * delta_v
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
                    k = world_map[math.floor(y-1)][math.floor(x)]
                    if k != 0:
                        return fish_eye_(d_h, r_straal, r_speler), k, 'x', x
                    else:
                        d_h += delta_h
                else:
                    return 10, 0, "b", 0
        if r_straal_y > 0:
            d_h = (1-p_speler_y - math.floor(p_speler_y)) * delta_h
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

"""
def raycasting(p_speler_x, p_speler_y, stralen, r_speler):
    muren = []
    
    for i, straal in enumerate(stralen):
        d, k, side, side_d = raycast(p_speler_x, p_speler_y, straal)
        muren.append((i, d, k, side, side_d))

    
    aantal = 1
    for j, straal in enumerate(stralen):
        if j == 0:
            d, k, side, side_d = raycast(p_speler_x, p_speler_y, straal, r_speler)
            muren.append((j, d, k, side, side_d))
            vorige_straal = straal
        elif j % (aantal+1) == 0:
            vorig = muren[-1]
            d, k, side, side_d = raycast(p_speler_x, p_speler_y, straal, r_speler)
            if vorig[2] == k and 0.95 < vorig[1]/d < 1.05 and vorig[3] == side:
                for i in range(aantal):
                    dist = vorig[1] + (i + 1) * (d - vorig[1]) / (aantal + 2)
                    side_dist = cosinusregel(vorige_straal, stralen[j-aantal+i],vorig[1],dist)
                    muren.append((j - aantal + i, dist, k, side, vorig[4] + side_dist*sign(vorig[4]-d)))
                    #muren.append((j-1,(d + muren[-1][1])/2,k))
            else:
                for i in range(aantal):
                    d2, k2, side2, side_d2 = raycast(p_speler_x, p_speler_y, stralen[j- aantal+ i], r_speler)
                    muren.append((j - aantal + i, d2, k2, side2, side_d2))
            muren.append((j, d, k, side, side_d))
            vorige_straal = straal
        elif j > BREEDTE-aantal:
            d, k, side, side_d = raycast(p_speler_x, p_speler_y, straal, r_speler)
            muren.append((j, d, k, side, side_d))
    return muren"""