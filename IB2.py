import math
import random
import time
import numpy as np

import sdl2.ext

# Constanten
BREEDTE = 800
HOOGTE = 600

#
# Globale variabelen
changes = False
stralen = []

# positie van de speler
p_speler_x, p_speler_y = 3 + 1 / math.sqrt(2), 4 - 1 / math.sqrt(2)

# richting waarin de speler kijkt
r_speler_hoek = -math.pi / 4
r_speler = np.array([math.cos(r_speler_hoek), math.sin(r_speler_hoek)])
r_speler_x,r_speler_y = r_speler

# cameravlak
r_cameravlak = np.array([math.cos(r_speler_hoek - math.pi / 2), math.sin(r_speler_hoek - math.pi / 2)])
r_cameravlak_x, r_cameravlak_y = r_cameravlak

# wordt op True gezet als het spel afgesloten moet worden
moet_afsluiten = False

# FOV (FOV slider implementeren of niet?)
d_camera = 1
# de "wereldkaart". Dit is een 2d matrix waarin elke cel een type van muur voorstelt
# Een 0 betekent dat op deze plaats in de game wereld geen muren aanwezig zijn
world_map = [[2, 2, 2, 2, 2, 2, 2],
             [2, 0, 0, 1, 1, 1, 2],
             [2, 0, 0, 0, 0, 1, 2],
             [2, 0, 0, 0, 0, 0, 2],
             [2, 0, 0, 0, 0, 0, 2],
             [2, 0, 0, 0, 0, 0, 2],
             [2, 2, 2, 2, 2, 2, 2]]

# Vooraf gedefinieerde kleuren
kleuren = [
    sdl2.ext.Color(0, 0, 0),  # 0 = Zwart
    sdl2.ext.Color(255, 0, 0),  # 1 = Rood
    sdl2.ext.Color(0, 255, 0),  # 2 = Groen
    sdl2.ext.Color(0, 0, 255),  # 3 = Blauw
    sdl2.ext.Color(64, 64, 64),  # 4 = Donker grijs
    sdl2.ext.Color(128, 128, 128),  # 5 = Grijs
    sdl2.ext.Color(192, 192, 192),  # 6 = Licht grijs
    sdl2.ext.Color(255, 255, 255),  # 7 = Wit
]


#
# Verwerkt alle input van het toetsenbord en de muis
#
# Argumenten:
# @delta       Tijd in milliseconden sinds de vorige oproep van deze functie
#
def verwerk_input(delta):
    global moet_afsluiten

    # Handelt alle input events af die zich voorgedaan hebben sinds de vorige
    # keer dat we de sdl2.ext.get_events() functie hebben opgeroepen
    events = sdl2.ext.get_events()
    for event in events:
        # Een SDL_QUIT event wordt afgeleverd als de gebruiker de applicatie
        # afsluit door bv op het kruisje te klikken
        if event.type == sdl2.SDL_QUIT:
            moet_afsluiten = True
            break
        # Een SDL_KEYDOWN event wordt afgeleverd wanneer de gebruiker een
        # toets op het toetsenbord indrukt.
        # Let op: als de gebruiker de toets blijft inhouden, dan zien we
        # maar 1 SDL_KEYDOWN en 1 SDL_KEYUP event.
        elif event.type == sdl2.SDL_KEYDOWN:
            key = event.key.keysym.sym
            if key == sdl2.SDLK_q:
                moet_afsluiten = True
            break
        # Analoog aan SDL_KEYDOWN. Dit event wordt afgeleverd wanneer de
        # gebruiker een muisknop indrukt
        elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
            button = event.button.button
            if button == sdl2.SDL_BUTTON_LEFT:
                # ...
                continue
        # Een SDL_MOUSEWHEEL event wordt afgeleverd wanneer de gebruiker
        # aan het muiswiel draait.
        elif event.type == sdl2.SDL_MOUSEWHEEL:
            if event.wheel.y > 0:
                # ...
                continue
        # Wordt afgeleverd als de gebruiker de muis heeft bewogen.
        # Aangezien we relative motion gebruiken zijn alle coordinaten
        # relatief tegenover de laatst gerapporteerde positie van de muis.
        elif event.type == sdl2.SDL_MOUSEMOTION:
            # Aangezien we in onze game maar 1 as hebben waarover de camera
            # kan roteren zijn we enkel geinteresseerd in bewegingen over de
            # X-as
            beweging = event.motion.xrel
            continue

    # Polling-gebaseerde input. Dit gebruiken we bij voorkeur om bv het ingedrukt
    # houden van toetsen zo accuraat mogelijk te detecteren
    key_states = sdl2.SDL_GetKeyboardState(None)

    # if key_states[sdl2.SDL_SCANCODE_UP] or key_states[sdl2.SDL_SCANCODE_W]:
    # beweeg vooruit...

    if key_states[sdl2.SDL_SCANCODE_ESCAPE]:
        moet_afsluiten = True

