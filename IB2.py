# import cProfile
# import pstats
#from line_profiler_pycharm import profile

import math
import time
import random
import numpy as np
import heapq
import sdl2.ext
import sys
import sdl2.sdlimage
import sdl2.sdlmixer
from sdl2 import *
from worlds import *
from Classes import *
from Raycaster import *
from rendering import *
from configparser import ConfigParser

config = ConfigParser()

# Constanten
BREEDTE = 1000
HOOGTE = int(BREEDTE/10*7)
POSITIE_MAIN_MENU = [
    [365, 253],  # 0: Start Game
    [300, 401],  # 1: Settings
    [420, 572]  # 2: Quit Game
]
POSITIE_SETTINGS_MENU = [
    [170, 55],  # 0: Back
    [150, 200],  # 1: volume
    [200, 230]  # 2: sensitivity
]
POSITIE_PAUZE = [
    [540, 175],  # 0: Continue
    [520, 310],  # 1: Settings
    [595, 450],  # 2: Main Menu
    [590, 585]  # 3: Quit Game
]
#
# Globale variabelen
#
game_state = 0  # 0: main menu, 1: settings menu, 2: game actief, 3: garage,
sound = True
paused = False
main_menu_index = 0
settings_menu_index = 0
main_menu_positie = [0, 0]
settings_menu_positie = [0, 0]
pauze_index = 0
eindbestemming = (50*9, 50*9)
pad = []
pauze_positie = POSITIE_PAUZE[0]
sprites = []
lijst_mogelijke_bestemmingen = []
# verwerking van config file: ook globale variabelen
config.read("config.ini")
volume = int(config.get("settings", "volume"))
sensitivity_rw = int(config.get("settings",
                                "sensitivity"))  # echte sensitivity gaat van 100 - 300, 300 traagst, 100 snelst. Raw sensitivity gaat van 0 tot 100
sensitivity = -2 * sensitivity_rw + 300

# wordt op True gezet als het spel afgesloten moet worden
moet_afsluiten = False

# positie van de speler
p_speler_x, p_speler_y = 50.4 * 9, 49 * 9

# richting waarin de speler kijkt
r_speler_hoek = math.pi / 4
# FOV
d_camera = 1
#
# Speler aanmaken
speler = Player(p_speler_x, p_speler_y, r_speler_hoek, BREEDTE)
speler.aanmaak_r_stralen(d_camera=d_camera)

# world
world_map = np.ones((10,10))
# world_map = worldlijst[wereld_nr]
# y_dim, x_dim = np.shape(world_map)




# Vooraf gedefinieerde kleuren
kleuren = [
    sdl2.ext.Color(0, 0, 0),  # 0 = Zwart
    sdl2.ext.Color(255, 0, 20),  # 1 = Rood
    sdl2.ext.Color(0, 255, 0),  # 2 = Groen
    sdl2.ext.Color(0, 0, 255),  # 3 = Blauw
    sdl2.ext.Color(225, 165, 0),  # 4 = oranje
    sdl2.ext.Color(64, 64, 64),  # 4 = Donker grijs
    sdl2.ext.Color(128, 128, 128),  # 5 = Grijs
    sdl2.ext.Color(192, 192, 192),  # 6 = Licht grijs
    sdl2.ext.Color(255, 255, 255),  # 7 = Wit
    sdl2.ext.Color(120, 200, 250),  # 8 = Blauw_lucht
    sdl2.ext.Color(106, 13, 173)  # 9 = Purple
]
kleuren_textures = []

# Start Audio
sdl2.sdlmixer.Mix_Init(0)
sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.sdlmixer.MIX_DEFAULT_FORMAT, 2, 1024)  # 44100 = 16 bit, cd kwaliteit
sdl2.sdlmixer.Mix_AllocateChannels(6)
sdl2.sdlmixer.Mix_MasterVolume(80)
geluiden = [
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/8-Bit Postman Pat.wav", "UTF-8")),
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/arcade_select.wav", "UTF-8")),
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/arcade_start.wav", "UTF-8")),
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/concrete-footsteps.wav", "UTF-8")),
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/throw sound effect.wav", "UTF-8"))
]


