import math
import numpy as np
import sdl2.ext
from configparser import ConfigParser


#dramcontroller
poort = 'com15'
baudrate = 115200
dramco_active = False

politie_active = False

debugging = False



config = ConfigParser()

# Constanten
BREEDTE = 1000
HOOGTE = int(BREEDTE / 10 * 7)
POSITIE_MAIN_MENU = [
    [365, 253],  # 0: Start Game
    [300, 401],  # 1: Settings
    [420, 572]  # 2: Quit Game
]
POSITIE_SETTINGS_MENU = [
    [170, 55],  # 0: Back
    [150, 200],  # 1: volume
    [200, 230],  # 2: sensitivity
    [350, 260],  # 3: restore
    [220, 290]  # 4: reset
]
POSITIE_PAUZE = [
    [540, 175],  # 0: Continue
    [520, 310],  # 1: Settings
    [595, 450],  # 2: Main Menu
    [590, 585]  # 3: Quit Game
]
POSITIE_GAME_OVER = [
    [600, 210],  # 0: Play Again
    [600, 388],  # 1: Main Menu
    [600, 563]  # 2: Quit Game
]
POSITIE_GARAGE = [
    [520, 24],  # 0: Prijs
    [160, 444],  # 1: #pakjes
    [163, 495],  # 2: snelheid
    [190, 540],  # 3: versnelling
    [85, 588],  # 4: HP
    [145, 635],  # 5: Gears
    [900, 24],  # 6: Geld
    [750, 510]  # 7: kleur
]
#
# Globale variabelen
#
game_state = 0  # 0: main menu, 1: settings menu, 2: game actief, 3: garage, 4: kantoor
prijzen = [0, 20, 100]
lijst_postbussen = []
balkje_tijd = 0
pakjes_aantal = 0
politie_wagen = 0
sound = True
paused = False
show_map = False
game_over = False
starting_game = True
politie_tijd = 0
spawn_x = 0
spawn_y = 0
game_over_index = 0
game_over_positie = [0, 0]
quiting = 0
verandering = 1
main_menu_index = 0
settings_menu_index = 0
main_menu_positie = [0, 0]
settings_menu_positie = [0, 0]
map_positie = [0, 0]
afstand_map = 50
pauze_index = 0
eindbestemming = (50 * 9, 50 * 9)
pad = []
pauze_positie = POSITIE_PAUZE[0]
sprites = []
lijst_mogelijke_bestemmingen = []
sprites_dozen = []
sprites_bomen = []
sprites_autos = []
kantoor_sprites = []
garage_index = 0
opgeslaan_na_game_over = False
# verwerking van config file: ook globale variabelen
config.read("config.ini")
volume = int(config.get("settings", "volume"))
sensitivity_rw = int(config.get("settings", "sensitivity"))
highscore = int(config.get("gameplay", "highscore"))
money = int(config.get("gameplay", "money"))
gekocht_str = config.get("gameplay", "gekocht")
gekocht = [eval(i) for i in gekocht_str.split(" ")]
selected_car = int(config.get("gameplay", "selected_car"))
# echte sensitivity gaat van 100 - 300, 300 traagst, 100 snelst. Raw sensitivity gaat van 0 tot 100
sensitivity = -2 * sensitivity_rw + 300


# wordt op True gezet als het spel afgesloten moet worden
moet_afsluiten = False

# Speler
p_speler_x, p_speler_y = 50.4 * 9, 49 * 9
auto_x, auto_y = p_speler_x + 3, p_speler_y + 3
politie_cord = []

r_speler_hoek = math.pi / 4
d_camera = 1

# Kantoor postbode
pakjesx, pakjesy = 451, 433

# world
world_map = np.zeros((10, 10))

# Vooraf gedefinieerde kleuren
kleuren = [
    sdl2.ext.Color(0, 0, 0),  # 0 = Zwart
    sdl2.ext.Color(255, 0, 20),  # 1 = Rood
    sdl2.ext.Color(0, 255, 0),  # 2 = Groen
    sdl2.ext.Color(0, 0, 255),  # 3 = Blauw
    sdl2.ext.Color(225, 165, 0),  # 4 = oranje
    sdl2.ext.Color(64, 64, 64),  # 5 = Donker grijs
    sdl2.ext.Color(128, 128, 128),  # 6 = Grijs
    sdl2.ext.Color(192, 192, 192),  # 7 = Licht grijs
    sdl2.ext.Color(255, 255, 255),  # 8 = Wit
    sdl2.ext.Color(120, 200, 250),  # 9 = Blauw_lucht
    sdl2.ext.Color(106, 13, 173),  # 10 = Purple
    sdl2.ext.Color(255, 200, 0)  # 11 = Geel
]
kleuren_textures = []

# Start Audio
sdl2.sdlmixer.Mix_Init(0)
sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.sdlmixer.MIX_DEFAULT_FORMAT, 4, 1024)  # 44100 = 16 bit, cd kwaliteit
sdl2.sdlmixer.Mix_AllocateChannels(10)  # 9: ENKEL POLITIEWAGEN
sdl2.sdlmixer.Mix_MasterVolume(volume)
geluiden = [
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/8-Bit Postman Pat.wav", "UTF-8")),  # 0
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/arcade_select.wav", "UTF-8")),  # 1
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/arcade_start.wav", "UTF-8")),  # 2
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/concrete-footsteps.wav", "UTF-8")),  # 3
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/throw sound effect.wav", "UTF-8")),  # 4
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/cartoon_doorbell.wav", "UTF-8")),  # 5
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/regular_doorbell.wav", "UTF-8")),  # 6
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/door_knocking.wav", "UTF-8")),  # 7
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/dogs_barking.wav", "UTF-8")),  # 8
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/car_start.wav", "UTF-8")),  # 9
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/car_gear_1.wav", "UTF-8")),  # 10
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/car_gear_2.wav", "UTF-8")),  # 11
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/car_gear_3.wav", "UTF-8")),  # 12
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/car_gear_4.wav", "UTF-8")),  # 13
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/car_loop.wav", "UTF-8")),  # 14
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/car crash.wav", "UTF-8")),  # 15
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/hit sound.wav", "UTF-8")),  # 16
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/cash register.wav", "UTF-8")),  # 17
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/fail.wav", "UTF-8")),  # 18
    sdl2.sdlmixer.Mix_LoadWAV(bytes("muziek/politie sirene.wav", "UTF-8"))  # 19
]
gears = ["car loop", "car gear 1", "car gear 2", "car gear 3", "car gear 4", "car gear 4", "car gear 4"]
last_car_sound_played = 0

RGB = (255, 160, 160)