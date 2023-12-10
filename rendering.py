import numpy as np
import sdl2.ext
import math
from IB2 import kleuren, HOOGTE, BREEDTE

"""ALLES RELATED AAN DRAWING OP HET SCHERM"""


def draw_nav(renderer, kleuren_textures, arrow, Map, speler, pad, sprites):
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
        if x_min < sprite.x < x_max- sprite.map_grootte / 2 and y_min < sprite.y < y_max- sprite.map_grootte / 2:
            if sprite.x == speler.p_x and sprite.y == speler.p_y: continue;
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
    draw_arrow(renderer, arrow, speler, pad)

    # renderer.fill(((speler.p_x-0.25)*unit_d,(speler.p_y-0.25)*unit_d,unit_d/2,unit_d/2),kleuren[9])
    # for sprite in sprites:
    # renderer.copy(sprite.image, dstrect=(int(sprite.x), int(sprite.y), sprite.image.size[0], sprite.image.size[1]))


def render_kolom(renderer, window, kolom, d_muur, k_muur):
    d_muur = d_muur * 2
    renderer.draw_line((kolom, window.size[1] / 2 - window.size[1] * (1 / d_muur), kolom,
                        window.size[1] / 2 + [1] * (1 / d_muur)), kleuren[k_muur])
    return


def renderen(renderer, d, d_v, k, muren_info, angle):
    d = 1 / d
    d_v = d_v % 1
    k -= 1
    scherm_y = HOOGTE / 2
    if angle == 0:
        for kolom, (d_muur, unit_d, k_muur) in enumerate(zip(d, d_v, k)):
            if k_muur >= 0:
                wall_texture, breedte, hoogte = muren_info[k_muur]
                hoogte *= d_muur
                renderer.copy(wall_texture, srcrect=(breedte * unit_d, 0, 1, 890),
                        dstrect=(kolom, scherm_y - hoogte / 2, 1, hoogte))
            elif k_muur < 0:
                wall_texture, breedte, hoogte = muren_info[0]
                hoogte *= d_muur
                renderer.copy(wall_texture, srcrect=(breedte * unit_d, 0, 1, 890),
                              dstrect=(kolom, scherm_y - hoogte / 2, 1, hoogte))
    else:
        for kolom, (d_muur, unit_d, k_muur) in enumerate(zip(d, d_v, k)):
            if k_muur >= 0:
                wall_texture, breedte, hoogte = muren_info[k_muur]
                hoogte *= d_muur
                hoek = math.atan2(hoogte / 2, kolom - BREEDTE / 2) + angle / 180 * math.pi
                afstand = ((kolom - BREEDTE / 2) ** 2 + (hoogte / 2) ** 2) ** (1 / 2)
                y = scherm_y - math.sin(hoek) * afstand
                x = math.cos(hoek) * afstand + BREEDTE / 2
                renderer.copy(wall_texture, srcrect=(breedte * unit_d, 0, 1, 890),
                              dstrect=(x, y, 1, hoogte), angle=angle)





def z_renderen(renderer, d, d_v, k, muren_info):
    scherm_y = HOOGTE / 2
    for kolom, (d_muur, unit_d, kleur) in enumerate(zip(d, d_v, k)):
        if kleur == 0:
            continue
        wall_texture, breedte, hoogte = muren_info[kleur]
        renderer.copy(wall_texture, srcrect=(unit_d * breedte, 0, 1, hoogte),
                      dstrect=(kolom, scherm_y - d_muur * hoogte / 2, 1, d_muur * hoogte))


def renderText(font, renderer, text, x, y):
    text = sdl2.ext.renderer.Texture(renderer, font.render_text(text))
    x_s, y_s = text.size
    renderer.copy(text, dstrect=(int((x - x_s) / 2), y, x_s, y_s))
def render_police(logo,renderer):
    renderer.copy(logo, dstrect=(405, 56, 180, 180))

def render_balkje(Tijd,Time_bar,renderer):
    index = 10 - (round(Tijd/6))
    if index >= 10:
        renderer.copy(Time_bar[10], dstrect=(10, 192, 180, 80))
        return False
    elif index < 0:
        return True
    else:
        renderer.copy(Time_bar[index], dstrect=(10, 192, 180, 80))
        return False


