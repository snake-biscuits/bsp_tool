import fnmatch
import pytest

from . import files

from bsp_tool.archives.id_software import Pak
from bsp_tool.branches.id_software import quake
from bsp_tool.id_software import QuakeBsp


pak_dirs: files.LibraryGames
pak_dirs = {
    "Steam": {
        "Quake": ["Quake/Id1"]}}

library = files.game_library()
paks = {
    f"{section} | {game} | {short_path}": Pak.from_file(full_path)
    for section, game, paths in library.scan(pak_dirs, "*.PAK")
    for short_path, full_path in paths}

pak_bsps = {
    f"{pak_id} | {bsp_path}": (pak, bsp_path)
    for pak_id, pak in paks.items()
    for bsp_path in fnmatch.filter(pak.namelist(), "*.bsp")}


@pytest.mark.parametrize("pak,bsp_path", pak_bsps.values(), ids=pak_bsps.keys())
def test_from_archive(pak: Pak, bsp_path: str):
    bsp = QuakeBsp.from_archive(quake, bsp_path, pak)
    assert bsp.loading_errors == dict()
