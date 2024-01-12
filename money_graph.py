from TwitchChannelPointsMiner.classes.utils.money_graph import run_graph
from TwitchChannelPointsMiner.classes.entities.Pokemon.Discord import Discord
from TwitchChannelPointsMiner.classes.entities.Pokemon.Utils import load_from_file
from TwitchChannelPointsMiner.classes.entities.Pokemon.PokemonCG import SETTINGS_FILE


def main():

    settings = load_from_file(SETTINGS_FILE)
    discord = Discord()
    discord.set(settings["discord"])
    discord.connect()

    run_graph(discord)
    print("Done")


if __name__ == "__main__":
    main()
