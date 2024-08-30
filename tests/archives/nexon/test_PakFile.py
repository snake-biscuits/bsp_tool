from itertools import zip_longest

from bsp_tool.archives import nexon
from bsp_tool.utils import binary

import pytest


pakfiles = {
    "empty": b"".join([  # just an EOCD
        b"CS\x05\x06", b"\x00" * 16, b"\x01", b"\x00" * 4]),
    # TODO: with a file
    # "deflate": b"".join([
    #     # LocalFile
    #     b"CS\x03\x04",
    #     ...,
    #     b"test.txthello~\n",
    #     # CentralDirectory
    #     b"CS\x01\x02",
    #     ...,
    #     b"test.txt"
    #     # EOCD
    #     b"CS\x05\x06",
    #     ...])
    # TODO: with an LZMA compressed file
    }


@pytest.mark.parametrize("raw_pakfile", pakfiles.values(), ids=pakfiles.keys())
def test_from_bytes(raw_pakfile: bytes):
    pakfile = nexon.PakFile.from_bytes(raw_pakfile)
    pakfile_bytes = pakfile.as_bytes()
    # compare
    original = binary.xxd_bytes(raw_pakfile)
    remake = binary.xxd_bytes(pakfile_bytes)
    for expected, actual in zip_longest(original, remake, fillvalue=""):
        assert expected == actual
