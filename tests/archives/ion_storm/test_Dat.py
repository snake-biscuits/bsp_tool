import fnmatch
import os

import pytest

from bsp_tool.archives import ion_storm

from ... import utils


dats = dict()
archive = utils.archive_dirs()
if archive.steam_dir is not None:
    ax_dir = os.path.join(archive.steam_dir, "Anachronox/anoxdata")
    dats = {
        f"Anachronox | {dat_filename}": os.path.join(ax_dir, dat_filename)
        for dat_filename in fnmatch.filter(os.listdir(ax_dir), "*.dat")}


@pytest.mark.parametrize("filename", dats.values(), ids=dats.keys())
def test_from_file(filename: str):
    dat = ion_storm.Dat.from_file(filename)
    namelist = dat.namelist()
    assert isinstance(namelist, list), ".namelist() failed"
    if len(namelist) != 0:
        first_file = dat.read(namelist[0])
        assert isinstance(first_file, bytes), ".read() failed"
