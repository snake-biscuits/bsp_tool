import pytest

from bsp_tool.archives import infinity_ward

from ... import files


iwd_dirs: files.LibraryGames
iwd_dirs = {
    "Steam": {
        "Call of Duty 2": ["Call of Duty 2/main/"]}}


library = files.game_library()
iwds = {
    f"{section} | {game} | {short_path}": full_path
    for section, game, paths in library.scan(iwd_dirs, "*.iwd")
    for short_path, full_path in paths}


@pytest.mark.parametrize("filename", iwds.values(), ids=iwds.keys())
def test_from_file(filename: str):
    iwd = infinity_ward.Iwd.from_file(filename)
    namelist = iwd.namelist()
    assert isinstance(namelist, list), ".namelist() failed"
    if len(namelist) != 0:
        first_file = iwd.read(namelist[0])
        assert isinstance(first_file, bytes), ".read() failed"
