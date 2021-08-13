import collections
import fnmatch
import os

import pytest

from bsp_tool import load_bsp
from bsp_tool import IdTechBsp, D3DBsp, RespawnBsp, ValveBsp


# TODO: generate by searching for gameinfo.txt files
goldsrc_dirs = {
        "Half-Life": ["bshift/maps",    # 37 maps | 54 MB | Half-Life: Blue Shift
                      "cstrike/maps",   # 25 maps | 81 MB | Counter-Strike
                      "czero/maps",     # 22 maps | 83 MB | Counter-Strike: Condition Zero
                      "czeror/maps",    # 73 maps | 177 MB | Counter-Strike: Condition Zero - Deleted Scenes
                      "dmc/maps",       # 7 maps | 9 MB | Deathmatch: Classic
                      "dod/maps",       # 22 maps | 91 MB | Day of Defeat
                      "gearbox/maps",   # 68 maps | 137 MB | Half-Life: Opposing Force
                      "ricochet/maps",  # 3 maps | 2 MB | Ricochet
                      "tfc/maps",       # 15 maps | 41 MB | Team Fortress: Classic
                      "valve/maps"],    # 115 maps | 188 MB | Half-Life
        "Halfquake Trilogy": ["valve/maps"],  # 152 maps | 207 MB
        "Sven Co-op": ["svencoop/maps",  # 107 maps | 521 MB
                       # "svencoop_addon/maps",
                       # "svencoop_downloads/maps",
                       "svencoop_event_april/maps"]}  # 4 maps | 31 MB
# ^ {"game_dir": ["map_dir"]}

source_dirs = {
         "Alien Swarm": ["swarm/maps"],  # 9 maps | 299 MB
         "Alien Swarm Reactive Drop": ["reactivedrop/maps"],  # 53 maps | 1.3 GB
         "Counter-Strike Global Offensive": ["csgo/maps"],  # 38 maps | 5.9 GB
         "counter-strike source": ["cstrike/maps",  # 20 maps | 237 MB
                                   # "cstrike/download/maps"
                                   ],
         "day of defeat source": ["dod/maps"],  # 9 maps | 299 MB
         "G String": ["gstringv2/maps"],  # 76 maps | 2.49 GB | Seriously Impressive
         "GarrysMod": ["garrysmod/maps"],  # 2 maps | 84 MB
         "Half-Life 1 Source Deathmatch": ["hl1mp/maps"],  # 11 maps | 53 MB
         "half-life 2": ["ep2/maps",         # HL2:EP2 |  22 maps | 703 MB
                         "episodic/maps",    # HL2:EP1 |  20 maps | 554 MB
                         "hl1/maps",         # HL:S    | 110 maps | 339 MB
                         "hl2/maps",         # HL2     |  80 maps | 815 MB
                         "lostcoast/maps"],  # HL2:LC  |   4 maps | 101 MB
         "half-life 2 deathmatch": ["hl2mp/maps"],  # 8 maps | 72 MB
         "Half-Life 2 Update": ["hl2/maps"],  # 76 maps | 2.9 GB
         "left 4 dead": ["left4dead/maps",   # 45 maps | 975 maps
                         "left4dead_dlc3/maps"],  # 3 maps | 67 MB
         "Left 4 Dead 2": ["left4dead2/maps",  # 8 maps | 186 MB
                           "left4dead2_dlc1/maps",  # 3 maps | 60 MB
                           "left4dead2_dlc2/maps",  # 8 maps | 186 MB
                           "left4dead2_dlc3/maps"],  # 21 maps | 481 MB
         "SourceFilmmaker": ["game/tf/maps"],  # 71 maps | 3.3 GB
         "NEOTOKYO": ["neotokyosource/maps"],  # 24 maps | 303 MB
         "Portal": ["portal/maps"],  # 26 maps | 426 MB
         "Portal 2": ["portal2/maps",  # 106 maps | 2.7 GB
                      "portal2_dlc1/maps",  # 10 maps | 313 MB
                      "portal2_dlc2/maps"],  # 1 map | 687 KB
         "Portal Reloaded": ["portalreloaded/maps"],  # 12 maps | 448 MB
         "Team Fortress 2": ["tf/maps",  # 194 maps | 5.2 GB
                             "tf/download/maps"]}  # 111 maps | 1.9 GB
# ^ {"game_dir": ["map_dir"]}

# TODO: steam_workshop_dirs

