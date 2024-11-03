"""The MegaTest"""
import fnmatch
import os
import re

from . import maplist
from bsp_tool import branches
from bsp_tool import load_bsp
from bsp_tool import lumps
from bsp_tool.autodetect import BspClass_for_magic
from bsp_tool.branches import (
    ace_team, arkane, gearbox, id_software, infinity_ward,
    nexon, outerlight, raven, respawn, ritual, strata, utoplanet, valve)
from bsp_tool.id_software import QuakeBsp
from bsp_tool.infinity_ward import D3DBsp, InfinityWardBsp
from bsp_tool.nexon import NexonBsp
from bsp_tool.valve import GoldSrcBsp

import pytest


# TEST MAP DATABASE
all_branches = {*branches.quake_based, *branches.source_based}

# "It's OK to have garbage data if you never read it" - Earl Hammon Jr.
spec_of = {path: (branch, branch.GAME_VERSIONS[game])
           for branch in all_branches
           for game, path in branch.GAME_PATHS.items()
           if game in branch.GAME_VERSIONS}
# sourcemods
spec_of.update({mod: (valve.orange_box, 20) for mod in maplist.sourcemod_dirs})
# apex archive
apex_seasons = [
    "Preseason", "Wild Frontier", "Battle Charge", "Meltdown", "Assimilation", "Fortune's Favour", "Boosted",
    "Ascension", "Fight Night", "Mayhem", "Legacy", "Emergence", "Evolution", "Escape", "Defiance", "Saviours",
    "Hunted", "Eclipse", "Revelry", "Arsenal", "Resurrection", "Ignite", "Breakout", "Upheaval", "Shockwave"]
# TODO: split season10; v49 until season10.1 (depot/r5-101 | 14sep21/maps)
# TODO: split season21; v51.1 mp_canyonlands_staging_mu1 & mp_rr_freedm_skulltown
spec_of.update({
    **{f"ApexLegends/season{i}": (respawn.apex_legends, 47) for i in range(7)},
    "ApexLegends/season7": (respawn.apex_legends, 48),
    **{f"ApexLegends/season{i}": (respawn.apex_legends, 49) for i in (8, 9)},
    "ApexLegends/season10": (respawn.apex_legends50, 50),
    **{f"ApexLegends/season{i}": (respawn.apex_legends50, (50, 1)) for i in (11, 12)},
    **{f"ApexLegends/season{i}": (respawn.apex_legends51, (51, 1)) for i in range(13, 21)},
    **{f"ApexLegends/season{i}": (respawn.apex_legends52, (52, 1)) for i in (21, 22)}})
# local test maps (./tests/maps/game/, not .../game/mod/maps/)
spec_of.update({
    "Momentum Mod": (strata.strata, 25),
    "ReMakeQuake": (id_software.remake_quake, None),
    "Team Fortress 2": (valve.orange_box, 20),
    "Titanfall 2": (respawn.titanfall2, 37)})
# steam dirs (demos, multiple mods per-game & not listed in branches)
spec_of.update({
    "Contagion": spec_of["Contagion/contagion"],
    "dayofinfamy": (valve.sdk_2013, 21),
    "Dino D-Day": (valve.sdk_2013, 21),
    "Double Action": (valve.orange_box, 20),
    "EYE Divine Cybermancy Demo/EYE": spec_of["EYE Divine Cybermancy/EYE"],
    "Fistful of Frags": (valve.orange_box, 20),
    "Fortress Forever": (valve.orange_box, 20),
    "Half-Life 2 Update": (valve.orange_box, 20),
    "Half-Life 2 VR": (valve.orange_box, 20),
    "insurgency2": (valve.sdk_2013, 21),
    "Jabroni Brawl Episode 3": (valve.sdk_2013, 21),
    "left 4 dead": spec_of["left 4 dead/left4dead"],
    "Left 4 Dead 2": spec_of["Left 4 Dead 2/left4dead2"],
    "MINERVA": (valve.orange_box, 20),
    "Momentum Mod Playtest": spec_of["Momentum Mod/momentum"],
    "nmrih": (valve.orange_box, 20),
    "Portal 2": spec_of["Portal 2/portal2"],
    "Portal Reloaded": spec_of["Portal 2/portal2"],
    "Portal Revolution": (strata.strata, 25),
    "Sven Co-op": spec_of["Sven Co-op/svencoop"],
    "Synergy": (valve.orange_box, 20),
    "Transmissions Element 120": (valve.orange_box, 20)})
