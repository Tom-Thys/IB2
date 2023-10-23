import math
import time
import random
import numpy as np

import sdl2.ext
import sdl2.sdlimage
import sdl2.sdlmixer
from sdl2 import *
from worlds import worldlijst
from Classes import *
from rendering import *


# Constanten
BREEDTE = 1000
HOOGTE = 700

POSITIE_START_GAME = [365, 253]
POSITIE_SETTINGS = [300, 401]
POSITIE_QUIT_GAME = [420, 572]
#
# Globale variabelen
#
game = False
garage = False
sound = True
index = 0
positie = [0,0]
stapgeluid = sdl2.sdlmixer.Mix_LoadMUS(f"muziek/concrete-footsteps.wav".encode())
# wordt op True gezet als het spel afgesloten moet worden
moet_afsluiten = False


# positie van de speler
p_speler_x, p_speler_y = 3 + 1 / math.sqrt(2), 5 + 1 / math.sqrt(2)

# richting waarin de speler kijkt
r_speler_hoek = math.pi / 4
# FOV
d_camera = 1
#
#Speler aanmaken
speler = Player(p_speler_x, p_speler_y, r_speler_hoek, BREEDTE)
speler.aanmaak_r_stralen(d_camera=d_camera)



#world
wereld_nr = 0
world_map = worldlijst[wereld_nr]
#y_dim, x_dim = np.shape(world_map)

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
    sdl2.ext.Color(106, 13, 173)    #9 = Purple
]


#
# Verwerkt alle input van het toetsenbord en de muis
#
# Argumenten:
# @delta       Tijd in milliseconden sinds de vorige oproep van deze functie
#
def verwerk_input(delta):
    global moet_afsluiten, game, garage, index

    # Handelt alle input events af die zich voorgedaan hebben sinds de vorige
    # keer dat we de sdl2.ext.get_events() functie hebben opgeroepen
    events = sdl2.ext.get_events()
    key_states = sdl2.SDL_GetKeyboardState(None)
    if (key_states[sdl2.SDL_SCANCODE_UP] or key_states[sdl2.SDL_SCANCODE_E]) and game:
        speler.move(1, 0.1,world_map)
    if (key_states[sdl2.SDL_SCANCODE_DOWN] or key_states[sdl2.SDL_SCANCODE_D]) and game:
        speler.move(-1, 0.1,world_map)
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
            if not moet_afsluiten and not game:
                if key == sdl2.SDLK_DOWN:
                    index += 1
                if key == sdl2.SDLK_UP:
                    index -= 1
                if key == sdl2.SDLK_SPACE and index == 0:
                    game = True
                if key == sdl2.SDLK_SPACE and index == 1:
                    break
                if key == sdl2.SDLK_SPACE and index == 2:
                    moet_afsluiten = True
                    break
            if not moet_afsluiten and game:
                if key == sdl2.SDLK_m:
                    game = False
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

""" STAAT NU IN class Player
def bereken_r_straal(kolom):
    r_straal_kolom = d_camera * r_speler + (1 - (2 * kolom) / BREEDTE) * r_cameravlak
    r_straal = np.divide(r_straal_kolom, np.linalg.norm(r_straal_kolom))
    return r_straal


def draaien(hoek):
    
    global r_cameravlak, r_speler, stralen
    draai_matrix = np.array([[math.cos(hoek), -math.sin(hoek)],
                             [math.sin(hoek), math.cos(hoek)]])
    r_speler = np.matmul(draai_matrix, r_speler)
    r_cameravlak = np.matmul(draai_matrix, r_cameravlak)
    for i, straal in enumerate(stralen):
        stralen[i] = np.matmul(draai_matrix, straal)
    return r_speler, r_cameravlak


def move(dir, stap):
    Geef stap, veranderd positie speler volgens r_speler
    aan muur volgt het slechts vector die niet in de weg zit
    global p_speler_x, p_speler_y
    x = p_speler_x + dir * stap * r_speler[0]
    y = p_speler_y + dir * stap * r_speler[1]
    if world_map[math.floor(y)][math.floor(x)] == 0 and 0<x<x_dim-1 and 0<y<y_dim-1:
        p_speler_x = x
        p_speler_y = y
    else:
        pass
        # Kan gebruikt worden voor muren die schade aanrichten enzo
"""


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


