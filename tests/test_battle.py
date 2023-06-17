from . import weakness_resistance


def test_weakness():
    assert weakness_resistance("Fire", ["Fire"]) == 0.5
    assert weakness_resistance("Rock", ["Fighting", "Ground"]) == 0.25
    assert weakness_resistance("Ground", ["Fire", "Flying"]) == 0
    assert weakness_resistance("Grass", ["Water"]) == 2
    assert weakness_resistance("Grass", ["Water", "Ground"]) == 4
    assert weakness_resistance("Fighting", ["Dark", "Ground"]) == 2
