import pytest

from bsp_tool.archives import padus

from ... import files


cdi_dirs: files.LibraryGames
cdi_dirs = {
    "Dreamcast": {
        "Disc Images": [""]}}  # not looking in subdirs


library = files.game_library()
cdis = {
    f"{section} | {game} | {short_path}": full_path
    for section, game, paths in library.scan(cdi_dirs, "*.cdi")
    for short_path, full_path in paths}


@pytest.mark.parametrize("filename", cdis.values(), ids=cdis.keys())
def test_from_file(filename: str):
    cdi = padus.Cdi.from_file(filename)
    assert len(cdi.tracks) != 0
    assert len(cdi.extras) == len(cdi.tracks)
    for track in cdi.tracks:
        assert track.name in cdi.extras
