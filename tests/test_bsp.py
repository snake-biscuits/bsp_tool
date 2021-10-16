import fnmatch
import os

import pytest

from . import maplist
from bsp_tool import branches
from bsp_tool import load_bsp
from bsp_tool import IdTechBsp, InfinityWardBsp, RespawnBsp, ValveBsp


# helper for harder to detect games
game_scripts = {**{gp: branches.valve.sdk_2013 for gp in branches.valve.sdk_2013.GAME_PATHS},
                "BlackMesa": branches.valve.sdk_2013,  # for extracted_dirs
                "Half-Life/blue_shift": branches.gearbox.blue_shift,
                "Hexen2": branches.raven.hexen2,
                "left 4 dead": branches.valve.left4dead,
                "Left 4 Dead 2": branches.valve.left4dead2,
                "Vampire The Masquerade - Bloodlines": branches.troika.vampire,
                "Vindictus": branches.nexon.vindictus}
# ^ {"game_name": branch_script}


# NOTE: due to the dynamic way LumpClasses are loaded, they are not tested by this function
# -- only header.length % struct.calcsize(LumpClass._format) & SpecialLumpClasses are tested in-depth
@pytest.mark.parametrize("group_path,game_name,map_dirs", [(*gps, ms) for gps, ms in maplist.installed_games.items()])
def test_load_bsp(group_path, game_name, map_dirs):
    """MEGATEST: 69GB+ of .bsp files!"""
    branch_script = game_scripts.get(game_name)
    # NOTE: this is ugly and results in quite a few errors
    # auto-detection really shouldn't have to rely on precise strings
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
                        continue  # hl2/maps/d2_coast_02 is 0 bytes, idk why it shipped
                    if game_name == "half-life 2/episodic" and m == "ep1_citadel_00_demo.bsp":
                        continue  # broken HL2:EP1 map (game crashes on load)
                    elif game_name == "half-life 2/hl1" and m in ("c4a1y.bsp", "c4a1z.bsp"):
                        continue  # broken HL:Source maps (y is v18 and won't run, z is v19 and has broken IO)
                    bsp = load_bsp(bsp_filename, branch_script)
                    loading_errors = {**bsp.loading_errors}
                    if hasattr(bsp, "GAME_LUMP"):
                        loading_errors.update(bsp.GAME_LUMP.loading_errors)
                    failed_lumps = ', '.join(loading_errors.keys())
                    assert len(loading_errors) == 0, f"Failed to load the following lumps: {failed_lumps}"
                except AssertionError as ae:
                    print(bsp)  # print filename, branch_script & version to stdout
                    errors[f"{map_dir}/{m}"] = ae
                    del bsp
    assert errors == dict(), f"failed on {len(errors)} out of {total} .bsps"


# TODO: generate from documentation / branch_scripts
expected_branch = {"ApexLegends": (RespawnBsp, 47, "respawn.apex_legends"),  # + 48 & 49
                   "Counter-Strike Global Offensive": (ValveBsp, 21, "valve.sdk_2013"),
                   "counter-strike source": (ValveBsp, 19, "valve.cs_s"),
                   "CoD1": (InfinityWardBsp, 59, "infinity_ward.call_of_duty1"),
                   "CoD2": (InfinityWardBsp, 4, "infinity_ward.call_of_duty1"),
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