#
# Verwerkt alle input van het toetsenbord en de muis
#
# Argumenten:
# @delta       Tijd in milliseconden sinds de vorige oproep van deze functie
#

def verwerk_input(delta,events=0):
    global moet_afsluiten, index, world_map, game_state, main_menu_index, settings_menu_index, volume, sensitivity
    global sensitivity_rw, paused, pauze_index, sprites

    # Handelt alle input events af die zich voorgedaan hebben sinds de vorige
    # keer dat we de sdl2.ext.get_events() functie hebben opgeroepen
    if events == 0:
        events = sdl2.ext.get_events()
    key_states = sdl2.SDL_GetKeyboardState(None)
    if (key_states[sdl2.SDL_SCANCODE_UP] or key_states[sdl2.SDL_SCANCODE_E]) and game_state == 2 and not paused:
        speler.move(1, 0.1, world_map)
        muziek_spelen("footsteps", False, 4)
    if (key_states[sdl2.SDL_SCANCODE_DOWN] or key_states[sdl2.SDL_SCANCODE_D]) and game_state == 2 and not paused:
        speler.move(-1, 0.1, world_map)
        muziek_spelen("footsteps", False, 4)
    if (key_states[sdl2.SDL_SCANCODE_RIGHT] or key_states[sdl2.SDL_SCANCODE_F]) and game_state == 2 and not paused:
        speler.draaien(-math.pi / sensitivity)
    if (key_states[sdl2.SDL_SCANCODE_LEFT] or key_states[sdl2.SDL_SCANCODE_S]) and game_state == 2 and not paused:
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
            if key == sdl2.SDLK_r:
                x, y = speler.position
                coords = ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1))
                for coord in coords:
                    positie = (y + coord[1], x + coord[0])  # huidige node x en y + "verschuiving" x en y
                    # kijken of deze nodes binnen de wereldmap vallen
                    if positie[0] > world_map.shape[1] or positie[0] < 0 or positie[1] > world_map.shape[0] or positie[
                        1] < 0:
                        continue
                    if world_map[positie] < 0:
                        deur = deuren[world_map[positie]]
                        deur.start()
            if not moet_afsluiten and game_state == 0:
                if key == sdl2.SDLK_DOWN:
                    main_menu_index += 1
                    muziek_spelen("main menu select", channel=2)
                if key == sdl2.SDLK_UP:
                    main_menu_index -= 1
                    muziek_spelen("main menu select", channel=2)
                if key == sdl2.SDLK_SPACE or key == sdl2.SDLK_KP_ENTER or key == sdl2.SDLK_RETURN:
                    if main_menu_index == 0:
                        game_state = 2
                        return
                    if main_menu_index == 1:
                        game_state = 1
                        return
                    if main_menu_index == 2:
                        moet_afsluiten = True
                        break
            if not moet_afsluiten and game_state == 1:
                if key == sdl2.SDLK_DOWN:
                    settings_menu_index += 1
                    muziek_spelen("main menu select", False, 2)
                if key == sdl2.SDLK_UP:
                    settings_menu_index -= 1
                    muziek_spelen("main menu select", False, 2)
                if key == sdl2.SDLK_SPACE or key == sdl2.SDLK_KP_ENTER or key == sdl2.SDLK_RETURN:
                    if settings_menu_index == 0:
                        game_state = 0 if not paused else 2
                        settings_menu_index = 0
                        return
                    if settings_menu_index == 1:
                        pass
                    if settings_menu_index == 2:
                        pass
                if key == sdl2.SDLK_LEFT:
                    if settings_menu_index == 1:
                        volume -= 1
                        sdl2.sdlmixer.Mix_MasterVolume(volume)
                    if settings_menu_index == 2:
                        sensitivity_rw -= 1
                if key == sdl2.SDLK_RIGHT:
                    if settings_menu_index == 1:
                        volume += 1
                        sdl2.sdlmixer.Mix_MasterVolume(volume)
                    if settings_menu_index == 2:
                        sensitivity_rw += 1
                if volume < 0:
                    volume = 0
                if volume > 100:
                    volume = 100
                if sensitivity_rw < 0:
                    sensitivity_rw = 0
                if sensitivity_rw > 100:
                    sensitivity_rw = 100
                if key == sdl2.SDLK_m:
                    game_state = 0 if not paused else 2
            if not moet_afsluiten and game_state == 2:
                if key == sdl2.SDLK_m and not paused:
                    game_state = 0
                    speler.reset()
                if key == sdl2.SDLK_p:
                    paused = True if not paused else False
                if key == sdl2.SDLK_UP or key == sdl2.SDLK_DOWN or key == sdl2.SDLK_e or key == sdl2.SDLK_d:
                    pass
                if paused:
                    if key == sdl2.SDLK_UP or key == sdl2.SDLK_e:
                        pauze_index -= 1
                        muziek_spelen("main menu select", False, 2)
                    if key == sdl2.SDLK_DOWN or key == sdl2.SDLK_d:
                        pauze_index += 1
                        muziek_spelen("main menu select", False, 2)
                    if pauze_index == 0 and key == sdl2.SDLK_SPACE:
                        paused = False
                    if pauze_index == 1 and key == sdl2.SDLK_SPACE:
                        game_state = 1
                    if pauze_index == 2 and key == sdl2.SDLK_SPACE:
                        game_state = 0
                        paused = False
                        speler.reset()
                    if pauze_index == 3 and key == sdl2.SDLK_SPACE:
                        moet_afsluiten = True
                else:
                    if key == sdl2.SDLK_SPACE:
                        geworpen_doos = speler.trow(world_map)
                        sprites.append(geworpen_doos)
                        muziek_spelen("throwing", channel=2)
        elif event.type == sdl2.SDL_KEYUP:
            key = event.key.keysym.sym
            if key == sdl2.SDLK_f or key == sdl2.SDLK_s:
                pass
            if not moet_afsluiten and game_state == 1:
                pass
            if not moet_afsluiten and game_state == 2:
                if key == sdl2.SDLK_UP or key == sdl2.SDLK_DOWN or key == sdl2.SDLK_e or key == sdl2.SDLK_d:
                    muziek_spelen(0, False, 4)
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
        elif event.type == sdl2.SDL_MOUSEMOTION and game_state == 2 and not paused:
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