def render_pakjes_aantal(pakjes_aantal,renderer):
    font_2 = sdl2.ext.FontTTF(font='counter.ttf', size=60, color=kleuren[5])
    renderText(font_2, renderer, str(pakjes_aantal), 1910, 10)

def render_floor_and_sky(renderer, kleuren_textures):
    """Rendert achtergrond top half blauw bottom grijs"""
    """# SKY in blauw
    renderer.fill((0, 0, BREEDTE, HOOGTE // 2), kleuren[9])
    # Floor in grijs
    renderer.fill((0, HOOGTE // 2, BREEDTE, HOOGTE // 2), kleuren[6])
    # SKY in blauw"""

    renderer.copy(kleuren_textures[9],
                  dstrect=(0, 0, BREEDTE, HOOGTE // 2))
    # Floor in grijs
    renderer.copy(kleuren_textures[6],
                  dstrect=(0, HOOGTE // 2, BREEDTE, HOOGTE // 2))


def draw_path(renderer, kleuren_textures, path, speler, packet):
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


def render_map(renderer,kleuren_textures, pngs_mappen, map_settings,speler,pad, sprites):

    map_png, gps_grote_map = pngs_mappen
    map_positie, afstand_map, worldshape = map_settings

    linker_bovenhoek_x = map_positie[0] - afstand_map if map_positie[0] - afstand_map >= 0 else 0
    linker_bovenhoek_y = map_positie[1] - afstand_map if map_positie[1] - afstand_map >= 0 else 0

    # speler_grootte = int((-17/190)*(afstand_map-10)+20)
    # speler_png_x = (BREEDTE//2)-2*(map_positie[0]-speler.position[0])+speler_grootte//2
    # speler_png_y = (HOOGTE//2)+(map_positie[1]-speler.position[1])-speler_grootte

    if afstand_map + map_positie[0] > worldshape[1]:
        linker_bovenhoek_x = worldshape[1] - 2 * afstand_map
    if afstand_map + map_positie[1] > worldshape[0]:
        linker_bovenhoek_y = worldshape[0] - 2 * afstand_map

    renderer.copy(gps_grote_map,
                  srcrect=(0, 0, gps_grote_map.size[0], gps_grote_map.size[1]),
                  dstrect=(80, 70, BREEDTE - 120, HOOGTE - 140),
                  flip=2)
    renderer.copy(map_png,
                  srcrect=(linker_bovenhoek_x, linker_bovenhoek_y, 2 * afstand_map, 2 * afstand_map),
                  dstrect=(160, 112, BREEDTE - 300, HOOGTE - 222),
                  flip=2)
    #print(afstand_map)
    #speler_grootte = int((-17/190)*((afstand_map/1.2)-10)+20)
    speler_grootte = 1/math.sinh((1/200)*afstand_map) + 5
    node_grootte = 1/math.sinh((1/200)*afstand_map) + 1
    for item, locatie in enumerate(pad):
        if linker_bovenhoek_x < locatie[0] < linker_bovenhoek_x+2*afstand_map and linker_bovenhoek_y < locatie[1] < linker_bovenhoek_y+2*afstand_map:
            locatie_x = int(160 + (locatie[0]-linker_bovenhoek_x) / (2*afstand_map) * (BREEDTE-300))
            locatie_y = int(112 + (-locatie[1] + linker_bovenhoek_y+2*afstand_map) / (2 * afstand_map) * (HOOGTE-222)) - node_grootte
            if item == 0:
                renderer.copy(kleuren_textures[1],
                              srcrect=(0, 0, 1, 1),
                              dstrect=(locatie_x + node_grootte//2, locatie_y, node_grootte, node_grootte))
            elif item == len(pad)-1:
                renderer.copy(kleuren_textures[2],
                              srcrect=(0, 0, 1, 1),
                              dstrect=(locatie_x + node_grootte//2, locatie_y, node_grootte, node_grootte))
            else:
                renderer.copy(kleuren_textures[7],
                              srcrect=(0, 0, 1, 1),
                              dstrect=(locatie_x + node_grootte//2, locatie_y, node_grootte, node_grootte/1.2))
        else:
            continue
    if linker_bovenhoek_x < speler.p_x < linker_bovenhoek_x+2*afstand_map and linker_bovenhoek_y < speler.p_y < linker_bovenhoek_y+2*afstand_map:
        speler_png_x = int(160 + (speler.position[0] - linker_bovenhoek_x) / (2*afstand_map) * (BREEDTE-300))
        speler_png_y = int(112 + (-speler.position[1] + linker_bovenhoek_y+2*afstand_map) / (2 * afstand_map) * (HOOGTE-222))
        renderer.copy(speler.png,
                    dstrect=(speler_png_x-speler_grootte//2, speler_png_y-speler_grootte//2, speler_grootte, speler_grootte),
                    angle=2 * math.pi - speler.hoek / math.pi * 180 + 40, flip=0)

def auto_info_renderen(renderer, font, pngs, car):
    hoogte_dashboard = 150
    start_dashboard = 200
    renderer.copy(pngs[0], dstrect=(start_dashboard, HOOGTE - hoogte_dashboard, BREEDTE-2*start_dashboard, hoogte_dashboard))
    renderText(font, renderer, car.versnellingen[car.versnelling], 1400, HOOGTE - 100)
    snelheid = str(abs(round(car.speed * 400)))
    renderText(font, renderer, snelheid, 600, HOOGTE - 100)
    renderText(font, renderer, str(car.dozen), 50, HOOGTE - 100)
    renderer.copy(pngs[2], dstrect=(50,HOOGTE - 105, 60, 60))

    x_pos = (BREEDTE - 250) // 2
    y_pos = HOOGTE - 230
    hoek = -car.stuurhoek * 180 / math.pi * 100 * car.speed
    renderer.copy(pngs[1], dstrect=(x_pos, y_pos, 250, 250), angle=hoek)
    car.stuurhoek = 0



def draw_bestemming(renderer, bestemming, speler, texture):
    kolommen = []
    afstanden = 0
    coords = [(0, 0), (0, 1), (1, 1), (1, 0)]
    linear_solve_b = np.array([speler.r_speler[0] + speler.r_camera[0] / 1000, speler.r_speler[1] + speler.r_camera[1] / 1000])
    for coord in coords:
        rx = bestemming[0] + coord[0] - speler.p_x
        ry = bestemming[1] + coord[1] - speler.p_y
        hoek = math.atan2(ry, rx) % (2 * math.pi)
        hoek_verschil = abs(speler.hoek - hoek)
        if speler.hoek <= 1 and hoek >= math.pi * 7 / 4:
            hoek_verschil = math.pi * 2 - hoek_verschil

        if speler.hoek >= math.pi * 7 / 4 and hoek <= 1:
            hoek_verschil = math.pi * 2 - hoek_verschil

        if hoek_verschil >= (math.pi / 3.7):
            continue

        linear_solve_a = np.array([[rx,speler.r_camera[0]/500],[ry,speler.r_camera[1]/500]])
        scherm_kolom = np.linalg.solve(linear_solve_a, linear_solve_b)[1]  + 500
        if 0 >= scherm_kolom > BREEDTE:
            #norm = (rx ** 2 + ry ** 2) ** (1 / 2)
            afstand = rx * speler.r_speler + ry * speler.r_speler
            kolommen.append(scherm_kolom)
            afstanden = max(afstanden, afstand)
        if len(kolommen) > 1:
            k1 = min(kolommen)
            k2 = max(kolommen)
            hoogte = HOOGTE/2 + 445 * afstanden
            renderer.copy(texture, dstrect=(k1, 0, k2-k1, hoogte))





def draw_arrow(renderer, arrow, speler, pad):
    if len(pad) > 6:
        pos = pad[-6]
    elif pad != []:
        pos = pad[0]
    else:
        return
    hoek = (speler.hoek - math.atan2(speler.p_y-pos[1],speler.p_x-pos[0])+math.pi/2) / math.pi * 180
    renderer.copy(arrow, dstrect=(100,HOOGTE-100,100,100),angle=hoek)
