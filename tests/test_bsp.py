import collections
import fnmatch
import os

from bsp_tool import load_bsp
from bsp_tool import IdTechBsp, D3DBsp, RespawnBsp, ValveBsp


global bsps
bsps = dict()
# TODO: make a dict for each bsp variant


def test_load_bsp():  # must run first!
    """load all maps in tests/maps for testing"""
    bsps["test2"] = load_bsp("tests/maps/test2.bsp")
    bsps["upward"] = load_bsp("tests/maps/pl_upward.bsp")
    bsps["bigbox"] = load_bsp("tests/maps/test_bigbox.bsp")
    assert isinstance(bsps["test2"], ValveBsp)
    assert isinstance(bsps["upward"], ValveBsp)
    assert isinstance(bsps["bigbox"], IdTechBsp)
    # TODO: assert branch and version for each bsp


steam_directories = ["C:/Program Files (x86)/Steam",  # default Windows
                     "D:/SteamLibrary"]
# TODO: search for Origin installation (Titanfall & Apex Legends)

# NOTE: GoldSrc .bsps are not yet supported
# NOTE: all rBSPs are in .vpks, and cannot easily be extracted
# TODO: Dark Messiah maps are in .vpks
# WARNING: Tests every .bsp it can find on your PC, very slow
# games_to_test = {  # Valve Bsp
#          # Black Mesa
#          "Counter-Strike Global Offensive": ["csgo/maps"],
#          "counter-strike source": ["cstrike/maps", "cstrike/download/maps"],
#          # Condition Zero / CZ Deleted Scenes
#          "day of defeat source": ["dod/maps"],
#          "half-life 2": ["hl2/maps"],
#          "Left 4 Dead 2": ["left4dead2/maps", "left4dead2_dlc1/maps",
#                            "left4dead2_dlc2/maps", "left4dead2_dlc3/maps"],
#          "SourceFilmmaker": ["game/tf/maps"],
#          "Team Fortress 2": ["tf/maps", "tf/download/maps"],
#
#          # PRE-EXCTRACTED .BSPS (E:/Mod/...)
#          "CSO2": ["maps"],  # Nexon's Counter-Strike: Online 2
#          # NOTE: some CSO2 maps are from an older engine version, with no in file indication of this
#          # D3DBsp
#          "CoD1": ["maps", "maps/MP"],
#          "CoD2": ["maps", "maps/mp"],  # *.d3dbsp
#          "CoD4": ["maps"],  # not yet extracted
#          # RespawnBsp
#          "Titanfall": ["maps", "r1/maps"],
#          "TitanfallOnline": ["maps", "r1/maps"],  # Nexon's TitanfallOnline
#          "Titanfall2": ["maps", "r2/maps"],
#          "ApexLegends": ["maps"],  # (Steam)  "Apex Legends": ["r5/maps"]  # or vpk/
#          # IdTechBsp
#          "QuakeIII": ["maps"]}  # (Steam)  "Quake 3 Arena": ["baseq3"]  # .pk3s
# # ^ {"game": ["map_dir"]}

games_to_test = {"Titanfall": ["maps"],  # E:/Mod/Titanfall/maps
                 "CoD1": ["maps", "maps/MP"]}  # Call of Duty 1 .bsps, extracted from .pk3s
# ^ fast test to double check rBSP & D3DBsp

expected_branch = {"CoD1": (D3DBsp, 59, "infinity_ward.call_of_duty1"),
                   # "CSO2": (ValveBsp, 100, "nexon.cso2"),  # NOTE: both 2013 & 2017 bsps are version 100
                   "Titanfall": (RespawnBsp, 29, "respawn.titanfall")}
# ^ {"game": (type(bsp), BSP_VERSION, "branch")}


def test_load_all_bsps():  # WARNING: will take hours if you have lots of games installed
    """Scan system for .bsp files & test them all"""
    game_map_dirs = collections.defaultdict(list)
    # ^ {"game": "steam_dir" + "game" + "map_dir"}
    for steam_dir in steam_directories:
        # find installed games that might have .bsps
        if os.path.exists(steam_dir):
            games = os.listdir(os.path.join(steam_dir, "steamapps/common"))
            for game in games:
                if game not in games_to_test:
                    continue
                for map_dir in games_to_test[game]:
                    game_map_dirs[game].append(os.path.join(steam_dir, "steamapps/common", game, map_dir))
        # # check sourcemods too, why not  (because it's slow that's why not!)
        # sourcemods_path = os.path.join(steam_dir, "steamapps/sourcemods")
        # if os.path.exists(sourcemods_path):
        #     for sourcemod in os.listdir(sourcemods_path):
        #         if os.path.isdir(os.path.join(sourcemods_path, sourcemod)):
        #             game_map_dirs[sourcemod].append(os.path.join(sourcemods_path, sourcemod, "maps"))
    extracted_games = os.listdir("E:/Mod")  # maps extracted from .vpks etc.
    for game in extracted_games:
        if game not in games_to_test:
            continue
        for map_dir in games_to_test[game]:
            game_map_dirs[game].append(os.path.join("E:/Mod", game, map_dir))

    # for every valid game
    failures = list()
    for game_name, map_dirs in game_map_dirs.items():
        for map_dir in map_dirs:
            if not os.path.exists(map_dir):
                continue
            map_names = fnmatch.filter(os.listdir(map_dir), "*.bsp")
            if "CoD2" in map_dir:  # HACK: lazy edge case workaround for CoD2
                map_names = fnmatch.filter(os.listdir(map_dir), "*.d3dbsp")
            # load every map
            for map in map_names:
                try:
                    loaded_bsp = load_bsp(os.path.join(map_dir, map))
                    variant, bsp_version, branch = expected_branch[game_name]
                    assert isinstance(loaded_bsp, variant)
                    assert loaded_bsp.BSP_VERSION == bsp_version
                    assert loaded_bsp.branch.__name__ == f"bsp_tool.branches.{branch}"
                    assert len(loaded_bsp.loading_errors) == 0
                    del loaded_bsp
                except Exception as exc:
                    # TODO: log more info per failure, write to file
                    # -- would make a good github action artifact
                    failures.append((map, exc))

    print(failures)
    assert len(failures) == 0


class TestIdTechBsp:
    def test_no_errors(self):
        assert len(bsps["bigbox"].loading_errors) == 0

    def test_entities_loaded(self):
        assert bsps["bigbox"].ENTITIES[0]["classname"] == "worldspawn"


class TestValveBsp:
    def test_no_errors(self):
        assert len(bsps["test2"].loading_errors) == 0
        assert len(bsps["upward"].loading_errors) == 0

    def test_entites_loaded(self):
        assert bsps["test2"].ENTITIES[0]["classname"] == "worldspawn"
        assert bsps["upward"].ENTITIES[0]["classname"] == "worldspawn"
