# import cProfile
# import pstats
# from line_profiler_pycharm import profile

import time
import warnings

from pathfinding import pathfinding_gps2, politie_pathfinding
import logging
from multiprocessing import Process, Manager
import sdl2.ext
import sdl2.sdlimage
import sdl2.sdlmixer
from worlds import *
from Classes import Voertuig, Player, PostBus
from rendering import *
from variabelen import *
import serial.tools.list_ports

logging.basicConfig(level=logging.DEBUG, filename="log.log", filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")


def sign(x):
    if abs(x) < 3:
        return 0
    elif abs(x) == x:
        return 1
    else:
        return -1


def verwerk_arduino_input(delta):
    if not dramco_active:
        return
    global dramcontroller

    in_menu = paused or game_over or game_state in [0, 1]

    move_speed = delta / 3  # NEEDS RECALCULATING
    if speler.in_auto:
        move_speed *= 4
    elif game_state == 4:
        move_speed *= 3

    if godmode:
        move_speed *= 1.5

    while dramcontroller.in_waiting:
        lijn = str(dramcontroller.readline())[2:-5]
        data = lijn.split(" ")
        try:
            data[1] = int(data[1])
        except:
            break
        if data[0] == "Roll - now not active" and not in_menu and not show_map:
            speler.move(int(data[1]), move_speed, world_map)
            if not speler.in_auto:
                muziek_spelen("footsteps", channel=4)
            elif speler.car.speed < speler.car.versnelling * 0.0499:
                muziek_spelen(gears[speler.car.versnelling], channel=4)
        elif data[0] == "Pitch" and not in_menu and not show_map:
            if not speler.in_auto:
                speler.draaien(-math.pi * int(data[1]) / (sensitivity * 5))
            else:
                speler.sideways_move(int(data[1]), move_speed, world_map)
        elif data[0] == "Proximity" and not in_menu and not show_map and speler.in_auto:
            speler.move(int(data[1]), move_speed, world_map)
            muziek_spelen(gears[speler.car.versnelling], channel=4)


        elif data[0] == "Roll" and show_map and not in_menu:
            map_positie[1] += sign(int(data[1]))
        elif data[0] == "Pitch" and show_map and not in_menu:
            map_positie[0] += sign(int(data[1]))


#
# Verwerkt alle input van het toetsenbord en de muis
#
# Argumenten:
# @delta       Tijd in milliseconden sinds de vorige oproep van deze functie
#
def verwerk_input(delta, events=0, factory=None):
    global moet_afsluiten, index, world_map, game_state, main_menu_index, settings_menu_index, volume, sensitivity
    global sensitivity_rw, paused, pauze_index, sprites, show_map, map_positie
    global afstand_map, quiting, game_over, game_over_index, money, highscore, pakjes_aantal, garage_index
    global selected_car, gekocht, prijzen, lijst_postbussen, sprites_autos, RGB, kleuren_index, godmode

    verwerk_arduino_input(delta)

    move_speed = delta * 2
    if speler.in_auto:
        move_speed *= 4
    elif game_state == 4:
        move_speed *= 3

    if godmode:
        move_speed *= 1.5

    # Handelt alle input events af die zich voorgedaan hebben sinds de vorige
    # keer dat we de sdl2.ext.get_events() functie hebben opgeroepen
    if events == 0:
        events = sdl2.ext.get_events()

    key_states = sdl2.SDL_GetKeyboardState(None)
    if game_state in [2, 4] and not paused and not show_map and not game_over and not (dramco_active and speler.in_auto):
        if key_states[20]:
            print("a")
        if key_states[sdl2.SDL_SCANCODE_UP] or key_states[sdl2.SDL_SCANCODE_E]:
            speler.move(1, move_speed, world_map)
            if not speler.in_auto:
                muziek_spelen("footsteps", channel=4)
            elif speler.car.speed < speler.car.versnelling * 0.0499:
                muziek_spelen(gears[speler.car.versnelling], channel=4)


        elif key_states[sdl2.SDL_SCANCODE_DOWN] or key_states[sdl2.SDL_SCANCODE_D]:
            speler.move(-1, move_speed, world_map)
            if not speler.in_auto:
                muziek_spelen("footsteps", channel=4)
        if key_states[sdl2.SDL_SCANCODE_RIGHT] or key_states[sdl2.SDL_SCANCODE_F]:
            speler.sideways_move(1, move_speed, world_map)
            if not speler.in_auto:
                muziek_spelen("footsteps", channel=4)
        elif key_states[sdl2.SDL_SCANCODE_LEFT] or key_states[sdl2.SDL_SCANCODE_S]:
            speler.sideways_move(-1, move_speed, world_map)
            if not speler.in_auto:
                muziek_spelen("footsteps", channel=4)
        if (key_states[sdl2.SDL_SCANCODE_LEFT] or key_states[sdl2.SDL_SCANCODE_W]) and not speler.in_auto:
            speler.draaien(math.pi / sensitivity)
        elif (key_states[sdl2.SDL_SCANCODE_RIGHT] or key_states[sdl2.SDL_SCANCODE_R]) and not speler.in_auto:
            speler.draaien(-math.pi / sensitivity)

    if game_state == 2 and show_map:
        if key_states[sdl2.SDL_SCANCODE_UP] or key_states[sdl2.SDL_SCANCODE_E]:
            map_positie[1] += 1
        if key_states[sdl2.SDL_SCANCODE_DOWN] or key_states[sdl2.SDL_SCANCODE_D]:
            map_positie[1] -= 1
        if key_states[sdl2.SDL_SCANCODE_RIGHT] or key_states[sdl2.SDL_SCANCODE_F]:
            map_positie[0] += 1
        if key_states[sdl2.SDL_SCANCODE_LEFT] or key_states[sdl2.SDL_SCANCODE_S]:
            map_positie[0] -= 1
        if key_states[sdl2.SDL_SCANCODE_LSHIFT] or key_states[sdl2.SDL_SCANCODE_L]:
            afstand_map -= 1
        if key_states[sdl2.SDL_SCANCODE_LCTRL] or key_states[sdl2.SDL_SCANCODE_O]:
            afstand_map += 1

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
                quiting += 100
                if quiting > 1000:
                    moet_afsluiten = True
                    break
                continue
            if key == sdl2.SDLK_g and game_state == 4:
                x, y = speler.position
                coords = ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1))
                for coord in coords:
                    positie = (y + coord[1], x + coord[0])  # huidige node x en y + "verschuiving" x en y
                    # kijken of deze nodes binnen de wereldmap vallen
                    if positie[0] > world_map.shape[1] or positie[0] < 0 or positie[1] > world_map.shape[0] or positie[
                        1] < 0:
                        continue
                    if world_map[positie] < -2:
                        deur = [world_map[positie]]
                        speler.start_deur(deur)

            elif key == sdl2.SDLK_g:
                game_state = 3 if game_state == 2 else 2
            if key == sdl2.SDLK_t and game_state in [3, 4]:
                game_state = 2

            if game_state == 0:
                if key == sdl2.SDLK_DOWN or key == sdl2.SDLK_d:
                    main_menu_index += 1
                    muziek_spelen("main menu select", channel=2)
                if key == sdl2.SDLK_UP or key == sdl2.SDLK_e:
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
                        money += pakjes_aantal * 5
                        pakjes_aantal = 0
                        config.set("gameplay", "money", f"{money}")
                        if pakjes_aantal > highscore:
                            config.set("gameplay", "highscore", f"{pakjes_aantal}")
                        with open("config.ini", "w") as f:
                            config.write(f)
                        break
            elif game_state == 1:
                if key == sdl2.SDLK_DOWN or key == sdl2.SDLK_d:
                    settings_menu_index += 1
                    muziek_spelen("main menu select", channel=2)
                if key == sdl2.SDLK_UP or key == sdl2.SDLK_e:
                    settings_menu_index -= 1
                    muziek_spelen("main menu select", channel=2)
                if key == sdl2.SDLK_SPACE or key == sdl2.SDLK_KP_ENTER or key == sdl2.SDLK_RETURN:
                    if settings_menu_index == 0:
                        game_state = 0 if not paused else 2
                        settings_menu_index = 0
                        return
                    if settings_menu_index == 1:
                        pass
                    if settings_menu_index == 2:
                        pass
                    if settings_menu_index == 3:
                        config.set("settings", "volume", "50")
                        config.set("settings", "sensitivity", "50")
                        volume = 50
                        sensitivity_rw = 50
                        with open("config.ini", "w") as f:
                            config.write(f)
                    if settings_menu_index == 4:
                        config.set("gameplay", "highscore", "0")
                        config.set("gameplay", "money", "0")
                        config.set("gameplay", "gekocht", "0")
                        config.set("gameplay", "selected_car", "0")
                        highscore = 0
                        money = 0
                        gekocht = [0]
                        selected_car = 0
                        speler.car = lijst_postbussen[selected_car]
                        with open("config.ini", "w") as f:
                            config.write(f)
                if key == sdl2.SDLK_LEFT or key == sdl2.SDLK_s:
                    if settings_menu_index == 1:
                        volume -= 1
                        sdl2.sdlmixer.Mix_MasterVolume(volume)
                    if settings_menu_index == 2:
                        sensitivity_rw -= 1
                if key == sdl2.SDLK_RIGHT or key == sdl2.SDLK_f:
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
            elif game_state == 2:
                if key == sdl2.SDLK_m and not paused:
                    show_map = not show_map
                if key == sdl2.SDLK_p:
                    paused = not paused

                if key == sdl2.SDLK_j:
                    godmode = not godmode
                    print(f"Godmode: {godmode}")

                if key == sdl2.SDLK_UP or key == sdl2.SDLK_DOWN or key == sdl2.SDLK_e or key == sdl2.SDLK_d:
                    pass
                if paused:
                    if key == sdl2.SDLK_UP or key == sdl2.SDLK_e:
                        pauze_index -= 1
                        muziek_spelen("main menu select", channel=2)
                    if key == sdl2.SDLK_DOWN or key == sdl2.SDLK_d:
                        pauze_index += 1
                        muziek_spelen("main menu select", channel=2)
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
                elif show_map:
                    pass
                elif game_over:
                    if key == sdl2.SDLK_UP or key == sdl2.SDLK_e:
                        game_over_index -= 1
                        muziek_spelen("main menu select", channel=2)
                    if key == sdl2.SDLK_DOWN or key == sdl2.SDLK_d:
                        game_over_index += 1
                        muziek_spelen("main menu select", channel=2)
                    if game_over_index == 0 and key == sdl2.SDLK_SPACE:
                        game_over = False
                    if game_over_index == 1 and key == sdl2.SDLK_SPACE:
                        game_over = False
                        game_state = 0
                    if game_over_index == 2 and key == sdl2.SDLK_SPACE:
                        moet_afsluiten = True
                else:
                    if key == sdl2.SDLK_SPACE and not speler.in_auto:
                        if not speler.doos_vast:
                            if pakjesx - 1 < speler.p_x < pakjesx + 1 and pakjesy - 1 < speler.p_y < pakjesy + 1:
                                speler.doos_vast = True
                                continue
                            for doos in sprites_dozen:
                                if doos.afstand < 1.5:
                                    sprites_dozen.remove(doos)
                                    speler.doos_vast = True
                                    break
                            if not speler.car.dozen or speler.doos_vast: continue;
                            backend_car = speler.car.x - speler.car.vector[0], speler.car.y - speler.car.vector[1]
                            afstand_back = (speler.p_x - backend_car[0]) ** 2 + (speler.p_y - backend_car[1]) ** 2
                            if speler.car.afstand < 2 and afstand_back < 2.5:
                                speler.doos_vast = True
                                speler.car.dozen -= 1
                                # IB2
                                if dramco_active:
                                    dramcontroller.write(("L" + str(min(5, speler.car.dozen))).encode(encoding='ascii'))
                        elif speler.laatste_doos < time.time() - 0.5:
                            geworpen_doos = speler.trow(world_map)
                            sprites_dozen.append(geworpen_doos)
                            muziek_spelen("throwing", channel=2)
                            # IB2 sem2
                            if dramco_active:
                                dramcontroller.write("1".encode(encoding='ascii'))
                                pass

                            speler.doos_vast = False
            elif game_state == 3:
                if key == sdl2.SDLK_RIGHT or key == sdl2.SDLK_f:
                    garage_index += 1
                if key == sdl2.SDLK_LEFT or key == sdl2.SDLK_s:
                    garage_index -= 1
                if key == sdl2.SDLK_SPACE:
                    if speler.car in sprites_autos:
                        sprites_autos.remove(speler.car)
                    if garage_index in gekocht:
                        selected_car = garage_index
                        speler.car = lijst_postbussen[selected_car]
                        sprites_autos.append(speler.car)
                        muziek_spelen("main menu select", channel=7)
                    else:
                        if money - prijzen[garage_index] >= 0:
                            money -= prijzen[garage_index]
                            print(f"money: {money}")
                            muziek_spelen("cash register", channel=7)
                            selected_car = garage_index
                            speler.car = lijst_postbussen[selected_car]
                            gekocht.append(garage_index)
                            config.set("gameplay", "money", f"{money}")
                            gekocht_str = "".join(f"{i} " for i in gekocht)
                            config.set("gameplay", "gekocht", gekocht_str)
                        else:
                            sprites_autos.append(speler.car)
                            muziek_spelen("fail", channel=7)
                    config.set("gameplay", "selected_car", f"{selected_car}")
                    with open("config.ini", "w") as f:
                        config.write(f)

                    speler.car.x = auto_x
                    speler.car.y = auto_y

                if key == sdl2.SDLK_l:
                    # IB2
                    lijst_postbussen[garage_index].kleur = car_colors[kleuren_index]
                    kleuren_index += 1
                    if kleuren_index == len(car_colors):
                        kleuren_index = 0
                    change_color(factory, lijst_postbussen, garage_index)
            elif game_state == 4:
                if key == sdl2.SDLK_SPACE:
                    if not speler.doos_vast:
                        speler.doos_vast = True
                    elif speler.laatste_doos < time.time() - 0.5:
                        if kantoor_sprites[0].afstand < 2 and speler.car.dozen < speler.car.max_dozen:
                            speler.car.dozen += 1
                            continue
                        geworpen_doos = speler.trow(world_map)
                        kantoor_sprites.append(geworpen_doos)
                        muziek_spelen("throwing", channel=2)
                        speler.doos_vast = False

            if key == sdl2.SDLK_k:
                if game_state == 2:
                    game_state = 4
                elif game_state == 4:
                    game_state = 2
                    speler.reset()
        elif event.type == sdl2.SDL_KEYUP:
            key = event.key.keysym.sym
            if key == sdl2.SDLK_t:
                if speler.in_auto:
                    speler.car.player_leaving(world_map, speler)
                else:
                    speler.car.player_enter(speler)
                    if speler.in_auto:
                        muziek_spelen("car start", channel=7)
            if key == sdl2.SDLK_y or key == sdl2.SDLK_r:
                if speler.car.versnelling != speler.car.max_versnelling and (
                        speler.car.versnelling == 0 or speler.car.speed > (
                        speler.car.versnelling - 0.5) * speler.car.snelheid_incr):
                    speler.car.versnelling += 1
            elif key == sdl2.SDLK_h or key == sdl2.SDLK_z:
                if speler.car.versnelling != 0:
                    speler.car.versnelling -= 1
            if key == sdl2.SDLK_b:
                speler.reset()
            if key == sdl2.SDLK_n:
                logging.info(f"Speler r-straal = {speler.r_speler}")
                logging.info(f"Speler hoek = {speler.hoek}")
                logging.info(f"Speler positie = {speler.position}")
                logging.info(f"Auto = {speler.car}")
                print(sprites_autos, sprites, speler.car.vector)

            if key == sdl2.SDLK_f or key == sdl2.SDLK_s:
                pass
            if game_state == 1:
                pass
            if game_state == 2:
                if not speler.in_auto:
                    if key == sdl2.SDLK_UP or key == sdl2.SDLK_DOWN or key == sdl2.SDLK_e or key == sdl2.SDLK_d or key == sdl2.SDLK_RIGHT \
                            or key == sdl2.SDLK_LEFT or key == sdl2.SDLK_s or key == sdl2.SDLK_f:
                        muziek_spelen(0, False, 4)
                if speler.in_auto:
                    if key == sdl2.SDLK_UP or key == sdl2.SDLK_DOWN or key == sdl2.SDLK_e or key == sdl2.SDLK_d:
                        muziek_spelen(0, channel=4)
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
        elif event.type == sdl2.SDL_MOUSEMOTION and game_state in [2,
                                                                   4] and not paused and not show_map and not game_over:
            # Aangezien we in onze game maar 1 as hebben waarover de camera
            # kan roteren zijn we enkel geinteresseerd in bewegingen over de
            # X-as
            draai = event.motion.xrel
            if speler.in_auto:
                speler.sideways_move(1, math.pi / 40 * draai * move_speed, world_map)
            else:
                speler.draaien(-math.pi / 100 * draai * move_speed)
                beweging = event.motion.yrel
                speler.move(1, beweging / 20 * move_speed, world_map)
            continue

    # Polling-gebaseerde input. Dit gebruiken we bij voorkeur om bv het ingedrukt
    # houden van toetsen zo accuraat mogelijk te detecteren
    key_states = sdl2.SDL_GetKeyboardState(None)

    # if key_states[sdl2.SDL_SCANCODE_UP] or key_states[sdl2.SDL_SCANCODE_W]:
    # beweeg vooruit...

    if key_states[sdl2.SDL_SCANCODE_ESCAPE]:
        moet_afsluiten = True


