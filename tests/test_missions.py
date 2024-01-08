from . import Missions, Pokemon, load_mission_data

MISSIONS = Missions()

MISSION_DATA = {
    str(x): load_mission_data(x) for x in range(1, 16)
}


def test_check_missions_case1():
    MISSIONS.set(MISSION_DATA["1"])
    pokemon = Pokemon()
    pokemon.types = ["Normal", "Fairy"]
    reasons = MISSIONS.check_all_missions(pokemon)
    wondertrade_reasons = MISSIONS.check_all_wondertrade_missions(pokemon)

    assert len(reasons) == 1
    assert len(wondertrade_reasons) == 1
    assert "miss" in reasons
    assert len([x for x in wondertrade_reasons if x.startswith("type ")]) > 0
    assert MISSIONS.have_wondertrade_missions()


def test_check_missions_completed():
    MISSIONS.set(MISSION_DATA["1"])
    tmp_missions = {"missions": []}
    mission_title = "Wondertrade normal types"

    for mission in MISSION_DATA["1"]["missions"]:
        if mission["name"] == mission_title:
            mission_goal = mission["goal"]
            mission["progress"] = mission_goal
            reward = mission["rewardItem"]["name"]
            reward_amount = mission["rewardItem"]["amount"]
        tmp_missions["missions"].append(mission)

    MISSIONS.set(tmp_missions)

    completed = MISSIONS.get_completed()
    assert len(completed) == 1
    assert completed[0][0] == f"{mission_title} ({mission_goal})"
    assert completed[0][1]["reward"] == f"{reward_amount} {reward}"


def test_check_missions_case2():
    MISSIONS.set(MISSION_DATA["2"])
    pokemon = Pokemon()
    pokemon.types = ["Fire", "Fairy"]
    pokemon.hp = 200
    reasons = MISSIONS.check_all_missions(pokemon)
    wondertrade_reasons = MISSIONS.check_all_wondertrade_missions(pokemon)

    assert len(reasons) == 1
    assert len(wondertrade_reasons) == 1
    assert len([x for x in reasons if x.startswith("type ")]) > 0
    assert "bst" in wondertrade_reasons

    pokemon = Pokemon()
    pokemon.types = ["Fairy"]
    pokemon.hp = 900
    reasons = MISSIONS.check_all_missions(pokemon)
    wondertrade_reasons = MISSIONS.check_all_wondertrade_missions(pokemon)

    assert len(reasons) == 0
    assert len(wondertrade_reasons) == 0
    assert MISSIONS.have_wondertrade_missions()


def test_check_missions_case3():
    MISSIONS.set(MISSION_DATA["3"])
    pokemon = Pokemon()
    pokemon.types = ["Ghost", "Ground"]
    pokemon.weight = 300
    reasons = MISSIONS.check_all_missions(pokemon)
    wondertrade_reasons = MISSIONS.check_all_wondertrade_missions(pokemon)

    assert len(reasons) == 2
    assert len(wondertrade_reasons) == 1
    assert len([x for x in reasons if x.startswith("type ")]) > 0
    assert "weight" in reasons
    assert len([x for x in wondertrade_reasons if x.startswith("type ")]) > 0


def test_check_missions_case4():
    MISSIONS.set(MISSION_DATA["4"])
    missions = MISSIONS.data
    assert len(missions.keys()) == 5
    assert len(missions.get("bst", [])) == 1
    assert missions.get("bst", [(0, 0)])[0] == (0, 333)
    assert len(missions.get("type", [])) == 1
    assert missions.get("type", ["none"])[0] == "Psychic"
    assert missions.get("attempt", False) == True
    assert missions.get("miss", False) == True
    assert missions.get("wondertrade", False) == True


def test_check_missions_case5_fish():
    MISSIONS.set(MISSION_DATA["5"])
    missions = MISSIONS.data
    assert missions.get("fish", False) == True
    assert missions.get("weight", [(0, 0)])[0] == (250, 9999)


def test_check_missions_case6():
    MISSIONS.set(MISSION_DATA["6"])
    missions = MISSIONS.data
    assert missions.get("miss", False) == False
    assert missions.get("attempt", False) == True
    assert missions.get("miss_type", []) == ["Fighting"]


def test_check_missions_case7():
    MISSIONS.set(MISSION_DATA["7"])
    missions = MISSIONS.data

    wondertrade_bst = missions.get("wondertrade_bst", [])
    assert len(wondertrade_bst) == 1
    assert wondertrade_bst[0] == (500, 9999)
    assert "Fire" in missions.get("type", [])
    assert missions.get("attempt", False)
    assert "Fighting" in missions.get("miss_type", [])
    assert "Dragon" in missions.get("type", [])
    assert "Normal" in missions.get("type", [])


def test_check_missions_case8():
    MISSIONS.set(MISSION_DATA["8"])
    missions = MISSIONS.data

    wondertrade_bst = missions.get("wondertrade_bst", [])
    assert len(wondertrade_bst) == 1
    assert wondertrade_bst[0] == (500, 9999)
    assert "Dragon" in missions.get("wondertrade_type", [])

    pokemon = Pokemon()

    pokemon.types = ["Ghost", "Dragon"]
    pokemon.hp = 700

    reasons = MISSIONS.check_all_wondertrade_missions(pokemon)
    assert len(reasons) == 2
    assert len([x for x in reasons if x.startswith("type ")]) > 0
    assert "bst" in reasons
    assert MISSIONS.have_wondertrade_missions()


