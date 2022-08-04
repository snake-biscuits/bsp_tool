# import fnmatch
import os

import bsp_tool


# STEAM_DIR = "D:/SteamLibrary/steamapps/common"
# SFM = "SourceFilmmaker/game/tf/maps"
# TF2 = "Team Fortress 2/tf/download/maps"

MOD_DIR = "E:/Mod"
VIND = "Vindictus/maps"

# X360_DIR = "E:/Mod/X360"
# L4D = "Left4Dead/left4dead/maps"
# P2 = "Portal2/portal2/maps"

maps = {
        # (STEAM_DIR, SFM): ["ctf_foundry.bsp",
        #                    "ctf_gorge.bsp",
        #                    "koth_lakeside_event.bsp",
        #                    "pl_cactuscanyon.bsp",
        #                    "pl_upward.bsp",
        #                    "rd_asteroid.bsp",
        #                    "sd_doomsday_event.bsp"],  # 7 / 71
        # (STEAM_DIR, TF2): ["arena_idolon_mc18_a1.bsp",
        #                    "bananaland_rc5a.bsp",
        #                    "cp_e1m1mountainlab.bsp",
        #                    "cp_ismac_mc18_a1.bsp",
        #                    "cp_ismac_mc18_a2.bsp"],  # 5 / 514
        (MOD_DIR, VIND): ["17e.bsp",
                          "17e_ending.bsp",
                          "3_24_ending.bsp",
                          "arisha_teaser.bsp",
                          "arisha_teaser_b.bsp",
                          "h03_cut_b.bsp",
                          "lobby_beautyshop_body.bsp",
                          "lobby_beautyshop_cichol.bsp",
                          "lobby_showcase_ari_runway_01.bsp",
                          "lobby_showcase_ari_runway_02.bsp",
                          "lobby_showcase_ari_runway_03.bsp",
                          "lobby_showcase_ari_runway_04.bsp",
                          "lobby_showcase_ari_runway_05.bsp",
                          "lobby_showcase_runway_chinatube.bsp",
                          "lobby_showcase_silhouette.bsp",
                          "lobby_showcase_silhouette_ari.bsp",
                          "s3_game_create_character.bsp"],  # 17 / 474
        # (X360_DIR, L4D): [fn for fn in fnmatch.filter(os.listdir(os.path.join(X360_DIR, L4D)), "*.bsp")
        #                   if fn not in ("credits.360.bsp", "l4d_airport02_offices.360.bsp")],  # 42 / 44
        # (X360_DIR, P2): [*fnmatch.filter(os.listdir(os.path.join(X360_DIR, P2)), "*.bsp")]  # 105 / 105
       }

bsps = {
        # (STEAM_DIR, SFM): [],
        # (STEAM_DIR, TF2): [],
        (MOD_DIR, VIND): [],
        # (X360_DIR, L4D): [],
        # (X360_DIR, P2): []
       }

for group_dir, game_dir in maps:
    map_list = maps[(group_dir, game_dir)]
    if __name__ == "__main__":
        print(game_dir.split("/")[0])
    for map_name in map_list:
        bsp = bsp_tool.load_bsp(os.path.join(group_dir, game_dir, map_name))
        bsps[(group_dir, game_dir)].append(bsp)
        if __name__ == "__main__":
            print("\t", f"{map_name:<40}", ", ".join([f"{k} v{bsp.headers[k].version}" for k in bsp.loading_errors]),
                  ", ".join([f"{k} {bsp.GAME_LUMP.headers[k].version}" for k in bsp.GAME_LUMP.loading_errors]))
