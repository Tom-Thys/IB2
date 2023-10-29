#import cProfile
#import pstats
#from line_profiler_pycharm import profile

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
from configparser import ConfigParser
config = ConfigParser()


# Constanten
BREEDTE = 1000
HOOGTE = 700

POSITIE_START_GAME = [365, 253]
POSITIE_SETTINGS = [300, 401]
POSITIE_QUIT_GAME = [420, 572]
POSITIE_SETTINGS_BACK = [170, 55]
#
# Globale variabelen
#
game_state = 0  # 0: main menu, 1: settings menu, 2: game actief, 3: garage,
sound = True
main_menu_index = 0
settings_menu_index = 0
main_menu_positie = [0, 0]
settings_menu_positie = [0, 0]
# verwerking van config file: ook globale variabelen
config.read("config.ini")
volume = int(config.get("settings", "volume"))
sensitivity_rw = int(config.get("settings", "sensitivity")) # echte sensitivity gaat van 100 - 300, 300 traagst, 100 snelst. Raw sensitivity gaat van 0 tot 100
sensitivity = -2 * sensitivity_rw + 300

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
    global moet_afsluiten,game_state, main_menu_index, settings_menu_index, volume, sensitivity, sensitivity_rw

    # Handelt alle input events af die zich voorgedaan hebben sinds de vorige
    # keer dat we de sdl2.ext.get_events() functie hebben opgeroepen
    events = sdl2.ext.get_events()
    key_states = sdl2.SDL_GetKeyboardState(None)
    if (key_states[sdl2.SDL_SCANCODE_UP] or key_states[sdl2.SDL_SCANCODE_E]) and game_state == 2:
        speler.move(1, 0.1,world_map)
    if (key_states[sdl2.SDL_SCANCODE_DOWN] or key_states[sdl2.SDL_SCANCODE_D]) and game_state == 2:
        speler.move(-1, 0.1,world_map)
    if (key_states[sdl2.SDL_SCANCODE_RIGHT] or key_states[sdl2.SDL_SCANCODE_F]) and game_state == 2:
        speler.draaien(-math.pi / sensitivity)
    if (key_states[sdl2.SDL_SCANCODE_LEFT] or key_states[sdl2.SDL_SCANCODE_S]) and game_state == 2:
        speler.draaien(math.pi / sensitivity)

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
            if not moet_afsluiten and game_state == 0:
                if key == sdl2.SDLK_DOWN:
                    main_menu_index += 1
                    #muziek_spelen("main menu select", False, 2)
                if key == sdl2.SDLK_UP:
                    main_menu_index -= 1
                    #muziek_spelen("main menu select", False, 2)
                if key == sdl2.SDLK_SPACE or key == sdl2.SDLK_KP_ENTER or key == sdl2.SDLK_RETURN:
                    if main_menu_index == 0:
                        game_state = 2
                    if main_menu_index == 1:
                        game_state = 1
                        pass
                    if main_menu_index == 2:
                        moet_afsluiten = True
                        break
            if not moet_afsluiten and game_state == 1:
                if key == sdl2.SDLK_DOWN:
                    settings_menu_index += 1
                    #muziek_spelen("main menu select", False, 2)
                if key == sdl2.SDLK_UP:
                    settings_menu_index -= 1
                    #muziek_spelen("main menu select", False, 2)
                if key == sdl2.SDLK_SPACE or key == sdl2.SDLK_KP_ENTER or key == sdl2.SDLK_RETURN:
                    if settings_menu_index == 0:
                        pass
                    if settings_menu_index == 1:
                        pass
                    if settings_menu_index == 2:
                        game_state = 0
                        settings_menu_index = 0
                if key == sdl2.SDLK_m:
                    game_state = 0
                if key == sdl2.SDLK_LEFT:
                    if settings_menu_index == 0:
                        volume -= 1
                        sdl2.sdlmixer.Mix_MasterVolume(volume)
                    if settings_menu_index == 1:
                        sensitivity_rw -= 1
                if key == sdl2.SDLK_RIGHT:
                    if settings_menu_index == 0:
                        volume += 1
                        sdl2.sdlmixer.Mix_MasterVolume(volume)
                    if settings_menu_index == 1:
                        sensitivity_rw += 1
                if volume < 0:
                    volume = 0
                if volume > 100:
                    volume = 100
                if sensitivity_rw < 0:
                    sensitivity_rw = 0
                if sensitivity_rw > 100:
                    sensitivity_rw = 100
            if not moet_afsluiten and game_state == 2:
                if key == sdl2.SDLK_m:
                    game_state = 0


        elif event.type == sdl2.SDL_KEYUP:
            key = event.key.keysym.sym
            if key == sdl2.SDLK_f or key == sdl2.SDLK_s:
                pass
            if not moet_afsluiten and game_state == 1:
                pass
            if not moet_afsluiten and game_state == 2:
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
        elif event.type == sdl2.SDL_MOUSEMOTION and game_state == 2:
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
            #d_muur = 10 / d_muur
            kolom = BREEDTE-kolom
            scherm_y = HOOGTE / 2
            renderer.copy(wall_texture, srcrect=(rij, 0, 1, 100),
                          dstrect=(kolom, scherm_y - d_muur * hoogte / 2, 1, d_muur * hoogte))


