import os
from typing import Dict, List, Tuple


DirList = Dict[str, List[str]]
# ^ {"Game": ["maps_dir"]}

GameDirList = Dict[str, DirList]
# ^ {"SteamFolder": {**DirList_1, **DirList_2}}
# ^ {"External/Backup": {**DirList_1, **DirList_2}}

goldsrc_dirs: DirList  # GoldSrc titles
source_dirs: DirList  # Source Engine titles
extracted_dirs: DirList  # .bsps from archives (.007, .hfs, .iwd, .ff, .pak, .pk3, .pkg, .sin, .vpk) & non-steam games
sourcemod_dirs: DirList  # Source SDK games @ Steam/steamapps/sourcemods
every_bsp_dir: DirList  # all of the above in one dict (used with external HDD)
group_dirs: GameDirList  # groups folders to install dirs (steam installs, external HDDs etc.)
installed_games: Dict[Tuple[str], List[str]]
# ^ {("SteamFolder", "Game"): ["maps_dir"]}


# TODO: generate by searching for gameinfo.txt files
goldsrc_dirs = {
        "Cry of Fear/cryoffear": ["maps"],  # 235 maps | 1.9 GB | Cry of Fear
        **{f"Half-Life/{mod}": ["maps"] for mod in [
                        "blue_shift",    # 37 maps | 54 MB | Half-Life: Blue Shift
                        "cstrike",   # 25 maps | 81 MB | Counter-Strike
                        "czero",     # 22 maps | 83 MB | Counter-Strike: Condition Zero
                        "czeror",    # 73 maps | 177 MB | Counter-Strike: Condition Zero - Deleted Scenes
                        "dmc",       # 7 maps | 9 MB | Deathmatch: Classic
                        "dod",       # 22 maps | 91 MB | Day of Defeat
                        "gearbox",   # 68 maps | 137 MB | Half-Life: Opposing Force
                        # https://www.moddb.com/mods/natural-selection
                        "ns",        # 27 maps | 124 MB | Natural Selection
                        "ricochet",  # 3 maps | 2 MB | Ricochet
                        "tfc",       # 15 maps | 41 MB | Team Fortress: Classic
                        "valve"]},   # 115 maps | 188 MB | Half-Life
        "Halfquake Trilogy/valve": ["maps"],  # 152 maps | 207 MB
        "Sven Co-op": ["svencoop/maps",  # 107 maps | 521 MB
                       # "svencoop_addon/maps",  # 0 maps | 0 MB
                       # "svencoop_downloads/maps",  # 0 maps | 0 MB
                       "svencoop_event_april/maps"]}  # 4 maps | 31 MB
# ^ {"game_dir": ["map_dir"]}

# TODO: generate by searching for gameinfo.txt files
source_dirs = {
         "Alien Swarm/swarm": ["maps"],  # 9 maps | 299 MB
         "Alien Swarm Reactive Drop/reactivedrop": ["maps"],  # 53 maps | 1.3 GB
         "Blade Symphony/berimbau": ["maps"],  # 21 maps | 1.0 GB
         "counter-strike source/cstrike": ["maps"],  # 20 maps | 237 MB
         "day of defeat source/dod": ["maps"],  # 9 maps | 299 MB
         "dayofinfamy": ["doi/maps"],  # 16 maps | 1.09 GB
         "Dino D-Day": ["dinodday/maps"],  # 14 maps | 434 MB
         "Double Action": ["dab/maps"],  # 10 maps | 255 MB
         "EntropyZero2/entropyzero2": ["maps"],  # 72 maps | 1.58 GB
         "EYE Divine Cybermancy Demo/EYE": ["maps"],  # 6 maps | 176 MB
         "Fistful of Frags": ["fof/maps"],  # 39 maps | 1.68 GB
         "Fortress Forever": ["FortressForever/maps"],  # 22 maps | 618 MB
         "G String/gstringv2": ["maps"],  # 76 maps | 2.49 GB | Seriously Impressive
         "GarrysMod/garrysmod": ["maps"],  # 2 maps | 84 MB
         "Half-Life 1 Source Deathmatch/hl1mp": ["maps"],  # 11 maps | 53 MB
         **{f"half-life 2/{mod}": ["maps"] for mod in [
                         "ep2",          # HL2:EP2 |  22 maps | 703 MB
                         "episodic",     # HL2:EP1 |  20 maps | 554 MB
                         "hl1",          # HL:S    | 110 maps | 339 MB
                         "hl2",          # HL2     |  80 maps | 815 MB
                         "lostcoast"]},  # HL2:LC  |   4 maps | 101 MB
         "half-life 2 deathmatch/hl2mp": ["maps"],  # 8 maps | 72 MB
         "Half-Life 2 Update": ["hl2/maps"],  # 76 maps | 2.9 GB
         "Half-Life 2 VR": ["hl2/maps",  # 79 maps | 777 MB
                            "hlvr/maps"],  # 1 map | 7 MB
         "insurgency2": ["insurgency/maps"],  # 49 maps | 2.54 GB
         "Jabroni Brawl Episode 3": ["jbep3/maps"],  # 133 maps | 2.64 GB
         "left 4 dead": ["left4dead/maps",   # 45 maps | 975 MB
                         "left4dead_dlc3/maps"],  # 3 maps | 67 MB
         "Left 4 Dead 2": ["left4dead2/maps",  # 8 maps | 186 MB
                           "left4dead2_dlc1/maps",  # 3 maps | 60 MB
                           "left4dead2_dlc2/maps",  # 8 maps | 186 MB
                           "left4dead2_dlc3/maps"],  # 21 maps | 481 MB
         "MINERVA": ["metastasis/maps"],  # 6 maps | 201 MB
         "Momentum Mod Playtest": ["momentum/maps"],  # 4 maps | 39 MB
         "NEOTOKYO/neotokyosource": ["maps"],  # 24 maps | 303 MB
         "nmrih": ["nmrih/maps"],  # 31 maps | 1.1 GB
         "Portal/portal": ["maps"],  # 26 maps | 426 MB
         "Portal 2": ["portal2/maps",  # 106 maps | 2.7 GB
                      "portal2_dlc1/maps",  # 10 maps | 313 MB
                      "portal2_dlc2/maps"],  # 1 map | 687 KB
         "Portal Reloaded": ["portalreloaded/maps"],  # 12 maps | 448 MB
         "Portal Revolution": ["revolution/maps"],  # 46 maps | 1.93 GB
         "SourceFilmmaker/game/tf": ["maps"],  # 71 maps | 3.3 GB
         "Synergy": ["synergy/maps"],  # 21 maps | 407 MB
         # TODO: compile Tactical Intervention sample .vmfs
         "TacticalIntervention": ["maps",  # 5 maps | 533 MB
                                  "maps/b3174"],  # 27 maps | 1.58 GB
         "Team Fortress 2": ["tf/maps",  # 194 maps | 5.2 GB
                             "tf/download/maps"],  # 187 maps | 2.6 GB
         "Transmissions Element 120": ["te120/maps"],  # 5 maps | 281 MB
         "Vampire The Masquerade - Bloodlines/Vampire": ["maps"],  # 101 maps | 430 MB
         "Zeno Clash Demo/zenozoik": ["maps"]}  # 20 maps | 16 MB
