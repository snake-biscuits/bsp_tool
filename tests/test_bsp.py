import collections
import fnmatch
import os

import pytest

from . import maplist
from bsp_tool import load_bsp
from bsp_tool import IdTechBsp, D3DBsp, RespawnBsp, ValveBsp


@pytest.mark.parametrize("group_path,game_name,map_dirs", [(*gps, ms) for gps, ms in maplist.installed_games.items()])
def test_load_bsp(group_path, game_name, map_dirs):
    """MEGATEST: 64GB+ of .bsp files!"""
    errors = collections.defaultdict(list)
    # ^ {"game": ["errors"]}
    for map_dir in map_dirs:
        full_path = os.path.join(group_path, game_name, map_dir)
        if os.path.exists(full_path):
            files = os.listdir(full_path)
            maps = fnmatch.filter(files, "*bsp")  # .bsp & CoD2 .d3dbsp
            # associated_files = fnmatch.filter(files, "*.lmp")  # Source Engine External Lumps
            # associated_files.extend(fnmatch.filter(files, "*.bsp_lump"))  # Respawn external lumps
            # associated_files.extend(fnmatch.filter(files, "*.ent"))  # Respawn bonus entity lumps
            # TODO: .nav, .ain, /graphs, soundscript, particle manifest, .vmf, .map
            assert len(maps) != 0, f"couldn't find any maps for {game_name} in {map_dir}"
            for m in maps:  # load every .bsp
                try:
                    bsp = load_bsp(os.path.join(full_path, m))
                    # NOTE: hitting max ram usage (16GB) on Apex Legends
                    # -- do broken RespawnBsp leave their external lumps in memory?
                    # TODO: verify documentation matches game
                    assert len(bsp.loading_errors) == 0, f"incorrect lump format(s) for {game_name}"
                except AssertionError:
                    errors[f"{map_dir}:{m}"].append(bsp.loading_errors)
                    del bsp
    # try to report on as many maps at once
    assert len(errors) == 0


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

# TODO: verify documentation
