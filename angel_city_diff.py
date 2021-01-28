# 64bit python only! these files are big!
import bsp_tool


ported_maps = {"mp_angel_city": "mp_angel_city",
               "mp_colony": "mp_colony",
               "mp_relic": "mp_relic02",
               "mp_wargames": "mp_wargames"}


for r1_filename, r2_filename in ported_maps.items():
    print(r1_filename)
    r1_map = bsp_tool.load_bsp(f"E:/Mod/Titanfall/maps/{r1_filename}.bsp", "Titanfall 2")
    r2_map = bsp_tool.load_bsp(f"E:/Mod/Titanfall2/maps/{r2_filename}.bsp")

    # TODO: compare headers
    for lump in bsp_tool.branches.respawn.titanfall2.LUMP:
        print(f"{lump.value:04X}  {lump.name}")
        print("\t", r1_map.HEADERS[lump.name])
        print("\t", r2_map.HEADERS[lump.name])
        # size differences?
        # unused by engine version?
        # compare first index if not raw
    # TODO: compare .MODELS[0]
    # TODO: compare .TEXDATA_STRING_DATA
    # TODO: compare unused lumps

    del r1_map, r2_map
    print("=" * 80)
