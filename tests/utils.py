import collections
import fnmatch
import os
import socket  # gethostname
from types import ModuleType
from typing import Dict, List

from bsp_tool.base import Bsp


BranchDirs = Dict[ModuleType, List[str]]
# ^ {branch_script: ["Game"]}

test_maps_dir = os.path.join(os.getcwd(), "tests/maps")
# TODO: we can't safely assume cwd() is tests/../
# -- use __file__ to get the test maps dir instead

ArchiveDirs = collections.namedtuple("ArchiveDirs", ["steam_dir", "mod_dir"])

archivist_aliases = {"Jared@ITANI_WAYSOUND": "bikkie"}

archivists = {
    # Windows Desktop
    ("bikkie", "ITANI_WAYSOUND"): ArchiveDirs(
        "D:/SteamLibrary/steamapps/common/",
        "E:/Mod/"),
    # Linux Laptop
    ("bikkie", "coplandbentokom-9876"): ArchiveDirs(
        None,
        "/media/bikkie/3964-39352/Mod/")}


def archive_available() -> bool:
    return archivist_login() in archivists


def archive_dirs() -> ArchiveDirs:
    return archivists.get(archivist_login(), ArchiveDirs(*[None] * 2))


def archivist_login() -> (str, str):
    user = os.getenv("USERNAME", os.getenv("USER"))
    host = os.getenv("HOSTNAME", os.getenv("COMPUTERNAME", socket.gethostname()))
    user = archivist_aliases.get(f"{user}@{host}", user)
    return (user, host)


# TODO: include maplist.installed_games test_maps
# -- should use archivists[archivist_login()] to get dirs
# -- will require a refactor of maplist
# -- megatest spec lists would be really handy too
def get_test_maps(BspClass: Bsp, branch_dirs: BranchDirs, pattern: str = "*.bsp") -> Dict[str, Bsp]:
    bsps = dict()
    for branch in branch_dirs:
        for map_dir in branch_dirs[branch]:
            full_map_dir = os.path.join(test_maps_dir, map_dir)
            for map_name in fnmatch.filter(os.listdir(full_map_dir), pattern):
                map_path = os.path.join(map_dir, map_name).replace("\\", "/")
                bsps[map_path] = BspClass.from_file(branch, os.path.join(test_maps_dir, map_path))
    return bsps
