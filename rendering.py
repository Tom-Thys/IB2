import numpy as np
from IB2 import kleuren
import math

def draw_nav(renderer, map, plattegrond, speler, sprites, b_w=3):
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
    if x_dim < 2 * b_w:
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
            """renderer.copy(plattegrond, srcrect=(0, 0, breedte, h_max * blok_d),
                          dstrect=(0, 0, width, height - scherm_h))"""
        elif speler.p_y > y_dim - b_h:
            pass
        else:
            pass
    else:
        b_h = b_w * height / width

        pass

    x = width
    y = x/breedte*hoogte
    renderer.copy(plattegrond, srcrect=(0, 0, breedte, hoogte),
                  dstrect=(0, 0, x, y))
    unit_d = x/x_dim
    renderer.fill(((speler.p_x-0.25)*unit_d,(speler.p_y-0.25)*unit_d,unit_d/2,unit_d/2),kleuren[9])
    #for sprite in sprites:
       #renderer.copy(sprite.image, dstrect=(int(sprite.x), int(sprite.y), sprite.image.size[0], sprite.image.size[1]))