def render_floor_and_sky(renderer, window):
    # SKY in blauw
    renderer.fill((0, 0, window.size[0], window.size[1] // 2), kleuren[8])
    # Floor in grijs
    renderer.fill((0, window.size[1] // 2, window.size[0], window.size[1] // 2), kleuren[5])


def wheelSprite(renderer,window,sprite):
    window_width, window_height = window.size
    x_pos = (window_width - 250) // 2
    y_pos = window_height - 230
    renderer.copy(sprite,dstrect=(x_pos,y_pos,250,250))

"""def render_sprites(renderer, sprites, player, camera_direction):
    sprites.sort(key=lambda sprite: np.linalg.norm(sprite.position - player.position))#Sorteren op afstand

    for sprite in sprites:
        # Bereken de richting van de sprite vanuit de speler
        sprite_direction = sprite.position - player.position
        sprite_distance = np.linalg.norm(sprite_direction)

        # Bereken de grootte van de sprite op basis van de afstand
        sprite_size = max(1, min(64, int(HOOGTE / sprite_distance)))

        # Bereken de hoek tussen de kijkrichting van de speler en de sprite
        sprite_angle = math.atan2(sprite_direction[1], sprite_direction[0]) - camera_direction


        screen_x = int((BREEDTE / 2) * (1 + sprite_angle / (70 / BREEDTE)))#Met 70 als field of view
        screen_y = int(HOOGTE / 2)#wordt in het midden gezet

        renderer.copy(sprite.texture, srcrect=(0, 0, sprite.texture.size[0], sprite.texture.size[1]),
                dstrect=(screen_x - sprite_size // 2, screen_y - sprite_size // 2, sprite_size, sprite_size))
"""

def show_fps(font, renderer, window):
    fps_list = [1]
    loop_time = 0

    while True:
        if (time.time() - loop_time) != 0:
            fps_list.append(1 / (time.time() - loop_time))
            #print(min(fps_list))
            loop_time = time.time()

        fps = sum(fps_list) / len(fps_list)
        if len(fps_list) == 20:
            fps_list.pop(0)
        text = sdl2.ext.renderer.Texture(renderer, font.render_text(f'{fps:.2f} fps'))
        renderer.copy(text, dstrect=(int((window.size[0] - text.size[0]) / 2), 20,
                                     text.size[0], text.size[1]))
        yield fps


def muziek_spelen(geluid, looped = False):
    global stapgeluid
    if not sound:
        return
    else:
        volume = 80
        if geluid == 0:
            sdl2.sdlmixer.Mix_FadeOutMusic(500)
            sdl2.sdlmixer.Mix_CloseAudio()
            return
        if sdl2.sdlmixer.Mix_PlayingMusic():  # controleren of dat muziek al gespeeld word
            return
        sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.sdlmixer.MIX_DEFAULT_FORMAT, 1, 1024)  # 44100 = 16 bit, cd kwaliteit
        if geluid == "concrete-footsteps":
            sdl2.sdlmixer.Mix_PlayMusic(stapgeluid, -1)
        liedje = sdl2.sdlmixer.Mix_LoadMUS(f"muziek/{geluid}.wav".encode())
        if not looped:
            sdl2.sdlmixer.Mix_PlayMusic(liedje, -1)  # channel, chunk, loops: channel = -1(channel maakt niet uit), chunk = Mix_LoadWAV(moet WAV zijn), loops = -1: oneindig lang
        else:
            sdl2.sdlmixer.Mix_PlayMusic(liedje, 0)
        if geluid == "8-Bit Postman Pat":
            volume = 64
        sdl2.sdlmixer.Mix_MasterVolume(volume)  # volume 0-127, we kunnen nog slider implementen / afhankelijk van welk geluid het volume aanpassen

def main_menu_nav():
    global index, positie
    if index == 0:
        positie = POSITIE_START_GAME
        return
    elif index == 1:
        positie = POSITIE_SETTINGS
        return
    elif index == 2:
        positie = POSITIE_QUIT_GAME
        return
    if index > 2:
        index = 2
    if index < 0:
        index = 0

def main():
    global game, garage, BREEDTE
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
    achtergrond = factory.from_image(resources.get_path("game_main_menu.png"))
    menu_pointer = factory.from_image(resources.get_path("game_main_menu_pointer.png"))
    wheel = factory.from_image(resources.get_path("Wheel.png"))
    sprites = []
    sprites.append(Sprite(image=resources.get_path("Tree.png"), x=2, y=2))
    while not moet_afsluiten:
        muziek_spelen("8-Bit Postman Pat")
        sdl2.SDL_SetRelativeMouseMode(False)
        while not game and not moet_afsluiten and not garage:
            start_time = time.time()
            renderer.clear()
            muziek_spelen("8-Bit Postman Pat")
            delta = time.time() - start_time
            verwerk_input(delta)
            main_menu_nav()
            renderer.copy(achtergrond,
                          srcrect=(0, 0, achtergrond.size[0], achtergrond.size[1]),
                          dstrect=(0, 0, BREEDTE, HOOGTE))
            renderer.copy(menu_pointer,
                          srcrect=(0, 0, menu_pointer.size[0], menu_pointer.size[1]),
                          dstrect=(positie[0], positie[1], 80, 50))
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
            #render_sprites(renderer,sprites,window)
            # Render de huidige frame




            #muren = speler.raycasting(world_map, muren)
            (k, d, v, kl) = speler.n_raycasting(world_map)
            #print(k, d, v, kl)

            for i in k:
                # r_straal = bereken_r_straal(kolom)
                # (d_muur, k_muur) = raycast_4(p_speler_x, p_speler_y, r_straal)
                # render_kolom(renderer, window, kolom, d_muur, k_muur)
                renderen(renderer, window, i, d[i], v[i], kl[i], soort_muren)


            draw_nav(renderer, world_map, map_textuur[wereld_nr], speler,sprites)
            delta = time.time() - start_time
            wheelSprite(renderer,window,wheel)
            verwerk_input(delta)

            # Toon de fps
            next(fps_generator)

            # Verwissel de rendering context met de frame buffer
            renderer.present()

    # Sluit SDL2 af
    sdl2.ext.quit()


if __name__ == '__main__':
    main()