def renderText(font, renderer, text, x, y, window = 0):
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


def wheelSprite(renderer,sprite):
    x_pos = (BREEDTE - 250) // 2
    y_pos = HOOGTE - 230
    renderer.copy(sprite,dstrect=(x_pos,y_pos,250,250))

def render_sprites(renderer, sprites, player):
    sprites.sort(reverse=True, key=lambda sprite: np.sqrt((sprite.x - player.p_x) ** 2 + (sprite.y - player.p_y) ** 2))#Sorteren op afstand
    #Dit is beetje dubbel atm omdat je een stap later weer de afstand berekend

    for sprite in sprites:
        # richting
        sprite_distance = np.sqrt((sprite.x - player.p_x) ** 2 + (sprite.y - player.p_y) ** 2)
        sprite_distance += math.pi


        if sprite_distance >= 60:continue;
        # grootte
        sprite_size_breedte = sprite.breedte/sprite_distance*10
        sprite_size_hoogte = sprite.hoogte/sprite_distance*10

        # hoek

        hoek_sprite = np.arctan((sprite.y-player.p_y)/(sprite.x-player.p_x))


        if player.p_x > sprite.x and player.p_y > sprite.y: hoek_sprite += math.pi;
        if player.p_x > sprite.x and player.p_y < sprite.y: hoek_sprite += math.pi;
        if player.p_x < sprite.x and player.p_y > sprite.y: hoek_sprite += 2*math.pi;


        """while player.hoek <= 2 * np.pi: #Fixxed this in speler.draaien()
            player.hoek += 2 * np.pi

        while player.hoek >= 2 * np.pi:
            player.hoek -= 2 * np.pi"""

        hoek_verschil = player.hoek - hoek_sprite
        if abs(hoek_verschil) >= (math.pi/3.7): continue; #net iets minder gepakt als 4 zodat hij langs rechts er niet afspringt



        screen_y = (HOOGTE - sprite_size_hoogte) / 2    #wordt in het midden gezet
        screen_x = int(BREEDTE / 2 + hoek_verschil * (BREEDTE * 2) / math.pi - sprite_size_breedte / 2)

        renderer.copy(sprite.image,dstrect=(screen_x,screen_y, sprite_size_breedte,sprite_size_hoogte))


def show_fps(font, renderer):
    fps_list = [1]
    loop_time = 0

    while True:
        fps_list.append(1 / (time.time() - loop_time))
        """if fps_list[-1] > 190:
            print(fps_list[-1])"""
        """if (time.time() - loop_time) != 0:
            fps_list.append(1 / (time.time() - loop_time))
            #print(min(fps_list))"""
        loop_time = time.time()

        fps = sum(fps_list) / len(fps_list)
        if len(fps_list) == 20:
            fps_list.pop(0)
        text = sdl2.ext.renderer.Texture(renderer, font.render_text(f'{fps:.2f} fps'))
        renderer.copy(text, dstrect=(int((BREEDTE - text.size[0]) / 2), 20,
                                     text.size[0], text.size[1]))
        yield fps


def muziek_spelen(geluid, looped=False, channel=1):
    global volume
    if not sound:
        return
    if geluid == 0:
        sdl2.sdlmixer.Mix_HaltChannel(channel)
    else:
        sdl2.sdlmixer.Mix_MasterVolume(volume)
        if sdl2.sdlmixer.Mix_Playing(channel) == 1:
            return
        geluiden = [
            sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/8-Bit Postman Pat.wav", "UTF-8")),
            sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/arcade_select.wav", "UTF-8")),
            sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/arcade_start.wav", "UTF-8")),
            sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/concrete-footsteps.wav", "UTF-8"))
        ]
        liedjes = {
            "main menu": geluiden[0],
            "main menu select": geluiden[1],
            "game start": geluiden[2],
            "footsteps": geluiden[3]
        }
        if looped == False:
            sdl2.sdlmixer.Mix_PlayChannel(channel, liedjes[geluid], 0)
        else:
            sdl2.sdlmixer.Mix_PlayChannel(channel, liedjes[geluid], -1)


