"""The MegaTest"""
import fnmatch
import os

from . import maplist
from bsp_tool import BspVariant_for_magic
from bsp_tool import branches
from bsp_tool import load_bsp
from bsp_tool import lumps
from bsp_tool.branches import (ace_team, arkane, gearbox, id_software,
                               infinity_ward, nexon, outerlight, raven,
                               respawn, ritual, strata, utoplanet, valve)
from bsp_tool.infinity_ward import D3DBsp, InfinityWardBsp
from bsp_tool.id_software import QuakeBsp, ReMakeQuakeBsp
from bsp_tool.respawn import RespawnBsp
from bsp_tool.valve import GoldSrcBsp, ValveBsp

import pytest


# TEST MAP DATABASE
all_branches = {*branches.quake_based, *branches.source_based}

BspClass_for = {branch: BspVariant_for_magic.get(branch.FILE_MAGIC, None) for branch in all_branches}
BspClass_for.update({branch: QuakeBsp for branch in branches.of_engine["Quake"]})
BspClass_for.update({branch: GoldSrcBsp for branch in branches.of_engine["GoldSrc"]})
BspClass_for.update({branch: InfinityWardBsp for branch in infinity_ward.scripts})
BspClass_for.update({infinity_ward.modern_warfare: D3DBsp})
# ^ {valve.orange_box: ValveBsp}

# "It's OK to have garbage data if you never read it" - Earl Hammon Jr.
spec_of = {path: (BspClass_for[branch], branch, branch.GAME_VERSIONS[game])
           for branch in all_branches for game, path in branch.GAME_PATHS.items()
           if game in branch.GAME_VERSIONS}
# sourcemods
spec_of.update({mod: (ValveBsp, valve.orange_box, 20) for mod in maplist.sourcemod_dirs})
# apex archive
apex_seasons = ["Preseason", "Wild Frontier", "Battle Charge", "Meltdown", "Assimilation", "Fortune's Favour", "Boosted",
                "Ascension", "Fight Night", "Mayhem", "Legacy", "Emergence", "Evolution", "Escape", "Defiance", "Saviours",
                "Hunted", "Eclipse", "Revelry", "Arsenal", "Resurrection"]
spec_of.update({f"ApexLegends/season{i}": (RespawnBsp, respawn.apex_legends, 47) for i in range(7)})
spec_of.update({"ApexLegends/season7": (RespawnBsp, respawn.apex_legends, 48)})
spec_of.update({f"ApexLegends/season{i}": (RespawnBsp, respawn.apex_legends, 49) for i in (8, 9)})
spec_of.update({"ApexLegends/season10": (RespawnBsp, respawn.apex_legends, 50)})
spec_of.update({f"ApexLegends/season{i}": (RespawnBsp, respawn.apex_legends, (50, 1)) for i in (11, 12)})
spec_of.update({f"ApexLegends/season{i}": (RespawnBsp, respawn.apex_legends, (51, 1)) for i in range(13, 19)})
# local test maps (./tests/maps/game/, not .../game/mod/maps/)
spec_of.update({"Momentum Mod": (ValveBsp, strata.strata, 25),
                "ReMakeQuake": (ReMakeQuakeBsp, id_software.remake_quake, None),
                "Team Fortress 2": (ValveBsp, valve.orange_box, 20),
                "Titanfall 2": (RespawnBsp, respawn.titanfall2, 37)})
# games & mods not listed in branches
spec_of.update({"CSMalvinas": (ValveBsp, valve.orange_box, 20),
                "Dreamcast/Paranoia": (GoldSrcBsp, valve.goldsrc, valve.goldsrc.BSP_VERSION),
                "Vindictus/Client v1.69 EU": (ValveBsp, nexon.vindictus69, 20),
                "Xbox/Half-Life2": (ValveBsp, valve.source, 19)})

id_of = {path: game for branch in all_branches for game, path in branch.GAME_PATHS.items()}
id_of.update({f"ApexLegends/season{i}": f"Apex Legends - Season {i} - {name}" for i, name in enumerate(apex_seasons)})
id_of.update({"Quake/rerelease": "2021 Quake Re-Release",
              "Quake/rerelease/dopa": "Dimension of the Past",
              "Titanfall/beta": "Titanfall (Beta)",
              "TitanfallOnline": "Titanfall: Online",
              "Vindictus/Client v1.69 EU": "Vindictus v1.69"})

megatest_dirs = [(*dg, tuple(mds)) for dg, mds in maplist.installed_games.items()]
# ^ [("D:/Steam...", "Team Fortress 2", ("tf/maps", ...))]


def spec_str(BspClass, branch, version) -> str:
    BspClass = BspClass.__name__
    branch = ".".join(branch.__name__.split(".")[-2:])
    if version is None:
        return f"{BspClass} {branch}"
    if isinstance(version, tuple):
        major, minor = version
        version = f"v{major}.{minor}"
    else:
        version = f"v{version}"
    return " ".join([BspClass, branch, version])


