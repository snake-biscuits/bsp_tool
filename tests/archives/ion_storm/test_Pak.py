import fnmatch
import os

import pytest

from bsp_tool.archives import ion_storm

from ... import utils


paks = dict()
archive = utils.archive_dirs()
if archive.steam_dir is not None:
    dk_dir = os.path.join(archive.steam_dir, "Daikatana/data")
    paks = {
        f"Daikatana | {pak_filename}": os.path.join(dk_dir, pak_filename)
        for pak_filename in fnmatch.filter(os.listdir(dk_dir), "*.pak")}


@pytest.mark.parametrize("filename", paks.values(), ids=paks.keys())
def test_from_file(filename: str):
    pak = ion_storm.Pak.from_file(filename)
    namelist = pak.namelist()
    assert isinstance(namelist, list), ".namelist() failed"
    # NOTE: all entries in pak2.pak are compressed
    # -- decompression takes approx. 1min per MB
    if len(namelist) != 0:
        first_file = pak.read(namelist[0])
        assert isinstance(first_file, bytes), ".read() failed"
