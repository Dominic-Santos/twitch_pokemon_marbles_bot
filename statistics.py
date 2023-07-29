import argparse
import copy
import json
from dateutil.parser import parse
from datetime import datetime, timedelta
from utils import load_settings

TIERS = ["S", "A", "B", "C"]

DEFAULT_DICT = {
    "catch": [],
    "fail": [],
    "skip": [],
    "catch_balls": [],
    "fail_balls": [],
    "catch_tiers": [],
    "fail_tiers": [],
    "skip_tiers": []
}

DIV_ZERO = "-"
NEEDS_FILE = "need.json"


class Args():
    def __init__(self, args):
        self.when = args.when
        self.start = args.start
        self.end = args.end
        self.timeframe = args.timeframe
        self.fill = args.fill
        self.detailed = args.detailed
        self.days = args.days
        self.pokemon = args.pokemon
        self.lookup = args.lookup
        self.need = args.need

    def clean_args(self):
        today = datetime.now().date()
        if self.days is None or self.days <= 0:
            self.days = 30

        if self.lookup is not None:
            self.lookup = self.lookup.title().strip()

        if self.when == "all":
            self.when = "before"
            self.start = None
        elif self.when == "last":
            self.when = "after"
            self.start = str(today - timedelta(days=self.days))
        elif self.when == "today":
            self.when = "on"
            self.start = None
        elif self.when == "yesterday":
            self.when = "on"
            self.start = str(today - timedelta(days=1))

        if self.timeframe is None:
            self.timeframe = "daily"
        else:
            self.timeframe = self.timeframe

        if self.start is None:
            self.start = today
        else:
            try:
                self.start = parse(self.start).date()
            except Exception as e:
                print(e)
                self.start = today

        if self.end is None:
            self.end = self.start
        else:
            try:
                self.end = parse(self.end).date()
            except Exception as e:
                print(e)
                self.end = self.start

        if self.end < self.start:
            self.end = self.start


def main():
    funcs = {
        "on": when_on,
        "between": when_between,
        "after": when_after,
        "before": when_before,
        "all": None,
        "last": None,
        "today": None,
        "yesterday": None
    }

    parser = argparse.ArgumentParser(description="Statistics for the Pokemon Comunity Game catch rates")
    parser.add_argument("when", help="look at data relating to when", choices=sorted(funcs.keys()))
    parser.add_argument("-s", "--start", help="start date")
    parser.add_argument("-e", "--end", help="end date")
    parser.add_argument("-x", "--days", help="number of days to use with last", type=int)
    parser.add_argument("-t", "--timeframe", help="timeframe", choices=["hourly", "daily", "monthly"])
    parser.add_argument("-d", "--detailed", help="detailed summary", action="store_true")
    parser.add_argument("-p", "--pokemon", help="counts of pokemon that spawned", action="store_true")
    parser.add_argument("-l", "--lookup", help="how many times a pokemon has spawned")
    parser.add_argument("-f", "--fill", help="fill holes in data", action="store_true")
    parser.add_argument("-n", "--need", help="pokemon that have spawned and never caught", action="store_true")

    args = Args(parser.parse_args())
    args.clean_args()

    data = read_logs()
    funcs[args.when](data, args.start, args.end, args.fill)

    final = apply_timeframe(data, args.timeframe)

    if args.lookup is not None and args.lookup != "":
        lookup_pokemon(final, args.lookup)
    elif args.need:
        show_escaped(final)
    elif args.pokemon:
        show_pokemon(final)
    else:
        if args.timeframe == "hourly":
            length = 1
        elif args.timeframe == "daily":
            length = 2
        else:
            length = 3

        show_results(final, args.detailed, length)


