import pytest

from bsp_tool.archives import ion_storm

from ... import files


dat_dirs: files.LibraryGames
dat_dirs = {
    "Steam": {
        "Anachronox": ["Anachronox/anoxdata"]}}


library = files.game_library()
dats = {
    f"{section} | {game} | {short_path}": full_path
    for section, game, paths in library.scan(dat_dirs, "*.dat")
    for short_path, full_path in paths}


@pytest.mark.parametrize("filename", dats.values(), ids=dats.keys())
def test_from_file(filename: str):
    dat = ion_storm.Dat.from_file(filename)
    namelist = dat.namelist()
    assert isinstance(namelist, list), ".namelist() failed"
    if len(namelist) != 0:
        first_file = dat.read(namelist[0])
        assert isinstance(first_file, bytes), ".read() failed"