# extracted dirs
spec_of.update({
    "Alkaline": spec_of["Quake"],
    "ApexLegends": (respawn.apex_legends, 47),  # mixed?
    "BlackMesa": (valve.sdk_2013, 21),
    "BloodyGoodTime": (outerlight.outerlight, 20),
    "CSGO/csgo_backup": (valve.sdk_2013, 21),
    "CSMalvinas": (valve.orange_box, 20),
    "CSS/Bocuma747_SurfMaps": (valve.source, 19),
    "CSS/OiuSURF_SurfMaps": (valve.source, 19),
    "CoD1": (infinity_ward.call_of_duty1, 59),
    "CoD1Demo/burnville": (infinity_ward.call_of_duty1_demo, 58),
    "CoD1Demo/dawnville": (infinity_ward.call_of_duty1_demo, 58),
    "CoD2": (infinity_ward.call_of_duty2, 4),
    "CoD4": (infinity_ward.modern_warfare, 22),
    "DarkMessiah/multiplayer": (arkane.dark_messiah_mp, (20, 4)),
    "DarkMessiah/singleplayer": (arkane.dark_messiah_sp, (20, 4)),
    "DearEsther/dearesther": (valve.sdk_2013, 21),
    "DDayNormandy": spec_of["Quake 2"],
    "HL2DM/patbytes": spec_of["half-life 2 deathmatch/hl2mp"],
    "HereticII": spec_of["Quake 2"],
    "HexenII": spec_of["Hexen 2"],
    "Infra": spec_of["infra/infra"],
    "MomentumMod": spec_of["Momentum Mod/momentum"],
    "Nexuiz": spec_of["Quake 3 Arena"],
    "Nightfire": (gearbox.nightfire, 42),
    "Quake/2psb": (id_software.remake_quake_old, None),
    "Quake/rerelease": (id_software.quake, 29),
    "Quake/rerelease/dopa": (id_software.remake_quake, None),
    "Quake64": (id_software.quake64, None),
    "QuakeII": spec_of["Quake 2"],
    "QuakeII/rerelease": spec_of["Quake 2"],  # mixed
    "QuakeIII": spec_of["Quake 3 Arena"],
    "QuakeLive": (id_software.quake3, 47),
    "RTCW": (id_software.quake3, 47),
    "SiNEpisodes": (valve.source, 19),
    "StarTrekEliteForce": (id_software.quake3, 46),
    "TacticalIntervention": (valve.orange_box, 20),
    "TeamFortressQuake": spec_of["Quake"],
    "TheHiddenSource": (valve.orange_box, 20),
    "TheShip": (outerlight.outerlight, 20),
    "Titanfall/beta": spec_of["Titanfall"],
    "Vindictus": (nexon.vindictus, 20),
    "Vindictus/Client v1.69 EU": (nexon.vindictus69, 20),
    "Warfork": (id_software.qfusion, 1),
    "WolfET": (id_software.quake3, 47),
    "Xonotic": (id_software.quake3, 46)})
# console dirs
spec_of.update({
    "Half-Life2": (valve.source, 19),
    "Left4Dead": (valve.orange_box_x360, 20),
    "Left4Dead2": (valve.orange_box_x360, 20),
    "OrangeBox": (valve.orange_box_x360, 20),
    "Paranoia": (valve.goldsrc, 30),
    "Portal2": (valve.sdk_2013_x360, 21)})

id_of = {
    path: game
    for branch in all_branches
    for game, path in branch.GAME_PATHS.items()}
# apex archive
id_of.update({
    f"ApexLegends/season{i}": f"Apex Legends - Season {i} - {name}"
    for i, name in enumerate(apex_seasons)})
# multi-mod-dir games
id_of.update({
    "Contagion": id_of["Contagion/contagion"],
    "left 4 dead": id_of["left 4 dead/left4dead"],
    "Left 4 Dead 2": id_of["Left 4 Dead 2/left4dead2"],
    "Sven Co-op": id_of["Sven Co-op/svencoop"]})
