import pytest

from bsp_tool.archives import pi_studios

from ... import files


# NOTE: this may be the only publically existing Pi Studios .bpk
bpk_dirs: files.LibraryGames
bpk_dirs = {
    "Xbox360": {
        "Quake Arena Arcade": ["QuakeArenaArcade/baseq3/"]}}


library = files.game_library()
bpks = {
    f"{section} | {game} | {short_path}": full_path
    for section, game, paths in library.scan(bpk_dirs, "*.bpk")
    for short_path, full_path in paths}


@pytest.mark.parametrize("filename", bpks.values(), ids=bpks.keys())
def test_from_file(filename: str):
    bpk = pi_studios.Bpk.from_file(filename)
    assert isinstance(bpk.headers, list)
    assert isinstance(bpk.files, list)
    # NOTE: no .namelist() or .read() yet
