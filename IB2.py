import math
import random
import time
import numpy as np
import random

import sdl2.ext

# Constanten
BREEDTE = 800
HOOGTE = 600

#
# Globale variabelen
#

# positie van de speler
p_speler_x, p_speler_y = 3 + 1 / math.sqrt(2), 4 - 1 / math.sqrt(2)

# richting waarin de speler kijkt
r_speler_x, r_speler_y = 1 / math.sqrt(2), -1 / math.sqrt(2)

# cameravlak
r_cameravlak_x, r_cameravlak_y = -1 / math.sqrt(2), -1 / math.sqrt(2)

# wordt op True gezet als het spel afgesloten moet worden
moet_afsluiten = False

# FOV (FOV slider implementeren of niet?)
d_camera = 1
# de "wereldkaart". Dit is een 2d matrix waarin elke cel een type van muur voorstelt
# Een 0 betekent dat op deze plaats in de game wereld geen muren aanwezig zijn
world_map = [[2, 2, 2, 2, 2, 2, 2],
             [2, 0, 0, 0, 1, 2, 2],
             [2, 0, 0, 0, 0, 1, 2],
             [2, 0, 0, 0, 0, 0, 2],
             [2, 0, 0, 0, 0, 0, 2],
             [2, 0, 0, 0, 0, 0, 2],
             [2, 2, 2, 2, 2, 2, 2]]
x_dim = len(world_map[0])
y_dim = len(world_map)

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


def bereken_r_straal(r_speler_x, r_speler_y, kolom):
    r_speler = np.array([r_speler_x, r_speler_y])
    r_cameravlak = np.array([r_cameravlak_x, r_cameravlak_y])
    r_straal_kolom = d_camera * r_speler + (-1 + (2*kolom)/BREEDTE) * r_cameravlak
    r_straal = np.divide(r_straal_kolom, np.linalg.norm(r_straal_kolom))
    return r_straal


def raycast(p_speler_x, p_speler_y, r_straal_x, r_straal_y):
    x, y = 0, 0
    delta_v = 1/np.abs(r_straal_x)
    delta_h = 1/np.abs(r_straal_y)
    p_speler = np.array([p_speler_x, p_speler_y])
    r_straal = np.array([r_straal_x, r_straal_y])
    x_nd, y_nd = np.shape(world_map)
    if r_straal_y < 0:
        d_hor = (p_speler_y - np.floor(p_speler_y)) * delta_h
    else:
        d_hor = (1-p_speler_y + np.floor(p_speler_y)) * delta_h
    if r_straal_x < 0:
        d_vert = (p_speler_x - np.floor(p_speler_x)) * delta_v
    else:
        d_vert = (1-p_speler_x + np.floor(p_speler_x)) * delta_v

    if d_hor + x * delta_h <= d_vert + y * delta_v:
        i_hor = p_speler + (d_hor + x * delta_h) * r_straal
        x += 1
        if r_straal_y >= 0:
            if world_map[x][y] != 0:
                d_muur = np.linalg.norm([d_hor, d_vert])
                k_muur = world_map[x][y-1]
        else:
            if world_map[x][y+1] != 0:
                d_muur = np.linalg.norm([d_hor, d_vert])
                k_muur = world_map[x][y+1]
    else:
        i_vert = p_speler + (d_vert + y * delta_v) * r_straal
        y += 1
        if r_straal_x < 0:
            if world_map[x-1][y] != 0:
                d_muur = np.linalg.norm([d_hor, d_vert])
                k_muur = world_map[x-1][y]
        else:
            if world_map[x][y] != 0:
                d_muur = np.linalg.norm([d_hor, d_vert])
                k_muur = world_map[x-1][y]
    if x > np.shape(world_map)[0] or y > np.shape(world_map)[1]:
        print("Error")
    return d_muur, k_muur

def raycast_2(p_speler_x, p_speler_y, r_straal_x, r_straal_y):
    d_h = p_speler_x - math.floor(p_speler_x)
    d_v = p_speler_y - math.floor(p_speler_y)
    d_x = 100
    if r_straal_x > 0:
        v = 1/r_straal_x
        for i in range(math.floor(x_dim-p_speler_x)):
            x = math.floor(p_speler_y+i+1)
            y = p_speler_y+(1-d_h+i)*v*r_straal_y
            if y < y_dim and 0 < y:
                if world_map[math.floor(y)][x] == 1:
                    d_x = ((x-p_speler_x)**2+(y-p_speler_y)**2)**(1/2)
                    x_f = x
                    y_f = y
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
                    x_f = x
                    y_f = y
                    break
            else:
                break
    d_y = 100
    if r_straal_y > 0:
        h = 1/r_straal_y
        for i in range(math.floor(y_dim - p_speler_y)):
            y = math.floor(p_speler_y+i+1)
            x = p_speler_x+(1-d_v+i)*h*r_straal_x
            if x < x_dim and 0 < x:
                if world_map[y][math.floor(x)] == 1:
                    d_y = ((x-p_speler_x)**2+(y-p_speler_y)**2)**(1/2)
                    x_f = x
                    y_f = y
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
                    x_f = x
                    y_f = y
                    break
            else:
                break
    if d_x < d_y:
        d = d_x
        return d, kleuren[2]
    elif d_y != 100:
        d = d_y
        return d, kleuren[1]
    else:
        return 1, kleuren[0]



def render_kolom(renderer, window, kolom, d_muur, k_muur):
    d_muur = d_muur*2
    renderer.draw_line((kolom, window.size[1]/2-window.size[1]*(1/d_muur), kolom, window.size[1]/2+window.size[1]*(1/d_muur)), k_muur)
    return


def show_fps(font, renderer, window):
    fps_list = []
    fps = 0
    loop_time = 1

    while True:
        fps_list.append(1 / (time.time() - loop_time))
        loop_time = time.time()
        if len(fps_list) == 20:
            fps = sum(fps_list)/len(fps_list)
            fps_list = []
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
        for kolom in range(0, window.size[0]):
            (r_straal_x, r_straal_y) = bereken_r_straal(r_speler_x, r_speler_y, kolom)
            (d_muur, k_muur) = raycast_2(p_speler_x, p_speler_y, r_straal_x, r_straal_y)
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
