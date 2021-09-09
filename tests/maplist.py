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
         "Fortress Forever": ["FortressForever/maps"],  # 22 maps | 618 MB
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
         "Synergy": ["synergy/maps"],  # 21 maps | 407 MB
         "Team Fortress 2": ["tf/maps",  # 194 maps | 5.2 GB
                             "tf/download/maps"],  # 203 maps | 4.9 GB
         # TODO: Vamprire: The Masquerade - Bloodlines
              }
# ^ {"game_dir": ["map_dir"]}

# TODO: workshop_dirs

extracted_dirs = {
        # IdTechBsp
        # TODO: American McGee's Alice
        # TODO: DOOM 3 BFG Edition  # .resources .pk4 (https://forum.xentax.com/viewtopic.php?t=9752)
        # https://modwiki.dhewm3.org/Maps_(folder) states that DOOM 3 / IdTech 4 doesn't use .bsp? just raw .map?
        # what about DOOM 2016? DOOM Eternal? RAGE? RAGE 2? Quake 4? Brink?
        "Hexen2": ["pak0/maps",  # 4 maps | 6 MB | .pak
                   "pak1/maps"],  # 38 maps | 47 MB | .pak
        "Quake": ["Id1/pak0/maps",  # 21 maps | 10 MB | .pak
                  "Id1/pak1/maps",  # 30 maps | 31 MB | .pak
                  "hipnotic/pak0/maps",  # 18 maps | 30 MB | .pak
                  "rogue/pak0/maps",  # 23 maps | 28 MB | .pak
                  "rerelease/id1/pak0/maps",  # 55 maps | 49 MB | .pak
                  "rerelease/id1/pak0/maps/test",  # 14 maps | 1 MB | .pak
                  "rerelease/dopa/maps",  # 13 maps | 25 MB | .pak
                  "rerelease/hipnotic/pak0/maps",  # 18 maps | 30 MB
                  "rerelease/mg1/maps",  # 20 maps | 240 MB | .pak
                  "rerelease/rogue/pak0/maps"],  # 23 maps | 28 MB | .pak
        # TODO: Quake Arcane Dimensions (https://www.moddb.com/mods/arcane-dimensions/downloads)
        "QuakeII": ["pak0/maps",  # 39 maps | 89 MB | .pak
                    "pak1/maps"],  # 8 maps | 10 MB | .pak
        "QuakeIII": ["maps"],  # 31 maps | 116 MB | .pk3
        # TODO: Quake Champions .pak (Saber3D)
        "QuakeLive": ["pak00/maps"],  # 149 maps | 764 MB | .pk3
        # D3DBsp
        "CoD1": ["maps",  # 33 maps | 488 MB | .pk3
                 "maps/MP"],  # 16 maps | 229 MB | .pk3
        "CoD2": ["maps",  # 39 maps | 1.5 GB | .d3dbsp
                 "maps/mp"],  # 15 maps | 395 MB | .d3dbsp
        # TODO: CoD4  # .ff
        # ValveBsp
        "BlackMesa": ["maps"],  # 109 maps | 5.5 GB | .vpk
        "CSMalvinas": ["maps"],  # 1 map | 13 MB | Counter-Strike: Malvinas
        "CSO2": ["maps"],  # 97 maps | 902 MB | Counter-Strike: Online 2 | .pkg
        "DarkMessiah": ["singleplayer/maps",  # 35 maps | 1.4 GB | .vpk
                        "multiplayer/maps"],  # 11 maps | 564 MB | .vpk
        "TacticalIntervention": ["maps"],  # 26 maps | 3.5 GB | Tactical Intervention
        # https://www.moddb.com/mods/team-fortress/downloads
        "TeamFortressQuake": ["tf25rel/maps",  # 1 map | 1.88 MB | v2.5
                              "tf28/FORTRESS/maps",  # 1 map | 1.88 MB
                              "tfbot080/MAPS"],  # 1 map | 212 KB
        "TitanfallOnline": ["maps"],  # 18 maps | 2.2 GB | .pkg
        # TODO: Vindictus .hfs (encrypted)
        # RespawnBsp (NOTE: .bsp_lump & .ent sizes not counted)
        "Titanfall": ["maps"],  # 26 maps | 3,5 GB | .vpk
        "Titanfall2": ["maps"],  # 36 maps | 6.6 GB | .vpk
        # Thanks to https://apexlegends.fandom.com/wiki/Version_History
        # see also: https://github.com/Syampuuh/TitanfallApexLegends
        # TODO: reduce list to smallest possible set with bsp_tool.extensions.diff
        # -- could eventually create an archive of all map related patches
        "ApexLegends": ["maps",  # 9 maps | 3.3 GB
                        # season1:  Wild Frontier [19th Mar 2019]
                        # season2:  Battle Charge [2nd Jul 2019]
                        "season2/maps",  # 1 map | 16.9 MB
                        # season3:  Meltdown - patch 5  [1st Oct 2019]
                        "season3_30oct19/maps",  # 8 maps | 4.9 GB
                        "season3_30oct19/depot/r5launch/game/r2/maps",  # 8 maps | 4.9 GB
                        "season3_30oct19/depot/r5staging/game/r2/maps",  # 6 maps | 3.2 GB
                        "season3_3dec19/maps",  # 8 maps | 4.9 GB
                        # season4:  Assimilation [4th Feb 2020]
                        # season5:  Fortune's Favour  [12th May 2020]
                        "season5/maps",  # 3 maps | 1.2 GB
                        # season6:  Boosted  [18th Aug 2020]
                        # season7:  Ascension  [4th Nov 2020]
                        # season8:  Mayhem  [2nd Feb 2021]
                        "season8/maps",  # 1 map | 1.9 MB
                        # season9:  Legacy  [4th May 2021]
                        "season9/maps",  # 4 maps | 226 MB
                        # season10:  Emergence  [3rd Aug 2021]
                        "season10_3aug21/maps",  # 2 maps | 813 MB
                        "season10_3aug21/maps",  # 8 maps | 2.8 GB
                        "season10_3aug21/depot/r5-100/game/r2/maps"]}  # 8 maps | 2.8 GB
# ^ {"game_dir": ["map_dir"]}

# https://geshl2.com
# https://www.moddb.com/mods/riot-act
# https://www.moddb.com/mods/map-labs
# TODO: https://tf2classic.com
# TODO: https://github.com/mapbase-source/source-sdk-2013
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