def draaien(hoek):
    """Geef hoek op in radialen, geeft r_straal en r_cameravlak terug"""
    global r_cameravlak, r_speler, stralen, changes
    draai_matrix = np.array([[math.cos(hoek), -math.sin(hoek)],
                             [math.sin(hoek), math.cos(hoek)]])
    r_speler = np.matmul(draai_matrix, r_speler)
    r_cameravlak = np.matmul(draai_matrix, r_cameravlak)
    for i,straal in enumerate(stralen):
        stralen[i] = np.matmul(draai_matrix,straal)
    changes = True
    return r_speler, r_cameravlak


def move(dir, stap):
    """Geef stap, veranderd positie speler volgens r_speler
    aan muur volgt het slechts vector die niet in de weg zit"""
    global p_speler_x, p_speler_y, changes
    x = p_speler_x + dir * stap * r_speler[0]
    y = p_speler_y + dir * stap * r_speler[1]
    if world_map[math.floor(y)][math.floor(x)] == 0:
        p_speler_x = x
        p_speler_y = y
        changes = True
    else:
        pass
        # Kan gebruikt worden voor muren die schade aanrichten enzo

def nr_rond(nr, tol=3):
    p = 10**tol
    acc = 0.5
    if 0 < nr < np.inf:
        return int(nr * p + acc) / p
    elif nr < 0:
        return -1
    elif nr == 0:
        return 0
    else:
        return np.inf


def bereken_r_straal(kolom):
    r_straal_kolom = d_camera * r_speler + (-1 + (2*kolom)/BREEDTE) * r_cameravlak
    r_straal = np.divide(r_straal_kolom, np.linalg.norm(r_straal_kolom))
    return r_straal


