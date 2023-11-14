import numpy as np
import sdl2.ext
import math
from IB2 import kleuren, HOOGTE, BREEDTE

"""ALLES RELATED AAN DRAWING OP HET SCHERM"""


def draw_nav(renderer, kleuren_textures, Map, speler, pad, sprites):
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
    mid_x, mid_y = speler.position
    width = 200
    height = 200
    midden = 100
    speler_grootte = 10
    afstand = 20
    y_dim, x_dim = Map.world_size

    hoek = 2 * math.pi - speler.hoek / math.pi * 180 - 48

    unit_d = (width / (2 * afstand))
    midden += unit_d/2

    start_x = 0
    start_y = 0
    x_min = speler.p_x - afstand
    y_min = speler.p_y - afstand
    x_max = speler.p_x + afstand
    y_max = speler.p_y + afstand
    if x_max > x_dim:
        width *= (x_dim - x_min) / (2 * afstand)
    if y_max > y_dim:
        h = height
        height *= (y_dim - y_min) / (2 * afstand)
        start_y = h * (1 - height / h)
    if x_min < 0:
        w = width
        width *= x_max / (2 * afstand)
        start_x = w * (1 - width / w)
    if y_min < 0:
        height *= y_max / (2 * afstand)

    renderer.copy(Map.png, srcrect=(x_min, y_min, 2 * afstand, 2 * afstand), dstrect=(start_x, start_y, width, height),
                  flip=2)
    for sprite in sprites:
        if x_min < sprite.x < x_max and y_min < sprite.y < y_max:
            pos_x = (sprite.x - speler.position[0]) / afstand * midden + midden - sprite.map_grootte / 2
            pos_y = (-sprite.y + speler.position[1]) / afstand * midden + midden - sprite.map_grootte / 2
            renderer.copy(sprite.map_png, dstrect=(pos_x, pos_y, sprite.map_grootte, sprite.map_grootte))

    renderer.copy(speler.png,
                  dstrect=(midden - speler_grootte / 2, midden - speler_grootte / 2, speler_grootte, speler_grootte),
                  angle=hoek, flip=2)

    """for i in range(-afstand, afstand):
        for j in range(afstand, -afstand-1,-1):
            x = i + mid_x
            y = j + mid_y
            if x % 3 == 0 and y % 3 == 0 and i < afstand-2 and j < afstand - 2:
                if x < 0 or y < 0 or x >= Map.world_size[1] or y >= Map.world_size[0]:
                    # renderer.fill(((j + afstand) * unit_d, (i + afstand) * unit_d, 3 * unit_d, 3 * unit_d), kleuren[6])
                    renderer.copy(kleuren_textures[6],
                                  srcrect=(0, 0, 1, 1),
                                  dstrect=((j + afstand) * unit_d, (i + afstand) * unit_d, 3 * unit_d, 3 * unit_d))
                else:
                    #renderer.fill(((j + afstand) * unit_d, (i + afstand) * unit_d, 3*unit_d, 3*unit_d),
                                  #kleuren[Map.world_map[y, x]])
                    renderer.copy(kleuren_textures[Map.world_map[y, x]],
                                  srcrect=(0, 0, 1, 1),
                                  dstrect=((j + afstand) * unit_d, (i + afstand) * unit_d, 3*unit_d, 3*unit_d))
            elif i < -afstand+3 or j < -afstand+3 or i > afstand-3 or j > afstand-3:
                if x < 0 or y < 0 or x >= Map.world_size[1] or y >= Map.world_size[0]:
                    #renderer.fill(((j + afstand) * unit_d, (i + afstand) * unit_d, unit_d, unit_d), kleuren[6])
                    renderer.copy(kleuren_textures[6],
                                  srcrect=(0, 0, 1, 1),
                                  dstrect=((j + afstand) * unit_d, (i + afstand) * unit_d, unit_d, unit_d))
                else:
                    #renderer.fill(((j + afstand) * unit_d, (i + afstand) * unit_d, unit_d, unit_d),
                                  #kleuren[Map.world_map[y, x]])
                    renderer.copy(kleuren_textures[Map.world_map[y, x]],
                                  srcrect= (0, 0, 1, 1),
                                  dstrect=((j + afstand) * unit_d, (i + afstand) * unit_d, unit_d, unit_d))
            if i == 0 and j == 0:
                #renderer.fill(((i + afstand) * unit_d, (j + afstand) * unit_d, unit_d, unit_d), kleuren[9])
                renderer.copy(kleuren_textures[9],
                              srcrect=(0, 0, 1, 1),
                              dstrect=((i + afstand) * unit_d, (j + afstand) * unit_d, unit_d, unit_d))"""

    packet = (x_min, x_max, y_min, y_max, midden, afstand, unit_d)

    draw_path(renderer, kleuren_textures, pad, speler, packet)

    # renderer.fill(((speler.p_x-0.25)*unit_d,(speler.p_y-0.25)*unit_d,unit_d/2,unit_d/2),kleuren[9])
    # for sprite in sprites:
    # renderer.copy(sprite.image, dstrect=(int(sprite.x), int(sprite.y), sprite.image.size[0], sprite.image.size[1]))


