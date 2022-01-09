import fnmatch
import os

import bsp_tool
from tests.maplist import installed_games


log_paths = {"r1_logs": ("E:/Mod", "Titanfall"),
             "r1o_logs": ("E:/Mod", "TitanfallOnline"),
             "r2_logs": ("E:/Mod", "Titanfall2"),
             "r5_logs": ("E:/Mod", "ApexLegends")}

for log_dir, base_dir in log_paths.items():
    map_dirs = installed_games[base_dir]
    for map_dir in map_dirs:
        map_dir = os.path.join(*base_dir, map_dir)
        print(f"Searching {map_dir} ...")
        for map_name in fnmatch.filter(os.listdir(map_dir), "*.bsp"):
            bsp = bsp_tool.load_bsp(os.path.join(map_dir, map_name))
            if not hasattr(bsp, "PAKFILE"):
                continue
            logs = fnmatch.filter(bsp.PAKFILE.namelist(), "*.txt")
            for logfile in logs:
                print(f"Extracting {logfile} from {bsp.filename} ...")
                bsp.PAKFILE.extract(logfile, path=log_dir)
