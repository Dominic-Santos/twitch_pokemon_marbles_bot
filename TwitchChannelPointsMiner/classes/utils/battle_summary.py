from dateutil.parser import parse

from ..ChatLogs import LOGFILE


def get_battle_logs(the_date):
    total_exp = 0
    total_cash = 0
    total_battles = 0
    total_wins = 0

    with open(LOGFILE, mode="rb") as file:
        for uline in file:
            try:
                line = uline.decode("utf-8").rstrip()
            except:
                continue

            linedate = parse(line.split(" ")[0])
            if linedate.date() != the_date:
                continue

            if "the battle!" in line:
                rewards = line.split("rewards: ")[1].split(" and ")
                exp = int(rewards[0][:-3])
                cash = int(rewards[1][:-1])

                total_exp += exp
                total_cash += cash
                total_battles += 1
                if "Won" in line:
                    total_wins += 1

    return {
        "cash": total_cash,
        "exp": total_exp,
        "battles": total_battles,
        "wins": total_wins,
    }


def battle_summary(battle_date):
    battle_stats = get_battle_logs(battle_date)

    discord_msg = f"""Battle Summary - {battle_date}:
    Wins: {battle_stats['wins']}/{battle_stats['battles']}
    Exp: {battle_stats['exp']}
    $: {battle_stats['cash']}"""

    return discord_msg
