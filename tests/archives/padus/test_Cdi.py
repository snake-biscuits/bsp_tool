import fnmatch
import os

import pytest

from bsp_tool.archives import padus

from ... import files


cdis = dict()
archive = files.archive_dirs()
if archive.dreamcast_dir is not None:
    dc_dir = archive.dreamcast_dir
    cdis = {
        f"{cdi_filename}": os.path.join(dc_dir, cdi_filename)
        for cdi_filename in fnmatch.filter(os.listdir(dc_dir), "*.cdi")}


@pytest.mark.parametrize("filename", cdis.values(), ids=cdis.keys())
def test_from_file(filename: str):
    cdi = padus.Cdi.from_file(filename)
    namelist = cdi.namelist()
    assert isinstance(namelist, list), ".namelist() failed"
    if len(namelist) != 0:
        first_file = cdi.read(namelist[0])
        assert isinstance(first_file, bytes), ".read() failed"
