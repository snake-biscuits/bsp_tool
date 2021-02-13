"""Run with 64-bit python! Respawn .bsp files are large!"""
from bsp_tool import RespawnBsp
from bsp_tool.branches.respawn import titanfall, titanfall2


ported_maps = [("mp_angel_city", "mp_angel_city"),
               ("mp_colony", "mp_colony02"),
               ("mp_relic", "mp_relic02"),
               ("mp_rise", "mp_rise"),
               ("mp_wargames", "mp_wargames")]


for r1_filename, r2_filename in ported_maps:
    print(r1_filename.upper())
    r1_map = RespawnBsp(titanfall, f"E:/Mod/Titanfall/maps/{r1_filename}.bsp")
    r1o_map = RespawnBsp(titanfall, f"E:/Mod/TitanfallOnline/maps/{r1_filename}.bsp")
    r2_map = RespawnBsp(titanfall2, f"E:/Mod/Titanfall2/maps/{r2_filename}.bsp")

    # TODO: compare headers
    for lump in titanfall2.LUMP:
        print(f"{lump.value:04X}  {lump.name}")
        print(f"{'r1':<8}", r1_map.HEADERS[lump.name])
        print(f"{'r1o':<8}", r1o_map.HEADERS[lump.name])
        print(f"{'r2':<8}", r2_map.HEADERS[lump.name])
        # size differences?
        # unused by engine version?
        # compare first index if not raw
    # TODO: compare .MODELS[0]
    # TODO: compare .TEXDATA_STRING_DATA
    # TODO: compare unused lumps
    # TODO: list import errors by game version

    del r1_map, r1o_map, r2_map
    print("=" * 80)
