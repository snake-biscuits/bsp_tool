# TODO: more in-depth tests
import fnmatch
import os
import pytest

from bsp_tool import ValveBsp
from bsp_tool.branches.valve import orange_box


bsps = []
map_dir = os.path.join(os.getcwd(), "tests/maps/Team Fortress 2")
# TODO: add more Team Fortress 2 dirs from maplist.installed_games & make it optional
for map_name in fnmatch.filter(os.listdir(map_dir), "*[Bb][Ss][Pp]"):
    bsps.append(ValveBsp(orange_box, os.path.join(map_dir, map_name)))


@pytest.mark.parametrize("bsp", bsps)
def test_no_errors(bsp: ValveBsp):  # NOTE: covered by test_bsp.py
    assert len(bsp.loading_errors) == 0, bsp.filename
    assert len(bsp.GAME_LUMP.loading_errors) == 0, bsp.filename


@pytest.mark.parametrize("bsp", bsps)
def test_entities_loaded(bsp: ValveBsp):
    assert bsp.ENTITIES[0]["classname"] == "worldspawn", bsp.filename


# TODO: implement .save_as method and test that uneditted saves match EXACTLY
# @pytest.mark.parametrize("bsp", d3dbsps)
# def test_save_as(bsp):  # NotImplemented
#     with open(bsp.filename, "rb") as file:
#         original = file.read()
#     test2.save_as(f"{bsp.filename}.copy")
#     with open(f"{bsp.filename}.copy", "rb") as file:
#         saved = file.read()
#     os.remove(f"{bsp.filename}.copy")
#     assert original == saved

# TODO: assert UNUSED lump names are accurate
# -- warn if a lump is unexpectedly empty across all maps (test_deprecated?)
