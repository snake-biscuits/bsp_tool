"""Run with 64-bit python! Respawn .bsp files are large!"""
import os

from bsp_tool import RespawnBsp
from bsp_tool.branches.respawn import titanfall, titanfall2


ported_maps = [("mp_angel_city", "mp_angel_city"),
               ("mp_colony", "mp_colony02"),
               ("mp_relic", "mp_relic02"),
               ("mp_rise", "mp_rise"),
               ("mp_wargames", "mp_wargames")]


r1_relic = RespawnBsp(titanfall, "E:/Mod/Titanfall/maps/mp_relic.bsp")
r1o_relic = RespawnBsp(titanfall, "E:/Mod/TitanfallOnline/maps/mp_relic.bsp")

for lump in titanfall.LUMP:
    r1_header = r1_relic.HEADERS[lump.name]
    r1o_header = r1o_relic.HEADERS[lump.name]
    print(f"{lump.name}", end="  ")
    print("Y" if r1_header.offset == r1o_header.offset else "N", end="")
    print("Y" if r1_header.length == r1o_header.length else "N", end="")
    print("Y" if r1_header.version == r1o_header.version else "N", end="")
    print("Y" if r1_header.fourCC == r1o_header.fourCC else "N", end="  ")

    if hasattr(r1_relic, f"RAW_{lump.name}"):
        print("YES!" if getattr(r1_relic, f"RAW_{lump.name}") == getattr(r1o_relic, f"RAW_{lump.name}") else "NOPE")
    elif hasattr(r1_relic, lump.name):
        print("YES!" if getattr(r1_relic, lump.name) == getattr(r1o_relic, lump.name) else "NOPE")
    else:
        print("????")

for ent_file in ["ENTITIES_env", "ENTITIES_fx", "ENTITIES_script", "ENTITIES_snd", "ENTITIES_spawn"]:
    print(ent_file, end="  ")
    print("YES!" if getattr(r1_relic, ent_file) == getattr(r1o_relic, ent_file) else "NOPE")


# for r1_filename, r2_filename in ported_maps:
#     print(r1_filename.upper())
#     r1_map = RespawnBsp(titanfall, f"E:/Mod/Titanfall/maps/{r1_filename}.bsp")
#     r1o_map = RespawnBsp(titanfall, f"E:/Mod/TitanfallOnline/maps/{r1_filename}.bsp")
#     # r2_map = RespawnBsp(titanfall2, f"E:/Mod/Titanfall2/maps/{r2_filename}.bsp")
#
#     if not os.path.exists(f"E:/Mod/TitanfallOnline/maps/{r1_filename}.bsp"):
#         continue  # need to test r1o maps against r1
#     for i in range(128):
#         r1_lump = titanfall.LUMP(i)
#         r2_lump = titanfall2.LUMP(i)
#
#         print(r1_lump.name)
#         r1_header = r1_map.HEADERS[r1_lump.name]
#         r1o_header = r1o_map.HEADERS[r1_lump.name]
#         if r1o_header.offset - r1_header.offset == 1684:
#             print(True)
#         else:
#             print(False, r1o_header.offset - r1_header.offset)
        # TODO: skip empty lumps
        # print(f"{r1_lump.value:04X}  {r1_lump.name}")
        # print(f"{'r1':<8}", r1_map.HEADERS[r1_lump.name])
        # if os.path.exists(f"E:/Mod/TitanfallOnline/maps/{r1_filename}.bsp"):
        #     print(f"{'r1o':<8}", r1o_map.HEADERS[r1_lump.name])
        # print(f"{'r2':<8}", r2_map.HEADERS[r2_lump.name])

    # del r1_map, r1o_map  # , r2_map
    # print("=" * 80)