def raycast(p_speler_x, p_speler_y, r_straal):
    # stap 0: initialiseer x en y met waarde 0
    r_straal_x, r_straal_y = r_straal
    p_speler = np.array([p_speler_x, p_speler_y])
    y_nd, x_nd = np.shape(world_map)
    x, y = 0.0, 0.0
    # stap 1: bereken delta_h en delta_v
    delta_v = 1/abs(r_straal_x)
    delta_h = 1/abs(r_straal_y)
    # stap 2: bereken d_hor en d_vert
    # d_hor
    d_hor = (1 - p_speler_y + (p_speler_y//1)) * delta_h if r_straal_y >= 0 else (p_speler_y - (p_speler_y//1)) * delta_h
    # d_vert
    d_vert = (1 - p_speler_x + (p_speler_x//1)) * delta_v if r_straal_x >= 0 else (p_speler_x - (p_speler_x//1)) * delta_v
    # test d_hor + x * delta_h <= d_vert + y * delta_v
    while True:
        print(delta_h)
        print(d_hor)
        print(d_hor + x * delta_h)
        print(d_vert + y * delta_v)
        if d_hor + x * delta_h <= d_vert + y * delta_v:
            i_hor_x = p_speler + (d_hor + x * delta_h) * r_straal
            if r_straal_y >= 0:
                if world_map[(p_speler_y//1)-1][i_hor_x//1] != 0:
                    d_muur = x * delta_h
                    k_muur = world_map[p_speler_y-1][i_hor_x//1]
                    return d_muur, k_muur
                else:
                    x += 1
            else:
                if world_map[(p_speler_y//1)+1][i_hor_x//1] != 0:
                    d_muur = x * delta_h
                    k_muur = world_map[p_speler_y+1][i_hor_x//1]
                    return d_muur, k_muur
                else:
                    x += 1
        else:
            i_vert_y = p_speler + (d_vert + y * delta_v) * r_straal
            if r_straal_x >= 0:
                if world_map[i_vert_y//1][(p_speler_x//1)+1] != 0:
                    d_muur = x * delta_h
                    k_muur = world_map[i_vert_y][(p_speler_x//1)+1]
                    return d_muur, k_muur
                else:
                    y += 1
            else:
                if world_map[i_vert_y//1][(p_speler_x//1)-1] != 0:
                    d_muur = x * delta_h
                    k_muur = world_map[i_vert_y][(p_speler_x//1)-1]
                    return d_muur, k_muur
                else:
                    y += 1

def raycast_2(p_speler_x, p_speler_y, r_straal):
    r_straal_x, r_straal_y = r_straal
    d_h = p_speler_x - math.floor(p_speler_x)
    d_v = p_speler_y - math.floor(p_speler_y)
    d_x = d_y = 100
    x_dim, y_dim = np.shape(world_map)
    if r_straal_x > 0:
        v = 1/r_straal_x
        for i in range(math.floor(x_dim-p_speler_x)):
            x = math.floor(p_speler_y+i+1)
            y = p_speler_y+(1-d_h+i)*v*r_straal_y
            if y < y_dim and 0 < y:
                if world_map[math.floor(y)][x] == 1:
                    d_x = ((x-p_speler_x)**2+(y-p_speler_y)**2)**(1/2)
                    break
                elif world_map[math.floor(y)][x] == 2:
                    break
            else:
                break
    elif r_straal_x < 0:
        v = abs(1/r_straal_x)
        for i in range(math.floor(p_speler_x)):
            x = math.floor(p_speler_y-(i+1))
            y = p_speler_y+(d_h+i)*v*r_straal_y
            if y < y_dim and 0 < y:
                if world_map[math.floor(y)][x] == 1:
                    d_x = ((x-p_speler_x+1)**2+(y-p_speler_y)**2)**(1/2)
                    break
            else:
                break
    if r_straal_y > 0:
        h = 1/r_straal_y
        for i in range(math.floor(y_dim - p_speler_y)):
            y = math.floor(p_speler_y+i+1)
            x = p_speler_x+(1-d_v+i)*h*r_straal_x
            if x < x_dim and 0 < x:
                if world_map[y][math.floor(x)] == 1:
                    d_y = ((x-p_speler_x)**2+(y-p_speler_y)**2)**(1/2)
                    break
            else:
                break
    elif r_straal_y < 0:
        h = abs(1/r_straal_y)
        for i in range(math.floor(p_speler_y)):
            y = math.floor(p_speler_y-(i+1))
            x = p_speler_x+(d_v+i)*h*r_straal_x
            if x < x_dim and 0 < x:
                if world_map[y][math.floor(x)] == 1:
                    d_y = ((x-p_speler_x)**2+(y-p_speler_y+1)**2)**(1/2)
                    break
            else:
                break
    if d_x < d_y:
        d = fish_eye_(d_x,r_straal)
        return d, 2
    elif d_y != 100:
        d = fish_eye_(d_y,r_straal)
        return d, 1
    else:
        return 1, 0


def raycast_3(p_speler_x, p_speler_y, r_straal):
    r_straal_x = (r_straal[0])
    r_straal_y = (r_straal[1])
    delta_v = (1 / np.abs(r_straal_x))
    delta_h = (1 / np.abs(r_straal_y))
    y_nd, x_nd = np.shape(world_map)
    if r_straal_x > 0:
        if r_straal_y > 0:
            d_v = ((1 - (p_speler_x - math.floor(p_speler_x))) * delta_v)
            d_h = ((1 - (p_speler_y - math.floor(p_speler_y))) * delta_h)
            while True:
                if d_v < d_h:
                    x = int(nr_rond(p_speler_x + d_v * r_straal_x))
                    y = nr_rond(p_speler_y + d_v * r_straal_y)
                    if y < y_nd and x < x_nd:
                        if world_map[math.floor(y)][x] != 0:
                            return fish_eye_(d_v, r_straal), 2
                        else:
                            d_v += delta_v
                else:
                    x = nr_rond(p_speler_x + d_h * r_straal_x)
                    y = int(nr_rond(p_speler_y + d_h * r_straal_y))
                    if y < y_nd and x < x_nd:
                        if world_map[y][math.floor(x)] != 0:
                            return fish_eye_(d_h, r_straal), 1
                        else:
                            d_h += delta_h
                    else:
                        return 10, 0
    if r_straal_x > 0:
        if r_straal_y < 0:
            d_v = (1 - (p_speler_x - math.floor(p_speler_x))) * delta_v
            d_h = (p_speler_y - math.floor(p_speler_y)) * delta_h
            while True:
                if d_v < d_h:
                    x = int(nr_rond(p_speler_x + d_v * r_straal_x))
                    y = nr_rond(p_speler_y + d_v * r_straal_y)
                    if 0 <= y_nd and x < x_nd:
                        if world_map[math.floor(y)][x] != 0:
                            return fish_eye_(d_v, r_straal), 2
                        else:
                            d_v += delta_v
                else:
                    x = nr_rond(p_speler_x + d_h * r_straal_x)
                    y = int(nr_rond(p_speler_y + d_h * r_straal_y))
                    if 0 <= y and x < x_nd:
                        if world_map[y-1][math.floor(x)] != 0:
                            return fish_eye_(d_h, r_straal), 1
                        else:
                            d_h += delta_h
                    else:
                        return 10, 0
    if r_straal_x < 0:
        if r_straal_y > 0:
            d_v = (p_speler_x - math.floor(p_speler_x)) * delta_v
            d_h = (1 - (p_speler_y - math.floor(p_speler_y))) * delta_h
            while True:
                if d_v < d_h:
                    x = int(nr_rond(p_speler_x + d_v * r_straal_x))
                    y = nr_rond(p_speler_y + d_v * r_straal_y)
                    if y < y_nd and 0 <= x:
                        if world_map[math.floor(y)][x - 1] != 0:
                            return fish_eye_(d_v, r_straal), 2
                        else:
                            d_v += delta_v
                else:
                    x = nr_rond(p_speler_x + d_h * r_straal_x)
                    y = int(nr_rond(p_speler_y + d_h * r_straal_y))
                    if y < y_nd and 0 <= x:
                        if world_map[y][math.floor(x)] != 0:
                            return fish_eye_(d_h, r_straal), 1
                        else:
                            d_h += delta_h
                    else:
                        return 10, 0
    if r_straal_x < 0:
        if r_straal_y < 0:
            d_v = (p_speler_x - math.floor(p_speler_x)) * delta_v
            d_h = (p_speler_y - math.floor(p_speler_y)) * delta_h
            while True:
                if d_v < d_h:
                    x = int(nr_rond(p_speler_x + d_v * r_straal_x))
                    y = nr_rond(p_speler_y + d_v * r_straal_y)
                    if 0 <= y and 0 <= x:
                        if world_map[math.floor(y)][math.floor(x - 1)] != 0:
                            return fish_eye_(d_v, r_straal), 2
                        else:
                            d_v += delta_v
                else:
                    x = nr_rond(p_speler_x + d_h * r_straal_x)
                    y = int(nr_rond(p_speler_y + d_h * r_straal_y))
                    if 0 <= y and 0 <= x:
                        if world_map[math.floor(y - 1)][math.floor(x)] != 0:
                            return fish_eye_(d_h, r_straal), 1
                        else:
                            d_h += delta_h
                    else:
                        return 10, 0

    return 1, 0


def fish_eye_(d,r_straal):
    r_speler = np.array([r_speler_x,r_speler_y])
    hoek = np.dot(r_speler,r_straal)/(np.linalg.norm(r_speler)*np.linalg.norm(r_straal))
    return hoek*d

def render_kolom(renderer, window, kolom, d_muur, k_muur):
    d_muur = d_muur*2
    renderer.draw_line((kolom, window.size[1]/2-window.size[1]*(1/d_muur), kolom, window.size[1]/2+window.size[1]*(1/d_muur)), kleuren[k_muur])
    return


def show_fps(font, renderer, window):
    fps_list = []
    fps = 0
    loop_time = 1

    while True:
        fps_list.append(1 / (time.time() - loop_time))
        loop_time = time.time()
        fps = sum(fps_list) / len(fps_list)
        if len(fps_list) == 100:
            fps_list.pop(0)
        text = sdl2.ext.renderer.Texture(renderer, font.render_text(f'{fps:.2f} fps'))
        renderer.copy(text, dstrect=(int((window.size[0] - text.size[0]) / 2), 20,
                                     text.size[0], text.size[1]))
        yield fps


def main():
    # Initialiseer de SDL2 bibliotheek
    sdl2.ext.init()

    # Maak een venster aan om de game te renderen
    window = sdl2.ext.Window("Project Ingenieursbeleving 2", size=(BREEDTE, HOOGTE))
    window.show()

    # Begin met het uitlezen van input van de muis en vraag om relatieve coordinaten
    sdl2.SDL_SetRelativeMouseMode(False) #Even uitgezet

    # Maak een renderer aan zodat we in ons venster kunnen renderen
    renderer = sdl2.ext.Renderer(window)

    # Initialiseer font voor de fps counter
    fps_font = sdl2.ext.FontTTF(font='CourierPrime.ttf', size=20, color=kleuren[7])
    fps_generator = show_fps(fps_font, renderer, window)

    # Blijf frames renderen tot we het signaal krijgen dat we moeten afsluiten
    while not moet_afsluiten:

        # Onthoud de huidige tijd
        start_time = time.time()

        # Reset de rendering context
        renderer.clear()

        # Render de huidige frame
        tijd = 0
        for kolom in range(0, window.size[0]):
            r_straal = bereken_r_straal(kolom)
            (d_muur, k_muur) = raycast(p_speler_x, p_speler_y, r_straal)
            render_kolom(renderer, window, kolom, d_muur, k_muur)

        delta = time.time() - start_time

        verwerk_input(delta)

        # Toon de fps
        next(fps_generator)

        # Verwissel de rendering context met de frame buffer
        renderer.present()

    # Sluit SDL2 af
    sdl2.ext.quit()


if __name__ == '__main__':
    main()
