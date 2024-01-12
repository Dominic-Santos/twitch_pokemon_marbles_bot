from bs4 import BeautifulSoup
from PIL import Image
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg
import base64
import json
import os
import requests

PCG_AUTH = "pokemon_auth_token.txt"


def check_output_folder(folder):
    if os.path.exists(folder) is False:
        os.makedirs(folder)


def save_to_file(filename, data):
    with open(filename, "w") as f:
        f.write(json.dumps(data, indent=4))


def load_from_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(e)
    return {}


def save_to_json(func):
    def wrapped(obj, *args, **kwargs):
        obj_name = obj.__class__.__name__
        func_name = func.__name__

        result = func(obj, *args, **kwargs)

        check_output_folder(f"results/{obj_name}")
        save_to_file(f"results/{obj_name}/{func_name}.json", result)

        return result
    return wrapped


def save_pcg_auth(pcgauth):
    with open(PCG_AUTH, "w") as f:
        f.write(pcgauth)


def load_pcg_auth():
    with open(PCG_AUTH, "r") as f:
        return f.readlines()[0].strip()


def get_pokemon_battle_sprite(sprite_name, shiny=False, path=False, use_cache=False):
    check_output_folder(f"sprites/pokemon/shiny")

    is_shiny = "-shiny" if shiny else ""
    url = f"https://dev.bframework.de/static/pokedex/sprites/front{is_shiny}/{sprite_name}.gif"
    shiny_prefix = "shiny/" if shiny else ""
    file_path = f"sprites/pokemon/{shiny_prefix}{sprite_name}.gif"

    if use_cache is False or os.path.isfile(file_path) is False:
        res = requests.get(url)
        content = res.content

        with open(file_path, "wb") as o:
            o.write(content)

    if path:
        return file_path

    return open(file_path, "rb")


def get_pokemon_menu_sprite(sprite_name, shiny=False, path=False, use_cache=False):
    check_output_folder(f"sprites/menu_pokemon/shiny")

    is_shiny = "/shiny" if shiny else ""
    url = f"https://dev.bframework.de/static/pokedex/png-sprites/pokemon{is_shiny}/{sprite_name}.png"
    file_path = f"sprites/menu_pokemon{is_shiny}/{sprite_name}.png"

    if use_cache is False or os.path.isfile(file_path) is False:
        res = requests.get(url)
        content = res.content

        with open(file_path, "wb") as o:
            o.write(content)

    if path:
        return file_path

    return open(file_path, "rb")


def get_pokemon_sprite(sprite_name, shiny=False, battle=True, path=False, use_cache=False):
    if battle:
        return get_pokemon_battle_sprite(sprite_name, shiny, path, use_cache)

    return get_pokemon_menu_sprite(sprite_name, shiny, path, use_cache)


def get_sprite(sprite_type, sprite_name, shiny=False, battle=True, path=False, use_cache=False, tm_type=None):
    try:
        if sprite_type == "pokemon":
            return get_pokemon_sprite(sprite_name, shiny, battle, path, use_cache)
        elif sprite_type == "streamer":
            return get_streamer_avatar(sprite_name, path)
        return get_item_sprite(sprite_type, sprite_name, path, tm_type)
    except Exception as e:
        print(e)
    return None


def get_streamer_avatar(streamer, path=False):
    check_output_folder(f"sprites/avatars")
    file_path = f"sprites/avatars/{streamer}.png"

    if os.path.isfile(file_path):
        if path:
            return file_path
        return open(file_path, "rb")

    res = requests.get(f"https://www.twitch.tv/{streamer}")
    soup = BeautifulSoup(res.text, "html.parser")
    avatar = soup.find("meta", {"name": "twitter:image"})

    res = requests.get(avatar["content"])
    with open(file_path, "wb") as o:
        o.write(res.content)

    im = Image.open(file_path)
    im = im.resize((64, 64))
    im.save(file_path)

    if path:
        return file_path

    return open(file_path, "rb")


def get_item_sprite(sprite_type, sprite_name, path=False, tm_type=None):
    check_output_folder(f"sprites/{sprite_type}")

    tm_type = str(tm_type).lower()

    if sprite_type == "tm":
        file_path = f"sprites/tm/{tm_type}"
    else:
        file_path = f"sprites/{sprite_type}/{sprite_name}"

    if os.path.isfile(file_path + ".png"):
        if path:
            return file_path + ".png"
        return open(file_path + ".png", "rb")

    if sprite_type == "tm":
        url = f"https://poketwitch.bframework.de/static/twitchextension/items/tm/{tm_type}"
    else:
        url = f"https://poketwitch.bframework.de/static/twitchextension/items/{sprite_type}/{sprite_name}"
    try:

        res = requests.get(url + ".svg")

        soup = BeautifulSoup(res.text, "html.parser")
        svg = soup.find("image")

        if svg is None:
            with open(file_path + ".svg", "wb") as o:
                o.write(res.content)

            drawing = svg2rlg(file_path + ".svg")
            renderPM.drawToFile(drawing, file_path + ".png", fmt="PNG")

        else:
            href = svg["href"]

            s = href.split("base64,")[1]

            img_data = s.encode()
            content = base64.b64decode(img_data)
            with open(file_path + ".png", "wb") as o:
                o.write(content)
    except:
        url = url + ".png"

        res = requests.get(url)
        content = res.content

        if res.status_code != 200:
            return None

        with open(file_path + ".png", "wb") as o:
            o.write(content)

    file_path = file_path + ".png"

    if sprite_type != "pokemon":
        im = Image.open(file_path)
        im = im.resize((64, 64))
        im.save(file_path)

    if path:
        return file_path

    return open(file_path, "rb")