def menu_nav():
    global game_state, main_menu_index, settings_menu_index, main_menu_positie, settings_menu_positie
    if game_state == 0:
        if main_menu_index == 0:
            main_menu_positie = POSITIE_START_GAME
            return
        elif main_menu_index == 1:
            main_menu_positie = POSITIE_SETTINGS
            return
        elif main_menu_index == 2:
            main_menu_positie = POSITIE_QUIT_GAME
            return
        if main_menu_index > 2:
            main_menu_index = 0
        if main_menu_index < 0:
            main_menu_index = 2
    elif game_state == 1:
        if settings_menu_index == 0:
            settings_menu_positie = [150, 200]
            return
        elif settings_menu_index == 1:
            settings_menu_positie = [200, 230]
            return
        elif settings_menu_index:
            settings_menu_positie = POSITIE_SETTINGS_BACK
        if settings_menu_index > 2:
            settings_menu_index = 0
        if settings_menu_index < 0:
            settings_menu_index = 2


def pathfinding_gps(speler_pos_x, speler_pos_y):
    # Voor het pathfinden van de gps gebruiken we het A* algoritme
    # Begin- en eindnodes initialiseren met 0 cost
    begin = Node(None, (math.floor(speler_pos_x), math.floor(speler_pos_y)))
    begin.g = begin.h = begin.f = 0
    eind = Node(None, (8, 8))
    eind.g = eind.h = eind.f = 0

    # initialiseer open en closed lijsten
    open_list = []  # dit is de lijst van punten die geëvalueerd moeten worden
    closed_list = []  # dit is de lijst van punten die al geëvalueerd zijn
    open_list.append(begin)  # startnode toevoegen aan openlijst
    # loopen tot het einde gevonden is
    while len(open_list) > 0:
        # tijdelijke variabele current maken, is de node met minste f cost (in begin de beginnode)
        current_node = open_list[0]
        current_index = 0
        # zoeken naar de node met kleinste f cost
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index
        # current in de closed_list steken, aangezien deze geëvalueerd wordt
        open_list.pop(current_index)
        closed_list.append(current_node)
        # als de current node de eindnode is, dan is pathfinding voltooid
        if current_node == eind:
            pad = []
            current = current_node
            while current is not None:  # enkel het beginnende node heeft geen parent (None)
                pad.append(current.positie)
                current = current.parent
            return pad
        # nieuwe child nodes creëeren
        children_list = []
        for nieuwe_positie in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # enkel child nodes aanmaken boven, onder, links of rechts van de current node
            # positie krijgen
            node_positie = (current_node.positie[0] + nieuwe_positie[0], current_node.positie[1] + nieuwe_positie[1])  # huidige node x en y + "verschuiving" x en y
            # kijken of deze nodes binnen de wereldmap vallen
            if node_positie[0] > world_map.shape[0] or node_positie[0] < 0 or node_positie[1] > world_map.shape[1] or node_positie[1] < 0:
                continue  # gaat naar de volgende nieuwe_positie
            # kijken of we op deze node kunnen stappen
            if world_map[node_positie[0]][node_positie[1]] != 0:
                continue
            # nieuwe node creëeren
            nieuwe_node = Node(current_node, node_positie)
            children_list.append(nieuwe_node)
        for child in children_list:
            # kijken of child_node in de closed lijst zit
            is_closed = False
            for closed_child in closed_list:
                if child == closed_child:
                    is_closed = True
            if is_closed:
                continue

            # cost waarden berekenen
            child.g = current_node.g + 1  # afstand tot begin node
            child.h = ((child.positie[0] - eind.positie[0])**2) + ((child.positie[1]-eind.positie[1])**2)  # afstand tot eind node
            child.f = child.g + child.h

            # kijken of child_node in de open lijst zit
            is_open = False
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    is_open = True
            if is_open:
                continue
            # indien niet al in open list, nu toevoegen
            open_list.append(child)



