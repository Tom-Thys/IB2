import numpy as np
import sdl2.ext
from IB2 import kleuren, HOOGTE, BREEDTE,world_map

"""ALLES RELATED AAN DRAWING OP HET SCHERM"""

def draw_nav(renderer, map, plattegrond, speler, sprites = [], b_w=3):
    """
    Rendert PNG van world map in linkerbovenhoek
    Speler is zichtbaar in het midden
    Sprites worden door een kleur aangegeven op de map
    Navigatie naar volgende doel wordt via een lijn aangegeven op de map
    :param sprites: Lijst met alle mogelijke sprites die te tonen zijn
    :param width: Geeft aan hoe breed de wereld map standaard is NOG VAST TE LEGGEN
    :param height: Geeft aan hoe hoog de wereld map standaard is NOG VAST TE LEGGEN
    :param b_w: Aantal blokken links en rechts van speler op map worden getoond
    """
    width = 200
    height = 150
    y_dim, x_dim = np.shape(map)
    breedte = plattegrond.size[0]
    hoogte = plattegrond.size[1]
    blok_d = breedte / x_dim  # = hoogte/y_dim
    unit_d = width / x_dim
    # Check welk type wereld getoond moet worden
    """if x_dim < 2 * b_w:
        b_h = x_dim * height / width
        print(b_h)
        if y_dim < 2 * b_h:
            renderer.copy(plattegrond, srcrect=(0, 0, breedte, hoogte),
                          dstrect=(0, 0, width, height))
            renderer.fill(((speler.p_x - 0.25) * unit_d, (speler.p_y - 1.25) * unit_d, unit_d / 2, unit_d / 2),
                          kleuren[9])
        elif speler.p_y < b_h:
            h_min = y_dim + speler.p_y - b_h
            scherm_h = (b_h - speler.p_y) / (2 * b_h)
            h_max = speler.p_y + b_h
            renderer.copy(plattegrond, srcrect=(0, h_min * blok_d, breedte, scherm_h*hoogte),
                          dstrect=(0, height - scherm_h*height, width, scherm_h*height))
            renderer.copy(plattegrond, srcrect=(0, 0, breedte, h_max * blok_d),
                          dstrect=(0, 0, width, height - scherm_h))
        elif speler.p_y > y_dim - b_h:
            pass
        else:
            pass
    else:
        b_h = b_w * height / width

        pass"""

    x = width
    y = x/breedte*hoogte
    renderer.copy(plattegrond, srcrect=(0, 0, breedte, hoogte),
                  dstrect=(0, 0, x, y))
    unit_d = x/x_dim
    renderer.fill(((speler.p_x-0.25)*unit_d,(speler.p_y-0.25)*unit_d,unit_d/2,unit_d/2),kleuren[9])
    #for sprite in sprites:
       #renderer.copy(sprite.image, dstrect=(int(sprite.x), int(sprite.y), sprite.image.size[0], sprite.image.size[1]))

def render_kolom(renderer, window, kolom, d_muur, k_muur):
    d_muur = d_muur * 2
    renderer.draw_line((kolom, window.size[1] / 2 - window.size[1] * (1 / d_muur), kolom,
                        window.size[1] / 2 + [1] * (1 / d_muur)), kleuren[k_muur])
    return

def renderen(renderer, d, d_v, k, soort_muren, muren_info):
    for kolom in range(BREEDTE):
        d_muur = d[kolom]
        unit_d = d_v[kolom]
        k_muur = k[kolom]
        if k_muur >= 0:
            wall_texture = soort_muren[k_muur]
            breedte, hoogte = muren_info[k_muur]
            rij = unit_d * breedte
            # d_muur = 10 / d_muur
            scherm_y = HOOGTE / 2
            renderer.copy(wall_texture, srcrect=(rij, 0, 1, hoogte),
                          dstrect=(kolom, scherm_y - d_muur * hoogte / 2, 1, d_muur * hoogte))


def z_renderen(renderer, d, d_v, k, soort_muren, muren_info, deuren):
    for kolom in range(BREEDTE):
        if k[kolom] == 0: continue;
        deur = deuren[k[kolom]]
        d_muur = d[kolom]
        unit_d = d_v[kolom]
        if unit_d < deur.positie: continue;
        wall_texture = soort_muren[deur.kleur]
        breedte, hoogte = muren_info[deur.kleur]
        rij = (unit_d - deur.positie) % 1 * breedte
        # d_muur = 10 / d_muur
        scherm_y = HOOGTE / 2
        renderer.copy(wall_texture, srcrect=(rij, 0, 1, hoogte),
                      dstrect=(kolom, scherm_y - d_muur * hoogte / 2, 1, d_muur * hoogte))


def renderText(font, renderer, text, x, y, midden=0):
    text = sdl2.ext.renderer.Texture(renderer, font.render_text(text))
    if midden:
        renderer.copy(text, dstrect=(int((BREEDTE - text.size[0]) / 2), y, text.size[0], text.size[1]))
    else:
        renderer.copy(text, dstrect=(x, y, text.size[0], text.size[1]))


def render_floor_and_sky(renderer):
    # SKY in blauw
    renderer.fill((0, 0, BREEDTE, HOOGTE // 2), kleuren[8])
    # Floor in grijs
    renderer.fill((0, HOOGTE // 2, BREEDTE, HOOGTE // 2), kleuren[5])


def draw_path(renderer, path):
    if path == None:
        pass
    else:
        y_dim, x_dim = np.shape(world_map)
        unit_d = 200 / x_dim
        for item in range(len(path)):
            if item == 0:
                renderer.fill(((path[item][0] * unit_d), (path[item][1] * unit_d), unit_d, unit_d), kleuren[1])
            elif item == len(path) - 1:
                renderer.fill(((path[item][0] * unit_d + unit_d / 4), (path[item][1] * unit_d + unit_d / 4),
                               unit_d / 1.5, unit_d / 1.5), kleuren[2])
            else:
                renderer.fill(((path[item][0] * unit_d + unit_d / 4), (path[item][1] * unit_d + unit_d / 4),
                               unit_d / 1.5, unit_d / 1.5), kleuren[7])
