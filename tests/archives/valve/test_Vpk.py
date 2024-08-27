import fnmatch
import os
import socket  # gethostname

import pytest

from bsp_tool.archives import valve


steam_common = "D:/SteamLibrary/steamapps/common/"
vpk_dirs = {
    "Black Mesa": "bms/",
    "Bloody Good Time": "vpks/",
    "Contagion": "vpks/",
    "Dark Messiah Might and Magic Single Player": "vpks/",
    "Dark Messiah Might and Magic Multi-Player": "vpks/",
    "SiN Episodes Emergence": "vpks/",
    "The Ship": "vpks/",
    "The Ship Single Player": "vpks/",
    "The Ship Tutorial": "vpks/"}
# NOTE: Dark Messiah Singleplayer | depot_2109_dir.vpk is empty
# -- https://steamdb.info/depot/2109/ (mm_media)
# NOTE: The Ship | depot_2402_dir.vpk contains "umlaut e" b"\xEB" (latin_1)
# -- https://steamdb.info/depot/2402/ (The Ship Common)

# APEX ARCHIVE ARCHIVIST LOGIN
aliases = {"Jared@ITANI_WAYSOUND": "bikkie"}

user = os.getenv("USERNAME", os.getenv("USER"))
host = os.getenv("HOSTNAME", os.getenv("COMPUTERNAME", socket.gethostname()))
user = aliases.get(f"{user}@{host}", user)

archivists = {
    ("bikkie", "ITANI_WAYSOUND"): "D:/SteamLibrary/steamapps/common/"}

vpks = dict()
if (user, host) in archivists:
    steam_common = archivists[(user, host)]
    for game, vpk_dir in vpk_dirs.items():
        vpk_dir = os.path.join(steam_common, game, vpk_dir)
        for vpk_filename in fnmatch.filter(os.listdir(vpk_dir), "*_dir.vpk"):
            full_path = os.path.join(vpk_dir, vpk_filename)
            vpks[f"{game} | {vpk_filename}"] = full_path


@pytest.mark.parametrize("filename", vpks.values(), ids=vpks.keys())
def test_Vpk_from_file(filename: str):
    vpk = valve.Vpk.from_file(filename)
    assert isinstance(vpk.namelist(), list)
    # TODO: try a read
