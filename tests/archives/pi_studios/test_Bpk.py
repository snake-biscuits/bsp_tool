import os

import pytest

from bsp_tool.archives import pi_studios

from ... import utils


bpks = dict()
archive = utils.archive_dirs()
if archive.mod_dir is not None:
    # NOTE: this may be the only publically existing Pi Studios .bpk
    qaa_dir = "X360/QuakeArenaArcade/"
    bpks["Quake Arcade Arena | pak0.bpk"] = os.path.join(archive.mod_dir, qaa_dir, "baseq3/pak0.bpk")


@pytest.mark.parametrize("filename", bpks.values(), ids=bpks.keys())
def test_from_file(filename: str):
    bpk = pi_studios.Bpk.from_file(filename)
    assert isinstance(bpk.headers, list)
    assert isinstance(bpk.files, list)
    # NOTE: no .namelist() or .read() yet
