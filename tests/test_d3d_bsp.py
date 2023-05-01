# TODO: more in-depth tests
import fnmatch
import os
import pytest

from bsp_tool import D3DBsp
from bsp_tool.branches.infinity_ward import modern_warfare


bsps = list()
map_dirs = [os.path.join(os.getcwd(), "tests/maps/Call of Duty 4"),
            os.path.join(os.getcwd(), "tests/maps/Call of Duty 4/mp")]
# TODO: add more Call of Duty 4 dirs from maplist.installed_games & make it optional
for map_dir in map_dirs:
    for map_name in fnmatch.filter(os.listdir(map_dir), "*.d3dbsp"):
        bsps.append(D3DBsp(modern_warfare, os.path.join(map_dir, map_name)))


@pytest.mark.parametrize("bsp", bsps)
def test_no_errors(bsp: D3DBsp):
    assert len(bsp.loading_errors) == 0


@pytest.mark.parametrize("bsp", bsps)
def test_entites_loaded(bsp: D3DBsp):
    assert bsp.ENTITIES[0]["classname"] == "worldspawn"


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
