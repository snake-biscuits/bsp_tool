import fnmatch
import os
from types import ModuleType
from typing import Dict, List

from bsp_tool.base import Bsp


BranchDirs = Dict[ModuleType, List[str]]


# TODO: include maplist.installed_games test_maps
def get_test_maps(BspClass: Bsp, branch_dirs: BranchDirs, pattern: str = "*.bsp") -> List[Bsp]:
    bsps = list()
    for branch in branch_dirs:
        for map_dir in branch_dirs[branch]:
            map_dir = os.path.join(os.getcwd(), "tests/maps", map_dir)
            for map_name in fnmatch.filter(os.listdir(map_dir), pattern):
                bsps.append(BspClass(branch, os.path.join(map_dir, map_name)))
    return bsps
