import os
from typing import Dict, List, Tuple


DirList = Dict[str, List[str]]
# ^ {"Game": ["maps_dir"]}
GameDirList = Dict[str, DirList]
# ^ {"SteamFolder": {**DirList_1, **DirList_2}}

goldsrc_dirs: DirList  # GoldSrc titles
source_dirs: DirList  # Source Engine titles
extracted_dirs: DirList  # .bsps from archives (.ff, .pak, .pak3, .pkg, .vpk) & non-steam games
sourcemod_dirs: DirList  # Source SDK games @ Steam/steamapps/sourcemods
every_bsp_dir: DirList  # all of the above in one dict (used with external HDD)
group_dirs: GameDirList
installed_games: Dict[Tuple[str], List[str]]
# ^ {("SteamFolder", "Game"): ["maps_dir"]}


# TODO: generate by searching for gameinfo.txt files
goldsrc_dirs = {
        **{f"Half-Life/{mod}": ["maps"] for mod in [
                        "bshift",    # 37 maps | 54 MB | Half-Life: Blue Shift
                        "cstrike",   # 25 maps | 81 MB | Counter-Strike
                        "czero",     # 22 maps | 83 MB | Counter-Strike: Condition Zero
                        "czeror",    # 73 maps | 177 MB | Counter-Strike: Condition Zero - Deleted Scenes
                        "dmc",       # 7 maps | 9 MB | Deathmatch: Classic
                        "dod",       # 22 maps | 91 MB | Day of Defeat
                        "gearbox",   # 68 maps | 137 MB | Half-Life: Opposing Force
                        "ricochet",  # 3 maps | 2 MB | Ricochet
                        "tfc",       # 15 maps | 41 MB | Team Fortress: Classic
                        "valve"]},   # 115 maps | 188 MB | Half-Life
        "Halfquake Trilogy": ["valve/maps"],  # 152 maps | 207 MB
        "Sven Co-op": ["svencoop/maps",  # 107 maps | 521 MB
                       # "svencoop_addon/maps",
                       # "svencoop_downloads/maps",
                       "svencoop_event_april/maps"]}  # 4 maps | 31 MB
# ^ {"game_dir": ["map_dir"]}

