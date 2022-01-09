import fnmatch
import os
import shutil

import bsp_tool
from tests.maplist import installed_games


log_paths = {"r1_logs": ("E:/Mod", "Titanfall"),
             "r1o_logs": ("E:/Mod", "TitanfallOnline"),
             "r2_logs": ("E:/Mod", "Titanfall2"),
             "r5_logs": ("E:/Mod", "ApexLegends")}

for log_dir, base_dir in log_paths.items():
    map_dirs = installed_games[base_dir]
    for map_dir in map_dirs:
        full_map_dir = os.path.join(*base_dir, map_dir)
        print(f"Searching {full_map_dir} ...")
        for map_name in fnmatch.filter(os.listdir(full_map_dir), "*.bsp"):
            bsp = bsp_tool.load_bsp(os.path.join(full_map_dir, map_name))
            if not hasattr(bsp, "PAKFILE"):
                continue
            # print all file extensions
            # extensions = sorted({os.path.splitext(f)[1] for f in bsp.PAKFILE.namelist()})
            # print(f"  {bsp.filename:<32s} {' '.join(extensions)}")
            logs = fnmatch.filter(bsp.PAKFILE.namelist(), "*.txt")
            for log_file in logs:
                print(f"Extracting {log_file} from {bsp.filename} ...")
                bsp.PAKFILE.extract(log_file, path=log_dir)
                ext_filename = os.path.join(log_dir, log_file)
                ext_dir, ext_file = os.path.split(ext_filename)
                new_filename = os.path.join(ext_dir, f"{map_dir.replace('/', '.')}.{ext_file}")
                shutil.move(ext_filename, new_filename)
                print(f"\-> Renamed to {new_filename}")
