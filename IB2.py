import math
import time
import random
import numpy as np

import sdl2.ext
import sdl2.sdlimage
import sdl2.sdlmixer
from sdl2 import *
from worlds import worldlijst
from Raycaster import *
from Classes import *


# Constanten
BREEDTE = 1000
HOOGTE = 700

#
# Globale variabelen
#
game = False
garage = False
sound = True


# positie van de speler
p_speler_x, p_speler_y = 3 + 1 / math.sqrt(2), 5 + 1 / math.sqrt(2)

# richting waarin de speler kijkt
r_speler_hoek = math.pi / 4
# FOV
d_camera = 1
#
#Speler aanmaken
speler = Player(p_speler_x, p_speler_y, r_speler_hoek, BREEDTE)
speler.aanmaak_r_stralen(BREEDTE, d_camera)


# alle stralen die vauit de speler vertrekken
stralen = []
changes = False

# cameravlak
r_cameravlak_x, r_cameravlak_y = -1 / math.sqrt(2), -1 / math.sqrt(2)
r_cameravlak = np.array([math.cos(r_speler_hoek - math.pi / 2), math.sin(r_speler_hoek - math.pi / 2)])

# wordt op True gezet als het spel afgesloten moet worden
moet_afsluiten = False










#world
world_map = worldlijst[0]
y_dim, x_dim = np.shape(world_map)

# Vooraf gedefinieerde kleuren
kleuren = [
    sdl2.ext.Color(0, 0, 0),  # 0 = Zwart
    sdl2.ext.Color(255, 0, 20),  # 1 = Rood
    sdl2.ext.Color(0, 255, 0),  # 2 = Groen
    sdl2.ext.Color(0, 0, 255),  # 3 = Blauw
    sdl2.ext.Color(64, 64, 64),  # 4 = Donker grijs
    sdl2.ext.Color(128, 128, 128),  # 5 = Grijs
    sdl2.ext.Color(192, 192, 192),  # 6 = Licht grijs
    sdl2.ext.Color(255, 255, 255),  # 7 = Wit
    sdl2.ext.Color(120, 200, 250),  # 8 = Blauw_lucht
]


#
# Verwerkt alle input van het toetsenbord en de muis
#
# Argumenten:
# @delta       Tijd in milliseconden sinds de vorige oproep van deze functie
#
def verwerk_input(delta):
    global moet_afsluiten, game, garage

    # Handelt alle input events af die zich voorgedaan hebben sinds de vorige
    # keer dat we de sdl2.ext.get_events() functie hebben opgeroepen
    events = sdl2.ext.get_events()
    key_states = sdl2.SDL_GetKeyboardState(None)
    if (key_states[sdl2.SDL_SCANCODE_UP] or key_states[sdl2.SDL_SCANCODE_E]) and game:
        speler.move(1, 0.01,world_map)
    if (key_states[sdl2.SDL_SCANCODE_DOWN] or key_states[sdl2.SDL_SCANCODE_D]) and game:
        speler.move(-1, 0.01,world_map)
    if (key_states[sdl2.SDL_SCANCODE_RIGHT] or key_states[sdl2.SDL_SCANCODE_F]) and game:
        speler.draaien(-math.pi / 200)
    if (key_states[sdl2.SDL_SCANCODE_LEFT] or key_states[sdl2.SDL_SCANCODE_S]) and game:
        speler.draaien(math.pi / 200)
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
            if key == sdl2.SDLK_SPACE and not game:
                game = True
            if key == sdl2.SDLK_m:
                game = False
                garage = False
            break
        elif event.type == sdl2.SDL_KEYUP:
            key = event.key.keysym.sym
            if key == sdl2.SDLK_f or key == sdl2.SDLK_s:
                pass
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
                continue
        # Wordt afgeleverd als de gebruiker de muis heeft bewogen.
        # Aangezien we relative motion gebruiken zijn alle coordinaten
        # relatief tegenover de laatst gerapporteerde positie van de muis.
        elif event.type == sdl2.SDL_MOUSEMOTION and game:
            # Aangezien we in onze game maar 1 as hebben waarover de camera
            # kan roteren zijn we enkel geinteresseerd in bewegingen over de
            # X-as
            draai = event.motion.xrel
            speler.draaien(-math.pi / 4000 * draai)
            beweging = event.motion.yrel
            speler.move(1, beweging / 1000, world_map)
            continue

    # Polling-gebaseerde input. Dit gebruiken we bij voorkeur om bv het ingedrukt
    # houden van toetsen zo accuraat mogelijk te detecteren
    key_states = sdl2.SDL_GetKeyboardState(None)

    # if key_states[sdl2.SDL_SCANCODE_UP] or key_states[sdl2.SDL_SCANCODE_W]:
    # beweeg vooruit...

    if key_states[sdl2.SDL_SCANCODE_ESCAPE]:
        moet_afsluiten = True


