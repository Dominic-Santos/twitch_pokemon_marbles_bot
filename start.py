# pip install Twitch-Channel-Points-Miner-v2
# python -m pip install --upgrade --force-reinstall git+https://github.com/bossoq/Twitch-Channel-Points-Miner-v2.git@fix-integrity
import multiprocessing
import logging
from time import sleep
from colorama import Fore
from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.logger import LoggerSettings, ColorPalette
from TwitchChannelPointsMiner.classes.Chat import ChatPresence
from TwitchChannelPointsMiner.classes.Discord import Discord
from TwitchChannelPointsMiner.classes.Telegram import Telegram
from TwitchChannelPointsMiner.classes.Settings import Priority, Events, FollowersOrder
from TwitchChannelPointsMiner.classes.entities.Bet import Strategy, BetSettings, Condition, OutcomeKeys, FilterCondition, DelayMode
from TwitchChannelPointsMiner.classes.entities.Streamer import Streamer, StreamerSettings
from utils import load_settings, get_login
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

chrome_options = Options()
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument("--enable-javascript")

login = get_login()
CLAIM_DROPS = True

twitch_miner = TwitchChannelPointsMiner(
    username=login["username"],
    password=login["password"],           # If no password will be provided, the script will ask interactively
    claim_drops_startup=CLAIM_DROPS,                  # If you want to auto claim all drops from Twitch inventory on the startup
    priority=[                                  # Custom priority in this case for example:
        Priority.STREAK,                        # - We want first of all to catch all watch streak from all streamers
        Priority.DROPS,                         # - When we don't have anymore watch streak to catch, wait until all drops are collected over the streamers
        Priority.ORDER                          # - When we have all of the drops claimed and no watch-streak available, use the order priority (POINTS_ASCENDING, POINTS_DESCEDING)
    ],
    logger_settings=LoggerSettings(
        save=True,                              # If you want to save logs in a file (suggested)
        console_level=logging.INFO,             # Level of logs - use logging.DEBUG for more info
        file_level=logging.DEBUG,               # Level of logs - If you think the log file it's too big, use logging.INFO
        emoji=False,                             # On Windows, we have a problem printing emoji. Set to false if you have a problem
        less=False,                             # If you think that the logs are too verbose, set this to True
        colored=True,                           # If you want to print colored text
        color_palette=ColorPalette(             # You can also create a custom palette color (for the common message).
            STREAMER_online="GREEN",            # Don't worry about lower/upper case. The script will parse all the values.
            streamer_offline="red",             # Read more in README.md
            BET_wiN=Fore.MAGENTA                # Color allowed are: [BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET].
        ),
        telegram=Telegram(                                                          # You can omit or leave None if you don't want to receive updates on Telegram
            chat_id=123456789,                                                      # Chat ID to send messages @GiveChatId
            token="123456789:shfuihreuifheuifhiu34578347",                          # Telegram API token @BotFather
            events=[Events.STREAMER_ONLINE, Events.STREAMER_OFFLINE, "BET_LOSE"],   # Only these events will be sent to the chat
            disable_notification=True,                                              # Revoke the notification (sound/vibration)
        ),
        discord=Discord(
            webhook_api="https://discord.com/api/webhooks/0123456789/0a1B2c3D4e5F6g7H8i9J",  # Discord Webhook URL
            events=[Events.STREAMER_ONLINE, Events.STREAMER_OFFLINE, Events.BET_LOSE],       # Only these events will be sent to the chat
        )
    ),
    streamer_settings=StreamerSettings(
        make_predictions=False,                  # If you want to Bet / Make prediction
        follow_raid=True,                       # Follow raid to obtain more points
        claim_drops=CLAIM_DROPS,                       # We can't filter rewards base on stream. Set to False for skip viewing counter increase and you will never obtain a drop reward from this script. Issue #21
        watch_streak=True,                      # If a streamer go online change the priority of streamers array and catch the watch screak. Issue #11
        chat=ChatPresence.ONLINE,               # Join irc chat to increase watch-time [ALWAYS, NEVER, ONLINE, OFFLINE]
        bet=BetSettings(
            strategy=Strategy.SMART,            # Choose you strategy!
            percentage=5,                       # Place the x% of your channel points
            percentage_gap=20,                  # Gap difference between outcomesA and outcomesB (for SMART strategy)
            max_points=50000,                   # If the x percentage of your channel points is gt bet_max_points set this value
            stealth_mode=True,                  # If the calculated amount of channel points is GT the highest bet, place the highest value minus 1-2 points Issue #33
            delay_mode=DelayMode.FROM_END,      # When placing a bet, we will wait until `delay` seconds before the end of the timer
            delay=6,
            minimum_points=20000,               # Place the bet only if we have at least 20k points. Issue #113
            filter_condition=FilterCondition(
                by=OutcomeKeys.TOTAL_USERS,     # Where apply the filter. Allowed [PERCENTAGE_USERS, ODDS_PERCENTAGE, ODDS, TOP_POINTS, TOTAL_USERS, TOTAL_POINTS]
                where=Condition.LTE,            # 'by' must be [GT, LT, GTE, LTE] than value
                value=800
            )
        )
    )
)

def create_driver():
    dr = webdriver.Chrome(options=chrome_options)
    # dr.set_window_size(400, 400)
    return dr

# You can customize the settings for each streamer. If not settings were provided, the script would use the streamer_settings from TwitchChannelPointsMiner.
# If no streamer_settings are provided in TwitchChannelPointsMiner the script will use default settings.
# The streamers array can be a String -> username or Streamer instance.

# The settings priority are: settings in mine function, settings in TwitchChannelPointsMiner instance, default settings.
# For example, if in the mine function you don't provide any value for 'make_prediction' but you have set it on TwitchChannelPointsMiner instance, the script will take the value from here.
# If you haven't set any value even in the instance the default one will be used
def get_rewards_channels():
    driver = create_driver()

    to_return = []
    for x in ["marbles-on-stream", "palworld"]:
        url = f"https://www.twitch.tv/directory/category/{x}?filter=drops"
        driver.get(url)
        sleep(5)
        channels = driver.find_elements(By.XPATH, "//p[@data-a-target='preview-card-channel-link']/div")
        
        for channel in channels:
            channel_name = channel.text
            if "(" in channel_name:
                channel_name = channel_name.split("(")[1][:-1]
            to_return.append((channel_name, x))

    return to_return

def run_miner(rewards_channels=[]):
    blacklist = ["TheTonyBlacks"]
    priorities = {"palworld": 4, "marbles-on-stream": 3}

    settings = load_settings()
    streamers = settings["streamers"]
    for channel, game in rewards_channels:
        if channel not in blacklist:
            streamers[channel] = {"goal": 1000000, "priority": priorities.get(game, 10), "pcg": False, "marbles": False}
    streamers_ordered = sorted(streamers.keys(), key=lambda x: streamers[x]["priority"])
    print(streamers_ordered)

    twitch_miner.mine(
        [
            Streamer(
                streamer,
                settings=StreamerSettings(
                    marbles=streamers[streamer].get("marbles", False),
                    pcg=streamers[streamer].get("pcg", True)
                ),
            ) for streamer in streamers_ordered
        ],                                  # Array of streamers (order = priority)
        followers=False,                    # Automatic download the list of your followers
        followers_order=FollowersOrder.ASC  # Sort the followers list by follow date. ASC or DESC
    )

def main():
    channels = get_rewards_channels()
    print("marbles channels", channels)
    run_miner(channels)


if __name__ == "__main__":
    main()