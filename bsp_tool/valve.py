from collections import namedtuple
import lzma
import struct

from . import base
from .branches import valve


FILE_MAGIC = b"VBSP"
LumpHeader = namedtuple("LumpHeader", ["offset", "length", "version", "fourCC"])


def read_lump(file, header_address: int) -> (LumpHeader, bytes):
    # header
    file.seek(header_address)
    offset = int.from_bytes(file.read(4), "little")
    length = int.from_bytes(file.read(4), "little")
    version = int.from_bytes(file.read(4), "little")  # different lump versions have different formats!
    fourCC = int.from_bytes(file.read(4), "little")
    header = LumpHeader(offset, length, version, fourCC)
    if length == 0:
        return
    # lump data
    file.seek(offset)
    data = file.read(length)
    if fourCC != 0:  # lump is compressed
        source_lzma_header = struct.unpack("3I5c", data[:17])
        # b"LZMA" = source_lzma_header[0]
        actual_size = source_lzma_header[1]
        # compressed_size = source_lzma_header[2]
        properties = b"".join(source_lzma_header[3:])
        _filter = lzma._decode_filter_properties(lzma.FILTER_LZMA1, properties)
        decompressor = lzma.LZMADecompressor(lzma.FORMAT_RAW, None, [_filter])
        data = decompressor.decompress(data[17:])
        if len(data) != actual_size:
            data = data[:actual_size]
    return header, data


class ValveBsp(base.Bsp):
    read_lump = read_lump  # can you patch in a static method in this way? TEST
    ...