extracted_dirs = {
        # IdTechBsp
        # TODO: DOOM 3 BFG Edition  # .resources .pk4 (https://forum.xentax.com/viewtopic.php?t=9752)
        # -- DOOM 2016? DOOM Eternal? RAGE? RAGE 2?
        # TODO: Hexen 2  # .pak (http://fileformats.archiveteam.org/wiki/Quake_PAK)
        # TODO: Quake  # .pak
        # TODO: Quake Arcane Dimensions (https://www.moddb.com/mods/arcane-dimensions/downloads)
        # TODO: American McGee's Alice
        "QuakeIII": ["maps"],  # 31 maps | 116 MB | .pk3
        # D3DBsp
        "CoD1": ["maps",  # 33 maps | 488 MB | .pk3
                 "maps/MP"],  # 16 maps | 229 MB | .pk3
        "CoD2": ["maps",  # 39 maps | 1.5 GB | .d3dbsp
                 "maps/mp"],  # 15 maps | 395 MB | .d3dbsp
        # TODO: CoD4  # .ff
        # ValveBsp
        "BlackMesa": ["maps"],  # 109 maps | 5.5 GB | .vpk
        "DarkMessiah": ["singleplayer/maps",  # 35 maps | 1.4 GB | .vpk
                        "multi-player/maps"],  # 11 maps | 564 MB | .vpk
        "TacInt": ["maps"],  # 26 maps | 3.5 GB | Tactical Intervention
        # NEXON
        "CSO2": ["maps"],  # 97 maps | 902 MB | Counter-Strike: Online 2 | .pkg
        "TitanfallOnline": ["maps"],  # 18 maps | 2.2 GB | .pkg
        # RespawnBsp (NOTE: .bsp_lump & .ent sizes not counted)
        "Titanfall": ["maps"],  # 26 maps | 3,5 GB | .vpk
        "Titanfall2": ["maps"],  # 36 maps | 6.6 GB | .vpk
        # NOTE: Not a conclusive set! Map updates are listed on the Apex Legends wiki (via fandom.com)
        "ApexLegends": ["maps",  # 9 maps | 3.3 GB
                        # Season 1
                        "maps/Season 2",  # 1 map | 16.9 MB
                        "maps/Season 3",  # World's Edge
                        # Fight or Fright | King's mu1 (Shadowfall LTM)
                        # Season 4
                        "maps/Season 5",  # 3 maps | 1.2 GB | King's Canyon mu2
                        # Season 6
                        # Season 7 | Olympus
                        "maps/Season 8",  # 1 map | 1.9 MB  | Kings Canyon mu3 & staging
                        "maps/Season 9",  # 4 maps | 226 MB | Olympus mu1
                        # Arenas: Phase Runner, Party Crasher
                        # Thrillseekers | Overflow
                        "maps/Season 10"  # 1 map | 1.8 MB | World's Edge mu3
                        ]}
# ^ {"game_dir": ["map_dir"]}

# https://www.moddb.com/mods/map-labs
# https://geshl2.com
# https://tf2classic.com
# https://www.moddb.com/mods/riot-act
sourcemod_dirs = {"gesource": ["maps"],  # 26 maps | 775 MB | GoldenEye: Source
                  "episodeone": ["maps"],  # 11 maps | 281 MB | Map Labs #2
                  "RunThinkShootLiveVille2": ["maps"],  # 19 maps | 728 MB | Map Labs #3
                  "cromulentville2": ["maps"],  # 21 maps | 342 MB | Test Tube #7
                  "companionpiece2": ["maps"],  # 18 maps | 429 MB | Map Labs #8
                  "eyecandy": ["maps"],   # 41 maps | 652 MB | Test Tube #8
                  "tworooms": ["maps"]}  # 39 maps | 496 MB | Test Tube #9

# every_bsp_dir = {**sourcemod_dirs, **extracted_dirs, **goldsrc_dirs, **source_dirs}  # ~64GB

# NOTE: ls $group_dir+$game_dir+$map_dir
group_dirs = {"C:/Program Files (x86)/Steam/steamapps/sourcemods": sourcemod_dirs,
              "D:/SteamLibrary/steamapps/common": {**goldsrc_dirs, **source_dirs},
              "E:/Mod": extracted_dirs,  # Id Software, Respawn Entertainment & Nexon
              # "F:/bsps": every_bsp_dir,
              # "/media/bikkie/GAMES/bsps": every_bsp_dir
              }

game_dirs = {("./", "tests"): ["maps"]}
for group, games in group_dirs.items():
    if os.path.exists(group):
        for game, map_dirs in games.items():
            if os.path.exists(os.path.join(group, game)):
                game_dirs[(group, game)] = map_dirs


# TODO: conftest.py --skip [GAME | GROUP | ENGINE]
@pytest.mark.parametrize("group_path,game_name,map_dirs", [(*gps, ms) for gps, ms in game_dirs.items()])
def test_load_bsp(group_path, game_name, map_dirs):
    """MEGATEST: 64GB of .bsp files!"""
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
                    # TODO: verify documentation matches game
                    assert len(bsp.loading_errors) == 0, f"incorrect lump format(s) for {game_name}"
                    del bsp  # keep memory usage as low as possible
                except Exception as exc:
                    errors[game].append((m, exc))
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
