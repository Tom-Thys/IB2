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





def raycast(p_speler_x, p_speler_y, r_straal_xy):

    kolom, rij = math.floor(p_speler_x), math.floor(p_speler_y)
    delta_x = r_straal_xy[:, 0]
    delta_y = r_straal_xy[:, 1]
    mask_x = r_straal_xy[:, 0] != 0
    mask_y = r_straal_xy[:, 1] != 0
    delta_x[mask_x] = np.abs(1 / delta_x[mask_x])
    delta_x[~mask_x] = np.inf
    delta_y[mask_y] = np.abs(1 / delta_y[mask_y])
    delta_y[~mask_y] = np.inf

    step_x = np.where(r_straal_xy[:, 0] < 0, -1, 1)
    step_y = np.where(r_straal_xy[:, 1] < 0, -1, 1)

    side_x = np.where(r_straal_xy[:, 0] < 0, (p_speler_x - kolom) * delta_x, (kolom + 1.0 - p_speler_x) * delta_x)
    side_y = np.where(r_straal_xy[:, 1] < 0, (p_speler_y - rij) * delta_y, (rij + 1.0 - p_speler_y) * delta_y)

    while True:
        side_condition = side_x < side_y
        side_x = np.where(side_condition, side_x + delta_x, side_x)
        kolom = np.where(side_condition, kolom + step_x, kolom)
        side_y = np.where(~side_condition, side_y + delta_y, side_y)
        rij = np.where(~side_condition, rij + step_y, rij)

        side = np.where(side_condition, 0, 1)

        valid_indices = np.logical_and.reduce((0 <= kolom.any() < len(world_map[0]) and 0 <= rij.any() < len(world_map)))
        if np.any(valid_indices) and np.any(world_map[rij[valid_indices], kolom[valid_indices]] != 0):
            d_muur_eucl = np.where(side == 0, (kolom - p_speler_x + (1 - step_x) / 2) / r_straal_xy[valid_indices, 0],
                                   (rij - p_speler_y + (1 - step_y) / 2) / r_straal_xy[valid_indices, 1])

            k_muur = np.array([list(kleuren[x][:]) for x in world_map[rij[valid_indices], kolom[valid_indices]]])
            k_muur[:, :3] = np.maximum(0, k_muur[:, :3] - 50)
            k_muur = k_muur.astype(int)
            d_muur_a = d_muur_eucl.reshape(800, 1)
            k_muur_a = np.array([sdl2.ext.Color(*row) for row in k_muur], dtype=sdl2.ext.Color)
            return d_muur_a, k_muur_a

        if np.all(~valid_indices):
            # Ray doesn't hit anything
            break

def numpy_raycaster(p_x, p_y, r_stralen,world_map, breedte):
    y_dim, x_dim = np.shape(world_map)
    l = max(20, (x_dim**2 + y_dim**2)**(1/2))

    kleuren = np.zeros(breedte)
    d_muur = np.zeros(breedte)
    d_muur_vlak = np.zeros(breedte)

    x = np.full(breedte,math.floor(p_x))
    y = np.full(breedte,math.floor(p_y))

    delta_x = 1 / np.abs(r_stralen[:, 0])
    delta_y = 1 / np.abs(r_stralen[:, 1])

    richting_x = np.where(r_stralen[:, 0] >= 0, 1, -1)
    richting_y = np.where(r_stralen[:, 1] <= 0, 1, -1)

    d_v = np.where(r_stralen[:, 0] >= 0, (1 - (p_x - math.floor(p_x))),p_x - math.floor(p_x)) * delta_x
    d_h = np.where(r_stralen[:, 1] >= 0, (1 - (p_y - math.floor(p_y))),p_y - math.floor(p_y)) * delta_y

    while True:
        break_1 = d_v < l
        break_2 = d_h < l
        break_3 = kleuren == 0
        break_cond = break_1*break_2*break_3

        dist_cond = d_v < d_h
        least_distance = np.where(dist_cond, d_v, d_h)
        x = p_x + least_distance * r_stralen[:, 0]
        y = p_x + least_distance * r_stralen[:, 0]

        x = np.round(x, 5)
        y = np.round(y, 5)

        x_f = x.astype(int)
        y_f = y.astype(int)

        x_f = np.where(r_stralen[:, 0] >= 0, x_f, x_f - 1)
        y_f = np.where(r_stralen[:, 1] >= 0, y_f, y_f - 1)

        x_f = np.where(x_f < 0, x_f + x_dim, x_f)
        x_f = np.where(x_f >= x_dim, x_f - x_dim, x_f)
        y_f = np.where(y_f < 0, y_f + y_dim, y_f)
        y_f = np.where(y_f >= y_dim, y_f - y_dim, y_f)

        hit_wall = world_map[y_f, x_f] != 0
        kleuren += np.where(hit_wall, world_map[y_f, x_f], 0)
        d_muur += np.where(break_cond*hit_wall, least_distance, 0)
        d_muur_vlak += np.where(hit_wall*break_cond*dist_cond, y, 0)
        d_muur_vlak += np.where(hit_wall*break_cond*~dist_cond, x, 0)

        #incrementeren
        d_v += dist_cond * delta_x
        d_h += (~dist_cond) * delta_y

        if kleuren.any() != 0:
            print(kleuren)




        if break_cond.all() == 0:
            return d_muur, d_muur_vlak, kleuren





























