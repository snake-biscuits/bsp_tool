from collections import defaultdict
import fnmatch
import os
from typing import List, Tuple

from .megatest import id_of, loading_errors_of, spec_str_of
from bsp_tool import load_bsp

import pytest


test_map_dirs = {
    game: [""]
    for game in os.listdir("./tests/maps/")
    if game != "Xbox360"}

test_map_dirs.update({"Call of Duty 4": ["", "mp"]})
# NOTE: skipping Xbox360 as "Xbox360/The Orange Box" has invalid GameLump.sprp
# test_map_dirs.update({
#      f"Xbox360/{game}": [""]
#      for game in os.listdir("./tests/maps/Xbox360")})

# TODO: automate w/ megatest functions
spec_of = {
    "Call of Duty 4": "D3DBsp infinity_ward.modern_warfare v22",
    "Momentum Mod": "ValveBsp strata.strata v25",  # sprp v12
    "Quake": "QuakeBsp id_software.quake v29",
    "Quake 2": "IdTechBsp id_software.quake2 v38",
    "Quake 3 Arena": "IdTechBsp id_software.quake3 v46",
    "ReMakeQuake": "ReMakeQuakeBsp id_software.remake_quake",  # BSP2
    "Team Fortress 2": "ValveBsp valve.orange_box v20",  # sprp v10
    "Titanfall 2": "RespawnBsp respawn.titanfall2 v37"}  # sprp v12
#   "Xbox360/The Orange Box": "ValveBsp valve.orange_box_x360 v20"
# ^ {"game": "BspClass branch [vXX] [sprp vYY]"}


ext_of = defaultdict(lambda: "*.bsp")
ext_of.update({"Call of Duty 4": "*.d3dbsp"})


def maplist_of(game: str) -> List[Tuple[str]]:
    out = list()
    ext = ext_of[game]
    for map_dir in test_map_dirs[game]:
        full_map_dir = os.path.join("./tests/maps/", game, map_dir)
        out.extend([
            (os.path.join(full_map_dir, map_file), (os.path.join(map_dir, map_file)))
            for map_file in fnmatch.filter(os.listdir(full_map_dir), ext)])
    return out


test_args = [
    (spec_of[game], maplist_of(game))
    for game in test_map_dirs]

test_ids = [
    id_of.get(game, game)
    for game in test_map_dirs]


@pytest.mark.parametrize("spec,maps", test_args, ids=test_ids)
def test_autodetect(spec: str, maps: List[Tuple[str]]):
    errors = dict()  # {"map_dir/map_name.bsp": ["Error"]}
    for full_map_path, short_map_path in maps:
        try:
            bsp = load_bsp(full_map_path)
            assert spec_str_of(bsp) == spec
            assert len(loading_errors_of(bsp)) == 0
        except AssertionError as error:
            errors[short_map_path] = error
    no_fails = (len(errors) == 0)
    assert no_fails, f"{len(errors)} / {len(maps)} maps encountered loading errors"
