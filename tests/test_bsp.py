import fnmatch
import os

import pytest

from . import maplist
from bsp_tool import load_bsp
from bsp_tool import IdTechBsp, D3DBsp, RespawnBsp, ValveBsp


@pytest.mark.parametrize("group_path,game_name,map_dirs", [(*gps, ms) for gps, ms in maplist.installed_games.items()])
def test_load_bsp(group_path, game_name, map_dirs):
    """MEGATEST: 64GB+ of .bsp files!"""
    branch_names = {*maplist.goldsrc_dirs, *maplist.source_dirs}
    branch = game_name if game_name in branch_names else "unknown"
    errors = dict()
    # ^ {"game": ["errors"]}
    total = 0
    for map_dir in map_dirs:
        full_path = os.path.join(group_path, game_name, map_dir)
        if os.path.exists(full_path):
            files = os.listdir(full_path)
            maps = fnmatch.filter(files, "*bsp")  # .bsp & CoD2 .d3dbsp
            total += len(maps)
            assert len(maps) != 0, f"couldn't find any maps for {game_name} in {map_dir}"
            for m in maps:  # load every .bsp
                try:
                    bsp_filename = os.path.join(full_path, m)
                    if os.path.getsize(bsp_filename) == 0:
                        continue  # HL2/ d2_coast_02
                    bsp = load_bsp(bsp_filename, branch)
                    # NOTE: RAM usage skyrockets around ApexLegends
                    # -- do broken RespawnBsps leave their external lumps open in memory?
                    assert len(bsp.loading_errors) == 0, f"Bad formats: {', '.join(bsp.loading_errors.keys())}"
                except Exception as exc:
                    print(bsp)
                    errors[f"{map_dir}:{m}"] = exc
                    del bsp
    assert errors == dict(), f"failed on {len(errors)} out of {total} .bsps"


# TODO: generate from documentation / branch_scripts
expected_branch = {"ApexLegends": (RespawnBsp, 47, "respawn.apex_legends"),  # + 48 & 49
                   "Counter-Strike Global Offensive": (ValveBsp, 21, "valve.cs_go"),
                   "counter-strike source": (ValveBsp, 19, "valve.cs_s"),
                   "CoD1": (D3DBsp, 59, "infinity_ward.call_of_duty1"),
                   "CoD2": (D3DBsp, 4, "infinity_ward.call_of_duty1"),
                   "CSO2": (ValveBsp, 100, "nexon.cso2"),
                   "half-life 2": (ValveBsp, 19, "valve.cs_s"),
                   "Left 4 Dead 2": (ValveBsp, 20, "valve.orange_box"),
                   "SourceFilmmaker": (ValveBsp, 20, "valve.orange_box"),
                   "Team Fortress 2": (ValveBsp, 20, "valve.orange_box"),
                   "Titanfall": (RespawnBsp, 29, "respawn.titanfall"),
                   "TitanfallOnline": (RespawnBsp, 29, "respawn.titanfall"),
                   "Titanfall2": (RespawnBsp, 37, "respawn.titanfall2"),
                   "QuakeIII": (IdTechBsp, 46, "id_software.quake3")}
# ^ {"game": (type(bsp), bsp_version, "branch")}

# TODO: test_guess_by_file_magic