def main():
    global game_state, BREEDTE, volume, sensitivity_rw, sensitivity
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
    muren_info = []
    for i,muur in enumerate(soort_muren):
        muren_info.append((muur.size[0], muur.size[1]))


    # Inladen wereld_mappen
    map_resources = sdl2.ext.Resources(__file__,"mappen")
    # alle mappen opslaan in sdl2 textures
    map_textuur = []
    for i,map in enumerate(worldlijst):
        naam = f"map{i}.png"
        map_textuur.append(factory.from_image(map_resources.get_path(naam)))

    #Inladen sprites
    wheel = factory.from_image(resources.get_path("Wheel.png"))
    sprites = []
    tree = factory.from_image(resources.get_path("Tree_gecropt.png"))

    sprites.append(Sprite(tree, x=10, y=10))
    sprites.append(Sprite(tree, x=15, y=10))
    sprites.append(Sprite(tree, x=3, y=3))


    # Initialiseer font voor de fps counter
    font = sdl2.ext.FontTTF(font='CourierPrime.ttf', size=20, color=kleuren[7])
    fps_generator = show_fps(font, renderer)


    #Start  audio
    sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.sdlmixer.MIX_DEFAULT_FORMAT, 2, 1024)  # 44100 = 16 bit, cd kwaliteit
    sdl2.sdlmixer.Mix_AllocateChannels(6)
    sdl2.sdlmixer.Mix_MasterVolume(80)

    achtergrond = factory.from_image(resources.get_path("game_main_menu.png"))
    menu_pointer = factory.from_image(resources.get_path("game_main_menu_pointer.png"))
    settings_menu = factory.from_image(resources.get_path("settings_menu.png"))

    #Test Variable
    t = []

    while not moet_afsluiten:
        muziek_spelen("main menu", True)
        sdl2.SDL_SetRelativeMouseMode(False)
        while game_state == 0 and not moet_afsluiten:
            start_time = time.time()
            renderer.clear()
            delta = time.time() - start_time
            verwerk_input(delta)
            menu_nav()
            renderer.copy(achtergrond,
                          srcrect=(0, 0, achtergrond.size[0], achtergrond.size[1]),
                          dstrect=(0, 0, BREEDTE, HOOGTE))
            renderer.copy(menu_pointer,
                          srcrect=(0, 0, menu_pointer.size[0], menu_pointer.size[1]),
                          dstrect=(main_menu_positie[0], main_menu_positie[1], 80, 50))
            renderer.present()

        while game_state == 1 and not moet_afsluiten:
            start_time = time.time()
            renderer.clear()
            delta = time.time() - start_time
            verwerk_input(delta)
            menu_nav()
            renderer.copy(settings_menu,
                          srcrect=(0, 0, settings_menu.size[0], settings_menu.size[1]),
                          dstrect=(0, 0, BREEDTE, HOOGTE))
            volume_text = sdl2.ext.renderer.Texture(renderer, font.render_text(f"Volume: {volume}"))
            sensitivity_rw_text = sdl2.ext.renderer.Texture(renderer, font.render_text(f"Sensitivity: {sensitivity_rw}"))
            renderer.copy(volume_text, dstrect=(10, 200, volume_text.size[0], volume_text.size[1]))
            renderer.copy(sensitivity_rw_text, dstrect=(10, 230, sensitivity_rw_text.size[0], sensitivity_rw_text.size[1]))
            if settings_menu_index != 2:
                text = sdl2.ext.renderer.Texture(renderer, font.render_text("<>"))
                renderer.copy(text, dstrect=(settings_menu_positie[0], settings_menu_positie[1], text.size[0], text.size[1]))
            else:
                renderer.copy(menu_pointer,
                          srcrect=(0, 0, menu_pointer.size[0], menu_pointer.size[1]),
                          dstrect=(settings_menu_positie[0], settings_menu_positie[1], 80, 50))
            renderer.present()

        sdl2.SDL_SetRelativeMouseMode(True)
        if game_state != 0:  # enkel als game_state van menu naar game gaat mag game start gespeeld worden
            muziek_spelen(0)
            muziek_spelen("game start", False, 3)
        if game_state != 1:
            config.set("settings","volume",f"{volume}")  # indien er uit de settings menu gekomen wordt, verander de config file met juiste settings
            config.set("settings", "sensitivity", f"{sensitivity_rw}")
            sensitivity = -2 * sensitivity_rw + 300
            with open("config.ini", "w") as f:
                config.write(f)

        pad = pathfinding_gps(p_speler_x, p_speler_y)
        print(pad)
        while game_state == 2 and not moet_afsluiten:
            # Onthoud de huidige tijd
            start_time = time.time()
            # Reset de rendering context
            renderer.clear()
            render_floor_and_sky(renderer)
            # Render de huidige frame
            (d, v, kl) = speler.n_raycasting(world_map)

            t1 = time.time()
            renderen(renderer, d, v, kl, soort_muren, muren_info)

            render_sprites(renderer, sprites, speler)
            #t.append(time.time()-t1)
            draw_nav(renderer, world_map, map_textuur[wereld_nr], speler)
            delta = time.time() - start_time
            if speler.in_auto:
                wheelSprite(renderer, wheel)

            verwerk_input(delta)

            # Toon de fps
            next(fps_generator)

            # Verwissel de rendering context met de frame buffer
            renderer.present()
            #print(sum(t)/len(t))

    # Sluit SDL2 af
    sdl2.ext.quit()


if __name__ == '__main__':
    #profiler = cProfile.Profile()
    #profiler.enable()
    main()
    #profiler.disable()
    #stats = pstats.Stats(profiler)
    #stats.dump_stats('data.prof')