def render_kolom(renderer, window, kolom, d_muur, k_muur):
    d_muur = d_muur * 2
    renderer.draw_line((kolom, window.size[1] / 2 - window.size[1] * (1 / d_muur), kolom,
                        window.size[1] / 2 + [1] * (1 / d_muur)), kleuren[k_muur])
    return


def renderen(renderer, d, d_v, k, soort_muren, muren_info):
    d = 1 / d
    for kolom in range(BREEDTE):
        d_muur = d[kolom]
        unit_d = d_v[kolom]
        k_muur = k[kolom]
        if k_muur >= 0:
            wall_texture = soort_muren[k_muur]
            breedte, hoogte = muren_info[k_muur]
            rij = unit_d * breedte
            scherm_y = HOOGTE / 2
            renderer.copy(wall_texture, srcrect=(rij, 0, 1, hoogte),
                          dstrect=(kolom, scherm_y - d_muur * hoogte / 2, 1, d_muur * hoogte))


def z_renderen(renderer, d, d_v, k, soort_muren, muren_info, deuren):
    return
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


def render_floor_and_sky(renderer, kleuren_textures):
    """# SKY in blauw
    renderer.fill((0, 0, BREEDTE, HOOGTE // 2), kleuren[9])
    # Floor in grijs
    renderer.fill((0, HOOGTE // 2, BREEDTE, HOOGTE // 2), kleuren[6])
    # SKY in blauw"""
    renderer.copy(kleuren_textures[9],
                  srcrect=(0, 0, 1, 1),
                  dstrect=(0, 0, BREEDTE, HOOGTE // 2))
    # Floor in grijs
    renderer.copy(kleuren_textures[6],
                  srcrect=(0, 0, 1, 1),
                  dstrect=(0, HOOGTE // 2, BREEDTE, HOOGTE // 2))


def draw_path(renderer, kleuren_textures, path, speler, packet):
    if path == None:
        pass
        # Moeten we hier niet kijken dat er dan een nieuwe locatie wordt gevonden? Als de eindlocatie in ingesloten ruimte zit
    else:
        x_min, x_max, y_min, y_max, midden, afstand, unit_d = packet
        for item, locatie in enumerate(path):
            if x_min < locatie[0] < x_max and y_min < locatie[1] < y_max:
                x = (locatie[0] - speler.position[0]) / afstand * midden + midden - unit_d / (2*1.5)
                y = (-locatie[1] + speler.position[1]) / afstand * midden + midden - unit_d - unit_d / (2*1.5)
            else:
                continue
            """x = (locatie[1] - mid_y + afstand)*unit_d
            y = (locatie[0] - mid_x + afstand)*unit_d
            if x < 0 or y < 0 or x > 2 * afstand or y > 2 * afstand:
                continue
            if locatie[0] == 0:
                pass"""
            if item == 0:
                # renderer.fill(((x * unit_d), (y * unit_d), unit_d, unit_d), kleuren[1])
                renderer.copy(kleuren_textures[1],
                              srcrect=(0, 0, 1, 1),
                              dstrect=(x, y, unit_d, unit_d/1.5))
            elif item == len(path) - 1:
                # renderer.fill(((x * unit_d + unit_d / 4), (y * unit_d + unit_d / 4),
                # unit_d / 1.5, unit_d / 1.5), kleuren[2])
                renderer.copy(kleuren_textures[2],
                              srcrect=(0, 0, 1, 1),
                              dstrect=(x, y, unit_d / 1.5, unit_d / 1.5))
            else:
                # renderer.fill(((x * unit_d + unit_d / 4), (y * unit_d + unit_d / 4),
                # unit_d / 1.5, unit_d / 1.5), kleuren[7])
                renderer.copy(kleuren_textures[7],
                              srcrect=(0, 0, 1, 1),
                              dstrect=(x, y, unit_d / 1.5, unit_d / 1.5))
