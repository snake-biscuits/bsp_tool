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
                        "blue_shift",    # 37 maps | 54 MB | Half-Life: Blue Shift
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
                       # "svencoop_addon/maps",  # 0 maps | 0 MB
                       # "svencoop_downloads/maps",  # 0 maps | 0 MB
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
         "MINERVA": ["metastasis/maps"],  # 6 maps | 201 MB
         "NEOTOKYO": ["neotokyosource/maps"],  # 24 maps | 303 MB
         "Portal": ["portal/maps"],  # 26 maps | 426 MB
         "Portal 2": ["portal2/maps",  # 106 maps | 2.7 GB
                      "portal2_dlc1/maps",  # 10 maps | 313 MB
                      "portal2_dlc2/maps"],  # 1 map | 687 KB
         "Portal Reloaded": ["portalreloaded/maps"],  # 12 maps | 448 MB
         "SourceFilmmaker": ["game/tf/maps"],  # 71 maps | 3.3 GB
         "Synergy": ["synergy/maps"],  # 21 maps | 407 MB
         "Team Fortress 2": ["tf/maps",  # 194 maps | 5.2 GB
                             "tf/download/maps"],  # 187 maps | 2.6 GB
         "Transmissions Element 120": ["te120/maps"],  # 5 maps | 281 MB
         "Vampire The Masquerade - Bloodlines": ["Vampire/maps"]  # 101 maps | 430 MB
              }
# ^ {"game_dir": ["map_dir"]}

# TODO: workshop_dirs

extracted_dirs = {
        # IdTechBsp
        "Anachronox": ["maps",  # 98 maps | 377 MB | .dat
                       "anox1.zip/maps"],  # 3 maps | 4 MB | .zip
        "Daikatana": ["pak2/maps"],  # 83 maps | 291 MB | .pak
        "HereticII": ["Htic2-0.pak/maps"],  # 29 maps | 77 MB | .pak
        "Hexen2": ["pak0/maps",  # 4 maps | 6 MB | .pak
                   "pak1/maps"],  # 38 maps | 47 MB | .pak
        "RTCW": ["mp_pak0.pak3/maps",  # 8 maps | 89 MB | .pk3
                 "mp_pakmaps0.pak3/maps",  # 1 map | 8 MB | .pk3
                 "mp_pakmaps1.pak3/maps",  # 1 map | 11 MB | .pk3
                 "mp_pakmaps2.pak3/maps",  # 1 map | 10 MB | .pk3
                 "mp_pakmaps3.pak3/maps",  # 1 map | 14 MB | .pk3
                 "mp_pakmaps4.pak3/maps",  # 1 map | 16 MB | .pk3
                 "mp_pakmaps5.pak3/maps",  # 1 map | 12 MB | .pk3
                 "mp_pakmaps6.pak3/maps",  # 1 map | 11 MB | .pk3
                 "pak0.pak3/maps",  # 32 maps | 234 MB | .pk3
                 "sp_pak4.pak3/maps"],  # 3 maps | 24 MB | .pk3
        "SiN": ["maps",  # 65 maps | 170 MB | .sin (.pak) | SiN: Gold
                "download/maps"],  # 45 maps | 64 MB | .sin (.pak) | SiN mods
        "SoF": ["pak0/maps"],  # 32 maps | 131 MB | .pak
        "SoF2": ["maps.pk3/maps",  # 48 maps | 409 MB | .pk3
                 "mp.pk3/maps",  # 10 maps | 63 MB | .pk3
                 "update101.pk3/maps",  # 4 maps | 22 MB | .pk3
                 "update102.pk3/maps",  # 5 maps | 51 MB | .pk3
                 "update103.pk3/maps"],  # 4 maps | 31 MB | .pk3
        "StarTrekEliteForce": ["pak0/maps",  # 67 maps | 334 MB | .pak
                               "pak1/maps",  # 4 maps | 20 MB | .pak
                               "pak3/maps"],  # 22 maps | 107 MB | .pak
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
        # CoDBsp
        "CoD1": ["maps",  # 33 maps | 488 MB | .pk3
                 "maps/MP"],  # 16 maps | 229 MB | .pk3
        "CoD2": ["maps",  # 39 maps | 1.5 GB | .d3dbsp
                 "maps/mp"],  # 15 maps | 395 MB | .d3dbsp
        # TODO: CoD4  # .ff
        # ValveBsp
        "BlackMesa": ["maps"],  # 109 maps | 5.5 GB | .vpk
        "CSMalvinas": ["maps"],  # 1 map | 13 MB | Counter-Strike: Malvinas
        # https://github.com/L-Leite/UnCSO2
        "CSO2": ["maps"],  # 97 maps | 902 MB | Counter-Strike: Online 2 | .pkg
        "DarkMessiah/singleplayer": ["maps"],  # 35 maps | 1.4 GB | .vpk
        "DarkMessiah/multiplayer": ["maps"],  # 11 maps | 564 MB | .vpk
        # https://www.moddb.com/games/james-bond-007-nightfire/downloads/alura-zoe
        "Nightfire": ["ROOT/maps"],  # 53 maps | 405 MB | .007
        "TacticalIntervention": ["maps"],  # 26 maps | 3.5 GB | Tactical Intervention
        # https://www.moddb.com/mods/team-fortress/downloads
        "TeamFortressQuake": ["tf25rel/maps",  # 1 map | 1.88 MB | v2.5
                              "tf28/FORTRESS/maps",  # 1 map | 1.88 MB
                              "tfbot080/MAPS"],  # 1 map | 212 KB
        "TitanfallOnline": ["maps"],  # 18 maps | 2.2 GB | .pkg
        # https://github.com/yretenai/HFSExtract
        "Vindictus": ["maps"],  # 474 maps | 8.8 GB | .hfs
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
                        "season3_3dec19/maps",  # 8 maps | 4.6 GB
                        "season3_3dec19/maps/r5launch/game/r2/maps",  # 8 maps | 4.6 GB
                        "season3_3dec19/maps/r5staging/game/r2/maps",  # 8 maps | 3.0 GB
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
                        "season10_3aug21/depot/r5-100/game/r2/maps",  # 8 maps | 2.8 GB
                        "season10_14sep21/maps"  # 2 maps | 962 MB
                        "season10_14sep21/depot/r5-100/game/r2/maps",  # 1 map | 797 MB
                        "season10_14sep21/depot/r5-101/game/r2/maps",  # 2 maps | 949 MB
                        # season11:  Escape  [2nd Nov 2021]
                        "season11/maps",  # 1 map | 10 MB
                        "season11/depot/r5-110/game/r2/maps"  # 1 map | 9 MB
                        "season11_6nov21/maps",  # 1 map | 760 MB
                        "season11_6nov21/depot/r5-110/game/r2/maps"],  # 1 map | 749 MB
        # RitualBsp
        "FAKK2": ["maps",  # 30 maps | 150 MB | .pk3
                  "download/maps"],  # 6 maps | 25 MB | .pk3
        "Alice": ["maps",  # 42 maps | 196 MB | .pk3
                  "download/maps"],  # 1 map | 61 KB | .pk3
        "MoHAA": ["maps",  # 37 maps | 293 MB | .pk3
                  "maps/briefing",  # 6 maps | 319 KB | .pk3
                  "maps/DM",  # 7 maps | 48 MB | .pk3
                  "maps/obj"],  # 4 maps | 36 MB | .pk3
        "StarTrekEliteForceII": ["download/maps",  # 188 maps | 886 MB | .pk3
                                 "maps"],  # 88 maps | 607 MB | .pk3
        "StarWarsJediKnight": ["assets0.pk3/maps",  # 34 maps | 348 MB | .pk3
                               "assets0.pk3/maps/mp",  # 23 maps | 154 MB | .pk3
                               "assets3.pk3/maps/mp"],  # 4 maps | 32 MB | .pk3
        "StarWarsJediKnightII": ["maps"]}  # 45 maps | 361 MB | .pk3
