import pytest

from bsp_tool.archives import ritual

from ... import files


sin_dirs: files.LibraryGames
sin_dirs = {
    "Steam": {
        "SiN (2015)": ["SiN 1/2015"],
        "SiN (base)": ["SiN 1/base"],
        "SiN (ctf)": ["SiN 1/ctf"],
        "SiN Multiplayer (2015)": ["SiN 1 Multiplayer/2015"],
        "SiN Multiplayer (base)": ["SiN 1 Multiplayer/base"],
        "SiN Multiplayer (ctf)": ["SiN 1 Multiplayer/ctf"]}}


library = files.game_library()
paks = {
    f"{section} | {game} | {short_path}": full_path
    for section, game, paths in library.scan(sin_dirs, "*.sin")
    for short_path, full_path in paths}


@pytest.mark.parametrize("filename", paks.values(), ids=paks.keys())
def test_from_file(filename: str):
    pak = ritual.Sin.from_file(filename)
    namelist = pak.namelist()
    assert isinstance(namelist, list), ".namelist() failed"
    if len(namelist) != 0:
        first_file = pak.read(namelist[0])
        assert isinstance(first_file, bytes), ".read() failed"
