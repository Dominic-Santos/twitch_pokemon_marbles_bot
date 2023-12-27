import tkinter
import win32api
from threading import Thread

from TwitchChannelPointsMiner.classes.entities.Pokemon.CGApi import API as PCGApi
from TwitchChannelPointsMiner.classes.entities.Pokemon.PokemonCG import PokemonComunityGame
from TwitchChannelPointsMiner.classes.entities.Pokemon.Utils import get_sprite

POKEMON = PokemonComunityGame()
POKEMON_API = PCGApi()
POKEMON_API.refresh_auth()
IMAGES = {}
IMAGE_PATHS = {}


def sync_all():
    all_pokemon = POKEMON_API.get_all_pokemon()
    POKEMON.sync_computer(all_pokemon)

    dex = POKEMON_API.get_pokedex()
    POKEMON.sync_pokedex(dex)

    inv = POKEMON_API.get_inventory()
    POKEMON.sync_inventory(inv)


def get_image(img_path):
    if img_path in IMAGES:
        return IMAGES[img_path]
    tkimg = tkinter.PhotoImage(file=img_path)
    IMAGES[img_path] = tkimg
    return tkimg


def get_sprite_cached(sprite_type, sprite_name, tm_type=None):
    look_for = f"{sprite_type}_{sprite_name}"
    if look_for in IMAGE_PATHS:
        return IMAGE_PATHS[look_for]

    if sprite_type == "pokemon":
        img_path = get_sprite("pokemon", sprite_name, battle=True, path=True, use_cache=True)
    else:
        img_path = get_sprite(sprite_type, sprite_name, path=True, use_cache=True, tm_type=tm_type)

    IMAGE_PATHS[look_for] = img_path
    return img_path


def clear_widgets(app):
    for widget in app.winfo_children():
        widget.destroy()


def getBoolText(value):
    return "On" if value else "Off"


def getColor(value):
    return "green" if value else "#f0f0f0"


def create_alert(alert_func):
    worker = Thread(target=alert_func)
    worker.setDaemon(True)
    worker.start()


def ok_alert(msg, title):
    def inner_alert():
        win32api.MessageBox(0, msg, title, 0x00001000)
    create_alert(inner_alert)
