import pytest

from bsp_tool.archives import respawn

from ... import files


rpak_dirs: files.LibraryGames
rpak_dirs = {
    "Steam": {
        "Apex Legends": ["Apex Legends/paks/Win64/"],
        "Titanfall 2": ["Titanfall2/r2/paks/Win64/"]},
    "PS4": {
        "Titanfall 2 (Tech Test)": ["Titanfall2_tech_test/r2/paks/PS4/"]}}


library = files.game_library()
rpaks = {
    f"{section} | {game} | {short_path}": full_path
    for section, game, paths in library.scan(rpak_dirs, "*.rpak")
    for short_path, full_path in paths}


@pytest.mark.parametrize("filename", rpaks.values(), ids=rpaks.keys())
def test_from_file(filename: str):
    rpak = respawn.RPak.from_file(filename)
    if rpak.header.compression == respawn.rpak.Compression.NONE:
        assert isinstance(rpak.namelist(), list)
        # TODO: test .read() (NotYetImplemented)
