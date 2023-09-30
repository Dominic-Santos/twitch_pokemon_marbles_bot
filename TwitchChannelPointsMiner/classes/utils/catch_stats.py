import copy
from dateutil.parser import parse

from ..ChatLogs import LOGFILE

DIV_ZERO = "-"
DEFAULT_DICT = {
    "catch": [],
    "fail": [],
    "skip": [],
    "catch_balls": [],
    "fail_balls": [],
    "fail_tiers": [],
    "catch_tiers": [],
    "skip_tiers": [],
}


def read_catch_logs(the_date):
    data = copy.deepcopy(DEFAULT_DICT)
    tmp = {}

    # 2023-04-01 12:37:06 [32;20mCaught Drifloon (C) Lvl.9 7IV
    # 2023-04-01 13:52:18 [32;20mTrying to catch Carvanha with nightball because pokedex
    # 2023-04-01 13:52:23 [31;20mFailed to catch Carvanha
    # 2023-04-01 14:06:57 [31;20mDon't need pokemon, skipping
    # 2023-03-06 03:50:26 [36;20mPokemon spawned - processing 2023-03-06 03:50:04 Latias, 600BST, 40.0KG, tier S, types ['Dragon', 'Psychic']

    with open(LOGFILE, mode="rb") as file:
        for uline in file:
            try:
                line = uline.decode("utf-8").rstrip()
            except:
                continue
            linedate = parse(line.split(" ")[0])

            if "spawned" in line:
                lpm = line.split("processing")[1]
                if lpm.startswith(" 20"):
                    tmp["lastpokemon"] = lpm.split(":")[-1][3:].split(",")[0].strip()
                else:
                    tmp["lastpokemon"] = " ".join(lpm.split(",")[0].strip().split(" ")[1:]).strip()

                if tmp["lastpokemon"] != "":
                    tmp["lasttier"] = line.split("tier")[1].strip()[0]
                else:
                    tmp["lastpokemon"] = "unknown"
                    tmp["lasttier"] = "unknown"

            elif "Trying to catch" in line:
                tmp["usedball"] = line.split("with")[1].split("because")[0].strip()

            elif linedate.date() != the_date:
                continue

            elif "Failed to catch" in line:
                data["fail"].append(tmp.get("lastpokemon", "unknown"))
                data["fail_balls"].append(tmp.get("usedball", "unknown"))
                data["fail_tiers"].append(tmp.get("lasttier", "unknown"))

            elif "Caught" in line:
                data["catch"].append(tmp.get("lastpokemon", "unknown"))
                data["catch_balls"].append(tmp.get("usedball", "unknown"))
                data["catch_tiers"].append(tmp.get("lasttier", "unknown"))

            elif "Don't need pokemon" in line:
                data["skip"].append(tmp.get("lastpokemon", "unknown"))
                data["skip_tiers"].append(tmp.get("lasttier", "unknown"))

    return data


def show_results(data):
    lines = []

    final_catch = len(data["catch"])
    final_miss = len(data["fail"])
    final_skipped = len(data["skip"])
    final_attempts = final_catch + final_miss

    s = "Overall Catch Rate: {per}% ({catch}/{total}):".format(
        per=DIV_ZERO if final_attempts == 0 else round(final_catch * 100 / final_attempts),
        catch=final_catch,
        total=final_attempts
    )
    lines.append(s)

    if len(data["catch_balls"] + data["fail_balls"]) == 0:
        lines.append("\t--")

    else:
        all_balls = sorted(list(set(data["catch_balls"] + data["fail_balls"])))

        for ball in all_balls:
            ball_catch = data["catch_balls"].count(ball)
            ball_fail = data["fail_balls"].count(ball)
            ball_total = ball_catch + ball_fail
            s = "\t{ball}: {catch}/{total} ({percent}%)".format(
                ball=ball,
                catch=ball_catch,
                total=ball_total,
                percent=round(ball_catch * 100 / ball_total)
            )
            lines.append(s)

    lines.append("Skipped {skipped} Pokemon".format(skipped=final_skipped))

    return "\n".join(lines)


def get_catch_rates(the_date):
    data = read_catch_logs(the_date)
    result = show_results(data)
    return result
