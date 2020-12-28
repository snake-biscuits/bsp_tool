from collections import namedtuple
import struct

from . import base


LumpHeader = namedtuple("LumpHeader", ["offset", "length"])


class IdTechBsp(base.Bsp):
    # https://www.mralligator.com/q3/
    FILE_MAGIC = b"IBSP"

    @staticmethod
    def read_lump(file, header_address: int) -> (LumpHeader, bytes):
        # lump header
        file.seek(header_address)
        offset, length = struct.unpack("2i", file.read(8))
        header = LumpHeader(offset, length)
        if length == 0:
            return header, None
        # lump data
        file.seek(offset)
        data = file.read(length)
        return header, data