def handen_sprite(renderer, handen_doos):
    global verandering
    if speler.isWalking:
        if verandering < 36:
            verandering += 1
        else:
            verandering = 1
    else:
        if verandering > 1:
            verandering -= 1
        if verandering == 19:
            verandering = 1
        else:
            verandering = 1
    # IB2
    """
    uitkomst = 200 + 8 * math.sin(((2 * math.pi) / 36) * verandering)
    if uitkomst < 193:
        dramcontroller.write("3".encode(encoding='ascii'))
    elif uitkomst > 206:
        dramcontroller.write("2".encode(encoding='ascii'))
    """
    renderer.copy(handen_doos,
                  srcrect=(0, 0, handen_doos.size[0], handen_doos.size[1]),
                  dstrect=(200 + 8 * math.sin(((2 * math.pi) / 36) * verandering), 230, BREEDTE - 400, HOOGTE))


def garage(renderer, font, anim_index, garage_menu, lijst_postbussen):
    global garage_index, money
    # info: (prijs, #pakjes, snelheid, versnelling, HP, Gears)
    postbus = lijst_postbussen[garage_index]
    auto = postbus.images
    info = postbus.info

    image = auto[math.floor(anim_index)]
    money_txt = sdl2.ext.renderer.Texture(renderer, font.render_text(f"{money}"))

    if not postbus.render_text:
        prijs = sdl2.ext.renderer.Texture(renderer, font.render_text(f"{info[0]}"))
        pakjes = sdl2.ext.renderer.Texture(renderer, font.render_text(f"{info[1]}"))
        snelheid = sdl2.ext.renderer.Texture(renderer, font.render_text(f"{info[2]}"))
        versnelling = sdl2.ext.renderer.Texture(renderer, font.render_text(f"{info[3]}"))
        hp = sdl2.ext.renderer.Texture(renderer, font.render_text(f"{info[4]}"))
        gears = sdl2.ext.renderer.Texture(renderer, font.render_text(f"{info[5]}"))
        postbus.render_text = (prijs, pakjes, snelheid, versnelling, hp, gears)
    else:
        (prijs, pakjes, snelheid, versnelling, hp, gears) = postbus.render_text
    kleur_grootte = (100, 150)

    y_size = prijs.size[1]

    renderer.copy(garage_menu,
                  srcrect=(0, 0, BREEDTE, HOOGTE),
                  dstrect=(0, 0, BREEDTE, HOOGTE))
    renderer.rcopy(image,
                   loc=(BREEDTE // 2, 350),
                   size=(image.size[0], image.size[1]),
                   align=(0.5, 0.5))  # Auto image
    renderer.copy(prijs,
                  dstrect=(POSITIE_GARAGE[0][0], POSITIE_GARAGE[0][1], prijs.size[0], y_size))
    renderer.copy(pakjes,
                  dstrect=(POSITIE_GARAGE[1][0], POSITIE_GARAGE[1][1], pakjes.size[0], y_size))
    renderer.copy(snelheid,
                  dstrect=(POSITIE_GARAGE[2][0], POSITIE_GARAGE[2][1], snelheid.size[0], y_size))
    renderer.copy(versnelling,
                  dstrect=(POSITIE_GARAGE[3][0], POSITIE_GARAGE[3][1], versnelling.size[0], y_size))
    renderer.copy(hp,
                  dstrect=(POSITIE_GARAGE[4][0], POSITIE_GARAGE[4][1], hp.size[0], y_size))
    renderer.copy(gears,
                  dstrect=(POSITIE_GARAGE[5][0], POSITIE_GARAGE[5][1], gears.size[0], y_size))
    renderer.copy(money_txt,
                  dstrect=(POSITIE_GARAGE[6][0], POSITIE_GARAGE[6][1], money_txt.size[0], y_size))
    renderer.fill(color=postbus.kleur,
                  rects=(POSITIE_GARAGE[7][0], POSITIE_GARAGE[7][1], kleur_grootte[0], kleur_grootte[1]))
    renderText(font, renderer, str(postbus.kleur[0]), 1800, 520)
    renderText(font, renderer, str(postbus.kleur[1]), 1800, 570)
    renderText(font, renderer, str(postbus.kleur[2]), 1800, 620)


def render_sprites(renderer, sprites, player, d, delta, update):
    global world_map, sprites_autos, sprites_bomen, sprites_dozen
    sprites.sort(reverse=True, key=lambda sprite: sprite.afstanden(player.p_x, player.p_y))  # Sorteren op afstand

    max_dist = 80
    """AANPASSINGEN DOORTREKKEN NAAR RAYCASTER"""

    d /= (speler.r_stralen[:, 0] * speler.r_speler[0] + speler.r_stralen[:, 1] * speler.r_speler[1])
    zichtbaar = []

    for i, sprite in enumerate(sprites):
        if sprite.soort == "Politie":
            sprite.update(world_map, speler, delta)

        if sprite.afstand >= max_dist: continue;
        if update:
            if sprite.update(world_map, speler, delta) and sprite.soort == "Doos":
                for doos in sprites_dozen:
                    if doos == sprite:
                        sprites_dozen.remove(doos)
                        break
        if sprite.afstand <= 0.001: continue;

        # hoek
        rx = sprite.x - player.p_x
        ry = sprite.y - player.p_y
        hoek_sprite = math.atan2(ry, rx) % (math.pi * 2)
        player_hoek = math.atan2(speler.p_x, speler.p_y) % (math.pi * 2)
        # print("Player:" + str(player_hoek))

        hoek_verschil = abs(player.hoek - hoek_sprite)
        if player.hoek <= 1 and hoek_sprite >= math.pi * 7 / 4:
            hoek_verschil = math.pi * 2 - hoek_verschil
        if player.hoek >= math.pi * 7 / 4 and hoek_sprite <= 1:
            hoek_verschil = math.pi * 2 - hoek_verschil

        grond_hoek_verschil = abs(player_hoek - hoek_sprite)
        fout = False

        if player_hoek <= 0.85 and hoek_sprite <= 0.85:
            fout = True

        if sprite.images == []:
            image = sprite.image
        else:
            image = sprite.kies_sprite_afbeelding(grond_hoek_verschil, fout)

        if hoek_verschil >= (math.pi / 3.7):
            continue  # net iets minder gepakt als 4 zodat hij langs rechts er niet afspringt

        # richting
        sprite_distance = sprite.afstand * abs(math.cos(hoek_verschil))
        spriteBreedte, spriteHoogte = image.size
        # grootte
        sprite_size_breedte = int(spriteBreedte / sprite_distance * 10 * sprite.schaal)
        sprite_size_hoogte = int(spriteHoogte / sprite_distance * 10 * sprite.schaal)

        a = ((speler.r_speler[0] + speler.r_camera[0] / 1000 - speler.r_speler[1] * rx / ry - speler.r_camera[
            1] * rx / (1000 * ry)) / ((speler.r_camera[0] / 500) - (speler.r_camera[1] * rx / (500 * ry))))

        interval = (BREEDTE + sprite_size_breedte) / 2
        if not (-interval < a < interval):
            continue

        screen_y = int((sprite.height - sprite_size_hoogte) / 2) + 0.4 / sprite_distance * 850 - 1 / sprite_distance * 40  # wordt in het midden gezet
        screen_x = int(BREEDTE / 2 - a - sprite_size_breedte / 2)

        """kolomen = np.arange(sprite_size_breedte) / sprite_size_breedte - 1 / 2
        x = abs(kolomen * math.sin(hoek_sprite) + abs(rx))
        y = abs(kolomen * math.cos(hoek_sprite) + abs(ry))
        afstand = (x ** 2 + y ** 2) ** (1 / 2)"""

        kolom, breedte, initieel = -1, 0, 0
        for i in range(sprite_size_breedte):
            k = i + screen_x
            if k >= BREEDTE:
                break
            if k < 0:
                continue
            if not d[k] <= sprite.afstand:
                if kolom == -1:
                    kolom = k
                    breedte = 1
                    initieel = i
                else:
                    breedte = k - kolom + 1

        if kolom == -1:
            continue
        if sprite.fall == 0:
            renderer.copy(image, srcrect=(
                initieel / sprite_size_breedte * spriteBreedte, 0, spriteBreedte * breedte / sprite_size_breedte,
                sprite_size_hoogte * sprite.afstand),
                          dstrect=(kolom, screen_y, breedte, sprite_size_hoogte))
            zichtbaar.append(sprite)
            continue
        renderer.copy(image, srcrect=(
            initieel / sprite_size_breedte * spriteBreedte, 0, spriteBreedte * breedte / sprite_size_breedte,
            sprite_size_hoogte * sprite.afstand),
                      dstrect=(kolom, screen_y + 1000 * (time.time() - sprite.fall) / sprite_distance, breedte,
                               sprite_size_hoogte), angle=400 * (time.time() - sprite.fall))
        if time.time() - sprite.fall >= 0.2:
            sprites_bomen.remove(sprite)

    return zichtbaar


def collision_auto(zichtbare_sprites):
    global sprites_autos
    place_array = np.array([[sprite.x, sprite.y] for sprite in zichtbare_sprites])
    lenght = len(zichtbare_sprites)

    sprite_iter = iter(zichtbare_sprites)

    for i, sprite in enumerate(sprite_iter):
        if sprite.soort != "Auto":
            continue

        wh_self_array_x = place_array[:, 0] - sprite.x
        wh_self_array_y = place_array[:, 1] - sprite.y
        distances = wh_self_array_y ** 2 + wh_self_array_x ** 2
        distances[i] = 100

        check = distances < 1
        if check.any():
            pop_indexes = np.arange(0, lenght)[check]

            for index in pop_indexes:
                try:
                    check_sprite = zichtbare_sprites[index]
                except:
                    check[index] = False
                    continue
                soort = check_sprite.soort
                if soort in ["Doos", "PostBus", "Auto",
                             "Doosje"]:  # This is too long ago but i think this will error without Doosje at some point
                    check[index] = False
                    continue
                elif soort == "Boom":
                    check_sprite.fall = time.time()
                elif soort == "Politie":
                    #warnings.warn("Not implemented")
                    check[index] = False
                    continue
                    # raise NotImplementedError("Politie tegengekomen")
                else:
                    warnings.warn("Not implemented for " + soort)
                zichtbare_sprites.remove(check_sprite)

            place_array = place_array[~check, :]
            lenght = len(place_array)


def collision_detection(renderer, speler, sprites, hartje, polities, tree, map_voertuig, font_2):
    global eindbestemming, pad, world_map, sprites_bomen, sprites_autos, sprites_dozen, game_over, politie_tijd
    global balkje_tijd, pakjes_aantal, politie_wagen, politie_active, politie_x, politie_y

    for sprite in sprites:
        if sprite.afstand > 75:
            continue

        if sprite.soort == "Doos":
            if abs(sprite.position[0] - eindbestemming[0]) <= 1 and abs(sprite.position[1] - eindbestemming[1]) <= 1:
                lijst_objective_complete = ["cartoon doorbell", "doorbell", "door knocking"]
                rnd = randint(0, len(lijst_objective_complete) - 1)
                muziek_spelen(lijst_objective_complete[rnd], channel=5)
                if balkje_tijd >= 15:
                    balkje_tijd -= 30
                else:
                    balkje_tijd -= 15
                pakjes_aantal += 1

                # IB2
                if dramco_active:
                    doorsturen_score = pakjes_aantal
                    if len(str(doorsturen_score)) == 1:
                        doorsturen_score = "0" + str(doorsturen_score)
                    elif len(str(doorsturen_score)) == 2:
                        doorsturen_score = str(doorsturen_score)
                    else:
                        doorsturen_pakjes = doorsturen_pakjes % 100
                        if len(str(doorsturen_pakjes)) == 1:
                            doorsturen_pakjes = "0" + str(doorsturen_pakjes)
                        elif len(str(doorsturen_pakjes)) == 2:
                            doorsturen_pakjes = str(doorsturen_pakjes)

                    dramcontroller.write(("S" + str(doorsturen_score)).encode(encoding='ascii'))

                if randint(0, 10) <= 1:
                    muziek_spelen("dogs barking", channel=6)
                if not speler.doos_vast and speler.car.dozen == 0:
                    eindbestemming = (pakjesx, pakjesy)
                else:
                    eindbestemming = bestemming_selector()
                if sprite in sprites_dozen:
                    sprites_dozen.remove(sprite)
            continue
        if sprite.afstand < 1 and sprite.schadelijk:
            if sprite.soort == "Boom":
                if speler.in_auto == False:
                    speler.aantal_hartjes -= 1
                if sprite in sprites_bomen:
                    sprites_bomen.remove(sprite)
            elif sprite.soort == "Auto":
                if speler.in_auto == False:
                    speler.aantal_hartjes -= 2
                if sprite in sprites_autos:
                    sprites_autos.remove(sprite)
            elif sprite.soort == "Politie":
                game_over = True
            else:
                warnings.warn("Kan sprite niet verwijderen" + "  " + str(sprite.soort))
            if speler.in_auto:
                speler.car.hp -= 1
                speler.car.crashed = True

                # IB2
                if dramco_active:
                    dramcontroller.write("2".encode(encoding="ascii"))

                speler.car.crash_time = time.time()
                if speler.car.hp == 0:
                    speler.aantal_hartjes -= 1
                    speler.car.hp = 9
                    speler.car.player_leaving(world_map, speler)
                    speler.car.crashed = False
                    speler.hit = True

            else:

                speler.hit = True
    if speler.in_auto:
        if speler.car.crashed:
            speler.car.crashed = False
            muziek_spelen("car crash", channel=5)

            # IB2
            if dramco_active:
                dramcontroller.write("2".encode(encoding="ascii"))

        rijen = (speler.car.hp - 1) // 4
        for i in range(rijen + 1):
            kolom = 4
            if i == rijen:
                kolom = speler.car.hp - 4 * i
            for j in range(kolom):
                x_pos = BREEDTE - 50 - 50 * j
                y_pos = HOOGTE - 70 - 50 * i
                renderer.copy(hartje, dstrect=(x_pos, y_pos, 50, 50))
    else:
        if speler.hit:
            muziek_spelen("hit sound", channel=5)
            speler.hit = False

        if speler.aantal_hartjes <= 0 and godmode:
            speler.aantal_hartjes = 5

        i = 1
        while i <= speler.aantal_hartjes:
            x_pos = BREEDTE - 50 - 50 * i
            y_pos = HOOGTE - 70
            renderer.copy(hartje, dstrect=(x_pos, y_pos, 50, 50))
            i += 1

    if speler.aantal_hartjes <= 0:  # Politie logica
        if not politie_active:
            politie_tijd = time.time()
            politie_active = True
            politie_x, politie_y = speler.p_x, speler.p_y

        elif time.time() - politie_tijd <= 5:
            # Renders remaining Time
            renderText(font_2, renderer, str(round(time.time() - politie_tijd)), 1000, 200)

        elif politie_wagen == 0:
            # Time bigger then 5 seconds --> Politie starten
            politie_wagen = genereer_politie(speler, polities, tree, map_voertuig, HOOGTE,
                                             politie_pad, inf_world, politie_x, politie_y)
            sprites_autos.append(politie_wagen)

            # IB2
            if dramco_active:
                dramcontroller.write("BT".encode(encoding='ascii'))  # BT: Buzzer True (voor politie)




def show_fps(font, renderer):
    fps_list = [1]
    loop_time = 0

    while True:
        """
        fps_list.append(1 / (time.time() - loop_time))
        loop_time = time.time()

        fps = sum(fps_list) / len(fps_list)
        if len(fps_list) == 20:
            fps_list.pop(0)
        text = sdl2.ext.renderer.Texture(renderer, font.render_text(f'{fps:.2f} fps'))
        renderer.copy(text, dstrect=(int((BREEDTE - text.size[0]) / 2), 20,
                                     text.size[0], text.size[1]))
        yield fps"""
        yield 0


def muziek_spelen(geluid, looped=False, channel=1, distance=0, angle=0):
    global volume, geluiden, last_car_sound_played
    if not sound:
        return
    if geluid == 0:
        sdl2.sdlmixer.Mix_HaltChannel(channel)
    else:
        sdl2.sdlmixer.Mix_MasterVolume(volume)
        sdl2.sdlmixer.Mix_Volume(9, 80)
        if sdl2.sdlmixer.Mix_Playing(channel) == 1:
            return
        elif type(geluid) != str:
            chunk = sdl2.sdlmixer.Mix_QuickLoad_RAW(geluid, len(geluid))
            sdl2.sdlmixer.Mix_PlayChannel(channel, chunk, 0)
            return
        if geluid == last_car_sound_played:
            return
        liedjes = {
            "main menu": geluiden[0],
            "main menu select": geluiden[1],
            "game start": geluiden[2],
            "footsteps": geluiden[3],
            "throwing": geluiden[4],
            "cartoon doorbell": geluiden[5],
            "doorbell": geluiden[6],
            "door knocking": geluiden[7],
            "dogs barking": geluiden[8],
            "car start": geluiden[9],
            "car gear 1": geluiden[10],
            "car gear 2": geluiden[11],
            "car gear 3": geluiden[12],
            "car gear 4": geluiden[13],
            "car loop": geluiden[14],
            "car crash": geluiden[15],
            "hit sound": geluiden[16],
            "cash register": geluiden[17],
            "fail": geluiden[18],
            "politie sirene": geluiden[19]
        }
        if geluid in gears:
            if geluid != "car loop":
                last_car_sound_played = geluid
            else:
                pass
        if not looped:
            sdl2.sdlmixer.Mix_PlayChannel(channel, liedjes[geluid], 0)
        else:
            sdl2.sdlmixer.Mix_PlayChannel(channel, liedjes[geluid], -1)
        if channel == 9:
            sdl2.sdlmixer.Mix_SetPosition(9, angle, distance)


def menu_nav():
    global game_state, main_menu_index, settings_menu_index, main_menu_positie, settings_menu_positie, \
        pauze_index, pauze_positie, map_positie, afstand_map, game_over_index, game_over_positie, \
        garage_index
    if game_state == 0:
        if main_menu_index > 2:
            main_menu_index = 0
        if main_menu_index < 0:
            main_menu_index = 2
        main_menu_positie = POSITIE_MAIN_MENU[main_menu_index]
    elif game_state == 1:
        if settings_menu_index > 4:
            settings_menu_index = 0
        if settings_menu_index < 0:
            settings_menu_index = 4
        settings_menu_positie = POSITIE_SETTINGS_MENU[settings_menu_index]
    elif game_state == 3:
        if garage_index < 0:
            garage_index = 0
        if garage_index > 2:
            garage_index = 2
    elif paused:
        if pauze_index > 3:
            pauze_index = 0
        if pauze_index < 0:
            pauze_index = 3
        pauze_positie = POSITIE_PAUZE[pauze_index]
    elif show_map:
        if map_positie[0] < afstand_map:
            map_positie[0] = afstand_map
        if map_positie[0] > world_map.shape[1] - afstand_map:
            map_positie[0] = world_map.shape[1] - afstand_map
        if map_positie[1] < afstand_map:
            map_positie[1] = afstand_map
        if map_positie[1] > world_map.shape[0] - afstand_map:
            map_positie[1] = world_map.shape[0] - afstand_map
        if afstand_map < 10:
            afstand_map = 10
        if afstand_map > 200:
            afstand_map = 200
    elif game_over:
        if game_over_index > 2:
            game_over_index = 0
        if game_over_index < 0:
            game_over_index = 2
        game_over_positie = POSITIE_GAME_OVER[game_over_index]


def bestemming_selector(mode=""):
    global world_map, lijst_mogelijke_bestemmingen
    if mode == "start":
        lijst_mogelijke_bestemmingen = np.transpose((world_map == -1).nonzero()).tolist()
        # print(lijst_mogelijke_bestemmingen,"\n",'tekst')
        return
    x, y = speler.position
    spelerpositie = list(speler.position)
    range_min = [spelerpositie[1] - 30, spelerpositie[0] - 30]  # "linkerbovenhoek" v/d de matrix
    range_max = [spelerpositie[1] + 30, spelerpositie[0] + 30]  # "rechteronderhoek" v/d matrix
    range_te_dicht_min = [spelerpositie[1] - 10, spelerpositie[0] - 10]
    range_te_dicht_max = [spelerpositie[1] + 10, spelerpositie[0] + 10]
    dichte_locaties = list(
        filter(lambda m: m[0] >= range_min[0] and m[1] >= range_min[1] and m[0] <= range_max[0] and m[1] <= range_max[1] \
                         and (m[0] >= range_te_dicht_max[0] and m[1] >= range_te_dicht_max[1] or m[0] <=
                              range_te_dicht_min[0] and m[1] <= range_te_dicht_min[1]), lijst_mogelijke_bestemmingen))
    rnd = randint(0,
                  len(dichte_locaties) - 1)  # len(dichte_locaties) kan 0 zijn indien er geen dichte locaties zijn: vermijden door groot genoeg gebied te zoeken
    lijst_mogelijke_bestemmingen.remove(dichte_locaties[rnd])
    bestemming = (dichte_locaties[rnd][1], dichte_locaties[rnd][0])
    return bestemming


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


# @profile
def main(inf_world, shared_world_map, shared_pad, shared_eindbestemming, shared_spelerpositie):
    global game_state, BREEDTE, volume, sensitivity_rw, sensitivity, world_map, kleuren_textures, sprites, map_positie, undeletable_sprites
    global eindbestemming, paused, show_map, quiting, lijst_mogelijke_bestemmingen, sprites_bomen, sprites_autos, politie_wagen
    global balkje_tijd, pakjes_aantal, game_over, kantoor_sprites, starting_game, money, highscore, lijst_postbussen
    global politie_tijd, opgeslaan_na_game_over, politie_active, vorig_pakjes_aantal

    map_positie = [50, world_map.shape[0] - 50]  # This is needed for initialisation
    world_map = shared_world_map
    # Initialiseer de SDL2 bibliotheek
    sdl2.ext.init()

    # Maak een venster aan om de game te renderen
    window = sdl2.ext.Window("Project Ingenieursbeleving 2", size=(BREEDTE, HOOGTE))
    # window.show()
    # window.minimize()
    # screen = sdl2.ext.surface("Test",size=(BREEDTE,HOOGTE))
    # Begin met het uitlezen van input van de muis en vraag om relatieve coordinaten
    sdl2.SDL_SetRelativeMouseMode(True)
    sdl2.ext.renderer.set_texture_scale_quality('nearest')

    # Maak een renderer aan zodat we in ons venster kunnen renderen
    renderer = sdl2.ext.Renderer(window,
                                 flags=sdl2.render.SDL_RENDERER_ACCELERATED | sdl2.render.SDL_RENDERER_PRESENTVSYNC)

    # resources inladen
    resources = sdl2.ext.Resources(__file__, "resources")
    resources_mappen = sdl2.ext.Resources(__file__, "mappen")
    # Spritefactory aanmaken
    factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=renderer)
    # soorten muren opslaan in sdl2 textures

    achtergrond = factory.from_image(resources.get_path("game_main_menu_wh_tekst.png"))
    window.show()

    # Initialiseer font voor de fps counter
    font = sdl2.ext.FontTTF(font='CourierPrime.ttf', size=20, color=kleuren[8])
    font_2 = sdl2.ext.FontTTF(font='CourierPrime.ttf', size=60, color=kleuren[0])
    dash_font = sdl2.ext.FontTTF(font='CourierPrime.ttf', size=60, color=kleuren[8])
    garage_font = sdl2.ext.FontTTF(font='CourierPrime.ttf', size=40, color=kleuren[11])
    fps_generator = show_fps(font, renderer)  # Initialiseer font voor de fps counter

    soort_muren = [
        factory.from_image(resources.get_path("muur_test.png")),  # 1
        factory.from_image(resources.get_path("Rood_huis.png")),  # 2
        factory.from_image(resources.get_path("groen_huis.png")),  # 3
        factory.from_image(resources.get_path("Blauw_huis.png")),  # 4
        factory.from_image(resources.get_path("Grijs_huis.png")),  # 5
        factory.from_image(resources.get_path("Paars_huis.png")),  # 6
        factory.from_image(resources.get_path("Geel_huis.png")),  # 7
        factory.from_image(resources.get_path("Oranje_huis.png")),  # 8
        factory.from_image(resources.get_path("Hedge_donker.png")),  # 9
        factory.from_image(resources.get_path("stop bord pixel art.png")),  # 10
        factory.from_image(resources.get_path("warehouse.png")),  # 11
        factory.from_image(resources.get_path("post-office_1.png")),  # 12
        factory.from_image(resources.get_path("post-office_2.png")),  # 13
        factory.from_image(resources.get_path("garage_1.jpg")),  # 14
        factory.from_image(resources.get_path("garage_2.jpg")),  # 15
        factory.from_image(resources.get_path("garage_3.jpg")),  # 16
        factory.from_image(resources.get_path("garage_4.jpg")),  # 17
    ]
    muren_info = []
    for i, muur in enumerate(soort_muren):
        muren_info.append((muur, muur.size[0], 890))
    kleuren_textures = [factory.from_color(kleur, (1, 1)) for kleur in kleuren]
    # Inladen wereld_mappen
    map_resources = sdl2.ext.Resources(__file__, "mappen")
    # alle mappen opslaan in sdl2 textures
    inf_world.png = factory.from_image(map_resources.get_path('map.png'))

    # Inladen sprites
    hartje = factory.from_image(resources.get_path("Hartje.png"))
    wheel = factory.from_image(resources.get_path("Wheel.png"))
    dashboard = factory.from_image(resources.get_path("dashboard.png"))
    tree = factory.from_image(resources.get_path("Tree_gecropt.png"))
    sprite_map_png = factory.from_image(resources.get_path("map_boom.png"))
    map_voertuig = factory.from_image(resources.get_path("map_auto.png"))
    map_auto = factory.from_image(resources.get_path("map_voertuig.png"))
    doos = factory.from_image(resources.get_path("doos.png"))
    map_doos = factory.from_image(resources.get_path("map_doos.png"))
    speler_png = factory.from_image(resources.get_path("speler_sprite.png"))
    arrow = factory.from_image(resources.get_path("arrow.png"))
    logo = factory.from_image(resources.get_path("police.png"))

    time_bar = []
    Time = sdl2.ext.Resources(__file__, "resources/Time")
    for i in range(11):
        afbeelding_naam = str(i) + ".png"

        time_bar.append(factory.from_image(Time.get_path(afbeelding_naam)))

    speler.doos = doos
    speler.map_doos = map_doos
    speler.png = speler_png
    gps_grote_map = factory.from_image(resources.get_path("gps_grote_map.png"))

    boom = sdl2.ext.Resources(__file__, "resources/boom")
    rode_auto = sdl2.ext.Resources(__file__, "resources/Rode_auto")
    blauwe_auto = sdl2.ext.Resources(__file__, "resources/Blauwe_auto")
    Groene_auto = sdl2.ext.Resources(__file__, "resources/Groene_auto")
    Witte_auto = sdl2.ext.Resources(__file__, "resources/Witte_auto")
    Grijze_auto = sdl2.ext.Resources(__file__, "resources/Grijze_auto")
    humvee_map = sdl2.ext.Resources(__file__, "resources/Humvee")
    politie = sdl2.ext.Resources(__file__, "resources/Politie_auto")
    van_file = sdl2.ext.Resources(__file__, "resources/Van")

    bomen = []
    rode_autos = []
    blauwe_autos = []
    groene_autos = []
    witte_autos = []
    grijze_autos = []
    humvee = []
    polities = []
    van = []

    for i in range(361):
        afbeelding_naam = "map" + str(i + 1) + ".png"
        bomen.append(factory.from_image(boom.get_path(afbeelding_naam)))
        rode_autos.append(factory.from_image(rode_auto.get_path(afbeelding_naam)))
        blauwe_autos.append(factory.from_image(blauwe_auto.get_path(afbeelding_naam)))
        groene_autos.append(factory.from_image(Groene_auto.get_path(afbeelding_naam)))
        witte_autos.append(factory.from_image(Witte_auto.get_path(afbeelding_naam)))
        grijze_autos.append(factory.from_image(Grijze_auto.get_path(afbeelding_naam)))
        humvee.append(factory.from_image(humvee_map.get_path(afbeelding_naam)))
        polities.append(factory.from_image(politie.get_path(afbeelding_naam)))
        van.append(factory.from_image(van_file.get_path(afbeelding_naam)))

        """
        rode_autos = bomen
        blauwe_auto = bomen
        groene_autos = bomen
        witte_autos = bomen
        grijze_autos = bomen
        humvee = bomen
        polities = bomen
        #politie = bomen
        van = bomen"""

    kleuren_autos = [rode_autos, groene_autos, witte_autos, grijze_autos, blauwe_auto]
    # Eerste Auto aanmaken
    lijst_postbussen = [PostBus(tree, blauwe_autos, map_auto, auto_x, auto_y, HOOGTE, type=0, schaal=0.4),
                        PostBus(tree, humvee, map_auto, auto_x, auto_y, HOOGTE, type=1, schaal=0.4),
                        PostBus(tree, van, map_auto, auto_x, auto_y, HOOGTE, type=2, schaal=0.4)]

    lijst_postbussen[0].kleur = [44, 59, 118]
    lijst_postbussen[1].kleur = [105, 78, 34]
    lijst_postbussen[2].kleur = [7, 29, 50]

    speler.car = lijst_postbussen[selected_car]
    auto = speler.car
    auto.draai_sprites(125)
    sprites_autos.append(auto)

    bestemming_selector("start")
    # lijst_mogelijke_bestemmingen = inf_world.mogelijke_bestemmingen
    eindbestemming = bestemming_selector()

    shared_eindbestemming[:] = eindbestemming[:]

    menu_pointer = factory.from_image(resources.get_path("game_main_menu_pointer.png"))
    settings_menu = factory.from_image(resources.get_path("settings_menu.png"))
    pauze_menu = factory.from_image(resources.get_path("pause_menu.png"))
    game_over_menu = factory.from_image(resources.get_path("Game_over_menu.png"))
    handen_doos = factory.from_image(resources.get_path("box_hands.png"))
    garage_menu = factory.from_image(resources.get_path("garage_menu.png"))

    map_png = factory.from_image(resources_mappen.get_path("map.png"))
    pngs_mappen = (map_png, gps_grote_map)

    # UI
    uifactory = sdl2.ext.UIFactory(factory)
    startknop = uifactory.from_image(sdl2.ext.BUTTON,
                                     resources.get_path("start_game.png"))
    settingsknop = uifactory.from_image(sdl2.ext.BUTTON,
                                        resources.get_path("settings.png"))
    quitknop = uifactory.from_image(sdl2.ext.BUTTON,
                                    resources.get_path("quit_game.png"))

    startknop.position = POSITIE_MAIN_MENU[0][0] - 310, POSITIE_MAIN_MENU[0][1] - 15
    settingsknop.position = POSITIE_MAIN_MENU[1][0] - 250, POSITIE_MAIN_MENU[1][1] - 15
    quitknop.position = POSITIE_MAIN_MENU[2][0] - 375, POSITIE_MAIN_MENU[2][1] - 25

    startknop.click += start
    settingsknop.click += settings
    quitknop.click += quit

    spriterenderer = factory.create_sprite_render_system(window)
    uiprocessor = sdl2.ext.UIProcessor()
    garage_auto_index = 0

    # IB2
    if dramco_active:
        dramcontroller.write(("L" + str(min(5, speler.car.dozen))).encode(encoding='ascii'))
        time.sleep(0.05)
        dramcontroller.write("S00".encode(encoding='ascii'))

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
            restore_txt = sdl2.ext.renderer.Texture(renderer, font.render_text(f"Restore settings to default?"))
            reset_txt = sdl2.ext.renderer.Texture(renderer, font.render_text(f"Reset save file?"))
            highscore_txt = sdl2.ext.renderer.Texture(renderer, font.render_text(f"High score: {highscore}"))
            renderer.copy(volume_text, dstrect=(10, 200, volume_text.size[0], volume_text.size[1]))
            renderer.copy(sensitivity_rw_text,
                          dstrect=(10, 230, sensitivity_rw_text.size[0], sensitivity_rw_text.size[1]))
            renderer.copy(restore_txt, dstrect=(10, 260, restore_txt.size[0], restore_txt.size[1]))
            renderer.copy(reset_txt, dstrect=(10, 290, reset_txt.size[0], reset_txt.size[1]))
            renderer.copy(highscore_txt,
                          srcrect=(0, 0, highscore_txt.size[0], highscore_txt.size[1]),
                          dstrect=(BREEDTE - 250, 70, highscore_txt.size[0], highscore_txt.size[1]))
            if 3 > settings_menu_index > 0:
                text = sdl2.ext.renderer.Texture(renderer, font.render_text("<>"))
                renderer.copy(text,
                              dstrect=(settings_menu_positie[0], settings_menu_positie[1], text.size[0], text.size[1]))
            elif settings_menu_index >= 3:
                text = sdl2.ext.renderer.Texture(renderer, font.render_text("<-"))
                renderer.copy(text,
                              dstrect=(settings_menu_positie[0], settings_menu_positie[1], text.size[0], text.size[1]))
            else:
                renderer.copy(menu_pointer,
                              srcrect=(0, 0, menu_pointer.size[0], menu_pointer.size[1]),
                              dstrect=(settings_menu_positie[0], settings_menu_positie[1], 80, 50))
            renderer.present()

        # All settings going into the game
        sdl2.SDL_SetRelativeMouseMode(True)
        if game_state == 2:  # enkel als game_state van menu naar game gaat mag game start gespeeld worden
            muziek_spelen(0)
            muziek_spelen("game start", channel=3)
        if game_state != 1:
            config.set("settings", "volume",
                       f"{volume}")  # indien er uit de settings menu gekomen wordt, verander de config file met juiste settings
            config.set("settings", "sensitivity", f"{sensitivity_rw}")
            sensitivity = -2 * sensitivity_rw + 300
            config.set("gameplay", "highscore", f"{highscore}")
            config.set("gameplay", "money", f"{money}")
            with open("config.ini", "w") as f:
                config.write(f)

        if starting_game:  # only runs once --> no changes als je terugkeert van garage
            starting_game = False
            # Setup voor de game
            sprites_bomen = aanmaken_sprites_bomen(speler.p_x, speler.p_y, HOOGTE, bomen, sprite_map_png, tree,
                                                   world_map, sprites_bomen, aantalbomen=300)
            # sprites_autos
            for i in range(100):
                omgeving = 20
                x = randint(speler.tile[0] - omgeving, speler.tile[0] + omgeving) * 9 + 4
                y = randint(speler.tile[1] - omgeving, speler.tile[1] + omgeving) * 9 + 4
                if x <= 0 or x >= 1000 or y <= 0 or y >= 1000:
                    continue
                voertuig = Voertuig(tree, kleuren_autos[randint(0, 3)], map_voertuig, x, y, HOOGTE, world_map)
                if not voertuig.vector: continue;
                sprites_autos.append(voertuig)
            undeletable_sprites = []
            for i in range(15):
                x = random.uniform(450, 452)
                y = random.uniform(432, 434)
                Doos = Sprite(doos, [], map_doos, x, y, HOOGTE, "Doosje")
                Doos.schadelijk = False
                Doos.map_grootte = 3
                undeletable_sprites.append(Doos)

        t0 = 0
        start_tijd = time.time()
        speler.reset()

        while game_state == 2 and not moet_afsluiten:
            # Onthoud de huidige tijd
            start_time = time.time()
            shared_spelerpositie[:] = speler.position[:]
            shared_eindbestemming[:] = list(eindbestemming[:])
            pad[:] = shared_pad[:]
            if politie_wagen:
                shared_politiepositie[:] = politie_wagen.position[:]
                politie_wagen.pad[:] = shared_poltie_pad[:]
                # pad[:] = shared_poltie_pad[:]

            speler.idle()

            if time.time() < speler.car.crash_time + 0.16:
                if t0 < speler.car.crash_time or time.time() < t0:
                    t0 = time.time() + 5 * delta
                    angle = random.uniform(5, 10)
                    if randint(0, 1):
                        angle *= -1
                else:
                    angle /= 1.7
            else:
                angle = 0
            # Reset de rendering context
            renderer.clear()
            render_floor_and_sky(renderer, kleuren_textures)
            draw_bestemming(renderer, eindbestemming, speler, kleuren_textures[4])
            # Render de huidige frame
            (d, d_v, kl), _ = (speler.n_raycasting(world_map))  # 10% of the time

            renderen(renderer, d, d_v, kl, muren_info, angle)  # 41% of the time
            sprites_autos = sprites_auto_update(speler.tile[0], speler.tile[1], kleuren_autos, tree, map_voertuig,
                                                world_map, HOOGTE, sprites_autos, aantalautos=100)

            sprites_bomen = aanmaken_sprites_bomen(speler.p_x, speler.p_y, HOOGTE, bomen, sprite_map_png, tree,
                                                   world_map, sprites_bomen)
            sprites = sprites_bomen + sprites_autos + sprites_dozen + undeletable_sprites
            updatable = not (show_map or paused or game_over)
            zichtbare_sprites = render_sprites(renderer, sprites, speler, d, delta, updatable)  # 8% of the time

            collision_detection(renderer, speler, sprites, hartje, polities, tree, map_voertuig, font_2)
            if len(sprites_dozen) == 0 and not speler.doos_vast and speler.car.dozen == 0:
                eindbestemming = (pakjesx, pakjesy)

            collision_auto(zichtbare_sprites)

            # pakjes_aantal += 1
            # t.append(time.time()-t1)
            menu_nav()
            if pad is None:
                print(f"EINDBESTEMMING NONE: {eindbestemming}")
                print('NONE')
                eindbestemming = bestemming_selector()

            draw_nav(renderer, kleuren_textures, arrow, inf_world, speler, pad, sprites)
            delta = time.time() - start_time

            while delta < 0.005:  # This is a FPS limiter
                delta = time.time() - start_time

            verwerk_input(delta)
            if updatable and not debugging:
                balkje_tijd += delta
                if godmode:
                    balkje_tijd -= delta/1.8

            # Renders aantal pakjes
            renderText(font_2, renderer, str(pakjes_aantal), 1910, 10)
            straf = render_balkje(balkje_tijd, time_bar, renderer)
            if straf:
                game_over = True

            if politie_wagen != 0:
                render_police(logo, renderer)
                # hoek berekenen
                rx = politie_wagen.x - speler.p_x
                ry = politie_wagen.y - speler.p_y
                hoek_sprite = math.atan2(ry, rx) % (math.pi * 2)
                player_hoek = math.atan2(speler.p_x, speler.p_y) % (math.pi * 2)
                grond_hoek_verschil = abs(player_hoek - hoek_sprite)
                muziek_spelen("politie sirene", channel=9, distance=int(politie_wagen.afstand),
                              angle=int(grond_hoek_verschil), looped=True)

            if paused:
                renderer.copy(pauze_menu,
                              srcrect=(0, 0, pauze_menu.size[0], pauze_menu.size[1]),
                              dstrect=(0, 0, BREEDTE, HOOGTE))
                renderer.copy(menu_pointer,
                              srcrect=(0, 0, menu_pointer.size[0], menu_pointer.size[1]),
                              dstrect=(pauze_positie[0], pauze_positie[1], 80, 50))
                menu_nav()
            elif show_map:
                map_settings = (map_positie, afstand_map, np.shape(world_map))
                render_map(renderer, kleuren_textures, pngs_mappen, map_settings, speler, pad, sprites)
                menu_nav()
            elif game_over:
                muziek_spelen(0, channel=9)
                balkje_tijd = 0
                politie_tijd = 0
                politie_active = False
                if politie_wagen != 0 and politie_wagen in sprites_autos:
                    sprites_autos.remove(politie_wagen)
                    politie_wagen = 0
                speler.reset()
                speler.aantal_hartjes = 5
                if not opgeslaan_na_game_over:
                    # IB2
                    if dramco_active:
                        dramcontroller.write("BF".encode(encoding='ascii'))  # Buzzer False
                    print(
                        "game_over, money = " + str(money) + " highscore :" + str(highscore) + " aantal pakjes: " + str(
                            pakjes_aantal))
                    if pakjes_aantal > highscore:
                        config.set("gameplay", "highscore", f"{pakjes_aantal}")
                        highscore = pakjes_aantal
                    money += pakjes_aantal * 5
                    pakjes_aantal = 0
                    config.set("gameplay", "money", f"{money}")
                    with open("config.ini", "w") as f:
                        config.write(f)
                    opgeslaan_na_game_over = True

                highscore_txt = sdl2.ext.renderer.Texture(renderer, font.render_text(f"High score: {highscore}"))
                renderer.copy(game_over_menu,
                              srcrect=(0, 0, game_over_menu.size[0], game_over_menu.size[1]),
                              dstrect=(0, 0, BREEDTE, HOOGTE))
                renderer.copy(menu_pointer,
                              srcrect=(0, 0, menu_pointer.size[0], menu_pointer.size[1]),
                              dstrect=(game_over_positie[0], game_over_positie[1], 80, 50))
                renderer.copy(highscore_txt,
                              srcrect=(0, 0, highscore_txt.size[0], highscore_txt.size[1]),
                              dstrect=(BREEDTE // 2 - highscore_txt.size[0] // 2, 140, highscore_txt.size[0],
                                       highscore_txt.size[1]))
                menu_nav()

            else:
                next(fps_generator)
                map_positie = list(speler.position)
                if speler.in_auto:
                    auto_info_renderen(renderer, dash_font, (dashboard, wheel, doos), speler.car)
                elif speler.doos_vast:
                    handen_sprite(renderer, handen_doos)
                # speler.renderen(renderer, world_map)
                if speler.car.speed > 0:
                    muziek_spelen("car loop", channel=2)
                elif speler.car.speed < 0:
                    pass
                    # reversing beep ofz

            if quiting > 0:
                quiting -= 1
                renderText(font_2, renderer, "DON'T QUIT THE GAME!!!", BREEDTE, HOOGTE / 2)

            # Verwissel de rendering context met de frame buffer
            renderer.present()
            game_state = speler.check_postition(game_state)

        while game_state == 3 and not moet_afsluiten:
            start_time = time.time()
            speler.idle()
            renderer.clear()
            menu_nav()
            garage(renderer, garage_font, garage_auto_index, garage_menu, lijst_postbussen)
            garage_auto_index += 0.6
            if garage_auto_index > 360:
                garage_auto_index = 0
            renderer.present()
            delta = time.time() - start_time
            verwerk_input(delta, factory=factory)
        if game_state == 4:
            speler.kantoor_set()
            world_map = kantoor_map
            kantoor_sprites = []
            if speler.car != 0:
                Auto = Sprite(speler.car.image, speler.car.images, speler.car.map_png, 5, 15, HOOGTE, "PostBus")
                Auto.schadelijk = False
                kantoor_sprites.append(Auto)
            else:
                game_state = 3
            if speler.in_auto:  # This block is executed in Verwerk_input
                speler.in_auto = False
                speler.car.x = auto_x
                speler.car.y = auto_y
        if pakjes_aantal > vorig_pakjes_aantal + speler.car.max_dozen//2:  # giving a time bonus if half of the boxes are delivered
            if balkje_tijd > 15:
                balkje_tijd -= 15
            else:
                balkje_tijd = 0

            if speler.aantal_hartjes < 4:
                speler.aantal_hartjes += 2
            else:
                speler.aantal_hartjes = 5

        while game_state == 4 and not moet_afsluiten:
            muziek_spelen(0, channel=9)
            start_time = time.time()
            speler.idle()
            speler.update_kantoor_deuren()
            renderer.clear()
            render_floor_and_sky(renderer, kleuren_textures)
            # Render de huidige frame
            (d, d_v, kl), _ = (speler.n_raycasting(world_map))
            renderen(renderer, d, d_v, kl, muren_info, 0)
            if speler.car.dozen < speler.car.max_dozen:
                for i, sprite in enumerate(kantoor_sprites):
                    if sprite == Auto:
                        continue
                    if abs(Auto.x - sprite.x) < 0.7 and abs(Auto.y - sprite.y) < 0.7:
                        speler.car.dozen += 1
                        kantoor_sprites.remove(sprite)
                        if speler.car.dozen < speler.car.max_dozen:
                            break

            if eindbestemming == (pakjesx, pakjesy) and speler.car.dozen != 0:  # Making new destination for packaged
                coords = speler.position
                speler.position = [math.floor(speler.initial[0]), math.floor(speler.initial[0])]
                eindbestemming = bestemming_selector()
                speler.position = coords

            render_sprites(renderer, kantoor_sprites, speler, d, delta, True)
            if speler.doos_vast:
                handen_sprite(renderer, handen_doos)
            text = "Momenteel " + str(speler.car.dozen) + " dozen van de maximale " + str(
                speler.car.max_dozen) + " dozen in de auto"
            renderText(font, renderer, text, BREEDTE, HOOGTE - 100)

            delta = time.time() - start_time
            verwerk_input(delta)
            next(fps_generator)
            # Verwissel de rendering context met de frame buffer
            renderer.present()
        world_map = inf_world.world_map

    # Sluit SDL2 af
    sdl2.ext.quit()


