import os

from bsp_tool.branches.valve import source

import pytest


class TestPakFile:
    zips = {"empty.zip": b"".join([b"PK\x05\x06", b"\x00" * 16,
                                   b"\x20\x00XZP1 0", b"\x00" * 26]),
            "deflate.zip": b"".join([b"PK\x03\x04\x14", b"\x00" * 5,
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
    expected = {"empty.zip": dict(),
                "deflate.zip": {"test.txt": b"hello~\n"}}

    def test_new(self):
        """create & populate a PakFile from nothing"""
        pk = source.PakFile()
        pk.writestr("test.txt", "hello~\n")
        assert pk.namelist() == ["test.txt"]
        assert pk.read("test.txt") == b"hello~\n"

    def setup_method(self, method):
        """create test zipfiles"""
        if method.__name__ in ("test_from_file", "test_bytes"):
            for filename, data in self.zips.items():
                with open(filename, "wb") as zip_file:
                    zip_file.write(data)

    def teardown_method(self, method):
        """delete test zipfiles"""
        if method.__name__ in ("test_from_file", "test_bytes"):
            for filename in self.zips:
                os.remove(filename)

    @pytest.mark.parametrize("test_zip", zips)
    def test_from_file(self, test_zip: str):
        """open a .zip file"""
        pk = source.PakFile(test_zip)
        assert set(pk.namelist()) == set(self.expected[test_zip])
        for filename in pk.namelist():
            assert pk.read(filename) == self.expected[test_zip][filename]

    @pytest.mark.parametrize("test_zip", zips)
    def test_bytes(self, test_zip: str):
        raw_zip = self.zips[test_zip]
        pk = source.PakFile.from_bytes(raw_zip)
        assert pk.as_bytes() == raw_zip

    def test_save_changes(self):
        pk = source.PakFile()
        pk.writestr("test.txt", "hello~\n")
        raw_zip = pk.as_bytes()
        # valid zip
        pk2 = source.PakFile.from_bytes(raw_zip)
        assert pk.namelist() == pk2.namelist()
        for filename in pk.namelist():
            assert pk.read(filename) == pk2.read(filename)
        # continue editing
        pk.writestr("test2.txt", "~world\n")
        # pk.close()
        raw_zip = pk.as_bytes()
        # valid zip
        pk2 = source.PakFile.from_bytes(raw_zip)
        assert pk.namelist() == pk2.namelist()
        for filename in pk.namelist():
            assert pk.read(filename) == pk2.read(filename)