drive_id = {"./tests/maps": "Local",
            "C:/Program Files (x86)/Steam/steamapps/sourcemods": "Sourcemods",
            "D:/SteamLibrary/steamapps/common": "Steam",
            "E:/Mod": "Extracted",
            "E:/Mod/Dreamcast": "Dreamcast",
            "E:/Mod/PS4": "PS4",
            "E:/Mod/Xbox": "Xbox",
            "E:/Mod/X360": "Xbox360"}

test_args = list()
# ^ [(ValveBsp, orange_box, 20, [(".../tf/maps/pl_upward.bsp", "tf/maps/pl_upward.bsp")])]
test_ids = list()
# ^ ["Team Fortress 2"]
for drive, game, map_dirs in sorted(megatest_dirs, key=lambda x: x[1].lower()):
    BspClass, branch, version = spec_of[game]
    maps = list()
    for map_dir in map_dirs:
        path = os.path.join(drive, game, map_dir)
        d3d_branches = (infinity_ward.call_of_duty2, infinity_ward.modern_warfare)
        ext = "*.[bB][sS][pP]" if branch not in d3d_branches else "*.d3dbsp"
        dir_maps = fnmatch.filter(os.listdir(path), ext)
        # TODO: filter out breaking maps (0 bytes, secret .mdl etc.)
        # TODO: split dirs w/ mixed formats
        # -- Apex Legends (Season 11 depots; some seasons keep old maps)
        # -- CS:O2 (TODO: autodetect/cso2.json)
        # -- Half-Life: Source (v17 & v18)
        # -- Quake 2 Rerelease (TODO: autodetect/quake2_rerelease.json)
        # -- SiN (1 map)
        # -- Vindictus (TODO: autodetect/vindictus.json)
        ...
        maps.extend((os.path.join(path, m), os.path.join(map_dir, m)) for m in dir_maps)
    test_args.append([BspClass, branch, version, maps])
    test_ids.append(f"{drive_id[drive]} | {id_of.get(game, game)}")


subtle = (ace_team.zeno_clash, arkane.dark_messiah_mp,
          gearbox.blue_shift, nexon.cso2_2018, nexon.vindictus,
          nexon.vindictus69, outerlight.outerlight, raven.hexen2,
          raven.soldier_of_fortune, raven.soldier_of_fortune2,
          ritual.sin, utoplanet.merubasu, valve.alien_swarm,
          valve.left4dead, valve.left4dead2, valve.source_filmmaker)
# TODO: add breaking maps to xfails
# -- 0 byte .bsp
# -- DDay-Normandy exclude list

easy_ids, easy_args = list(), list()
subtle_ids, subtle_args = list(), list()
for args, id_ in zip(test_args, test_ids):
    BspClass, branch, version, maps = args
    args = (spec_str(BspClass, branch, version), maps)
    if branch not in subtle:
        easy_args.append(args)
        easy_ids.append(id_)
    else:
        subtle_args.append(args)
        subtle_ids.append(id_)


def spec_str_of(bsp) -> str:
    BspClass = bsp.__class__
    branch = bsp.branch
    version = bsp.bsp_version
    return spec_str(BspClass, branch, version)


def loading_errors_of(bsp):
    if bsp.branch in branches.source_based:
        out = {f"{L} v{bsp.headers[L].version}": err
               for L, err in bsp.loading_errors.items()}
        if not isinstance(bsp.GAME_LUMP, lumps.RawBspLump):
            out.update({f"{L} v{bsp.GAME_LUMP.headers[L].version}": err
                        for L, err in bsp.GAME_LUMP.loading_errors.items()})
        return out
    else:
        return bsp.loading_errors


# TODO: test respawn.ExternalLumpManager elsewhere
# NOTE: If too many maps fail pytest will eat all your RAM!
@pytest.mark.parametrize("spec,maps", easy_args, ids=easy_ids)
def test_autodetect(spec, maps):
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


@pytest.mark.xfail
@pytest.mark.parametrize("spec,maps", subtle_args, ids=subtle_ids)
def test_hinting(spec, maps):
    errors = dict()  # {"map_dir/map_name.bsp": ["Error"]}
    for full_map_path, short_map_path in maps:
        try:
            bsp = load_bsp(full_map_path, branch)  # <- branch hint
            assert spec_str_of(bsp) == spec_str(BspClass, branch, version)
            assert len(loading_errors_of(bsp)) == 0
        except AssertionError as error:
            errors[short_map_path] = error
    no_fails = (len(errors) == 0)
    assert no_fails, f"{len(errors)} / {len(maps)} maps encountered loading errors"
