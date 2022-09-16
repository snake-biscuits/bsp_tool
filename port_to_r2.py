if __name__ == "__main__":
    import fnmatch
    import os

    import bsp_tool
    from bsp_tool.extensions import upgrade

    r1o_md = "E:/Mod/TitanfallOnline/maps"
    outdir = r"D:\SteamLibrary\steamapps\common\Titanfall2\R2Northstar\mods\bikkie.TFOnlineMaps\mod\maps"
    for map_name in fnmatch.filter(os.listdir(r1o_md), "*.bsp"):
        bsp = bsp_tool.load_bsp(os.path.join(r1o_md, map_name))
        print(f"upgrading {map_name}...")
        upgrade.r1_to_r2(bsp, outdir)
