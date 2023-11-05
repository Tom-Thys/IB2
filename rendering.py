import numpy as np
import sdl2.ext
from IB2 import kleuren, HOOGTE, BREEDTE

"""ALLES RELATED AAN DRAWING OP HET SCHERM"""


def draw_nav(renderer, Map, speler, pad, sprites):
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
    height = 150
    afstand = 20

    unit_d = (width / (2 * afstand))
    for i in range(-afstand, afstand):
        for j in range(afstand, -afstand-1,-1):
            x = i + mid_x
            y = j + mid_y
            if x % 3 == 0 and y % 3 == 0 and i < afstand-2 and j < afstand - 2:
                if x < 0 or y < 0 or x >= Map.world_size[1] or y >= Map.world_size[0]:
                    renderer.fill(((j + afstand) * unit_d, (i + afstand) * unit_d, 3 * unit_d, 3 * unit_d), kleuren[6])
                else:
                    renderer.fill(((j + afstand) * unit_d, (i + afstand) * unit_d, 3*unit_d, 3*unit_d),
                                  kleuren[Map.world_map[y, x]])
            elif i < -afstand+3 or j < -afstand+3 or i > afstand-3 or j > afstand-3:
                if x < 0 or y < 0 or x >= Map.world_size[1] or y >= Map.world_size[0]:
                    renderer.fill(((j + afstand) * unit_d, (i + afstand) * unit_d, unit_d, unit_d), kleuren[6])
                else:
                    renderer.fill(((j + afstand) * unit_d, (i + afstand) * unit_d, unit_d, unit_d),
                                  kleuren[Map.world_map[y, x]])
            if i == 0 and j == 0:
                renderer.fill(((i + afstand) * unit_d, (j + afstand) * unit_d, unit_d, unit_d), kleuren[9])

    draw_path(renderer, pad, mid_x, mid_y, afstand, unit_d)

    # renderer.fill(((speler.p_x-0.25)*unit_d,(speler.p_y-0.25)*unit_d,unit_d/2,unit_d/2),kleuren[9])
    # for sprite in sprites:
    # renderer.copy(sprite.image, dstrect=(int(sprite.x), int(sprite.y), sprite.image.size[0], sprite.image.size[1]))


def render_kolom(renderer, window, kolom, d_muur, k_muur):
    d_muur = d_muur * 2
    renderer.draw_line((kolom, window.size[1] / 2 - window.size[1] * (1 / d_muur), kolom,
                        window.size[1] / 2 + [1] * (1 / d_muur)), kleuren[k_muur])
    return


def renderen(renderer, d, d_v, k, soort_muren, muren_info):
    for kolom in range(BREEDTE):
        d_muur = d[kolom]
        unit_d = d_v[kolom]
        k_muur = (k[kolom]-1)
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
    renderer.fill((0, 0, BREEDTE, HOOGTE // 2), kleuren[9])
    # Floor in grijs
    renderer.fill((0, HOOGTE // 2, BREEDTE, HOOGTE // 2), kleuren[6])


def draw_path(renderer, path, mid_x, mid_y, afstand, unit_d):
    if path == None:
        pass
        #Moeten we hier niet kijken dat er dan een nieuwe locatie wordt gevonden? Als de eindlocatie in ingesloten ruimte zit
    else:
        for item,locatie in enumerate(path):
            x = locatie[1] - mid_y + afstand
            y = locatie[0] - mid_x + afstand
            if x < 0 or y < 0 or x > 2*afstand or y > 2*afstand:
                continue
            if locatie[0] == 0:
                pass
            if item == 0:
                renderer.fill(((x * unit_d), (y * unit_d), unit_d, unit_d), kleuren[1])
            elif item == len(path) - 1:
                renderer.fill(((x * unit_d + unit_d / 4), (y * unit_d + unit_d / 4),
                               unit_d / 1.5, unit_d / 1.5), kleuren[2])
            else:
                renderer.fill(((x * unit_d + unit_d / 4), (y * unit_d + unit_d / 4),
                               unit_d / 1.5, unit_d / 1.5), kleuren[7])