# ^ {"game_dir": ["map_dir"]}

# TODO: steam_workshop_dirs

extracted_dirs = {
        # QuakeBsp
        "DarkPlaces": ["maps"],  # 16 maps | 1 MB | .zip
        # NOTE: contains b"IDPO", quake .mdl with .bsp extension?
        # -- b_batt0.bsp? quake map sources say this is a game model?
        # -- https://www.gamers.org/dEngine/quake/spec/quake-spec32.html#CMDLF
        "Quake": ["Id1/pak0/maps",  # 21 maps | 10 MB | .pak
                  "Id1/pak1/maps",  # 30 maps | 31 MB | .pak
                  "hipnotic/pak0/maps",  # 18 maps | 30 MB | .pak
                  "rogue/pak0/maps"],  # 23 maps | 28 MB | .pak
        "Quake/rerelease": ["id1/pak0/maps",  # 55 maps | 49 MB | .pak
                            "id1/pak0/maps/test",  # 14 maps | 1 MB | .pak
                            "hipnotic/pak0/maps",  # 18 maps | 30 MB
                            "mg1/pak0/maps",  # 20 maps | 240 MB | .pak
                            "rogue/pak0/maps"],  # 23 maps | 28 MB | .pak
        # Quake64Bsp
        # QuakeCon 2021 PC re-release of Midway's Nintendo 64 port
        # Download in-game (Quake Re-release) via addons; installs into %USERPROFILE%
        "Quake64": ["q64/pak0/maps"],  # 32 maps | 21 MB | .pak
        # http://quake.great-site.net/
        # ReMakeQuakeBsp
        "Alkaline": ["alkaline/pak0/maps",  # 23 maps | 132 MB | .pak
                     "alk1.1/pak0/maps",  # 27 maps | 188 MB | .pak
                     "alkaline_dk/maps"],  # 13 maps | 792 KB | .zip
        # rome.ro Quake Map Source compiled with `ericw-tool/qbsp -2psb`
        "Quake/2psb": ["maps"],  # 62 maps | 45 MB | .zip (.map)
        # Dimension of the Past
        "Quake/rerelease/dopa": ["pak0/maps"],  # 13 maps | 25 MB | .pak
        # TODO: Quake Arcane Dimensions (https://www.moddb.com/mods/arcane-dimensions/downloads)
        # IdTechBsp
        "Anachronox": ["maps",  # 98 maps | 377 MB | .dat
                       "anox1.zip/maps"],  # 3 maps | 4 MB | .zip
        "Daikatana": ["pak2/maps"],  # 83 maps | 291 MB | .pak
        "DDayNormandy": ["D-Day_ Normandy/dday/maps",  # 61 maps | 135 MB | .zip
                         "DDaynormandymaps-mappack/dday/maps"],  # 658 maps | 1.08 GB | .zip
        "HereticII": ["Htic2-0.pak/maps"],  # 29 maps | 77 MB | .pak
        "HexenII": ["pak0/maps",  # 4 maps | 6 MB | .pak
                    "pak1/maps"],  # 38 maps | 47 MB | .pak
        "Nexuiz": ["maps"],  # 39 maps | 146 MB | .pk3
        "RTCW": ["mp_pak0.pk3/maps",  # 8 maps | 89 MB | .pk3
                 "mp_pakmaps0.pk3/maps",  # 1 map | 8 MB | .pk3
                 "mp_pakmaps1.pk3/maps",  # 1 map | 11 MB | .pk3
                 "mp_pakmaps2.pk3/maps",  # 1 map | 10 MB | .pk3
                 "mp_pakmaps3.pk3/maps",  # 1 map | 14 MB | .pk3
                 "mp_pakmaps4.pk3/maps",  # 1 map | 16 MB | .pk3
                 "mp_pakmaps5.pk3/maps",  # 1 map | 12 MB | .pk3
                 "mp_pakmaps6.pk3/maps",  # 1 map | 11 MB | .pk3
                 "pak0.pk3/maps",  # 32 maps | 234 MB | .pk3
                 "sp_pak4.pk3/maps",  # 3 maps | 24 MB | .pk3
                 # https://www.moddb.com/mods/realrtcw-realism-mod
                 # https://store.steampowered.com/app/1379630/RealRTCW/
                 "realRTCW/maps"],  # 11 maps | 85 MB
        "SiN": ["maps",  # 65 maps | 170 MB | .sin (.pak) | SiN: Gold
                "download/maps"],  # 45 maps | 64 MB | .sin (.pak) | SiN mods
        "SoF": ["pak0/maps",  # 32 maps | 131 MB | .pak
                "pak0/maps/dm",  # 20 maps | 37 MB | .pak
                "pak2/maps/dm",  # 19 maps | 35 MB | .pak
                "pak3/maps/dm"],  # 5 maps | 8 MB | .pak
        "SoF2": ["maps.pk3/maps",  # 48 maps | 409 MB | .pk3
                 "mp.pk3/maps",  # 10 maps | 63 MB | .pk3
                 "update101.pk3/maps",  # 4 maps | 22 MB | .pk3
                 "update102.pk3/maps",  # 5 maps | 51 MB | .pk3
                 "update103.pk3/maps"],  # 4 maps | 31 MB | .pk3
        "StarTrekEliteForce": ["pak0/maps",  # 67 maps | 334 MB | .pk3
                               "pak1/maps",  # 4 maps | 20 MB | .pk3
                               "pak3/maps"],  # 22 maps | 107 MB | .pk3
        "QuakeII": ["pak0/maps",  # 39 maps | 89 MB | .pak
                    "pak1/maps",  # 8 maps | 10 MB | .pak
                    "zaero/pak0/maps"],  # 14 maps | 36 MB | .pak
        # QuakeCon 2023 re-release
        # NOTE: pak0/maps contains a handful of QbismBsp
        "QuakeII/rerelease": ["pak0/maps",  # 142 maps | 1.1 GB | .pak
                              "pak0/maps/e3",  # 10 maps | 18 MB | .pak
                              "pak0/maps/ec",  # 10 maps | 38 MB | .pak
                              "pak0/maps/old",  # 11 maps | 62 MB | .pak
                              "pak0/maps/q64",  # 30 maps | 23 MB | .pak
                              "pak0/maps/test"],  # 19 maps | 5 MB | .pak
        "QuakeIII": ["baseq3/pak0.pk3/maps",  # 31 maps | 110 MB | .pk3
                     "baseq3/pak2.pk3/maps",  # 2 maps | 7 MB | .pk3
                     # "baseq3/pak4.pk3/maps",  # only .aas files
                     "baseq3/pak6.pk3/maps",  # 4 maps | 14 MB | .pk3
                     "missionpack/pak0.pk3/maps",  # 21 maps | 150 MB | .pk3
                     # https://web.archive.org/web/20030207191220/http://www.interscope.com/quake/
                     "chronic/maps"],  # 1 map | 2.9 MB | .pk3
        # TODO: Quake Champions .pak (Saber3D)
        "QuakeLive": ["pak00/maps"],  # 149 maps | 764 MB | .pk3
        # https://www.splashdamage.com/games/wolfenstein-enemy-territory/
        "WolfET": ["pak0.pk3/maps",  # 6 maps | 86 MB | .pk
                   # https://www.moddb.com/mods/et/downloads/etsp
                   "singleplayer/maps",  # 32 maps | 288 MB | .pk3
                   # steamapps\workshop\content\1379630\2600685791 (realRTCW workshop)
                   "realRTCW_singleplayer/maps"],  # 2 maps | 31 MB | .pk3
        "WRATH": ["pak002.pk3/maps"],  # 7 maps | 395 MB | .pk3
        "Xonotic": ["maps"],  # 28 maps | 188 MB | .pk3
        # FusionBSP
        "Warfork": ["warfork/basewf/data1_21pure.pk3/maps",  # 43 maps | 558 MB | .pk3
                    "warfork-testing/basewf/maps"],  # 43 maps | 558 MB | awful dir tree
        "Warsow": ["maps"],  # 38 maps | 463 MB | .pk3
        # InfinityWardBsp
        "CoD1Demo/burnville": ["maps"],  # 1 map | 13 MB | .pk3
        "CoD1Demo/dawnville": ["maps"],  # 1 map | 16 MB | .pk3
        "CoD1": ["maps",  # 33 maps | 488 MB | .pk3
                 "maps/MP"],  # 16 maps | 229 MB | .pk3
        "CoD2": ["maps",  # 39 maps | 1.5 GB | .iwd | .d3dbsp
                 "maps/mp"],  # 15 maps | 395 MB | .iwd  | .d3dbsp
        # D3DBsp
        # TODO: Extract CoD4 maps from .ff archives
        # https://wiki.zeroy.com/index.php?title=Call_of_Duty_4:_FastFile_Format
        # https://github.com/Scobalula/Greyhound
        # https://github.com/ZoneTool/zonetool
        # https://github.com/promod/CoD4-Mod-Tools
        # "CoD4": ["devraw/maps",  # 1 map | 17 MB | .d3dbsp  (v17 InfinityWardBsp; not a CoD4 .d3dbsp?)
        "CoD4": ["maps",  # 3 maps | 7 MB | .d3dbsp
                 "maps/mp"],  # 1 map | 4 MB | .d3dbsp
        # GoldSrcBsp
        # https://www.moddb.com/games/james-bond-007-nightfire/downloads/alura-zoe
        "Nightfire": ["ROOT/maps"],  # 53 maps | 405 MB | .007
        # ValveBsp
        "BlackMesa": ["maps"],  # 109 maps | 5.5 GB | .vpk
        "BloodyGoodTime": ["maps"],  # 3 maps | 124 MB | .vpk
        "Contagion": ["maps"],  # 52 maps | 2.62 GB | .vpk
        # CS2 replaced CS:GO, made a backup
        "CSGO/csgo_backup": ["maps"],  # 41 maps | 4.93 GB
        # TODO: os.listdir("E:/Mod/CSGO/csgo_backup/workshop")  # 72 maps | 4.70 GB
        "CSMalvinas": ["maps"],  # 1 map | 13 MB | Counter-Strike: Malvinas
        # https://github.com/Bocuma747/SurfMaps
        "CSS/Bocuma747_SurfMaps": ["maps"],  # 72 maps | 2.1 GB | .zip
        # https://github.com/OuiSURF/Surf_Maps
        "CSS/OiuSURF_SurfMaps": ["maps"],  # 183 maps | 7.51 GB | .zip
        # https://github.com/L-Leite/UnCSO2
        "CSO2": ["maps"],  # 97 maps | 902 MB | Counter-Strike: Online 2 | .pkg
        "DarkMessiah/singleplayer": ["maps"],  # 35 maps | 1.4 GB | .vpk
        "DarkMessiah/multiplayer": ["maps"],  # 11 maps | 564 MB | .vpk
        # https://archive.org/details/dear_esther_linux
        "DearEsther/dearesther": ["maps"],  # 4 maps | 85 MB | .deb
        # https://www.hidden-source.com/downloads.htm
        # https://www.moddb.com/mods/hidden-source
        "TheHiddenSource": ["hidden/maps"],  # 15 maps | 112 MB | .exe (extracted from Beta4b installer)
        # https://gamebanana.com/members/submissions/sublog/1762428
        "HL2DM/patbytes": ["maps"],  # 46 maps | 895 MB | .7z
        "Infra": ["maps"],  # 49 maps | 5.5 GB | .vpk
        "Merubasu/shadowland": ["maps"],  # 29 maps | 315 MB | .apk
        # https://github.com/momentum-mod/BSPConversionLib
        "MomentumMod": ["chronic/maps",  # 1 map | 10 MB | .pk3 -> v25 VBSP
                        # http://nnsurf.site.nfoservers.com/Momentum/
                        "nfoservers/AhopMaps",  # 14 maps | 181 MB
                        "nfoservers/ConcMaps",  # 5 maps | 48 MB
                        "nfoservers/JumpMaps",  # 51 maps | 2.11 GB
                        "nfoservers/SurfMaps",  # 270 maps | 9.38 GB
                        "nfoservers/TricksurfMaps",  # 8 maps | 205 MB
                        # Momentum Mod Discord #gamemode-conc pins
                        "Zike/ff_conc/maps",  # 20 maps | 369 MB
                        "Zike/ff_skill/maps",  # 99 | 1.46 GB
                        "Zike/mmod_conc/maps"],  # 5 maps | 48 MB
        "SiNEpisodes": ["maps"],  # 32 maps | 345 MB | .vpk
        # Tactical Intervention release maps are 256-bit XOR encrypted
        # -- see `bsp_tool/extensions/decrypt_xor.py`
        "TacticalIntervention": ["maps"],  # 4 maps | 533 MB
        # https://www.moddb.com/mods/team-fortress/downloads
        "TeamFortressQuake": ["tf25rel/maps",  # 1 map | 1.88 MB | .zip
                              "tf28/FORTRESS/maps",  # 1 map | 1.88 MB | .zip
                              "tfbot080/MAPS"],  # 1 map | 212 KB | .zip
        "TheShip": ["base/maps",  # 11 maps | 223 MB | .vpk
                    "sp/maps",  # 14 maps | 245 MB | .vpk
                    "tutorial/maps"],  # 12 maps | 224 MB | .vpk
        # https://github.com/yretenai/HFSExtract
        "Vindictus": ["hfs/2022/maps",  # 474 maps | 8.08 GB | .hfs
                      "Colhen_Mod_BSP (Private Server Version)"],  # 1 map | 23 MB | .zip
        "Vindictus/Client v1.69 EU": ["hfs/maps"],  # 279 maps | 4.30 GB | .hfs
        # RespawnBsp
        "Titanfall": ["maps",  # 26 maps | 6.6 GB | .vpk
                      "depot/r1dev/game/r1/maps",  # 16 maps | 6.4 GB | .vpk
                      "depot/r1pcgold/game/r1/maps",  # 1 map | 2.2 GB | .vpk
                      "depot/r1pcstaging/game/r1/maps",  # 23 maps | 5.8 GB | .vpk
                      "depot/r1pcstaging/game/r1_dlc1/maps"],  # 3 maps | 796 MB | .vpk
        # https://archive.org/details/titanfall-beta
        "Titanfall/beta": ["maps",  # 4 maps | 901 MB | .vpk
                           "depot/r1beta/game/r1/maps"],  # 4 maps | 900 MB | .vpk
        # Xbox 360 maps loosely extracted from BluePoint .bpk
        # -- .bpk filenames are unknown, so .bsp, .bsp_lump & .ent may all be incorrect
        # NOTE: working to better extract files from .bpk with p0358
        # -- all files become null bytes after 131207 bytes (2 ** 17)
        # "Titanfall/x360": ["maps"],  # 17 maps | 349 MB
        # donated by p0358
        "TitanfallOnline": ["maps",  # 17 maps | 2.0 GB | .pkg
                            "v2905-dated-2017-04-08/maps",  # 13 maps | 1.3 GB | .7z
                            "v4050-datarevision-17228-dated-2017-08-17/maps"],  # 13 maps | 1.3 GB | .7z
        "Titanfall2": ["maps",  # 37 maps | 12.7 GB | .vpk
                       "depot/r2dlc3/game/r2/maps",       # 29 maps | 11.1 GB | .vpk
                       "depot/r2dlc4/game/r2/maps",       # 31 maps | 11.5 GB | .vpk
                       "depot/r2dlc5/game/r2/maps",       # 32 maps | 11.8 GB | .vpk
                       "depot/r2dlc6/game/r2/maps",       # 34 maps | 12.0 GB | .vpk
                       "depot/r2dlc7/game/r2/maps",       # 36 maps | 12.4 GB | .vpk
                       "depot/r2dlc8/game/r2/maps",       # 37 maps | 12.5 GB | .vpk
                       "depot/r2dlc9/game/r2/maps",       # 37 maps | 12.5 GB | .vpk
                       "depot/r2dlc10/game/r2/maps",      # 37 maps | 12.5 GB | .vpk
                       "depot/r2dlc11/game/r2/maps",      # 37 maps | 12.5 GB | .vpk
                       "depot/r2pcprecert/game/r2/maps",  # 25 maps | 10.9 GB | .vpk
                       "depot/r2staging/game/r2/maps"],   # 28 maps | 11.0 GB | .vpk
        # APEX ARCHIVE
        # Thanks to https://antifandom.com/apexlegends/wiki/Version_History
        # season0-6 archives from r-ex
        # season7-present from SteamDB Manifests + DepotDownloader
        # season0:  Preseason [4th February 2019]
        "ApexLegends/season0": ["4feb19/maps",  # 2 maps | 782 MB | .vpk
                                "4feb19/depot/r5launch/game/r2/maps"],  # 2 maps | 774 MB | .vpk
        # season1:  Wild Frontier [19th Mar 2019]
        "ApexLegends/season1": ["19mar19/maps",  # 2 maps | 779 MB | .vpk
                                "19mar19/depot/r5launch/game/r2/maps",  # 2 maps | 771 MB | .vpk
                                "16apr19/maps",  # 2 maps | 785 MB | .vpk
                                "16apr19/depot/r5launch/game/r2/maps",  # 2 maps | 777 MB | .vpk
                                "4jun19/maps",  # 2 maps | 782 MB | .vpk
                                "4jun19/depot/r5launch/game/r2/maps"],  # 2 maps | 773 MB | .vpk
        # season2:  Battle Charge [2nd Jul 2019]
        "ApexLegends/season2": ["2jul19/maps",  # 4 maps | 1.54 GB | .vpk
                                "2jul19/depot/r5launch/game/r2/maps",  # 4 maps | 1.52 GB | .vpk
                                "13aug19/maps",  # 4 maps | 1.54 GB | .vpk
                                "13aug19/depot/r5launch/game/r2/maps",  # 4 maps | 1.53 GB | .vpk
                                "3sep19/maps",  # 4 maps | 1.53 GB | .vpk
                                "3sep19/depot/r5launch/game/r2/maps"],  # 4 maps | 1.51 GB | .vpk
        # season3:  Meltdown [1st October 2019]
        "ApexLegends/season3": ["1oct19/maps",  # 6 maps | 3.04 GB | .vpk
                                "1oct19/depot/r5launch/game/r2/maps",  # 6 maps | 3.00 GB | .vpk
                                "5nov19/maps",  # 6 maps | 3.04 GB | .vpk
                                "5nov19/depot/r5launch/game/r2/maps",  # 6 maps | 3.00 GB | .vpk
                                "5nov19/depot/r5staging/game/r2/maps",  # 6 maps | 3.00 GB | .vpk
                                "3dec19/maps",  # 8 maps | 4.64 GB | .vpk
                                "3dec19/depot/r5launch/game/r2/maps",  # 8 maps | 4.58 GB | .vpk
                                "3dec19/depot/r5staging/game/r2/maps"],  # 6 maps | 3.00 GB | .vpk
        # season4:  Assimilation [4th Feb 2020]
        "ApexLegends/season4": ["4feb20/maps",  # 9 maps | 5.44 GB | .vpk
                                "4feb20/depot/r5launch/game/r2/maps",  # 9 maps | 5.38 GB | .vpk
                                "4feb20/depot/r5staging/game/r2/maps",  # 6 maps | 3.00 GB | .vpk
                                "3mar20/maps",  # 7 maps | 1.91 GB | .vpk
                                "3mar20/depot/r5launch/game/r2/maps",  # 7 maps | 1.91 GB | .vpk
                                "7apr20/maps",  # 7 maps | 1.91 GB | .vpk
                                "7apr20/depot/r5launch/game/r2/maps",  # 7 maps | 1.91 GB | .vpk
                                "7apr20/depot/r5staging/game/r2/maps"],  # 7 maps | 1.91 GB | .vpk
        # season5:  Fortune's Favour  [12th May 2020]
        "ApexLegends/season5": ["12may20/maps",  # 8 maps | 2.26 GB | .vpk
                                "12may20/depot/r5launch/game/r2/maps",  # 8 maps | 2.26 GB | .vpk
                                "23jun20/maps",  # 9 maps | 2.63 GB | .vpk
                                "23jun20/depot/r5launch/game/r2/maps",  # 9 maps | 2.63 GB | .vpk
                                "23jun20/depot/r5staging/game/r2/maps"],  # 8 maps | 2.26 GB | .vpk
        # season6:  Boosted  [18th Aug 2020]
        "ApexLegends/season6": ["18aug20/maps",  # 9 maps | 2.66 GB | .vpk
                                "18aug20/depot/r5-60/game/r2/maps",  # 9 maps | 2.66 GB | .vpk
                                "6oct20/maps",  # 9 maps | 2.71 GB | .vpk
                                "6oct20/depot/r5-60/game/r2/maps",  # 9 maps | 2.66 GB | .vpk
                                "6oct20/depot/r5-61/game/r2/maps"],  # 9 maps | 2.71 GB | .vpk
        # season7:  Ascension  [4th Nov 2020]
        "ApexLegends/season7": ["3nov20/depot/r5-70/game/r2/maps",  # 6 maps | 3.75 GB | .vpk
                                "3nov20/maps",  # 6 maps | 3.81 GB | .vpk
                                "5jan21/depot/r5-70/game/r2/maps",  # 11 maps | 6.91 GB | .vpk
                                "5jan21/depot/r5-71/game/r2/maps",  # 11 maps | 6.91 GB | .vpk
                                "5jan21/depot/r5-72/game/r2/maps",  # 11 maps | 6.75 GB | .vpk
                                "5jan21/maps"],  # 11 maps | 6.84 GB | .vpk
        # season8:  Mayhem  [2nd Feb 2021]
        "ApexLegends/season8": ["2feb21/depot/r5-80/game/r2/maps",  # 7 maps | 3.83 GB | .vpk
                                "2feb21/maps",  # 7 maps | 3.88 GB | .vpk
                                "9mar21/depot/r5-80/game/r2/maps",  # 7 maps | 3.83 GB | .vpk
                                "9mar21/depot/r5-81/game/r2/maps",  # 7 maps | 3.99 GB | .vpk
                                "9mar21/maps"],  # 7 maps | 4.04 GB | .vpk
        # season9:  Legacy  [4th May 2021]
        "ApexLegends/season9": ["4may21/depot/r5-90/game/r2/maps",  # 7 maps | 2.65 GB | .vpk
                                "4may21/maps",  # 7 maps | 2.69 GB | .vpk
                                "29jun21/depot/r5-90/game/r2/maps",  # 7 maps | 2.65 GB | .vpk
                                "29jun21/depot/r5-91/game/r2/maps",  # 10 maps | 4.27 GB | .vpk
                                "29jun21/maps"],  # 10 maps | 4.33 GB | .vpk
        # season10:  Emergence  [3rd Aug 2021]
        "ApexLegends/season10": ["3aug21/maps",  # 2 maps | 813 MB | .vpk
                                 "10aug21/maps",  # 8 maps | 2.8 GB | .vpk
                                 "10aug21/depot/r5-100/game/r2/maps",  # 8 maps | 2.8 GB | .vpk
                                 "14sep21/maps",  # 2 maps | 962 MB | .vpk
                                 "14sep21/depot/r5-100/game/r2/maps",  # 1 map | 797 MB | .vpk
                                 "14sep21/depot/r5-101/game/r2/maps",  # 2 maps | 949 MB | .vpk
                                 "24sep21/maps",  # 1 maps | 4 MB | .vpk
                                 "24sep21/depot/r5-100/game/r2/maps",  # 1 maps | 3 MB | .vpk
                                 "24sep21/depot/r5-101/game/r2/maps"],  # 1 maps | 3 MB | .vpk
        # season11:  Escape  [2nd Nov 2021]
        "ApexLegends/season11": ["2nov21/maps",  # 1 map | 10 MB | .vpk
                                 "2nov21/depot/r5-110/game/r2/maps",  # 1 map | 9 MB | .vpk
                                 "5nov21/maps",  # 1 map | 760 MB | .vpk
                                 "5nov21/depot/r5-110/game/r2/maps",  # 1 map | 749 MB | .vpk
                                 "17nov21/maps",  # 10 maps | 1.5 GB | .vpk
                                 "17nov21/depot/r5-110/game/r2/maps",  # 8 maps | 2.1 GB | .vpk
                                 "17nov21/depot/r5-111/game/r2/maps"],  # 10 maps | 1.4 GB | .vpk
        # TODO: season11.1 Raiders [7th Dec 2021]
        # season12:  Defiance [9th Feb 2022]
        "ApexLegends/season12": ["8feb22/maps",  # 11 maps | 1.91 GB | .vpk
                                 "8feb22/depot/r5-120/game/r2/maps",  # 11 maps | 1.86 GB | .vpk
                                 "29mar22/maps",  # 11 maps | 1.89 GB | .vpk
                                 "29mar22/depot/r5-120/game/r2/maps",  # 10 maps | 1.77 GB | .vpk
                                 "29mar22/depot/r5-121/game/r2/maps"],  # 11 maps | 1.84 GB | .vpk
        # season13:  Saviour [10th May 2022]
        "ApexLegends/season13": ["10may22/maps",  # 11 maps | 1.91 GB | .vpk
                                 "10may22/depot/r5-130/game/r2/maps",  # 11 maps | 1.86 GB | .vpk
                                 "21jun22/maps",  # 11 maps | 1.88 GB | .vpk
                                 "21jun22/depot/r5-130/game/r2/maps",  # 10 maps | 1.79 GB | .vpk
                                 "21jun22/depot/r5-131/game/r2/maps"],  # 11 maps | 1.82 GB | .vpk
        # season14:  Hunted [9th Aug 2022]
        "ApexLegends/season14": ["9aug22/maps",  # 11 maps | 1.85 GB | .vpk
                                 "9aug22/depot/r5-140/game/r2/maps",  # 11 maps | 1.80 GB | .vpk
                                 "20sep22/maps",  # 12 maps | 1.97 GB | .vpk
                                 "20sep22/depot/r5-140/game/r2/maps",  # 9 maps | 1.38 GB | .vpk
                                 "20sep22/depot/r5-141/game/r2/maps",  # 12 maps | 1.92 GB | .vpk
                                 "14oct22/maps",  # 2 maps | 400 MB | .vpk
                                 "14oct22/depot/r5-140/game/r2/maps",  # 1 map | 5.62 MB | .vpk
                                 "14oct22/depot/r5-141/game/r2/maps"],  # 2 maps | 387 MB | .vpk
        # season15:  Eclipse [1st Nov 2022]
        "ApexLegends/season15": ["1nov22/maps",  # 12 maps | 2.24 GB | .vpk
                                 "1nov22/depot/r5-150/game/r2/maps",  # 12 maps | 2.17 GB | .vpk
                                 "10jan23/maps",  # 2 maps | 395 MB | .vpk
                                 "10jan23/depot/r5-150/game/r2/maps"],  # 2 maps | 382 MB | .vpk
        # season16:  Revelry [14th Feb 2023]
        "ApexLegends/season16": ["14feb23/maps",  # 9 maps | 1.72 GB | .vpk
                                 "14feb23/depot/r5-160/game/r2/maps",  # 9 maps | 1.67 GB | .vpk
                                 "28mar23/maps",  # 11 maps | 2.19 GB | .vpk
                                 "28mar23/depot/r5-160/game/r2/maps",  # 9 maps | 1.67 GB | .vpk
                                 "28mar23/depot/r5-161/game/r2/maps"],  # 10 maps | 2.04 GB | .vpk
        # season17:  Arsenal [9th May 2023]
        "ApexLegends/season17": ["9may23/maps",  # 10 maps | 1.80 GB | .vpk
                                 "9may23/depot/r5-170/game/r2/maps",  # 10 maps | 1.74 GB | .vpk
                                 "20jun23/maps",  # 14 maps | 2.81 GB | .vpk
                                 "20jun23/depot/r5-170/game/r2/maps",  # 10 maps | 1.74 GB | .vpk
                                 "20jun23/depot/r5-171/game/r2/maps",  # 11 maps | 2.21 GB | .vpk
                                 "19jul23/maps",  # 2 maps | 169 MB | .vpk
                                 "19jul23/depot/r5-170/game/r2/maps",  # 1 map | 6 MB | .vpk
                                 "19jul23/depot/r5-171/game/r2/maps"],  # 2 maps | 168 MB | .vpk
        # TODO: extract all .rpak maps now that we have tools
        # season18:  Resurrection [8th Aug 2023]
        "ApexLegends/season18": ["8aug23/maps",  # 9 maps | 1.91 GB | .rpak
                                 "19sep23/maps"],  # 13 maps | 2.96 GB | .rpak
        # season19:  Ignite [31st October 2023]
        "ApexLegends/season19": ["1feb24/maps"],  # 11 maps | 2.26 GB | .rpak
        # season20:  Breakout [13th February 2024]
        "ApexLegends/season20": ["13feb24/maps"],  # 7 maps | 1.30 GB | .rpak
        # season21:  Upheaval [7th May 2024]
        "ApexLegends/season21": ["7may24/maps"],  # 8 maps | 1.61 GB | .rpak
        # season22:  Shockwave [6th August 2024]
        # TODO: season22/6aug24
        "ApexLegends/season22": ["30aug24/maps"],  # 9 maps | 1.63 GB | .rpak
        # RitualBsp
        "FAKK2": ["maps",  # 30 maps | 150 MB | .pk3
                  "download/maps"],  # 6 maps | 25 MB | .pk3
        "Alice": ["maps",  # 42 maps | 196 MB | .pk3 (includes maps from demo)
                  "download/maps"],  # 1 map | 61 KB | .pk3
        # https://archive.org/details/MedalOfHonourAlliedAssaultSinglePlayer
        "MoHAA/demo": ["Pak5.pk3/maps"],  # 2 maps | 10 MB | .pk3
        # NOTE: we don't test credits.bsp.old
        "MoHAA/main": ["Pak5.pk3/maps",  # 37 maps | 298 MB | .pk3
                       "Pak5.pk3/maps/briefing",  # 6 maps | 319 KB | .pk3
                       "Pak5.pk3/maps/DM",  # 7 maps | 48 MB | .pk3
                       "Pak5.pk3/maps/obj"],  # 4 maps | 36 MB | .pk3
        # DLC 1: Spearhead
        "MoHAA/mainta": ["pak1.pk3/maps",  # 19 maps | 255 MB | .pk3
                         "pak1.pk3/maps/briefing",  # 5 maps | 276 MB | .pk3
                         "pak1.pk3/maps/DM",  # 8 maps | 64 MB | .pk3
                         "pak1.pk3/maps/obj",  # 4 maps | 63 MB | .pk3
                         "pak3.pk3/maps",  # 9 maps | 136 MB | .pk3
                         "pak3.pk3/maps/DM",  # 4 maps | 39 MB | .pk3
                         "pak3.pk3/maps/obj"],  # 3 maps | 48 MB | .pk3
        # DLC 2: Breakthrough
        "MoHAA/maintt": ["pak1.pk3/maps",  # 22 maps | 288 MB | .pk3
                         "pak1.pk3/maps/briefing",  # 5 maps | 276 MB | .pk3
                         "pak1.pk3/maps/DM",  # 8 maps | 64 MB | .pk3
                         "pak1.pk3/maps/obj",  # 4 maps | 63 MB | .pk3
                         "pak3.pk3/maps",  # 2 maps | 28 MB | .pk3
                         "pak3.pk3/maps/lib",  # 2 maps | 21 MB | .pk3
                         "pak3.pk3/maps/obj"],  # 3 maps | 32 MB | .pk3
        "StarTrekEliteForceIIDemo": ["maps"],  # 2 maps | 32 MB | .pk3
        "StarTrekEliteForceII": ["maps",  # 88 maps | 607 MB | .pk3
                                 "download/maps"],  # 188 maps | 886 MB | .pk3
        "StarWarsJediKnight": ["assets0.pk3/maps",  # 34 maps | 348 MB | .pk3
                               "assets0.pk3/maps/mp",  # 23 maps | 154 MB | .pk3
                               "assets3.pk3/maps/mp"],  # 4 maps | 32 MB | .pk3
        "StarWarsJediKnightII": ["maps"],  # 45 maps | 361 MB | .pk3
        # Genesis3DBsp
        "Amsterdoom": ["Levels"]}  # 23 maps | 76.2 MB | .iso
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
                      "episodeone",  # 15 maps | 268 MB | Map Labs 2 + Test Tube 15
                      "RunThinkShootLiveVille2",  # 19 maps | 728 MB | Map Labs 3
                      "cromulentville2",  # 21 maps | 342 MB | Test Tube 7
                      "companionpiece2",  # 18 maps | 429 MB | Map Labs 8
                      "eyecandy",   # 41 maps | 652 MB | Test Tube 8
                      "backontrack",  # 32 maps | 787 MB | Map Labs 9
                      "tworooms",  # 39 maps | 496 MB | Test Tube 9
                      "fusionville2",  # 21 maps | 391 MB | Map Labs 10
                      "tunetwo",  # 12 maps | 114 MB | Test Tube 13
                      "lvl2",  # 14 maps | 461 MB | Map Labs 15
                      "thewrapuptwo",  # 27 maps | 226 MB | Test Tube 15
                      "halloweenhorror4",  # 25 maps | 274 MB | Map Labs 16
                      "halflifeeternal",  # 13 maps | 123 MB | Test Tube 16
                      "thelayout"]}  # 13 maps | 356 MB | Map Labs 17

