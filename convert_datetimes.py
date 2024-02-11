import json

FILENAME = "pokemon_computer.json"

def load_from_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(e)
    return {}


def save_to_file(filename, data):
    with open(filename, "w") as f:
        f.write(json.dumps(data, indent=4))


def main():
	data = load_from_file(FILENAME)
	save_to_file(FILENAME + ".bk", data)
	for poke_id in data.keys():
		if type(data[poke_id]["caughtAt"]) == dict:
			continue
		year, month, day = data[poke_id]["caughtAt"].split("T")[0].split("-")
		data[poke_id]["caughtAt"] = {"year": year, "month": month, "day": day}
	save_to_file(FILENAME, data)


if __name__ == "__main__":
	main()
