from itertools import zip_longest

from bsp_tool.archives import pkware
from bsp_tool.utils import binary

import pytest


zips = {
    "empty.zip": b"".join([
        b"PK\x05\x06", b"\x00" * 16,
        b"\x20\x00XZP1 0", b"\x00" * 26]),
    "deflate.zip": b"".join([
        b"PK\x03\x04\x14", b"\x00" * 5,
        b"\x92\x6E\xEF\x56\x99\xA0\xDC\x42",
        b"\x07\x00\x00\x00" * 2, b"\x08\x00\x00\x00",
        b"test.txthello~\n",
        b"PK\x01\x02\x14\x03\x14", b"\x00" * 5,
        b"\x92\x6E\xEF\x56\x99\xA0\xDC\x42",
        b"\x07\x00\x00\x00" * 2, b"\x08\x00\x00\x00",
        b"\x00" * 8, b"\x80\x01\x00\x00\x00\x00test.txt"
        b"PK\x05\x06\x00\x00\x00\x00\x01\x00\x01\x00",
        b"\x36\x00\x00\x00\x2D\x00\x00\x00",
        b"\x20\x00XZP1 0", b"\x00" * 26])}

expected = {
    "empty.zip": dict(),
    "deflate.zip": {
        "test.txt": b"hello~\n"}}


def test_new():
    """create & populate a Zip from nothing"""
    zip_ = pkware.Zip()
    zip_.writestr("test.txt", "hello~\n")
    assert zip_.namelist() == ["test.txt"]
    assert zip_.read("test.txt") == b"hello~\n"


# TODO: setup & teardown stages
# -- SETUP: write raw zip bytes to file
# -- TEARDOWN: delete file
# -- iirc python has built-in module for making temp folders, we should use it
# @pytest.mark.parametrize("test_zip", zips)
# def test_from_file(self, test_zip: str):
#     """open a .zip file"""
#     zip_ = pkware.Zip(test_zip)
#     assert set(zip_.namelist()) == set(self.expected[test_zip])
#     for filename in zip_.namelist():
#         assert zip_.read(filename) == self.expected[test_zip][filename]


@pytest.mark.parametrize("raw_zip", zips.values(), ids=zips.keys())
def test_bytes(raw_zip: bytes):
    zip_ = pkware.Zip.from_bytes(raw_zip)
    zip_bytes = zip_.as_bytes()
    # compare
    original = binary.xxd_bytes(raw_zip)
    remake = binary.xxd_bytes(zip_bytes)
    for expected, actual in zip_longest(original, remake, fillvalue=""):
        assert expected == actual


def test_save_changes():
    zip_1 = pkware.Zip()
    zip_1.writestr("test.txt", "hello~\n")
    raw_zip = zip_1.as_bytes()
    # valid zip
    zip_2 = pkware.Zip.from_bytes(raw_zip)
    assert zip_1.namelist() == zip_2.namelist()
    for filename in zip_1.namelist():
        assert zip_1.read(filename) == zip_2.read(filename)
    # continue editing
    zip_1.writestr("test2.txt", "~world\n")
    # zip_1.close()
    raw_zip = zip_1.as_bytes()
    # valid zip
    zip_2 = pkware.Zip.from_bytes(raw_zip)
    assert zip_1.namelist() == zip_2.namelist()
    for filename in zip_1.namelist():
        assert zip_1.read(filename) == zip_2.read(filename)