# sourcemods
id_of.update({
    "backontrack": "Map Labs 9 - Back on Track",
    "companionpiece2": "Map Labs 8 - Companion Piece 2: Companion Harder",
    "cromulentville2": "Test Tube 7 - CromulentVille 2",
    "episodeone": "Map Labs (Episode 1 maps)",
    "eyecandy": "Test Tube 8 - Eye Candy",
    "fusionville2": "Map Labs 10 - FusionVille 2",
    "gesource": "GoldenEye: Source",
    "half-life 2 riot act": "HL2: Riot Act",
    "halflifeeternal": "Test Tube 16 - Half-Life: Eternal",
    "halloweenhorror4": "Map Labs 16 - Halloween Horror 4: Nightmare on Reboot Street!",
    "lvl2": "Map Labs 15 - LVL2",
    "RunThinkShootLiveVille2": "Map Labs 3 - RunThinkShootLiveVille 2",
    "TFTS": "Run Think Shoot Live - Tales from the Source",
    "thelayout": "Map Labs 17 - The Layout",
    "thewrapuptwo": "Test Tube 15 - The Wrap-Up Two!",
    "tunetwo": "Test Tube 13 - TUNE TWO: Crossfade",
    "tworooms": "Test Tube 9 - Two Rooms"})
# general
id_of.update({
    "BlackMesa": "Black Mesa",
    "BloodyGoodTime": "Bloody Good Time",
    "CoD1": "Call of Duty (2003)",
    "CoD1Demo/burnville": "Call of Duty (Demo) - Burnville",
    "CoD1Demo/dawnville": "Call of Duty (Demo) - Dawnville",
    "CoD2": "Call of Duty 2",
    "CoD4": "Call of Duty: Modern Warfare (2007)",
    "CSGO/csgo_backup": "Counter-Strike: Global Offensive",
    "CSS/Bocuma747_SurfMaps": "CS:S Surf Archive - Bocuma747",
    "CSS/OiuSURF_SurfMaps": "CS:S Surf Archive - OiuSURF",
    "DarkMessiah/multiplayer": "Dark Messiah of Might & Magic Multi-Player",
    "DarkMessiah/singleplayer": "Dark Messiah of Might & Magic Single Player",
    "dayofinfamy": "Day of Infamy",
    "DearEsther/dearesther": "Dear Esther: Source",
    "DDayNormandy": "D-Day: Normandy",
    "Double Action": "Double Action: Boogaloo",
    "EYE Divine Cybermancy Demo/EYE": "E.Y.E. Divine Cybermancy (Demo)",
    "HereticII": "Heretic: Shadow of the Serpent Riders",
    "HexenII": "HeXen II",
    "HL2DM/patbytes": "patbytes HL2:DM Archive",
    "insurgency2": "Insurgency",
    "MINERVA": "MINERVA: Metastasis",
    "MomentumMod": "Momentum Mod",
    "Nightfire": "James Bond 007: Nightfire",
    "nmrih": "No More Room in Hell",
    "Quake/2psb": "Quake (2PSB)",
    "Quake/rerelease": "Quake (2021)",
    "Quake/rerelease/dopa": "Quake (2021) - Dimension of the Past",
    "QuakeII": "Quake II",
    "QuakeII/rerelease": "Quake II (2023)",
    "QuakeIII": "Quake III Arena",
    "QuakeLive": "Quake Live",
    "Quake64": "Quake 64 (PC)",
    "RTCW": "Return to Castle Wolfenstein",
    "SiNEpisodes": "SiN Episodes: Emergence",
    "StarTrekEliteForce": "Star Trek: Voyager - Elite Force",
    "TacticalIntervention": "Tactical Intervention",
    "TeamFortressQuake": "Team Fortress (Quake Mod)",
    "TheHiddenSource": "The Hidden",
    "TheShip": "The Ship",
    "Titanfall/beta": "Titanfall (Beta)",
    "TitanfallOnline": "Titanfall: Online",
    "Transmissions Element 120": "Transmissions: Element 120",
    "WolfET": "Wolfenstein: Enemy Territory",
    "Vindictus/Client v1.69 EU": "Vindictus v1.69"})

BspClass_for = {branch: BspClass_for_magic.get(branch.FILE_MAGIC, None) for branch in all_branches}
BspClass_for.update({
    **{branch: QuakeBsp for branch in branches.of_engine["Quake"] if branch != id_software.quake64},
    **{branch: GoldSrcBsp for branch in branches.of_engine["GoldSrc"]},
    **{branch: InfinityWardBsp for branch in infinity_ward.scripts},
    infinity_ward.modern_warfare: D3DBsp, nexon.cso2: NexonBsp, nexon.cso2_2018: NexonBsp})
# ^ {valve.orange_box: ValveBsp, ...}

megatest_dirs = [(*dg, tuple(mds)) for dg, mds in maplist.installed_games.items()]
# ^ [("D:/Steam...", "Team Fortress 2", ("tf/maps", ...))]


def spec_str(BspClass, branch, version) -> str:
    # TODO: sprp_version
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


