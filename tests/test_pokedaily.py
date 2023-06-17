from . import parse_message

TESTMSG = "You already have claimed your daily reward. Please come back in 5 hours, 25 minutes and 32 seconds."
TESTMSG2 = """You already have claimed your daily reward. Please come back in 13 hours, 54 minutes and 5 seconds.

Your last reward:

This is the Tentacool of the rewards, absolutely common:
:rarity_common::rarity_common::rarity_common::rarity_common::rarity_common::rarity_common::rarity_common:
:rarity_common: $10
:rarity_common: 2x Premier Ball
:rarity_common::rarity_common::rarity_common::rarity_common::rarity_common::rarity_common::rarity_common:"""
TESTMSG3 = """@Dom

You already have claimed your daily reward. Please come back in 16 hours, 25 minutes and 34 seconds.

Your last reward:

Did someone order an ultra rare reward?:
:rarity_ultra_rare::rarity_ultra_rare::rarity_ultra_rare::rarity_ultra_rare::rarity_ultra_rare::rarity_ultra_rare::rarity_ultra_rare:
:rarity_ultra_rare: $956
:rarity_ultra_rare: 1x Mood Mint
:rarity_ultra_rare: 1x Hyper Potion
:rarity_ultra_rare: 3x Repeat Ball
:rarity_ultra_rare: 1x Potion
:rarity_ultra_rare::rarity_ultra_rare::rarity_ultra_rare::rarity_ultra_rare::rarity_ultra_rare::rarity_ultra_rare::rarity_ultra_rare:"""


def test_pokedaily():
    result = parse_message(TESTMSG)
    assert result.repeat
    assert result.valid
    assert result.rarity == "unknown"
    assert len(result.rewards) == 0
    # hours minutes seconds in message + last_redeemed should add up to 20h 0m 0s
    assert result.last_redeemed["hours"] == 14
    assert result.last_redeemed["minutes"] == 34
    assert result.last_redeemed["seconds"] == 28


def test_pokedaily2():
    result = parse_message(TESTMSG2)
    assert result.repeat
    assert result.valid
    assert result.rarity == "common"
    assert len(result.rewards) == 2
    # hours minutes seconds in message + last_redeemed should add up to 20h 0m 0s
    assert result.last_redeemed["hours"] == 6
    assert result.last_redeemed["minutes"] == 5
    assert result.last_redeemed["seconds"] == 55


def test_pokedaily3():
    result = parse_message(TESTMSG3)
    assert result.repeat
    assert result.valid
    assert result.rarity == "ultra_rare"
    assert len(result.rewards) == 5
    # hours minutes seconds in message + last_redeemed should add up to 20h 0m 0s
    assert result.last_redeemed["hours"] == 3
    assert result.last_redeemed["minutes"] == 34
    assert result.last_redeemed["seconds"] == 26