def wheelSprite(renderer, sprite):
    x_pos = (BREEDTE - 250) // 2
    y_pos = HOOGTE - 230
    renderer.copy(sprite, dstrect=(x_pos, y_pos, 250, 250))


def render_sprites(renderer, sprites, player, d):
    global world_map
    sprites.sort(reverse=True, key=lambda sprite: sprite.afstanden(player))  # Sorteren op afstand
    # Dit is beetje dubbel atm omdat je een stap later weer de afstand berekend

    for i,sprite in enumerate(sprites):
        if sprite.update(world_map):
            sprites.pop(i)
            continue

        # hoek
        rx = sprite.x - player.p_x
        ry = sprite.y - player.p_y
        hoek_sprite = math.atan2(ry , rx)%(math.pi*2)
        if sprite.afstand >= 60: continue;



        hoek_verschil = abs(player.hoek - hoek_sprite)
        if hoek_verschil >= (math.pi / 3.7):
            continue  # net iets minder gepakt als 4 zodat hij langs rechts er niet afspringt

        a = ((speler.r_speler[0] + speler.r_camera[0] / 1000 - speler.r_speler[1] * rx / ry - speler.r_camera[
            1] * rx / (1000 * ry)) / ((speler.r_camera[0] / 500) - (speler.r_camera[1] * rx / (500 * ry))))
        if not (-BREEDTE*0.6 < a < BREEDTE*0.6):
            continue

        # richting
        sprite_distance = sprite.afstand*abs(math.cos(hoek_verschil))
        sprite_distance += 0.01



        # grootte
        sprite_size_breedte = int(sprite.breedte / sprite_distance * 10)
        sprite_size_hoogte = sprite.hoogte / sprite_distance * 10

        """a = np.array([[rx,speler.r_camera[0]/500],[ry,speler.r_camera[1]/500]])
        b = np.array([speler.r_speler[0]+speler.r_camera[0]/1000,speler.r_speler[1]+speler.r_camera[1]/1000])
        print(np.linalg.solve(a,b)[1])
        c = np.linalg.solve(a,b)[1]"""

        screen_y = (sprite.height - sprite_size_hoogte) / 2  # wordt in het midden gezet
        screen_x = int(BREEDTE / 2 - a - sprite_size_breedte / 2)
        #renderer.copy(sprite.image, dstrect=(screen_x, screen_y, sprite_size_breedte, sprite_size_hoogte))

        
        for i in range(sprite_size_breedte):
            kolom = i+ screen_x
            if kolom >= BREEDTE:
                continue
            if d[kolom] <= sprite.afstand:
                continue
            renderer.copy(sprite.image, srcrect=(i/sprite_size_breedte*sprite.breedte, 0, 1*sprite.afstand, sprite_size_hoogte*sprite.afstand),
                dstrect=(kolom, screen_y, 1, sprite_size_hoogte))