drive_id = {
    "./tests/maps": "Local",
    "C:/Program Files (x86)/Steam/steamapps/sourcemods": "Sourcemods",
    "D:/SteamLibrary/steamapps/common": "Steam",
    "E:/Mod": "Extracted",
    # consoles
    "E:/Mod/Dreamcast": "Dreamcast",
    "E:/Mod/PS4": "PS4",
    "E:/Mod/Switch": "Switch",
    "E:/Mod/Xbox": "Xbox",
    "E:/Mod/X360": "Xbox360"}

test_args = list()
# ^ [(ValveBsp, orange_box, 20, [(".../tf/maps/pl_upward.bsp", "tf/maps/pl_upward.bsp")])]
test_ids = list()
# ^ ["Team Fortress 2"]
for drive, game, map_dirs in megatest_dirs:
    branch, version = spec_of[game]
    maps = list()
    for map_dir in map_dirs:
        path = os.path.join(drive, game, map_dir)
        d3d_branches = (infinity_ward.call_of_duty2, infinity_ward.modern_warfare)
        ext = "*.[bB][sS][pP]" if branch not in d3d_branches else "*.d3dbsp"
        dir_maps = fnmatch.filter(os.listdir(path), ext)
        # TODO: filter out breaking maps (0 bytes, secret .mdl etc.)
        # TODO: handle dirs w/ mixed formats
        # -- Apex Legends (Season 11 depots; some seasons keep old maps)
        # -- CS:O2 (TODO: autodetect/cso2.json)
        # -- CS:S (valve.source 19 & valve.orange_box 20)
        # -- Half-Life: Source (v17 & v18)
        # -- Half-Life 2: Episode 1 (valve.source 19 & orange_box 20)
        # -- Quake 2 Rerelease (TODO: autodetect/quake2_rerelease.json)
        # -- SiN (1 map)
        # -- Vindictus (TODO: autodetect/vindictus.json)
        ...
        maps.extend((os.path.join(path, m), os.path.join(map_dir, m)) for m in dir_maps)
    test_args.append([BspClass_for[branch], branch, version, maps])
    test_ids.append(f"{drive_id[drive]} | {id_of.get(game, game)}")


def sort_func(test_id):
    drive_name, game_id = test_id.split(" | ")
    # NOTE: roman numerals don't exceed "III" so they sort just fine
    patterns = {
        r"Apex Legends - Season ([0-9]{1,2}) - .*": "Apex Legends - Season {:02d}",
        r"Map Labs ([0-9]{1,2}) - .*": "Map Labs {:02d}",
        r"Test Tube ([0-9]{1,2}) - .*": "Test Tube {:02d}"}
    for pattern, substitution in patterns.items():
        m = re.match(pattern, game_id)
        if m is not None:
            game_id = substitution.format(int(m.groups()[0]))
    return (list(drive_id.values()).index(drive_name), game_id)


test_order = [test_ids.index(x) for x in sorted(test_ids, key=sort_func)]
test_args = [test_args[i] for i in test_order]
test_ids = [test_ids[i] for i in test_order]


subtle = (
    ace_team.zeno_clash, arkane.dark_messiah_mp,
    gearbox.blue_shift, nexon.cso2_2018, nexon.vindictus,
    nexon.vindictus69, outerlight.outerlight, raven.hexen2,
    raven.soldier_of_fortune, raven.soldier_of_fortune2,
    ritual.sin, utoplanet.merubasu, valve.alien_swarm,
    valve.left4dead, valve.left4dead2, valve.source_filmmaker)

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
    # TODO: sprp_version
    BspClass = bsp.__class__
    branch = bsp.branch
    version = bsp.version
    return spec_str(BspClass, branch, version)


def loading_errors_of(bsp):
    if bsp.branch in branches.source_based:
        out = {
            f"{L} v{bsp.headers[L].version}": err
            for L, err in bsp.loading_errors.items()}
        if not isinstance(getattr(bsp, "GAME_LUMP", lumps.RawBspLump()), lumps.RawBspLump):
            out.update({
                f"{L} v{bsp.GAME_LUMP.headers[L].version}": err
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


# TODO: more xfails
# -- 0 byte .bsp
# -- DDay-Normandy exclude list:
# --- dday_mappack_excludes = (
# ---     "dday3bh.bsp", "dofdtownbhv3.bsp", "gb1stdaybh.bsp", "iraidbhv3.bsp",
# ---     "LIDDUX.bsp", "schlitz1.bsp", "wiltzbh.bsp", "wiltzbhv3.bsp")
# -- Xbox360 | Left 4 Dead / Portal 2
