from itertools import zip_longest

from bsp_tool.archives import nexon
from bsp_tool.utils import binary

import pytest


pakfiles = {
    "empty": b"".join([  # just an EOCD
        b"CS\x05\x06", b"\x00" * 16, b"\x01", b"\x00" * 4]),
    "deflate": b"".join([  # 1 file, uncompressed
        # LocalFile
        b"CS\x03\x04",
        b"\x00\x00",  # unused
        b"\x99\xA0\xDC\x42",  # crc32
        b"\x00\x00\x00\x00",  # compressed_size
        b"\x07\x00\x00\x00",  # uncompressed_size
        b"\x08\x00\x00\x00",  # path_size
        b"test.txt",  # path
        b"hello~\n",  # data
        # CentralDirectory
        b"CS\x01\x02",
        b"\x00\x00",  # unused
        b"\x99\xA0\xDC\x42",  # crc32
        b"\x00\x00\x00\x00",  # compressed_size
        b"\x07\x00\x00\x00",  # uncompressed_size
        b"\x08\x00\x00\x00",  # path_size
        b"\x00" * 6,  # unknown, header_offset
        b"test.txt",  # path
        # EOCD
        b"CS\x05\x06",
        b"\x00\x00\x00\x00",  # unknown
        b"\x01\x00\x01\x00",  # counts
        b"\x24\x00\x00\x00",  # sizeof_central_directories
        b"\x25\x00\x00\x00",  # sizeof_local_files
        b"\x01\x00\x00\x00",  # one
        b"\x00"])  # unused
    # TODO: with an LZMA compressed file
    # NOTE: .as_bytes() cannot recompress yet, test will fail
    }


@pytest.mark.parametrize("raw_pakfile", pakfiles.values(), ids=pakfiles.keys())
def test_from_bytes(raw_pakfile: bytes):
    # NOTE: also tests as_bytes
    pakfile = nexon.PakFile.from_bytes(raw_pakfile)
    pakfile_bytes = pakfile.as_bytes()
    # TODO: validate LocalFile.crc32
    # TODO: validate LocalFile matches CentralDirectory
    # TODO: validate EOCD counts & sizeofs
    # compare in hex view
    original = binary.xxd_bytes(raw_pakfile)
    remake = binary.xxd_bytes(pakfile_bytes)
    for expected, actual in zip_longest(original, remake, fillvalue=""):
        assert expected == actual