def show_escaped(data):
    try:
        need = load_settings(NEEDS_FILE)["need"]
    except:
        need = None

    final = {}
    for k in sorted(data.keys()):
        for arr in ["fail"]:
            for pokemon in data[k][arr]:
                if pokemon not in final:
                    final[pokemon] = {"count": 0, "last_seen": None}
                final[pokemon].update({"count": final[pokemon]["count"] + 1, "last_seen": k})
        for arr in ["catch", "mission_catch", "mission_fail", "skip"]:
            for pokemon in data[k][arr]:
                final.pop(pokemon, None)
                if need is not None and pokemon in need:
                    need = [p for p in need if pokemon != p]

    if need is not None:
        for pokemon in list(final.keys()):
            if pokemon not in need:
                final.pop(pokemon)
        for pokemon in need:
            if pokemon not in final:
                final[pokemon] = {"count": 0, "last_seen": None}

        with open(NEEDS_FILE, "w") as f:
            f.write(json.dumps({"need": need}, indent=4))

    sorted_data = sorted([(pokemon, final[pokemon]["count"], final[pokemon]["last_seen"]) for pokemon in final], key=lambda x: (x[1], x[0]))

    print("Pokemon Missing (%s):" % (len(sorted_data)))
    for pokemon, count, last_seen in sorted_data:
        print("\t{pokemon} spawned {count} time{counts}, {seen}{date}".format(
            pokemon=pokemon,
            count=count,
            counts="" if count == 1 else "s",
            seen="never seen" if last_seen is None else "last seen on ",
            date="" if last_seen is None else last_seen
        ))


def lookup_pokemon(data, pokemon):
    count = 0
    appearances = []
    for k in sorted(data.keys()):
        tmp_appearances = {}
        for arr in ["mission_catch", "skip", "dunno", "mission_fail", "fail", "catch"]:
            tmp_count = data[k][arr].count(pokemon)
            if tmp_count > 0:
                tmp_appearances[arr.split("_")[-1]] = tmp_appearances.get(arr.split("_")[-1], 0) + tmp_count
                count += tmp_count
        if len(tmp_appearances.keys()) > 0:
            tmp_times = sum(tmp_appearances.values())
            appearances.append("{n} time{p} on {k} ({details})".format(
                n=tmp_times,
                p="" if tmp_times == 1 else "s",
                k=k,
                details=", ".join(["{k} x{v}".format(k=k, v=v) for k, v in tmp_appearances.items()])
            ))

    print("{pokemon} appeared {count} times".format(pokemon=pokemon, count=count))
    for appearance in appearances:
        print("\t{appearance}".format(appearance=appearance))


def show_pokemon(data):
    counts = {}
    for k in sorted(data.keys()):
        for arr in ["catch", "mission_catch", "skip", "dunno", "mission_fail", "fail"]:
            for pokemon in data[k][arr]:
                counts[pokemon] = counts.get(pokemon, 0) + 1

    results = {}
    for pokemon, count in counts.items():
        results.setdefault(str(count), []).append(pokemon)

    total = 0
    print("Top Pokemon Spawns:")
    for count, poke_list in sorted(results.items(), key=lambda x: int(x[0]), reverse=True):
        poke_list_sorted = sorted(poke_list)
        print("\t{count}:".format(count=count))
        total += len(poke_list)
        for i in range(0, len(poke_list), 10):
            print("\t\t{pokemon}".format(count=count, pokemon=", ".join(poke_list_sorted[i:i + 10])))
    print("Total different seen: {total}".format(total=total))


def leading(n, length, zeros=False):
    return (("0" if zeros else " ") * (length - len(str(n)))) + str(n)


def ball_catch_rates(final_rates, catches, fails):
    to_return = {}
    all_balls = list(set(catches + fails))
    for ball in all_balls:
        if ball in catches or ball in fails:
            catch = catches.count(ball)
            total = fails.count(ball) + catch
            if ball not in final_rates:
                final_rates[ball] = {"catch": 0, "total": 0}
            final_rates[ball]["catch"] += catch
            final_rates[ball]["total"] += total
            to_return[ball] = "{catch}/{total} ({percent}%)".format(catch=catch, total=total, percent=DIV_ZERO if total == 0 else round(catch * 100 / total))
    return to_return