def test_check_missions_case9():
    MISSIONS.set(MISSION_DATA["9"])
    missions = MISSIONS.data

    wondertrade_bst = missions.get("wondertrade_bst", [])
    assert len(wondertrade_bst) == 1
    assert wondertrade_bst[0] == (0, 362)

    catch_type = missions.get("type", [])
    assert "Rock" in catch_type
    assert len(catch_type) == 1

    miss_type = missions.get("miss_type", [])
    assert "Grass" in miss_type
    assert len(miss_type) == 1

    assert missions.get("monotype", False)

    pokemon = Pokemon()
    pokemon.types = ["Rock", "Dragon"]
    pokemon.hp = 1
    reasons = MISSIONS.check_all_missions(pokemon)
    assert len([x for x in reasons if x.startswith("type ")]) > 0
    assert "monotype" not in reasons

    reasons = MISSIONS.check_all_wondertrade_missions(pokemon)
    assert "bst" in reasons

    pokemon = Pokemon()
    pokemon.types = ["Grass"]
    reasons = MISSIONS.check_all_missions(pokemon)
    assert "monotype" in reasons
    assert len([x for x in reasons if x.startswith("miss_type ")]) > 0

    assert missions.get("stadium", "") == "medium"
    assert MISSIONS.check_stadium_mission()
    assert MISSIONS.check_stadium_difficulty() == "medium"


def test_check_missions_case10():
    MISSIONS.set(MISSION_DATA["10"])
    missions = MISSIONS.data

    assert missions.get("stadium", "") == "easy"
    assert MISSIONS.check_stadium_mission()
    assert MISSIONS.check_stadium_difficulty() == "easy"

    catch_type = missions.get("type", [])
    assert "Bug" in catch_type
    assert len(catch_type) == 1

    wondertrade_type = missions.get("wondertrade_type", [])
    print("here", wondertrade_type, "here")
    assert "Fire" in wondertrade_type
    assert len(wondertrade_type) == 1


def test_check_missions_case11():
    MISSIONS.set(MISSION_DATA["11"])
    missions = MISSIONS.data

    assert MISSIONS.have_wondertrade_missions()
    assert MISSIONS.have_mission("wondertrade_level")

    wondertrade_level = missions.get("wondertrade_level", [])
    assert len(wondertrade_level) == 1
    assert wondertrade_level[0] == (13, 9999)

    pokemon = Pokemon()
    pokemon.types = ["Rock", "Dragon"]
    pokemon.level = 15
    reasons = MISSIONS.check_all_wondertrade_missions(pokemon)
    assert "level" in reasons

    pokemon.level = 5

    reasons = MISSIONS.check_all_wondertrade_missions(pokemon)
    assert "level" not in reasons


def test_check_missions_skipping():
    # name_goal_itemID_amount
    MISSIONS.skip = ["Wondertrade with a level higher than 13_14_27_6"]
    MISSIONS.set(MISSION_DATA["11"])
    missions = MISSIONS.data
    MISSIONS.skip = []

    assert MISSIONS.have_wondertrade_missions() is False
    assert MISSIONS.have_mission("wondertrade_level") is False

    wondertrade_level = missions.get("wondertrade_level", [])
    assert len(wondertrade_level) == 0

    pokemon = Pokemon()
    pokemon.types = ["Rock", "Dragon"]
    pokemon.level = 15
    reasons = MISSIONS.check_all_wondertrade_missions(pokemon)
    assert "level" not in reasons

    pokemon.level = 5

    reasons = MISSIONS.check_all_wondertrade_missions(pokemon)
    assert "level" not in reasons


def test_check_missions_event():
    MISSIONS.event = ["Fish", "Fire"]
    MISSIONS.set(MISSION_DATA["12"])
    missions = MISSIONS.data

    assert MISSIONS.have_mission("event")

    have_event_mission = missions.get("event", True)
    assert have_event_mission

    pokemon = Pokemon()
    pokemon.types = ["Rock", "Dragon"]
    pokemon.level = 15
    pokemon.is_fish = True
    reasons = MISSIONS.check_all_missions(pokemon)
    assert "event (Fish)" in reasons

    pokemon.types = ["Fire"]
    pokemon.is_fish = False
    reasons = MISSIONS.check_all_missions(pokemon)
    assert "event (Fire)" in reasons


def test_check_missions_miss_type():
    MISSIONS.set(MISSION_DATA["13"])

    assert MISSIONS.have_mission("miss_type")

    pokemon = Pokemon()
    pokemon.types = ["Rock", "Dragon"]
    reasons = MISSIONS.check_all_missions(pokemon)
    assert "miss_type (Normal)" not in reasons

    pokemon.types = ["Normal"]
    pokemon.is_fish = False
    reasons = MISSIONS.check_all_missions(pokemon)
    assert "miss_type (Normal)" in reasons


def test_check_ball_mission():
    MISSIONS.set(MISSION_DATA["14"])
    assert MISSIONS.have_mission("ball")
    assert MISSIONS.data["ball"] == ["great"]


def test_weight_mission():
    MISSIONS.set(MISSION_DATA["15"])
    assert MISSIONS.have_mission("weight")
    assert len(MISSIONS.data["weight"]) == 1
    assert MISSIONS.data["weight"][0] == (94, 9999)