# consoles
dreamcast_dirs = {"Paranoia": ["maps"],  # 54 maps | 77 MB | .cdi
                  "SoF": ["maps"],  # 117 maps | 171 MB | .gdi
                  "QuakeIII": ["maps"]}  # 38 maps | 64 MB | .zip
# extracted with the help of Taskinoz
ps4_dirs = {"Titanfall2": ["maps",  # 24 maps | 10.6 GB | .vpk
                           "depot/r2dlc3/game/r2/maps",  # 1 map | 764 MB | .vpk
                           "depot/r2dlc4/game/r2/maps",  # 1 map | 764 MB | .vpk
                           "depot/r2dlc5/game/r2/maps",  # 1 map | 764 MB | .vpk
                           "depot/r2dlc6/game/r2/maps",  # 1 map | 764 MB | .vpk
                           "depot/r2dlc7/game/r2/maps",  # 1 map | 764 MB | .vpk
                           "depot/r2dlc8/game/r2/maps",  # 1 map | 764 MB | .vpk
                           "depot/r2dlc9/game/r2/maps",  # 1 map | 764 MB | .vpk
                           "depot/r2dlc10/game/r2/maps",  # 1 map | 764 MB | .vpk
                           "depot/r2dlc11/game/r2/maps",  # 1 map | 764 MB | .vpk
                           "depot/r2pcprecert/game/r2/maps",  # 1 map | 764 MB | .vpk
                           "depot/r2ps4precert/game/r2/maps",  # 24 maps | 10.5 GB | .vpk
                           "depot/r2staging/game/r2/maps"],  # 1 map | 764 MB | .vpk
            # CUSA05988 R2PS4_TechTest_24 (v2.0.0.24)
            "Titanfall2_tech_test": ["maps",  # 5 maps | 1.14 GB | .vpk
                                     "depot/r2tt/game/r2/maps"]}  # 5 maps | 1.14 GB | .vpk
