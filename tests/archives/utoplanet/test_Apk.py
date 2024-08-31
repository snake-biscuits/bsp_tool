import fnmatch
import os

import pytest

from bsp_tool.archives import utoplanet

from ... import files


apks = dict()
librarian = files.library_card()
if librarian == ("bikkie", "ITANI_WAYSOUND"):
    apk_dir = "C:/PlayGra/Merubasu/shadowland/"
    apks = {
        f"Merubasu | {apk_filename}": os.path.join(apk_dir, apk_filename)
        for apk_filename in fnmatch.filter(os.listdir(apk_dir), "*.apk")}


@pytest.mark.parametrize("filename", apks.values(), ids=apks.keys())
def test_from_file(filename: str):
    apk = utoplanet.Apk.from_file(filename)
    namelist = apk.namelist()
    assert isinstance(namelist, list), ".namelist() failed"
    first_file = apk.read(namelist[0])
    assert isinstance(first_file, bytes), ".read() failed"
