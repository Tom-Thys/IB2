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
            d = []
            for i, dist in enumerate(d_muur):
                d.append(fish_eye_(dist, r_speler, r_stralen[i]))
            return d, d_muur_vlak, kleuren.astype(int)

        x = np.round(p_x + least_distance * r_stralen[:, 0], 5)
        y = np.round(p_y + least_distance * r_stralen[:, 1], 5)

        x_f = np.where(dist_cond, (x + richting_x).astype(int), x.astype(int))
        y_f = np.where(~dist_cond, (y + richting_y).astype(int), y.astype(int))

        valid = np.logical_and.reduce((0 <= x_f, x_f < len(world_map[0]), 0 <= y_f, y_f < len(world_map)))
        valid_indices = valid * break_cond
        muren_check[valid_indices] = np.where(world_map[y_f[valid_indices], x_f[valid_indices]], True, False)

        kleuren[muren_check] += world_map[y_f[muren_check], x_f[muren_check]]
        d_muur += np.where(break_cond * muren_check, least_distance, 0)
        d_muur_vlak += np.where(muren_check * break_cond * dist_cond, y, 0)
        d_muur_vlak += np.where(muren_check * break_cond * ~dist_cond, x, 0)

        # incrementeren
        d_v += dist_cond * delta_x
        d_h += (~dist_cond) * delta_y


def raycast_n(p_speler_x, p_speler_y, r_straal_xy, r_speler, breedte, world_map):
    kleuren = np.zeros(breedte)
    d_muur = np.zeros(breedte)
    d_v = np.zeros(breedte)
    muren_check = np.zeros(breedte)

    kolom, rij = math.floor(p_speler_x), math.floor(p_speler_y)
    delta_x = r_straal_xy[:, 0]
    delta_y = r_straal_xy[:, 1]

    delta_x = 1 / np.abs(delta_x[:])
    delta_y = 1 / np.abs(delta_y[:])

    """mask_x = r_straal_xy[:, 0] != 0
    mask_y = r_straal_xy[:, 1] != 0
    delta_x[mask_x] = np.abs(1 / delta_x[mask_x])
    delta_x[~mask_x] = np.inf
    delta_y[mask_y] = np.abs(1 / delta_y[mask_y])
    delta_y[~mask_y] = np.inf"""

    step_x = np.where(r_straal_xy[:, 0] < 0, -1, 1)
    step_y = np.where(r_straal_xy[:, 1] < 0, -1, 1)

    side_x = np.where(r_straal_xy[:, 0] < 0, (p_speler_x - kolom) * delta_x, (kolom + 1.0 - p_speler_x) * delta_x)
    side_y = np.where(r_straal_xy[:, 1] < 0, (p_speler_y - rij) * delta_y, (rij + 1.0 - p_speler_y) * delta_y)

    while True:
        muren_check *= 0
        condition = kleuren == 0
        side_condition = side_x < side_y
        # side_x += delta_x*side_condition
        side_x = np.where(side_condition, side_x + delta_x, side_x)
        kolom = np.where(side_condition, kolom + step_x, kolom)
        # side_y += delta_y*~side_condition
        side_y = np.where(~side_condition, side_y + delta_y, side_y)
        rij = np.where(~side_condition, rij + step_y, rij)

        valid_indices = (np.logical_and.reduce(
            (0 <= kolom, kolom < len(world_map[0]), 0 <= rij, rij < len(world_map)))) * condition

        muren_check[valid_indices] = np.where(world_map[rij[valid_indices], kolom[valid_indices]] == 0, 0, 1)
        muren_check = muren_check.astype(int)
        if np.any(muren_check):
            d_1 = np.where((~side_condition) * muren_check, side_y,
                           0)  # (kolom - p_speler_x + (1 - step_x)/ 2) / r_straal_xy[muren_check, 0],0.0)
            d_v1 = np.where((~side_condition) * muren_check, (kolom ** 2 - side_y ** 2) ** (1 / 2), 0)
            d_2 = np.where(side_condition * muren_check, side_x,
                           0)  # (rij - p_speler_y + (1 - step_y) / 2) / r_straal_xy[muren_check, 1], 0.0)
            d_v2 = np.where((side_condition) * muren_check, (rij ** 2 - side_x ** 2) ** (1 / 2), 0)
            kleuren[valid_indices] = world_map[rij[valid_indices], kolom[valid_indices]]
            d_muur += d_2 + d_1
            d_v += d_v2 + d_v1
            # print(d_1,d_2,d_muur)

        """
        k_muur = np.array([list(kleuren[x][:]) for x in world_map[rij[valid_indices], kolom[valid_indices]]])
        k_muur[:, :3] = np.maximum(0, k_muur[:, :3] - 50)
        k_muur = k_muur.astype(int)
        d_muur_a = d_muur_eucl.reshape(800, 1)
        k_muur_a = np.array([sdl2.ext.Color(*row) for row in k_muur], dtype=sdl2.ext.Color)
        return d_muur_a, k_muur_a"""

        if np.all(~condition):
            # Ray doesn't hit anything
            d = []
            for i, dist in enumerate(d_muur):
                d.append(fish_eye_(dist, r_speler, r_straal_xy[i]))
            return d, d_v, kleuren.astype(int)

        # If no wall is hit, return the default color and a long distance
    return d_muur, d_v, kleuren