# TODO: ApexLegends/season8-present
switch_dirs = {"ApexLegends/season9": ["maps",  # 7 maps | 2.4 GB | .vpk
                                       "depot/r5-90/game/r2/maps"]}  # 7 maps | 2.3 GB | .vpk
xbox_dirs = {"Half-Life2": ["GameMedia/maps"]}  # 90 maps | 415 MB | .iso
# extracted from xisos; a very painful process
# TODO: CS:GO, DarkMessiah: Elements, Titanfall
# -- DarkMessiah of Might & Magic Elements maps are in .bf / .bfm files / archives?
# -- file data is unknown, might require significant reverse engineering to extract .bsps, if possible
# -- Titanfall maps are in .bpk files, decrypter (TitanfallVPKTool) has a buffer limit so files are incomplete
x360_dirs = {"Left4Dead": ["left4dead/maps"],  # 44 maps | 295 MB
             "Left4Dead2": ["left4dead2/maps"],  # 23 maps | 196 MB
             "OrangeBox": ["ep2/maps",  # 22 maps | 134 MB
                           "episodic/maps",  # 18 maps | 121 MB
                           "hl2/maps",  # 76 maps | 376 MB
                           "portal/maps",  # 26 maps | 99 MB
                           "tf/maps"],  # 7 maps | 88 MB
             "Portal2": ["portal2/maps"]}  # 105 maps | 532 MB

