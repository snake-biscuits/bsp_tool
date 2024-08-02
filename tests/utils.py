import fnmatch
import os
from types import ModuleType
from typing import Dict, List

from bsp_tool.base import Bsp


BranchDirs = Dict[ModuleType, List[str]]
# ^ {branch_script: ["Game"]}

test_maps_dir = os.path.join(os.getcwd(), "tests/maps")


# TODO: include maplist.installed_games test_maps
def get_test_maps(BspClass: Bsp, branch_dirs: BranchDirs, pattern: str = "*.bsp") -> Dict[str, Bsp]:
    bsps = dict()
    for branch in branch_dirs:
        for map_dir in branch_dirs[branch]:
            full_map_dir = os.path.join(test_maps_dir, map_dir)
            for map_name in fnmatch.filter(os.listdir(full_map_dir), pattern):
                map_path = os.path.join(map_dir, map_name).replace("\\", "/")
                bsps[map_path] = BspClass.from_file(branch, os.path.join(test_maps_dir, map_path))
    return bsps
