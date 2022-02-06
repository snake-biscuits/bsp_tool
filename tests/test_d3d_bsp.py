# TODO: more in-depth tests
import fnmatch
import os
import pytest

from bsp_tool import D3DBsp
from bsp_tool.branches.infinity_ward import modern_warfare


d3dbsps = []
# TODO: add more Call of Duty 4 dirs from maplist.installed_games & make it optional
for map_dir in ["tests/maps/Call of Duty 4", "tests/maps/Call of Duty 4/mp"]:
    map_dir = os.path.join(os.getcwd(), map_dir)
    for map_name in fnmatch.filter(os.listdir(map_dir), "*[Bb][Ss][Pp]"):
        d3dbsps.append(D3DBsp(modern_warfare, os.path.join(map_dir, map_name)))


@pytest.mark.parametrize("d3dbsp", d3dbsps)
def test_no_errors(d3dbsp):
    assert len(d3dbsp.loading_errors) == 0, d3dbsp.filename


@pytest.mark.parametrize("d3dbsp", d3dbsps)
def test_entites_loaded(d3dbsp):
    assert d3dbsp.ENTITIES[0]["classname"] == "worldspawn", d3dbsp.filename


# TODO: implement .save_as method and test that uneditted saves match EXACTLY
# @pytest.mark.parametrize("d3dbsp", d3dbsps)
# def test_save_as(d3dbsp):  # NotImplemented
#     with open(d3d_bsp.filename, "rb") as file:
#         original = file.read()
#     test2.save_as(f"{d3dbsp.filename}.copy")
#     with open(f"{d3dbsp.filename}.copy", "rb") as file:
#         saved = file.read()
#     os.remove(f"{d3dbsp.filename}.copy")
#     assert original == saved

# TODO: assert UNUSED lump names are accurate
# -- warn if a lump is unexpectedly empty across all maps (test_deprecated?)