# NOTE: ls $group_dir+$game_dir+$maps_dir
group_dirs = {"C:/Program Files (x86)/Steam/steamapps/sourcemods": sourcemod_dirs,
              "D:/SteamLibrary/steamapps/common": {**goldsrc_dirs, **source_dirs},
              "E:/Mod": extracted_dirs,
              # console groups
              "E:/Mod/Dreamcast": dreamcast_dirs,
              "E:/Mod/PS4": ps4_dirs,
              "E:/Mod/Switch": switch_dirs,
              "E:/Mod/Xbox": xbox_dirs,
              "E:/Mod/X360": x360_dirs,
              # backup dirs; created with backup_bsps.py
              # "F:/bsps": every_bsp_dir,
              # "/media/bikkie/GAMES/bsps": every_bsp_dir
              }

# registering tests/maps first
installed_games = {("./tests/maps", game): [""] for game in os.listdir("./tests/maps/") if game != "Xbox360"}
installed_games.update({("./tests/maps", "Call of Duty 4"): ["", "mp"]})
installed_games.update({("./tests/maps", f"Xbox360/{game}"): [""] for game in os.listdir("./tests/maps/Xbox360")})
installed_games.pop(("./tests/maps", "Xbox360/The Orange Box"))  # failing
# add only the installed games from each group to tests
for group, games in group_dirs.items():
    if os.path.exists(group):
        for game, map_dirs in games.items():
            if os.path.exists(os.path.join(group, game)):
                installed_games[(group, game)] = map_dirs