if __name__ == '__main__':
    global dramcontroller, dramco_active
    for device in serial.tools.list_ports.comports():
        if "Bluetooth" in device.description:
            continue
        try:
            print(device)
            # Dramcontroller aanmaken
            dramcontroller = serial.Serial(port=device.device, baudrate=baudrate, timeout=.1)
            # dramcontroller.write(5)
            dramco_active = True
            break
        except:
            warnings.warn("Dramcontroller had issues")
    if not dramco_active:
        warnings.warn("Dramcontroller not found")

    # Speler aanmaken
    speler = Player(p_speler_x, p_speler_y, r_speler_hoek, BREEDTE)
    politie_postie = [450, 450]
    politie_pad = []
    with Manager() as manager:
        shared_eindbestemming = manager.list(eindbestemming)
        shared_spelerpositie = manager.list(speler.position)
        shared_pad = manager.list(pad)
        shared_politiepositie = manager.list(politie_postie)
        shared_poltie_pad = manager.list(politie_pad)

        inf_world = Map()
        inf_world.start()
        world_map = inf_world.world_map
        # inf_world.map_making(speler)
        shared_world_map = world_map  # manager.list(world_map)

        # profiler = cProfile.Profile()
        # profiler.enable()
        p2 = Process(target=pathfinding_gps2, args=(inf_world, shared_world_map, shared_pad,
                                                    shared_eindbestemming, shared_spelerpositie), daemon=True)

        p3 = Process(target=politie_pathfinding, args=(shared_world_map, shared_poltie_pad,
                                                       shared_politiepositie, shared_spelerpositie), daemon=True)
        p2.start()
        p3.start()
        main(inf_world, shared_world_map, shared_pad, shared_eindbestemming, shared_spelerpositie)
        p2.kill()
        p3.kill()

        money += pakjes_aantal * 5
        pakjes_aantal = 0
        config.set("gameplay", "money", f"{money}")
        if pakjes_aantal > highscore:
            config.set("gameplay", "highscore", f"{pakjes_aantal}")
            with open("config.ini", "w") as f:
                config.write(f)
    if dramco_active:
        dramcontroller.write("L0".encode(encoding='ascii'))
        time.sleep(0.05)
        dramcontroller.write("S00".encode(encoding='ascii'))
        dramcontroller.close()
