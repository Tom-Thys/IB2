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
    y_dim, x_dim = np.shape(world_map)
    l = max(20, (x_dim ** 2 + y_dim ** 2) ** (1 / 2))

    kleuren = np.zeros(breedte)
    d_muur = np.zeros(breedte)
    d_muur_vlak = np.zeros(breedte)

    delta_x = 1 / np.abs(r_stralen[:, 0])
    delta_y = 1 / np.abs(r_stralen[:, 1])

    richting_x = np.where(r_stralen[:, 0] >= 0, 0, -1)
    richting_y = np.where(r_stralen[:, 1] >= 0, 0, -1)

    d_v = np.where(r_stralen[:, 0] >= 0, (1 - (p_x - math.floor(p_x))) * delta_x, (p_x - math.floor(p_x)) * delta_x)
    d_h = np.where(r_stralen[:, 1] >= 0, (1 - (p_y - math.floor(p_y))) * delta_y, (p_y - math.floor(p_y)) * delta_y)

    while True:
        muren_check = np.full(breedte, False)

        dist_cond = d_v < d_h
        least_distance = np.where(dist_cond, d_v, d_h)

        break_1 = d_v < l
        break_2 = d_h < l
        break_3 = kleuren == 0
        break_cond = (dist_cond * break_1 + ~dist_cond * break_2) * break_3

        if np.all(~break_cond):
            return d_muur, d_muur_vlak, kleuren.astype(int)

        x = np.round(p_x + least_distance * r_stralen[:, 0], 5)
        y = np.round(p_y + least_distance * r_stralen[:, 1], 5)

        x_f = np.where(dist_cond, (x + richting_x).astype(int), x.astype(int))
        y_f = np.where(~dist_cond, (y + richting_y).astype(int), y.astype(int))

        valid = np.logical_and.reduce((0 <= x_f, x_f < len(world_map[0]), 0 <= y_f, y_f < len(world_map)))
        valid_indices = valid * break_cond
        muren_check[valid_indices] = np.where(world_map[y_f[valid_indices], x_f[valid_indices]], True, False)

        kleuren[muren_check] += world_map[y_f[muren_check], x_f[muren_check]]
        d_muur += np.where(break_cond * muren_check, least_distance*(r_stralen[:,0]*r_speler[0]+r_stralen[:,1]*r_speler[1]), 0)
        d_muur_vlak += np.where(muren_check * break_cond * dist_cond, y, 0)
        d_muur_vlak += np.where(muren_check * break_cond * ~dist_cond, x, 0)

        # incrementeren
        d_v += dist_cond * delta_x
        d_h += (~dist_cond) * delta_y