def bereken_r_straal(kolom):
    r_straal_kolom = d_camera * r_speler + (1 - (2 * kolom) / BREEDTE) * r_cameravlak
    r_straal = np.divide(r_straal_kolom, np.linalg.norm(r_straal_kolom))
    return r_straal


def draaien(hoek):
    """Geef hoek op in radialen, geeft r_straal en r_cameravlak terug"""
    global r_cameravlak, r_speler, stralen, changes
    draai_matrix = np.array([[math.cos(hoek), -math.sin(hoek)],
                             [math.sin(hoek), math.cos(hoek)]])
    r_speler = np.matmul(draai_matrix, r_speler)
    r_cameravlak = np.matmul(draai_matrix, r_cameravlak)
    for i, straal in enumerate(stralen):
        stralen[i] = np.matmul(draai_matrix, straal)
    changes = True
    return r_speler, r_cameravlak


def move(dir, stap):
    """Geef stap, veranderd positie speler volgens r_speler
    aan muur volgt het slechts vector die niet in de weg zit"""
    global p_speler_x, p_speler_y, changes
    x = p_speler_x + dir * stap * r_speler[0]
    y = p_speler_y + dir * stap * r_speler[1]
    if world_map[math.floor(y)][math.floor(x)] == 0 and 0<x<x_dim-1 and 0<y<y_dim-1:
        p_speler_x = x
        p_speler_y = y
        changes = True
    else:
        pass
        # Kan gebruikt worden voor muren die schade aanrichten enzo



def render_kolom(renderer, window, kolom, d_muur, k_muur):
    d_muur = d_muur * 2
    renderer.draw_line((kolom, window.size[1] / 2 - window.size[1] * (1 / d_muur), kolom,
                        window.size[1] / 2 + window.size[1] * (1 / d_muur)), kleuren[k_muur])
    return


def renderen(renderer, window, kolom, d_muur, unit_d, k_muur, soort_muren):

    if k_muur != 0:
        wall_texture = soort_muren[k_muur - 1]
        breedte = wall_texture.size[0]
        # rij = kolom % breedte
        rij = (unit_d % 1) * breedte
        hoogte = wall_texture.size[1]
        d_muur = 10 / d_muur
        textuur_x = rij
        textuur_y = 0
        scherm_x = 10
        kolom = BREEDTE-kolom
        scherm_y = window.size[1] / 2
        renderer.copy(wall_texture, srcrect=(textuur_x, textuur_y, 1, 100),
                      dstrect=(kolom, scherm_y - d_muur * hoogte / 2, 1, d_muur * hoogte))


def renderText(font, renderer, text, x, y, window = 0):
    text = sdl2.ext.renderer.Texture(renderer, font.render_text(text))
    if window:
        renderer.copy(text, dstrect=(int((window.size[0] - text.size[0]) / 2), y, text.size[0], text.size[1]))
    else:
        renderer.copy(text, dstrect=(x, y, text.size[0], text.size[1]))


def draw_nav(renderer, wall_texture , sprites = [], width = 200):
    """
    Rendert PNG van world map in linkerbovenhoek
    Speler is zichtbaar in het midden
    Sprites worden door een kleur aangegeven op de map
    Navigatie naar volgende doel wordt via een lijn aangegeven op de map
    :param width: Geeft aan hoe breed de wereld map standaard is
    """
    global p_speler_y, p_speler_x
    breedte = wall_texture.size[0]
    hoogte = wall_texture.size[1]
    x = width
    y = x/breedte*hoogte
    renderer.copy(wall_texture, srcrect=(0, 0, breedte, hoogte),
                  dstrect=(0, 0, x, y))
    unit_d = x/x_dim
    renderer.draw_rect((unit_d, unit_d, (x_dim-2)*unit_d, (y_dim-2)*unit_d),kleuren[3])


