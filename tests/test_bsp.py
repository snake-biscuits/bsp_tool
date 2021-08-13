import collections
import fnmatch
import os

import pytest

from bsp_tool import load_bsp
from bsp_tool import IdTechBsp, D3DBsp, RespawnBsp, ValveBsp


# NOTE: optional, just an extra step to ensure the docs are correct
# TODO: generate from branches/__init__.py
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


def test_load_bsp():
    """load all maps in tests/maps for testing. run first!"""
    test2 = load_bsp("tests/maps/test2.bsp")
    upward = load_bsp("tests/maps/pl_upward.bsp")
    bigbox = load_bsp("tests/maps/test_bigbox.bsp")
    assert isinstance(test2, ValveBsp)
    assert isinstance(upward, ValveBsp)
    assert isinstance(bigbox, IdTechBsp)
    # TODO: assert branch and version for each bsp


# NOTE: ls $steam_dir+$game_dir+$map_dir
steam_dirs = ["C:/Program Files (x86)/Steam",  # Windows default
              "D:/SteamLibrary"]

goldsrc_dirs = {
        "Half-Life": ["bshift/maps",    # Half-Life: Blue Shift
                      "cstrike/maps",   # Counter-Strike
                      "czero/maps",     # Counter-Strike: Condition Zero
                      "czeror/maps",    # Counter-Strike: Condition Zero - Deleted Scenes
                      "dmc/maps",       # Deathmatch: Classic
                      "dod/maps",       # Day of Defeat
                      "gearbox/maps",   # Half-Life: Opposing Force
                      "ricochet/maps",  # Ricochet
                      "tfc/maps",       # Team Fortress: Classic
                      "valve/maps"],    # Half-Life
        "Halfquake Trilogy": ["valve/maps"],
        "Sven Co-op": ["svencoop/maps",
                       # "svencoop_addon/maps", "svencoop_downloads/maps",
                       "svencoop_event_april/maps"]}
# ^ {"game_dir": ["map_dir"]}

source_dirs = {
         "Alien Swarm": ["swarm/maps"],
         "Alien Swarm Reactive Drop": ["reactivedrop/maps"],
         "Counter-Strike Global Offensive": ["csgo/maps"],
         "counter-strike source": ["cstrike/maps",
                                   # "cstrike/download/maps"
                                   ],
         "day of defeat source": ["dod/maps"],
         "G String": ["gstringv2/maps"],  # G-String | 76 maps | 2.49 GB
         "GarrysMod": ["garrysmod/maps"],
         "Half-Life 1 Source Deathmatch": ["hl1mp/maps"],
         "half-life 2": ["ep2/maps",         # HL2:EP2 |  22 maps | 670 MB
                         "episodic/maps",    # HL2:EP1 |  20 maps | 527 MB
                         "hl1/maps",         # HL:S    | 110 maps | 323 MB
                         "hl2/maps",         # HL2     |  80 maps | 777 MB
                         "lostcoast/maps"],  # HL2:LC  |   4 maps |  96 MB
         "half-life 2 deathmatch": ["hl2mp/maps"],
         "Half-Life 2 Update": ["hl2/maps"],
         "left 4 dead": ["left4dead/maps", "left4dead_dlc3/maps"],
         "Left 4 Dead 2": ["left4dead2/maps", "left4dead2_dlc1/maps",
                           "left4dead2_dlc2/maps", "left4dead2_dlc3/maps"],
         "SourceFilmmaker": ["game/tf/maps"],
         "NEOTOKYO": ["neotokyosource/maps"],  # 24 maps | 289 MB
         "Portal": ["portal/maps"],  # 26 maps | 406 MB
         "Portal 2": ["portal2/maps",  # 106 maps | 2.47 GB
                      "portal2_dlc1/maps",  # 10 maps | 289 MB
                      "portal2_dlc2/maps"],  # 1 map | 671 KB
         "Portal Reloaded": ["portalreloaded/maps"],  # 12 maps | 426 MB
         "TacInt": ["maps"],  # Tactical Intervention (E:/Mod)
         "Team Fortress 2": ["tf/maps", "tf/download/maps"]}
# ^ {"game_dir": ["map_dir"]}

# TODO: steam_workshop_dirs

