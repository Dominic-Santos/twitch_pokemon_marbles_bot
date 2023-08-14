import os
import json
import base64
import requests
from bs4 import BeautifulSoup
from PIL import Image
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

PCG_AUTH = "pokemon_auth_token.txt"


def check_output_folder(folder):
    if os.path.exists(folder) is False:
        os.makedirs(folder)


def save_to_file(filename, data):
    with open(filename, "w") as f:
        f.write(json.dumps(data, indent=4))


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


def get_pokemon_battle_sprite(sprite_name, shiny=False, path=False):
    check_output_folder(f"sprites/pokemon/shiny")

    is_shiny = "-shiny" if shiny else ""
    url = f"https://dev.bframework.de/static/pokedex/sprites/front{is_shiny}/{sprite_name}.gif"

    res = requests.get(url)
    content = res.content

    shiny_prefix = "shiny/" if shiny else ""
    file_path = f"sprites/pokemon/{shiny_prefix}{sprite_name}.gif"

    with open(file_path, "wb") as o:
        o.write(content)

    if path:
        return file_path

    return open(file_path, "rb")


def get_pokemon_menu_sprite(sprite_name, shiny=False, path=False):
    check_output_folder(f"sprites/menu_pokemon/shiny")

    is_shiny = "/shiny" if shiny else ""
    url = f"https://dev.bframework.de/static/pokedex/png-sprites/pokemon{is_shiny}/{sprite_name}.png"

    res = requests.get(url)
    content = res.content

    file_path = f"sprites/menu_pokemon{is_shiny}/{sprite_name}.png"

    with open(file_path, "wb") as o:
        o.write(content)

    if path:
        return file_path

    return open(file_path, "rb")


def get_pokemon_sprite(sprite_name, shiny=False, battle=True, path=False):
    if battle:
        return get_pokemon_battle_sprite(sprite_name, shiny, path)

    return get_pokemon_menu_sprite(sprite_name, shiny, path)


def get_sprite(sprite_type, sprite_name, shiny=False, battle=True, path=False):
    try:
        if sprite_type == "pokemon":
            return get_pokemon_sprite(sprite_name, shiny, battle, path)
        elif sprite_type == "streamer":
            return get_streamer_avatar(sprite_name, path)
        return get_item_sprite(sprite_type, sprite_name, path)
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


def get_item_sprite(sprite_type, sprite_name, path=False):
    check_output_folder(f"sprites/{sprite_type}")

    file_path = f"sprites/{sprite_type}/{sprite_name}"

    if os.path.isfile(file_path + ".png"):
        if path:
            return file_path + ".png"
        return open(file_path + ".png", "rb")

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