def render_floor_and_sky(renderer, window):
    # SKY in blauw
    renderer.fill((0, 0, window.size[0], window.size[1] // 2), kleuren[8])
    # Floor in grijs
    renderer.fill((0, window.size[1] // 2, window.size[0], window.size[1] // 2), kleuren[5])



def show_fps(font, renderer, window):
    fps_list = [1]
    fps = 0
    loop_time = 1

    while True:
        if (time.time() - loop_time) != 0:
            fps_list.append(1 / (time.time() - loop_time))
        loop_time = time.time()
        fps = sum(fps_list) / len(fps_list)
        if len(fps_list) == 20:
            fps_list.pop(0)
        text = sdl2.ext.renderer.Texture(renderer, font.render_text(f'{fps:.2f} fps'))
        renderer.copy(text, dstrect=(int((window.size[0] - text.size[0]) / 2), 20,
                                     text.size[0], text.size[1]))
        yield fps


def muziek_spelen(geluid, looped = False):
    volume = 100
    if not sound:
        return
    else:
        if geluid == 0:
            sdl2.sdlmixer.Mix_FadeOutMusic(500)
            sdl2.sdlmixer.Mix_CloseAudio()
            return
        if sdl2.sdlmixer.Mix_PlayingMusic():  # controleren of dat muziek al gespeeld word
            return

        sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.sdlmixer.MIX_DEFAULT_FORMAT, 1, 1024)  # 44100 = 16 bit, cd kwaliteit
        liedje = sdl2.sdlmixer.Mix_LoadMUS(f"muziek/{geluid}.wav".encode())
        if not looped:
            sdl2.sdlmixer.Mix_PlayMusic(liedje, -1)  # channel, chunk, loops: channel = -1(channel maakt niet uit), chunk = Mix_LoadWAV(moet WAV zijn), loops = -1: oneindig lang
        else:
            sdl2.sdlmixer.Mix_PlayMusic(liedje, 0)
        if geluid == "8-Bit Postman Pat":
            volume = 64
        sdl2.sdlmixer.Mix_MasterVolume(volume)  # volume 0-127, we kunnen nog slider implementen / afhankelijk van welk geluid het volume aanpassen

def main():
    global changes, game, garage, BREEDTE
    # Initialiseer de SDL2 bibliotheek
    sdl2.ext.init()
    sdl2.sdlmixer.Mix_Init(0)



    # Maak een venster aan om de game te renderen
    window = sdl2.ext.Window("Project Ingenieursbeleving 2", size=(BREEDTE, HOOGTE))
    window.show()
    #screen = sdl2.ext.surface("Test",size=(BREEDTE,HOOGTE))
    # Begin met het uitlezen van input van de muis en vraag om relatieve coordinaten
    sdl2.SDL_SetRelativeMouseMode(True)

    # Maak een renderer aan zodat we in ons venster kunnen renderen
    renderer = sdl2.ext.Renderer(window)



    # resources inladen
    resources = sdl2.ext.Resources(__file__, "resources")
    # Spritefactory aanmaken
    factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=renderer)
    # soorten muren opslaan in sdl2 textures
    soort_muren = [
        factory.from_image(resources.get_path("muur_test.png")),  # 1
        factory.from_image(resources.get_path("Red_house.png")),  # 2
        factory.from_image(resources.get_path("Pink_house.png")),  # 3
        factory.from_image(resources.get_path("yellow_house.png")),  # 4
        factory.from_image(resources.get_path("Gruis_house.png"))  # 5
    ]
    # Inladen wereld_mappen
    map_resources = sdl2.ext.Resources(__file__,"mappen")
    # alle mappen opslaan in sdl2 textures
    map_textuur = []
    for i,map in enumerate(worldlijst):
        naam = f"map{i}.png"
        map_textuur.append(factory.from_image(map_resources.get_path(naam)))



    # Initialiseer font voor de fps counter
    font = sdl2.ext.FontTTF(font='CourierPrime.ttf', size=20, color=kleuren[7])
    fps_generator = show_fps(font, renderer, window)

    # Blijf frames renderen tot we het signaal krijgen dat we moeten afsluiten



    #muren = speler.raycasting(world_map)
    #(k, d,v,kl) = speler.n_raycasting(world_map)
    sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.sdlmixer.MIX_DEFAULT_FORMAT, 1, 1024)  # 44100 = 16 bit, cd kwaliteit

    achtergrond = factory.from_image(resources.get_path("8-bit postman pat background.jpg"))
    while not moet_afsluiten:
        muziek_spelen("8-Bit Postman Pat")
        sdl2.SDL_SetRelativeMouseMode(False)
        while not game and not moet_afsluiten and not garage:
            start_time = time.time()
            renderer.clear()
            muziek_spelen("8-Bit Postman Pat")
            delta = time.time() - start_time
            verwerk_input(delta)
            #renderer.fill((0, 0, window.size[0], window.size[1]), kleuren[8])
            renderer.copy(achtergrond,
                          srcrect=(0, 0, achtergrond.size[0], achtergrond.size[1]),
                          dstrect=(0, 0, BREEDTE, HOOGTE))
            renderText(font, renderer, "Menu", 20, 50, window)
            renderText(font, renderer, "HIT SPACE TO CONTINUE", 20, HOOGTE-100, window)
            renderer.present()


        muziek_spelen(0)

        sdl2.SDL_SetRelativeMouseMode(True)
        muziek_spelen("arcade_start", True)
        while game and not moet_afsluiten and not garage:
            # Onthoud de huidige tijd
            start_time = time.time()
            # Reset de rendering context
            renderer.clear()
            render_floor_and_sky(renderer, window)
            # Render de huidige frame

            #muren = speler.raycasting(world_map, muren)
            (k, d, v, kl) = speler.n_raycasting(world_map)
            #print(k, d, v, kl)

            for i in k:
                # r_straal = bereken_r_straal(kolom)
                # (d_muur, k_muur) = raycast_4(p_speler_x, p_speler_y, r_straal)
                # render_kolom(renderer, window, kolom, d_muur, k_muur)
                renderen(renderer, window, i, d[i], v[i], kl[i], soort_muren)
            draw_nav(renderer, map_textuur[0])
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