# ^ {"game_dir": ["map_dir"]}

# https://geshl2.com
# https://www.moddb.com/mods/riot-act
# https://www.moddb.com/mods/map-labs
# TODO: https://openfortress.fun, https://prefortress.ml & https://tf2classic.com  (all currently unavailable)
sourcemod_dirs = {mod: ["maps"] for mod in [
                      "gesource",  # 26 maps | 775 MB | GoldenEye: Source
                      "half-life 2 riot act",  # 5 maps | 159 MB | HL2: Riot Act
                      # Run Think Shoot Live
                      "TFTS",  # 3 maps | 8 MB | Tales from the Source
                      # Map Labs
                      "episodeone",  # 15 maps | 268 MB | Map Labs # 2 + Test Tube # 15
                      "RunThinkShootLiveVille2",  # 19 maps | 728 MB | Map Labs # 3
                      "cromulentville2",  # 21 maps | 342 MB | Test Tube # 7
                      "companionpiece2",  # 18 maps | 429 MB | Map Labs # 8
                      "eyecandy",   # 41 maps | 652 MB | Test Tube # 8
                      "tworooms",  # 39 maps | 496 MB | Test Tube # 9
                      "fusionville2",  # 21 maps | 391 MB | Map Labs # 10
                      "lvl2",  # 14 maps | 461 MB | Map Labs # 15
                      "thewrapuptwo",  # 27 maps | 226 MB | Test Tube # 15
                      "halloweenhorror4"]}  # 25 maps | 274 MB | Map Labs # 16

# every_bsp_dir = {**sourcemod_dirs, **extracted_dirs, **goldsrc_dirs, **source_dirs}

# NOTE: ls $group_dir+$game_dir+$maps_dir
group_dirs = {"C:/Program Files (x86)/Steam/steamapps/sourcemods": sourcemod_dirs,
              "D:/SteamLibrary/steamapps/common": {**goldsrc_dirs, **source_dirs},
              "E:/Mod": extracted_dirs,  # Id Software, Respawn Entertainment, Nexon & More
              # "F:/bsps": every_bsp_dir,
              # "/media/bikkie/GAMES/bsps": every_bsp_dir
              }

installed_games = {("./", "tests"): ["maps"]}
for group, games in group_dirs.items():
    if os.path.exists(group):
        for game, map_dirs in games.items():
            if os.path.exists(os.path.join(group, game)):
                installed_games[(group, game)] = map_dirs