def show_results(data, detailed, zeros):
    lines = []
    final_catch = 0
    final_total = 0
    final_rates = {}
    for k in sorted(data.keys()):
        caught = len(data[k]["catch"])
        skipped = len(data[k]["skip"])
        total = len(data[k]["catch"] + data[k]["fail"])
        total_skip = total + len(data[k]["skip"])
        caught_per = 0 if total == 0 else round(caught * 100 / total)
        skiped_per = 0 if total_skip == 0 else round(skipped * 100 / total_skip)
        final_catch += caught
        final_total += total
        catch_rates = ball_catch_rates(final_rates, data[k]["catch_balls"], data[k]["fail_balls"])
        tiers = {t: (
            data[k]["catch_tiers"].count(t),
            data[k]["fail_tiers"].count(t),
            data[k]["skip_tiers"].count(t),
        ) for t in TIERS}

        if detailed:
            s = "{date}:\n\tcaught={caught} ({caught_str})\n\tmissed={missed} ({missed_str})\n\tskipped={skipped} ({skipped_str})\n\t(caught={c}%, skipped={s}%)\n\tCatch Rates:\n{balls}\n\tTiers:\n{tiers}".format(
                date=k,
                caught=leading(len(data[k]["catch"]), zeros),
                missed=leading(len(data[k]["fail"]), zeros),
                skipped=leading(len(data[k]["skip"]), zeros),
                caught_str=",".join(data[k]["catch"]),
                missed_str=",".join(data[k]["fail"]),
                skipped_str=",".join(data[k]["skip"]),
                c=leading(caught_per, 3),
                s=leading(skiped_per, 3),
                balls="\t\t--" if len(catch_rates.keys()) == 0 else "\n".join(["\t\t{ball}: {rate}".format(
                    ball=ball,
                    rate=catch_rates[ball]
                ) for ball in catch_rates]),
                tiers="\n".join(["\t\t{tier}: {caught}/{caught_missed} ({total})".format(
                    tier=tier,
                    caught=tiers[tier][0],
                    caught_missed=sum(tiers[tier][:2]),
                    total=sum(tiers[tier])
                ) for tier in TIERS if sum(tiers[tier]) > 0])
            )
        else:
            s = "{date}: caught={caught}/{total}  skipped={skipped}  (caught={c}%, skipped={s}%)  balls->{balls}".format(
                date=k,
                caught=leading(len(data[k]["catch"]), zeros),
                total=leading(len(data[k]["fail"]) + len(data[k]["catch"]), zeros),
                skipped=leading(len(data[k]["skip"]), zeros),
                c=leading(caught_per, 3),
                s=leading(skiped_per, 3),
                balls=" --" if len(catch_rates.keys()) == 0 else ", ".join(["{ball} {rate}".format(
                    ball=ball.replace("ball", ""),
                    rate=catch_rates[ball]
                ) for ball in catch_rates])
            )
        lines.append(s)
        print(s)

    s = "Overall Catch Rate: {per}% ({catch}/{total}):".format(per=DIV_ZERO if final_total == 0 else round(final_catch * 100 / final_total), catch=final_catch, total=final_total)
    lines.append(s)
    print(s)

    s = "{balls}".format(
        balls="\t--" if len(final_rates.keys()) == 0 else "\n".join(["\t{ball}: {catch}/{total} ({percent}%)".format(
            ball=ball,
            catch=final_rates[ball]["catch"],
            total=final_rates[ball]["total"],
            percent=round(final_rates[ball]["catch"] * 100 / final_rates[ball]["total"])
        ) for ball in final_rates])
    )
    lines.append(s)
    print(s)

    final_string = "\n".join(lines)
    with open('statistics.txt', 'wb') as f:
        f.write(final_string.encode("utf-8"))


def split_daily(d):
    return d.split(" ")[0]


def split_monthly(d):
    return "-".join(d.split["-"][0:2])


def apply_timeframe(data, timeframe):
    if timeframe == "hourly":
        return data

    timeframes = {
        "daily": split_daily,
        "monthly": split_monthly
    }
    final = {}
    func = timeframes[timeframe]

    for k in data:
        new_k = func(k)
        if new_k not in final:
            final[new_k] = copy.deepcopy(data[k])
        else:
            final[new_k]["catch"] = final[new_k]["catch"] + data[k]["catch"]
            final[new_k]["fail"] = final[new_k]["fail"] + data[k]["fail"]
            final[new_k]["skip"] = final[new_k]["skip"] + data[k]["skip"]
            final[new_k]["catch_balls"] = final[new_k]["catch_balls"] + data[k]["catch_balls"]
            final[new_k]["fail_balls"] = final[new_k]["fail_balls"] + data[k]["fail_balls"]
            final[new_k]["catch_tiers"] = final[new_k]["catch_tiers"] + data[k]["catch_tiers"]
            final[new_k]["fail_tiers"] = final[new_k]["fail_tiers"] + data[k]["fail_tiers"]
            final[new_k]["skip_tiers"] = final[new_k]["skip_tiers"] + data[k]["skip_tiers"]

    return final