# E:/Mod/<game_dir>/<map_dir>
extracted_dirs = {
        # IdTechBsp
        # TODO: DOOM 3 BFG Edition  # .resources .pk4 (https://forum.xentax.com/viewtopic.php?t=9752)
        # TODO: Hexen 2  # .pak (http://fileformats.archiveteam.org/wiki/Quake_PAK)
        # TODO: Quake  # .pak
        # TODO: Quake Arcane Dimensions (https://www.moddb.com/mods/arcane-dimensions/downloads)
        "QuakeIII": ["maps"],  # .pk3
        # D3DBsp
        "CoD1": ["maps", "maps/MP"],  # .pk3
        "CoD2": ["maps", "maps/mp"],  # .d3dbsp
        # TODO: CoD4  # .ff
        # ValveBsp
        "DarkMessiah": ["singleplayer/maps", "multi-player/maps"],  # .vpk
        "Black Mesa": ["bms/maps"],  # .vpk
        "CSO2": ["maps"],  # .vpk (Counter-Strike: Online 2 [NEXON])
        # RespawnBsp
        "Titanfall": ["maps"],  # .vpk
        "TitanfallOnline": ["maps"],  # .pkg
        "Titanfall2": ["maps"],
        "ApexLegends": ["maps", "maps/Season 2", "maps/Season 3", "maps/Season 5",
                        "maps/Season 8", "maps/Season 9", "maps/Season 10"]}
# ^ {"game_dir": ["map_dir"]}

# https://www.moddb.com/mods/map-labs
# https://geshl2.com
# https://tf2classic.com
# https://www.moddb.com/mods/riot-act
sourcemod_dirs = {"companionpiece2": ["maps"],  # Map Labs #8 - Companion Piece 2: Companion Harder
                  "cromulentville2": ["maps"],  # Test Tube #7 - CromulentVille 2
                  "episodeone": ["maps"],  # Map Labs #2: Episode One
                  "eyecandy": ["maps"],  # Test Tube #8 - Eye Candy
                  "gesource": ["maps"],  # GoldenEye: Source
                  "RunThinkShootLiveVille2": ["maps"],  # Map Labs #3 - RunThinkShootLiveVille 2
                  "tworooms": ["maps"]}  # Test Tube #9 - Two Rooms

game_dirs = {**goldsrc_dirs}  # **source_dirs
# TODO: pytest command line argument(s) to filter games
# --gigabytes XXXGB / --megabytes XXXMB  (added together?)
# --skip GAME


# TODO: calculate approx. time to execute (likely in hours)
@pytest.mark.slow
def test_load_all_bsps():
    """MEGATEST: Scan system for .bsp files & test them all"""
    game_map_dirs = collections.defaultdict(list)
    # ^ {"game": "steam_dir" + "game" + "map_dir"}
    for steam_dir in steam_dirs:
        # find installed games that might have .bsps
        if os.path.exists(steam_dir):
            games = os.listdir(os.path.join(steam_dir, "steamapps/common"))
            for game in games:
                if game not in game_dirs:
                    continue
                for map_dir in game_dirs[game]:
                    game_map_dirs[game].append(os.path.join(steam_dir, "steamapps/common", game, map_dir))
        # test ALL sourcemods
        sourcemods_path = os.path.join(steam_dir, "steamapps/sourcemods")
        if os.path.exists(sourcemods_path):
            for sourcemod in os.listdir(sourcemods_path):  # TODO: use sourcemod_dirs instead
                if os.path.isdir(os.path.join(sourcemods_path, sourcemod)):
                    game_map_dirs[sourcemod].append(os.path.join(sourcemods_path, sourcemod, "maps"))
    # maps extracted from .vpks etc.
    if os.path.exists("E:/Mod"):
        extracted_games = os.listdir("E:/Mod")
        for game in extracted_games:
            if game not in game_dirs:
                continue
            for map_dir in game_dirs[game]:
                game_map_dirs[game].append(os.path.join("E:/Mod", game, map_dir))

    # for every game found
    bytes_tested = 0
    failures = collections.defaultdict(list)
    for game_name, map_dirs in game_map_dirs.items():
        for map_dir in map_dirs:
            if not os.path.exists(map_dir):
                # TODO: log missing dlc / game / map folder
                continue
            map_names = fnmatch.filter(os.listdir(map_dir), "*.bsp")
            if "CoD2" in map_dir:  # HACK: CoD2 uses .d3dbsp
                map_names = fnmatch.filter(os.listdir(map_dir), "*.d3dbsp")
            # load every map
            for map in map_names:
                try:
                    loaded_bsp = load_bsp(os.path.join(map_dir, map))
                    bytes_tested += loaded_bsp.bsp_file_size
                    # TODO: add .associated_files sizes for external lumps / entities
                    # verify game format documentation
                    if game_name in expected_branch:
                        variant, bsp_version, branch = expected_branch[game_name]
                        assert isinstance(loaded_bsp, variant)
                        assert loaded_bsp.bsp_version == bsp_version, "wrong bsp version"
                        assert loaded_bsp.branch.__name__ == f"bsp_tool.branches.{branch}", "wrong branch"
                    assert len(loaded_bsp.loading_errors) == 0, f"failed to read {len(loaded_bsp.loading_errors)} lumps"
                    del loaded_bsp
                except Exception as exc:
                    failures[game_name].append((map, exc))

    assert bytes_tested != 0, "No .bsp files were found!"

    # only report failures once all mods / games have been tested
    for game_name in failures:
        # TODO: generate a detailed log
        assert len(failures[game_name]) == 0, f"Errors loading {game_name}"