source_dirs = {
         "Alien Swarm": ["swarm/maps"],  # 9 maps | 299 MB
         "Alien Swarm Reactive Drop": ["reactivedrop/maps"],  # 53 maps | 1.3 GB
         "Blade Symphony": ["berimbau/maps"],  # 21 maps | 1.0 GB
         "Counter-Strike Global Offensive": ["csgo/maps"],  # 38 maps | 5.9 GB
         "counter-strike source": ["cstrike/maps",  # 20 maps | 237 MB
                                   # "cstrike/download/maps"
                                   ],
         "day of defeat source": ["dod/maps"],  # 9 maps | 299 MB
         "G String": ["gstringv2/maps"],  # 76 maps | 2.49 GB | Seriously Impressive
         "GarrysMod": ["garrysmod/maps"],  # 2 maps | 84 MB
         "Half-Life 1 Source Deathmatch": ["hl1mp/maps"],  # 11 maps | 53 MB
         **{f"half-life 2/{mod}": ["maps"] for mod in [
                         "ep2",          # HL2:EP2 |  22 maps | 703 MB
                         "episodic",     # HL2:EP1 |  20 maps | 554 MB
                         "hl1",          # HL:S    | 110 maps | 339 MB
                         "hl2",          # HL2     |  80 maps | 815 MB
                         "lostcoast"]},  # HL2:LC  |   4 maps | 101 MB
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

# TODO: workshop_dirs

extracted_dirs = {
        # IdTechBsp
        # TODO: American McGee's Alice
        # TODO: DOOM 3 BFG Edition  # .resources .pk4 (https://forum.xentax.com/viewtopic.php?t=9752)
        # -- DOOM 2016? DOOM Eternal? RAGE? RAGE 2?
        # TODO: Hexen 2  # .pak (http://fileformats.archiveteam.org/wiki/Quake_PAK)
        # TODO: Quake  # .pak
        # TODO: Quake Arcane Dimensions (https://www.moddb.com/mods/arcane-dimensions/downloads)
        "QuakeIII": ["maps"],  # 31 maps | 116 MB | .pk3
        # D3DBsp
        "CoD1": ["maps",  # 33 maps | 488 MB | .pk3
                 "maps/MP"],  # 16 maps | 229 MB | .pk3
        "CoD2": ["maps",  # 39 maps | 1.5 GB | .d3dbsp
                 "maps/mp"],  # 15 maps | 395 MB | .d3dbsp
        # TODO: CoD4  # .ff
        # ValveBsp
        "BlackMesa": ["maps"],  # 109 maps | 5.5 GB | .vpk
        "CSMalvinas": ["maps"],  # 1 map | 13 MB | Counter-Strike: Malvinas
        "DarkMessiah": ["singleplayer/maps",  # 35 maps | 1.4 GB | .vpk
                        "multi-player/maps"],  # 11 maps | 564 MB | .vpk
        "TacInt": ["maps"],  # 26 maps | 3.5 GB | Tactical Intervention
        # NEXON
        "CSO2": ["maps"],  # 97 maps | 902 MB | Counter-Strike: Online 2 | .pkg
        "TitanfallOnline": ["maps"],  # 18 maps | 2.2 GB | .pkg
        # RespawnBsp (NOTE: .bsp_lump & .ent sizes not counted)
        "Titanfall": ["maps"],  # 26 maps | 3,5 GB | .vpk
        "Titanfall2": ["maps"],  # 36 maps | 6.6 GB | .vpk
        # Thanks to https://apexlegends.fandom.com/wiki/Version_History
        # see also: https://github.com/Syampuuh/TitanfallApexLegends
        # TODO: reduce list to smallest possible set with bsp_tool.extensions.diff
        # -- could eventually create an archive of all map related patches
        "ApexLegends": ["maps",  # 9 maps | 3.3 GB
                        "season2/maps",  # 1 map | 16.9 MB
                        # season3: Meltdown - patch 5  [3rd Dec 2019]
                        "season3/maps",  # 8 maps | 4.9 GB
                        "season3/depot/r5launch/game/r2/maps",  # 8 maps | 4.9 GB
                        "season3/depot/r5staging/game/r2/maps",  # 6 maps | 3.2 GB
                        # season5:  Fortune's Favour  [12th May 2020]
                        "season5/maps",  # 3 maps | 1.2 GB
                        # season6:  Boosted  [18th Aug 2020]
                        # season7:  Ascension  [4th Nov 2020]
                        # season8:  Mayhem  [2nd Feb 2021]
                        "season8/maps",  # 1 map | 1.9 MB
                        # season9:  Legacy  [4th May 2021]
                        "season9/maps",  # 4 maps | 226 MB
                        # season10:  Emergence  [3rd Aug 2021]
                        "season10/maps",  # 1 map | 1.8 MB
                        ]}
# ^ {"game_dir": ["map_dir"]}

# https://geshl2.com
# https://www.moddb.com/mods/riot-act
# https://www.moddb.com/mods/map-labs
# TODO: https://tf2classic.com
sourcemod_dirs = {mod: ["maps"] for mod in [
                      "gesource",  # 26 maps | 775 MB | GoldenEye: Source
                      "half-life 2 riot act",  # 5 maps | 159 MB | HL2: Riot Act
                      # Map Labs
                      "episodeone",  # 11 maps | 281 MB | Map Labs #2
                      "RunThinkShootLiveVille2",  # 19 maps | 728 MB | Map Labs #3
                      "cromulentville2",  # 21 maps | 342 MB | Test Tube #7
                      "companionpiece2",  # 18 maps | 429 MB | Map Labs #8
                      "eyecandy",   # 41 maps | 652 MB | Test Tube #8
                      "tworooms"]}  # 39 maps | 496 MB | Test Tube #9

# every_bsp_dir = {**sourcemod_dirs, **extracted_dirs, **goldsrc_dirs, **source_dirs}  # ~64GB

# NOTE: ls $group_dir+$game_dir+$maps_dir
group_dirs = {"C:/Program Files (x86)/Steam/steamapps/sourcemods": sourcemod_dirs,
              "D:/SteamLibrary/steamapps/common": {**goldsrc_dirs, **source_dirs},
              "E:/Mod": extracted_dirs,  # Id Software, Respawn Entertainment & Nexon
              # "F:/bsps": every_bsp_dir,
              # "/media/bikkie/GAMES/bsps": every_bsp_dir
              }

installed_games = {("./", "tests"): ["maps"]}
for group, games in group_dirs.items():
    if os.path.exists(group):
        for game, map_dirs in games.items():
            if os.path.exists(os.path.join(group, game)):
                installed_games[(group, game)] = map_dirs
