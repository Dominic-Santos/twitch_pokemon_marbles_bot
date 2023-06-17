from TwitchChannelPointsMinerLocal.classes.entities.Pokemon import Pokedaily
from TwitchChannelPointsMinerLocal.classes.Chat import DISCORD_POKEDAILY_SEARCH, POKEMON


def main():
    total_records = 25
    offset = 0
    rarities = {}

    while (offset < total_records):
        resp = POKEMON.discord.get(DISCORD_POKEDAILY_SEARCH.format(discord_id=POKEMON.discord.data["user"]) + f"&offset={offset}")
        total_records = resp["total_results"]

        for message in resp["messages"]:
            message_obj = Pokedaily.parse_message(message[0]["content"])

            if message_obj.valid and message_obj.repeat is False:
                rarities[message_obj.rarity] = rarities.get(message_obj.rarity, 0) + 1

        offset += 25

    print(rarities)


if __name__ == "__main__":
    main()
