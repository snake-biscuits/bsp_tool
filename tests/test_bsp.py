import fnmatch
import os

import pytest

from . import maplist
from bsp_tool import branches
from bsp_tool import lumps
from bsp_tool import load_bsp


# auto-detect helper for games with shared (file_magic, version)
# TODO: automatically detect the differences between these branches
# -- unique entities (not all maps wil have these)
# -- incorrect lump sizes (some maps may share a common denominator)
# -- a 100% accurate approach may not be possible
game_scripts = {**{gp: branches.valve.alien_swarm for gp in branches.valve.alien_swarm.GAME_PATHS},
                **{gp: branches.valve.sdk_2013 for gp in branches.valve.sdk_2013.GAME_PATHS},
                "BlackMesa": branches.valve.sdk_2013,  # for extracted_dirs
                "DarkMessiah/multiplayer": branches.arkane.dark_messiah_mp,
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

dday_mappack_excludes = ("dday3bh.bsp", "dofdtownbhv3.bsp", "gb1stdaybh.bsp", "iraidbhv3.bsp",
                         "LIDDUX.bsp", "schlitz1.bsp", "wiltzbh.bsp", "wiltzbhv3.bsp")
# TODO: make a pull request to https://github.com/PowaBanga/DDaynormandymaps removing these maps


# NOTE: due to the dynamic way LumpClasses are loaded, they are not tested by this function
# -- only header.length % struct.calcsize(LumpClass._format) & SpecialLumpClasses are tested in-depth
# TODO: this function is so general and has so many edge case handlers, you should really break if down smaller
@pytest.mark.parametrize("group_path,game_name,map_dirs", [(*gps, ms) for gps, ms in maplist.installed_games.items()])
def test_load_bsp(group_path, game_name, map_dirs):
    """MEGATEST: 69GB+ of .bsp files!"""
    # TODO: clean up all the edge case conditions elsewhere
    branch_script = game_scripts.get(game_name)  # forcing branch to test each branch_script
    # TODO: move branch_script tests to another test and test auto-detect here instead
    # -- e.g. test_list = [(BspClass, branch_script, ["mapdir", ...]), ...]
    errors = dict()
    # ^ {"map_dir/map_name.bsp": ["Error"]}
    types = set()  # printed on failure to aid in debugging
    # ^ {(BspClass, branch, version)}
    total = 0
    for map_dir in map_dirs:
        full_path = os.path.join(group_path, game_name, map_dir)
        if os.path.exists(full_path):
            files = os.listdir(full_path)
            maps = fnmatch.filter(files, "*[Bb][Ss][Pp]")  # .bsp, .BSP & CoD2 .d3dbsp
            maps = [m for m in maps if "." in m]  # DDayNormandy bomba2bsp edge case
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
                    elif game_name == "DDayNormandy" and m in dday_mappack_excludes:
                        continue  # maps probably tweaked in a text editor, all null bytes are spaces
                    bsp = load_bsp(bsp_filename, branch_script)
                    bsp.file.close()  # avoid OSError "Too many open files"
                    bsp_id = (bsp.__class__.__name__, bsp.branch.__name__, bsp.bsp_version)  # debug info
                    loading_errors = dict()
                    for lump_name, error in bsp.loading_errors.items():
                        lump_version = getattr(bsp.headers[lump_name], "version", None)
                        if lump_version is not None:
                            loading_errors[f"{lump_name} v{lump_version}"] = error
                        else:
                            loading_errors[lump_name] = error
                    if hasattr(bsp, "GAME_LUMP"):
                        if not isinstance(bsp.GAME_LUMP, lumps.RawBspLump):  # skip unmapped game lumps
                            loading_errors.update({f"{k} v{bsp.GAME_LUMP.headers[k].version}": v
                                                   for k, v in bsp.GAME_LUMP.loading_errors.items()})
                    if hasattr(bsp, "external"):
                        # TODO: actually read external SpecialLumpClasses lumps for a thorough check
                        # TODO: close any external lump files this opens to avoid OSError
                        # NOTE: if collecting external lumps for a BspClass w/o versions this will break
                        loading_errors.update({f"external.{k} v{bsp.external.headers[k].version}": v
                                               for k, v in bsp.external.loading_errors.items()})
                        if hasattr(bsp.external, "GAME_LUMP"):
                            if not isinstance(bsp.external.GAME_LUMP, lumps.RawBspLump):  # skip unmapped game lumps
                                loading_errors.update({f"external.GAME_LUMP.{k} v{bsp.external.GAME_LUMP.headers[k].version}": v  # noqa E501
                                                       for k, v in bsp.external.GAME_LUMP.loading_errors.items()})
                    del bsp  # close all open files before pytest freezes locals() on assert
                    assert len(loading_errors) == 0, ", ".join(loading_errors.keys())  # pass loading_errors out
                except NotImplementedError as nie:
                    # "DarkPlaces/maps/b_*.bsp" files are Quake .mdl with the .bsp extension
                    # https://www.gamers.org/dEngine/quake/spec/quake-spec32.html#CMDLF
                    # Quake stores pickup models as .bsp and renders them in a nested fashion
                    # so this is probably fine in Quake, but they still aren't .bsp files
                    if not (game_name == "DarkPlaces" and nie.args == ("Unknown file_magic: b'IDPO'",)):
                        errors[f"{map_dir}/{m}"] = nie
                except AssertionError as ae:  # should catch the `assert len(loading_errors) == ...` above
                    errors[f"{map_dir}/{m}"] = ae
                    types.add(bsp_id)
    assert errors == dict(), "\n".join([f"{len(errors)} out of {total} .bsps failed",
                                        *map(str, types),  # BspClass, branch_script, bsp_version
                                        *{ln for ae in errors.values() for ln in ae.args[0].split("\n")[0].split(", ")}])
