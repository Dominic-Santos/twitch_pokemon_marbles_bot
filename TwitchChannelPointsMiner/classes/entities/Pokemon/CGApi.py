import requests
import asyncio
from websockets.sync.client import connect
import ssl

from .Utils import save_to_json, load_pcg_auth

BASE_URL = "https://poketwitch.bframework.de/api/game/ext/"
TRAINER_URL = f"{BASE_URL}trainer/"
SHOP_URL = f"{BASE_URL}shop/"
BATTLE_URL = f"https://battle.bframework.de/api/game/ext/battle/"

ERROR_JWT_EXPIRE = -24


class API(object):
    def __init__(self, auth_token=None):
        self.auth = auth_token

    def get_headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Referer": "https://pm0qkv9g4h87t5y6lg329oam8j7ze9.ext-twitch.tv/",
            "Origin": "https://pm0qkv9g4h87t5y6lg329oam8j7ze9.ext-twitch.tv",
            "Accept": "application/json, text/plain, */*",
            "Authorization": self.auth
        }

    def get_auth_token(self):
        # replace with twitch method
        try:
            return load_pcg_auth()
        except:
            return None

    def refresh_auth(self):
        self.auth = self.get_auth_token()

    def _get_data(self, method, url, payload):
        if self.auth is None:
            return None

        response = requests.request(method, url, headers=self.get_headers(), json=payload)
        return response.json()

    def _do_request(self, method, url, payload={}):
        data = self._get_data(method, url, payload)

        if data is None or data.get("error", 0) == ERROR_JWT_EXPIRE:
            # jwt expired refresh token
            self.refresh_auth()

            # get data again, basically a retry
            data = self._get_data(method, url, payload)

        return data

    @save_to_json
    def get_pokemon(self, pokemon_id):
        return self._do_request("GET", TRAINER_URL + f"pokemon/{pokemon_id}/")

    @save_to_json
    def get_all_pokemon(self):
        return self._do_request("GET", TRAINER_URL + "pokemon/")

    @save_to_json
    def set_name(self, pokemon_id, name):
        return self._do_request("POST", TRAINER_URL + f"change-nickname/{pokemon_id}/", payload={"nickname": name})

    @save_to_json
    def get_inventory(self):
        return self._do_request("GET", TRAINER_URL + "inventory/")

    @save_to_json
    def get_pokedex(self):
        return self._do_request("GET", TRAINER_URL + "pokedex/")

    @save_to_json
    def get_pokedex_info(self, pokedex_id):
        # response {"content": {"pokedex_id": 1, "name": "Bulbasaur", "description": "etc", "weight": 6.9, "generation": 1, "type1": "poison", "type2": "grass", "base_stats": {"hp": 45, "speed": 45, "attack": 49, "defense": 49, "special_attack": 65, "special_defense": 65}}}
        return self._do_request("GET", TRAINER_URL + f"pokedex/info/?pokedex_id={pokedex_id}")

    @save_to_json
    def wondertrade(self, pokemon_id):
        # response is {"pokemon": {the info}}
        return self._do_request("POST", TRAINER_URL + f"wonder-trade/{pokemon_id}/")

    @save_to_json
    def get_missions(self):
        return self._do_request("GET", TRAINER_URL + "mission/")

    @save_to_json
    def get_shop(self):
        """
        returns:
        {
            "shopItems": [
                {
                    "name": "ultra_ball",
                    "price": 1000,
                    "displayName": "Ultra Ball",
                    "description": "An ultra-high-performance Pok\u00e9 Ball that provides a higher success rate for catching Pok\u00e9mon than a Great Ball.",
                    "type": 2,
                    "catchRate": "80%",
                    "category": "ball",
                    "tmType": null
                }, ...
            ]
        }

        """
        return self._do_request("GET", SHOP_URL)

    @save_to_json
    def buy_item(self, item_name, amount):
        # returns {"cash": 123}
        return self._do_request("POST", SHOP_URL + "purchase/", payload={"item_name": item_name, "amount": amount})

    @save_to_json
    def sell_item(self, item_id, amount):
        return self._do_request("POST", SHOP_URL + "sell-item/{item_id}/", payload={"amount": amount})

    # Battles

    @save_to_json
    def get_battle(self):
        # returns {"rejoinableBattle": false}
        return self._do_request("GET", BATTLE_URL + "check_if_rejoinable/")

    @save_to_json
    def get_teams(self):
        return self._do_request("GET", TRAINER_URL + "pokemon-team-list/")

    @save_to_json
    def team_remove(self, pokemon_id):
        return self._do_request("POST", TRAINER_URL + "pokemon-remove-team/", payload={"pokemon_id": pokemon_id})

    @save_to_json
    def team_add(self, pokemon_id):
        return self._do_request("POST", TRAINER_URL + "pokemon-set-team/", payload={"pokemon_id": pokemon_id})

    @save_to_json
    def team_change(self, team_id):
        return self._do_request("POST", TRAINER_URL + "pokemon-change-active-team/", payload={"team_id": team_id})

    @save_to_json
    def battle_create(self, mode, difficulty, team_id):
        # returns {"battle_id": 2993670}
        return self._do_request("POST", BATTLE_URL + "search/bot/", payload={"mode": mode, "difficulty": difficulty, "teamID": team_id})

    @save_to_json
    def battle_join(self):
        # returns {"battle_id": 2993670, "player_id": 5983522, "unique_battle_key": "CU8L4"}
        return self._do_request("POST", BATTLE_URL + "search/", payload={"action": "accept"})

    def battle_connect(self, battle_id, player_id):
        ssl_context = ssl.SSLContext()
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl_context.check_hostname = False
        try:

            connection = connect(
                f"wss://battle.bframework.de/ws/battle/?Authorization={self.auth}&battle_id={battle_id}&liveView=false&isViewer=false&language=en-gb&player_id={player_id}",
                ssl_context=ssl_context,
            )
        except Exception as e:
            print(e)
            connection = None
        return connection

    @save_to_json
    def use_item(self, item_id):
        # IE: wonder pass, returns {"itemsReceived": []}
        return self._do_request("POST", TRAINER_URL + f"use-item/{item_id}/")

    @save_to_json
    def use_item_on_pokemon(self, pokemon_id, item_id):
        # IE: use potion
        return self._do_request("POST", TRAINER_URL + f"use-item-on-pkm/", payload={"pokemon_id": pokemon_id, "item_id": item_id})

    @save_to_json
    def get_move(self, move_name):
        # returns {"name": "Poison Fang", "damage_class": "physical", "stat_chance": 0, "effect_chance": 50, "priority": 0, "description": "etc", "power": 50, "pp": 15, "accuracy": 100}
        return self._do_request("GET", BASE_URL + f"get-move-data/?move={move_name}")

    @save_to_json
    def add_to_team(self, pokemon_id, slot):
        # slot 0-5
        return self._do_request("POST", TRAINER_URL + f"pokemon-set-team-new/", payload={"pokemon_id": pokemon_id, "slot": slot})