def collision_detection(renderer, speler,sprites,hartje):
    global eindbestemming, pad
    for sprite in sprites:
        if sprite.afstand < 1 and sprite.schadelijk:
            sprites.remove(sprite)
            speler.aantal_hartjes -= 1
        sprite_pos = (math.floor(sprite.position[0]), math.floor(sprite.position[1]))
        if sprite.is_doos:
            print(f"sprite pos: {sprite_pos}")
            print(f"eindbestemming: {eindbestemming}")
        if sprite_pos == eindbestemming and sprite.is_doos:
            print("test")
            eindbestemming = bestemming_selector()
            pad = pathfinding_gps2(eindbestemming)
            sprites.remove(sprite)
    hartjes = speler.aantal_hartjes
    i = 1
    while i <= hartjes:
        x_pos = BREEDTE - 50  - 50*i
        y_pos = HOOGTE - 70
        renderer.copy(hartje, dstrect=(x_pos, y_pos, 50, 50))
        i += 1

def show_fps(font, renderer):
    fps_list = [1]
    loop_time = 0

    while True:
        fps_list.append(1 / (time.time() - loop_time))
        """if min(fps_list) < 20:
            print(min(fps_list))
        if fps_list[-1] > 190:
            print(fps_list[-1])
        if (time.time() - loop_time) != 0:
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
    global volume, geluiden
    if not sound:
        return
    if geluid == 0:
        sdl2.sdlmixer.Mix_HaltChannel(channel)
    else:
        sdl2.sdlmixer.Mix_MasterVolume(volume)
        if sdl2.sdlmixer.Mix_Playing(channel) == 1:
            return
        liedjes = {
            "main menu": geluiden[0],
            "main menu select": geluiden[1],
            "game start": geluiden[2],
            "footsteps": geluiden[3],
            "throwing": geluiden[4]
        }
        if looped == False:
            sdl2.sdlmixer.Mix_PlayChannel(channel, liedjes[geluid], 0)
        else:
            sdl2.sdlmixer.Mix_PlayChannel(channel, liedjes[geluid], -1)


def menu_nav():
    global game_state, main_menu_index, settings_menu_index, main_menu_positie, settings_menu_positie, pauze_index, pauze_positie
    if game_state == 0:
        if main_menu_index > 2:
            main_menu_index = 0
        if main_menu_index < 0:
            main_menu_index = 2
        main_menu_positie = POSITIE_MAIN_MENU[main_menu_index]
    elif game_state == 1:
        if settings_menu_index > 2:
            settings_menu_index = 0
        if settings_menu_index < 0:
            settings_menu_index = 2
        settings_menu_positie = POSITIE_SETTINGS_MENU[settings_menu_index]
    elif paused:
        if pauze_index > 3:
            pauze_index = 0
        if pauze_index < 0:
            pauze_index = 3
        pauze_positie = POSITIE_PAUZE[pauze_index]

def pathfinding_gps(eindpositie=(8, 8)):
    return [(450, 450), (451, 450), (451, 449), (452, 449), (452, 448), (453, 448), (453, 447), (453, 446), (453, 445), (453, 444), (453, 443), (453, 442), (453, 441)]
    # Voor het pathfinden van de gps gebruiken we het A* algoritme
    # Begin- en eindnodes initialiseren met 0 cost
    begin = Node(None, speler.position)
    begin.g = begin.h = begin.f = 0
    eind = Node(None, eindpositie)
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
            if item.f < current_node.f or (item.f == current_node.f and item.h < current_node.h):
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
        for nieuwe_positie in [(0, -1), (0, 1), (-1, 0),
                               (1, 0)]:  # enkel child nodes aanmaken boven, onder, links of rechts van de current node
            # positie krijgen
            node_positie = (current_node.positie[0] + nieuwe_positie[0],
                            current_node.positie[1] + nieuwe_positie[1])  # huidige node x en y + "verschuiving" x en y
            # kijken of deze nodes binnen de wereldmap vallen
            if node_positie[0] > world_map.shape[1] or node_positie[0] < 0 or node_positie[1] > world_map.shape[0] or \
                    node_positie[1] < 0:
                continue  # gaat naar de volgende nieuwe_positie
            # kijken of we op deze node kunnen stappen
            if world_map[node_positie[1]][node_positie[0]] > 0:
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
                        break
            """if any(child == closed for closed in closed_list):
                is_closed = True """
            if is_closed:
                continue
            # cost waarden berekenen
            child.g = current_node.g + 1  # afstand tot begin node
            #child.g = current_node.g + 10
            #child.h = int(10*np.linalg.norm((child.positie[0] - eind.positie[0], child.positie[1]-eind.positie[1])))  # afstand tot eind node
            y = abs(child.positie[0] - eind.positie[0])
            x = abs(child.positie[1] - eind.positie[1])
            #print(y)
            #print(x)
            child.h = 14*y + 10*(x-y) if y < x else 14*x + 10*(y-x)
            child.f = child.g + child.h
            print(f"h = {child.h}, g = {child.g}, f = {child.f}")

            # kijken of child_node in de open lijst zit
            is_open = False
            """for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    is_open = True 
                    break """
            if any(child == open_node and child.g > open_node.g for open_node in open_list):
                is_open = True
            """if any(child == open_node for open_node in open_list):
                is_open = True """
            if is_open:
                continue
            # indien niet al in open list, nu toevoegen
            open_list.append(child)

def heuristiek(a, b):
    y = abs(a[0]-b[0])
    x = abs(a[1]-b[1])
    return 14*y + 10*(x-y) if y < x else 14*x + 10*(y-x)
def pathfinding_gps2(eindpositie):
    start = speler.position
    buren = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # nu definieren, oogt beter bij de for loop
    close_set = set()  # set is ongeorderd, onveranderbaar en niet geïndexeerd
    came_from = {}  # dictionary die "parents" van de node klasse vervangt, aangezien zelfgemaakte klassen niet zo goed meespelen met heaps
    g_score = {start: 0}  # dictionary die g scores bijhoudt van alle posities
    f_score = {start: heuristiek(start, eindpositie)}  # dictionary die onze f scores bijhoudt bij iteratie
    oheap = []  # ~open_list van eerste pathfinding algoritme, bevat alle posities die we behandelen voor het kortste pad te vinden
    heapq.heappush(oheap, (f_score[start], start))  # we pushen de startpositie en f score op de oheap (f score later nodig)

    while oheap:  # kijken dat er posities zijn die we kunnen behandelen
        current = heapq.heappop(oheap)[1]  # pop en return kleinste item van de heap: hier bekijken we de kleinste f score, [1] betekent dat we de positie terug willen
        if current == eindpositie:
            pad = []
            while current in came_from:
                pad.append(current)
                current = came_from[current]
            return pad
        close_set.add(current)  # indien we geen pad gevonden hebben, zetten we de huidige positie op de closed set, aangezien we deze behandelen

        for positie in buren:  # door alle buren gaan + hun g score berekenen
            buur = (current[0] + positie[0], current[1] + positie[1])
            buur_g_score = g_score[current] + heuristiek(current, buur)
            if buur[0] > world_map.shape[1] or buur[0] < 0 or buur[1] > world_map.shape[0] or \
                    buur[1] < 0:
                continue  # gaat naar de volgende buur
            # kijken of we op deze positie kunnen stappen
            if world_map[buur[1]][buur[0]] > 0:
                continue
            if buur in close_set and buur_g_score >= g_score.get(buur, 0):  # dictionary.get(): buur: de positie van waar we de g score van terug willen, 0 indien er geen buur bestaat
                continue  # kijken of de buur al behandeld is en ofdat de g score van de buur die we nu berekenen groter is als een vorige buur (indien kleiner kan dit wel een beter pad geven)
            if buur_g_score < g_score.get(buur, 0) or buur not in [i[1] for i in oheap]:  # indien huidige buur g score lager is als een vorige buur of als de buur niet in de heap zit
                came_from[buur] = current  # buur komt van huidige positie
                g_score[buur] = buur_g_score
                f_score[buur] = buur_g_score + heuristiek(buur, eindpositie)
                heapq.heappush(oheap, (f_score[buur], buur))




def positie_check():
    if speler.position == (450, 450):
        print("bestemming bereikt")

def bestemming_selector(mode=""):
    global world_map, lijst_mogelijke_bestemmingen
    if mode == "start":
        lijst_mogelijke_bestemmingen = np.transpose((world_map == -1).nonzero()).tolist()
        return
    x, y = speler.position
    """checkmap = world_map[y-5:y+4, x-5:x+4]
    """
    spelerpositie = list(speler.position)
    range_min = [spelerpositie[0] - 20, spelerpositie[1] - 20]
    range_max = [spelerpositie[0] + 20, spelerpositie[1] + 20]
    """
    dichte_bestemmingen_bool = np.any() """

    dichte_locaties = list(filter(lambda m: m[0] >= range_min[0] and m[1] >= range_min[1] and m[0] <= range_max[0] and m[1] <= range_max[1], lijst_mogelijke_bestemmingen))
    print(f"len dichte locaties = {len(dichte_locaties)}")
    rnd = randint(0, len(dichte_locaties)-1)  # len(dichte_locaties) kan 0 zijn indien er geen dichte locaties zijn: vermijden door groot genoeg gebied te zoeken
    print(rnd)
    bestemming = tuple(dichte_locaties[rnd])
    print(spelerpositie)
    print(bestemming)
    return bestemming
    """
    lijst = []
    for i in range(-10,11):
        for j in range(-10,11):
            if world_map[y+i][x+j] == -1:
                lijst.append((y+i,x+j))
    if len(lijst) == 0:
        bestemming = (50*9, 50*9)
        return bestemming
    rnd = randint(0, len(lijst)-1)
    bestemming = lijst[rnd]
    print(bestemming)
    return bestemming
    print(checkmap)"""

"""Functies voor interactieve knoppen"""
def start(button, event):
    global game_state
    game_state = 2
def settings(button, event):
    global game_state
    game_state = 1
def quit(button, event):
    global moet_afsluiten
    moet_afsluiten = True

#@profile
def main():
    global game_state, BREEDTE, volume, sensitivity_rw, sensitivity, world_map, kleuren_textures, sprites, eindbestemming, pad

    inf_world = Map()
    inf_world.start()
    # inf_world.map_making(speler)
    world_map = inf_world.world_map



    # Initialiseer de SDL2 bibliotheek
    sdl2.ext.init()

    # Maak een venster aan om de game te renderen
    window = sdl2.ext.Window("Project Ingenieursbeleving 2", size=(BREEDTE, HOOGTE))
    window.show()
    # screen = sdl2.ext.surface("Test",size=(BREEDTE,HOOGTE))
    # Begin met het uitlezen van input van de muis en vraag om relatieve coordinaten
    sdl2.SDL_SetRelativeMouseMode(True)

    # Maak een renderer aan zodat we in ons venster kunnen renderen
    renderer = sdl2.ext.Renderer(window, flags=sdl2.render.SDL_RENDERER_ACCELERATED)


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
        factory.from_image(resources.get_path("Gruis_house.png")),  # 5
        factory.from_image(resources.get_path("hedge.png"))  # 6
    ]
    muren_info = []
    for i, muur in enumerate(soort_muren):
        muren_info.append((muur.size[0], 890))
    kleuren_textures = [factory.from_color(kleur, (1, 1)) for kleur in kleuren]
    # Inladen wereld_mappen
    map_resources = sdl2.ext.Resources(__file__, "mappen")
    # alle mappen opslaan in sdl2 textures
    inf_world.png = factory.from_image(map_resources.get_path('map.png'))


    # Inladen sprites
    hartje = factory.from_image(resources.get_path("Hartje.png"))
    wheel = factory.from_image(resources.get_path("Wheel.png"))
    tree = factory.from_image(resources.get_path("Tree_gecropt.png"))
    sprite_map_png = factory.from_image(resources.get_path("map_boom.png"))
    doos = factory.from_image(resources.get_path("doos.png"))
    map_doos = factory.from_image(resources.get_path("map_doos.png"))
    speler_png = factory.from_image(resources.get_path("speler_sprite.png"))
    speler.doos = doos
    speler.map_doos = map_doos
    speler.png = speler_png

    sprites.append(Sprite(tree, sprite_map_png, 50.4 * 9, 50 * 9, HOOGTE))
    sprites.append(Sprite(tree, sprite_map_png, 49.5 * 9, 50 * 9, HOOGTE))
    sprites.append(Sprite(tree, sprite_map_png, (49 * 9), (49.5 * 9), HOOGTE))



    # Initialiseer font voor de fps counter
    font = sdl2.ext.FontTTF(font='CourierPrime.ttf', size=20, color=kleuren[8])
    fps_generator = show_fps(font, renderer)


    achtergrond = factory.from_image(resources.get_path("game_main_menu_wh_tekst.png"))
    menu_pointer = factory.from_image(resources.get_path("game_main_menu_pointer.png"))
    settings_menu = factory.from_image(resources.get_path("settings_menu.png"))
    pauze_menu = factory.from_image(resources.get_path("pause_menu.png"))

    #UI
    uifactory = sdl2.ext.UIFactory(factory)
    startknop = uifactory.from_image(sdl2.ext.BUTTON,
                                  resources.get_path("start_game.png"))
    settingsknop = uifactory.from_image(sdl2.ext.BUTTON,
                                  resources.get_path("settings.png"))
    quitknop = uifactory.from_image(sdl2.ext.BUTTON,
                                  resources.get_path("quit_game.png"))

    startknop.position = POSITIE_MAIN_MENU[0][0]-310, POSITIE_MAIN_MENU[0][1]-15
    settingsknop.position = POSITIE_MAIN_MENU[1][0]-250, POSITIE_MAIN_MENU[1][1]-15
    quitknop.position = POSITIE_MAIN_MENU[2][0]-375, POSITIE_MAIN_MENU[2][1]-25

    startknop.click += start
    settingsknop.click += settings
    quitknop.click += quit

    spriterenderer = factory.create_sprite_render_system(window)
    uiprocessor = sdl2.ext.UIProcessor()

    while not moet_afsluiten:
        muziek_spelen("main menu", True)
        sdl2.SDL_SetRelativeMouseMode(False)
        while game_state == 0 and not moet_afsluiten:
            start_time = time.time()
            renderer.clear()
            delta = time.time() - start_time
            events = sdl2.ext.get_events()
            """Shitty fix maar UI werkt niet als ik ze in verwerk_inputs oproep"""
            verwerk_input(delta, events)
            for event in events:
                uiprocessor.dispatch([startknop, settingsknop, quitknop], event)
            menu_nav()
            renderer.copy(achtergrond,
                          srcrect=(0, 0, achtergrond.size[0], achtergrond.size[1]),
                          dstrect=(0, 0, BREEDTE, HOOGTE))
            renderer.copy(menu_pointer,
                          srcrect=(0, 0, menu_pointer.size[0], menu_pointer.size[1]),
                          dstrect=(main_menu_positie[0], main_menu_positie[1], 80, 50))
            spriterenderer.render((startknop, settingsknop, quitknop))
            renderer.clear(0)

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
            sensitivity_rw_text = sdl2.ext.renderer.Texture(renderer,
                                                            font.render_text(f"Sensitivity: {sensitivity_rw}"))
            renderer.copy(volume_text, dstrect=(10, 200, volume_text.size[0], volume_text.size[1]))
            renderer.copy(sensitivity_rw_text,
                          dstrect=(10, 230, sensitivity_rw_text.size[0], sensitivity_rw_text.size[1]))
            if settings_menu_index != 0:
                text = sdl2.ext.renderer.Texture(renderer, font.render_text("<>"))
                renderer.copy(text,
                              dstrect=(settings_menu_positie[0], settings_menu_positie[1], text.size[0], text.size[1]))
            else:
                renderer.copy(menu_pointer,
                              srcrect=(0, 0, menu_pointer.size[0], menu_pointer.size[1]),
                              dstrect=(settings_menu_positie[0], settings_menu_positie[1], 80, 50))
            renderer.present()

        sdl2.SDL_SetRelativeMouseMode(True)
        if game_state != 0:  # enkel als game_state van menu naar game gaat mag game start gespeeld worden
            muziek_spelen(0)
            muziek_spelen("game start", channel=3)
            bestemming_selector("start")
            #pad = pathfinding_gps2((50 * 9, 50 * 9))
            eindbestemming = bestemming_selector()
            pad = pathfinding_gps2(eindbestemming)
        if game_state != 1:
            config.set("settings", "volume",
                       f"{volume}")  # indien er uit de settings menu gekomen wordt, verander de config file met juiste settings
            config.set("settings", "sensitivity", f"{sensitivity_rw}")
            sensitivity = -2 * sensitivity_rw + 300
            with open("config.ini", "w") as f:
                config.write(f)

        while game_state == 2 and not moet_afsluiten:
            for key in deuren:
                deuren[key].update()
            # Onthoud de huidige tijd
            start_time = time.time()
            # Reset de rendering context
            renderer.clear()
            render_floor_and_sky(renderer, kleuren_textures)
            # Render de huidige frame
            (d, v, kl), (z_d, z_v, z_k) = (speler.n_raycasting(world_map, deuren))

            # t1 = time.time()
            renderen(renderer, d, v, kl, soort_muren, muren_info)
            if np.any(z_k) != 0:
                z_renderen(renderer, z_d, z_v, z_k, soort_muren, muren_info, deuren)
            render_sprites(renderer, sprites, speler, d)
            collision_detection(renderer, speler, sprites, hartje)
            # t.append(time.time()-t1)
            if pad == None:
                print('NONE')
                eindbestemming = bestemming_selector()
                pad = pathfinding_gps2(eindbestemming)
            elif abs(pad[-1][0] - speler.p_x) > 3 or abs(pad[-1][1] - speler.p_y) > 3:
                #bestemming_selector()
                pad = pathfinding_gps2(eindbestemming)
                print(len(pad))
            draw_nav(renderer, kleuren_textures, inf_world, speler, pad, sprites)
            delta = time.time() - start_time
            if speler.in_auto:
                wheelSprite(renderer, wheel)
            if paused:
                renderer.copy(pauze_menu,
                              srcrect=(0, 0, pauze_menu.size[0], pauze_menu.size[1]),
                              dstrect=(0, 0, BREEDTE, HOOGTE))
                renderer.copy(menu_pointer,
                              srcrect=(0, 0, menu_pointer.size[0], menu_pointer.size[1]),
                              dstrect=(pauze_positie[0], pauze_positie[1], 80, 50))
                menu_nav()
            else:
                positie_check()
                next(fps_generator)

            verwerk_input(delta)

            # Toon de fps
            #next(fps_generator)

            # Verwissel de rendering context met de frame buffer
            renderer.present()
            # print(sum(t)/len(t))

    # Sluit SDL2 af
    sdl2.ext.quit()


if __name__ == '__main__':
    # profiler = cProfile.Profile()
    # profiler.enable()
    main()
    # profiler.disable()
    # stats = pstats.Stats(profiler)
    # stats.dump_stats('data.prof')
