import fnmatch
import os

import pytest

from . import maplist
from bsp_tool import branches
from bsp_tool import lumps
from bsp_tool import load_bsp


# auto-detect helper for games with shared identifiers
# TODO: use unique entity values & lump sizes to identify tricky maps
game_scripts = {**{gp: branches.valve.alien_swarm for gp in branches.valve.alien_swarm.GAME_PATHS},
                **{gp: branches.valve.sdk_2013 for gp in branches.valve.sdk_2013.GAME_PATHS},
                "BlackMesa": branches.valve.sdk_2013,  # for extracted_dirs
                "DarkMessiah/multiplayer": branches.arkane.dark_messiah_multiplayer,
                "Half-Life/blue_shift": branches.gearbox.blue_shift,
                "Hexen2": branches.raven.hexen2,
                "left 4 dead": branches.valve.left4dead,
                "Left 4 Dead 2": branches.valve.left4dead2,
                "SiN": branches.ritual.sin,
                "SoF": branches.raven.soldier_of_fortune,
                "SoF2": branches.raven.soldier_of_fortune2,
                "StarWarsJediKnightII": branches.raven.soldier_of_fortune2,
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
    types = set()
    # ^ {(BspClass, branch, version)}
    total = 0
    for map_dir in map_dirs:
        full_path = os.path.join(group_path, game_name, map_dir)
        if os.path.exists(full_path):
            files = os.listdir(full_path)
            maps = fnmatch.filter(files, "*[Bb][Ss][Pp]")  # .bsp, .BSP & CoD2 .d3dbsp
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
                    # TODO: assert game_name, bsp_version and BspVariant match
                    loading_errors = {**bsp.loading_errors}
                    if hasattr(bsp, "GAME_LUMP"):
                        if not isinstance(bsp.GAME_LUMP, lumps.RawBspLump):  # HACK: incomplete Vindictus GameLump
                            loading_errors.update(bsp.GAME_LUMP.loading_errors)
                    assert len(loading_errors) == 0, ", ".join(loading_errors.keys())
                except AssertionError as ae:
                    errors[f"{map_dir}/{m}"] = ae
                    types.add((bsp.__class__.__name__, bsp.branch.__name__, bsp.bsp_version))
                    del bsp
    assert errors == dict(), "\n".join([f"{len(errors)} out of {total} .bsps failed", *map(str, types)])
