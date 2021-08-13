import fnmatch
import os
import shutil

import humanize  # PyPI humanize 3.11.0


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
         "Team Fortress 2": ["tf/maps", "tf/download/maps"]}
# ^ {"game_dir": ["map_dir"]}

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
        "BlackMesa": ["maps"],  # .vpk
        "CSO2": ["maps"],  # .vpk (Counter-Strike: Online 2 [NEXON])
        "TacInt": ["maps"],  # Tactical Intervention (unlisted on Steam)
        # RespawnBsp
        "Titanfall": ["maps"],  # .vpk
        "TitanfallOnline": ["maps"],  # .pkg
        "Titanfall2": ["maps"],
        "ApexLegends": ["maps", "maps/Season 2", "maps/Season 3", "maps/Season 5",
                        "maps/Season 8", "maps/Season 9", "maps/Season 10"]}
# ^ {"game_dir": ["map_dir"]}

sourcemod_dirs = {"companionpiece2": ["maps"],  # Map Labs #8 - Companion Piece 2: Companion Harder
                  "cromulentville2": ["maps"],  # Test Tube #7 - CromulentVille 2
                  "episodeone": ["maps"],  # Map Labs #2: Episode One
                  "eyecandy": ["maps"],  # Test Tube #8 - Eye Candy
                  "gesource": ["maps"],  # GoldenEye: Source
                  "RunThinkShootLiveVille2": ["maps"],  # Map Labs #3 - RunThinkShootLiveVille 2
                  "tworooms": ["maps"]}  # Test Tube #9 - Two Rooms


if __name__ == "__main__":
    steam_dirs = {"C:/Program Files (x86)/Steam/steamapps/sourcemods": sourcemod_dirs,
                  "E:/Mod": extracted_dirs,
                  "D:/SteamLibrary/steamapps/common": {**goldsrc_dirs, **source_dirs}}
    total_size = 0
    for steam_dir, game_dirs in steam_dirs.items():
        print("GROUP:", steam_dir)
        for game, map_dirs in game_dirs.items():
            for folder in map_dirs:
                _f = folder
                folder = os.path.join(steam_dir, game, folder)
                maps = fnmatch.filter(os.listdir(os.path.join(steam_dir, game, folder)), "*bsp")
                size = sum([os.path.getsize(os.path.join(folder, m)) for m in maps])
                total_size += size
                print(f"{game}/{folder}:",
                      f"{len(maps)} map{'s' if len(maps) > 0 else ''} | {humanize.naturalsize(size)}", sep="\n")
                os.makedirs(os.path.join("F:/bsps", game, _f), exist_ok=True)
                for m in maps:
                    shutil.copyfile(os.path.join(folder, m),
                                    os.path.join("F:/bsps", game, _f, m))
        print()
    print(humanize.naturalsize(total_size))