def when_on(data, start, end, fill):
    delete_before(data, start)
    delete_after(data, start)
    fill_data(fill, data, start, start)


def when_before(data, start, end, fill):
    delete_before(data, start)
    if len(data.keys()) > 0:
        first = parse(sorted(data.keys())[0].split(" ")[0]).date()
        fill_data(fill, data, first, start)


def when_after(data, start, end, fill):
    delete_after(data, start)
    if len(data.keys()) > 0:
        last = parse(sorted(data.keys())[-1].split(" ")[0]).date()
        fill_data(fill, data, start, last)


def when_between(data, start, end, fill):
    delete_before(data, end)
    delete_after(data, end)
    fill_data(fill, data, start, end)


def delete_before(data, d):
    for k in list(data.keys()):
        tmp = parse(k.split(" ")[0]).date()
        if tmp > d:
            del data[k]


def delete_after(data, d):
    for k in list(data.keys()):
        tmp = parse(k.split(" ")[0]).date()
        if tmp < d:
            del data[k]


def fill_data(fill, data, start, end):
    if not fill:
        return
    current_date = start
    while current_date <= end:
        for h in range(0, 24):
            d_string = "{d} {h}".format(
                d=str(current_date),
                h=leading(h, 2, zeros=True)
            )
            if d_string not in data:
                data[d_string] = copy.deepcopy(DEFAULT_DICT)
        current_date = current_date + timedelta(days=1)


def read_logs():
    data = {}

    # 2023-04-01 12:37:06 [32;20mCaught Drifloon (C) Lvl.9 7IV
    # 2023-04-01 13:52:18 [32;20mTrying to catch Carvanha with nightball because pokedex
    # 2023-04-01 13:52:23 [31;20mFailed to catch Carvanha
    # 2023-04-01 14:06:57 [31;20mDon't need pokemon, skipping
    # 2023-03-06 03:50:26 [36;20mPokemon spawned - processing 2023-03-06 03:50:04 Latias, 600BST, 40.0KG, tier S, types ['Dragon', 'Psychic']

    mindate = parse("2023-03-10")
    usedball = "unknown"
    lastpokemon = "unknown"
    lasttier = "unknown"

    with open("logs/pokemoncg.txt", mode="rb") as file:
        for uline in file:
            try:
                line = uline.decode("utf-8").rstrip()
            except:
                continue
            linedate = parse(line.split(" ")[0])
            if linedate < mindate:
                continue

            dateh = line.split(":")[0]
            if dateh not in data:
                data[dateh] = copy.deepcopy(DEFAULT_DICT)

            if "spawned" in line:
                lpm = line.split("processing")[1]
                if lpm.startswith(" 20"):
                    lastpokemon = lpm.split(":")[-1][3:].split(",")[0].strip()
                else:
                    lastpokemon = " ".join(lpm.split(",")[0].strip().split(" ")[1:]).strip()

                if lastpokemon != "":
                    print(">>", lastpokemon, "<<", line)
                    lasttier = line.split("tier")[1].strip()[0]
                else:
                    lastpokemon = "unknown"
                    lasttier = "unknown"

            elif "Trying to catch" in line:
                usedball = line.split("with")[1].split("because")[0].strip()

            elif "Failed to catch" in line:
                data[dateh]["fail"].append(lastpokemon)
                data[dateh]["fail_balls"].append(usedball)
                data[dateh]["fail_tiers"].append(lasttier)

            elif "Caught" in line:
                data[dateh]["catch"].append(lastpokemon)
                data[dateh]["catch_balls"].append(usedball)
                data[dateh]["catch_tiers"].append(lasttier)

            elif "Don't need pokemon" in line:
                data[dateh]["skip"].append(lastpokemon)
                data[dateh]["skip_tiers"].append(lasttier)

    return data


if __name__ == "__main__":
    main()
