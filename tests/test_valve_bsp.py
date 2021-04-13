import os

from bsp_tool import ValveBsp
from bsp_tool.branches.valve import orange_box


test2 = ValveBsp(orange_box, "tests/maps/test2.bsp")  # TF2
upward = ValveBsp(orange_box, "tests/maps/upward.bsp")  # TF2


def test_no_errors():
    assert len(test2.loading_errors) == 0
    assert len(upward.loading_errors) == 0


def test_entites_loaded():
    assert test2.ENTITIES[0]["classname"] == "worldspawn"
    assert upward.ENTITIES[0]["classname"] == "worldspawn"


def test_save_as():
    with open("tests/maps/test2.bsp", "rb") as file:
        original = file.read()
    test2.save_as("tests/maps/test2_save_test.bsp")
    with open("tests/maps/test2_save_test.bsp", "rb") as file:
        saved = file.read()
    os.remove("tests/maps/test2_save_test.bsp")

    assert original == saved
