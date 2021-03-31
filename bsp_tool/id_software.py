from collections import namedtuple
import enum  # for type hints
import struct

from . import base


LumpHeader = namedtuple("LumpHeader", ["offset", "length"])


class IdTechBsp(base.Bsp):
    # https://www.mralligator.com/q3/
    FILE_MAGIC = b"IBSP"
    # NOTE: these files are usually stored in .pk3 files
    # -- see bsp_tool.tools.pk3 for a handy extractor

    def _read_lump(self, LUMP: enum.Enum) -> (LumpHeader, bytes):
        # lump header
        self.file.seek(self.branch.lump_header_address[LUMP])
        offset, length = struct.unpack("2i", self.file.read(8))
        header = LumpHeader(offset, length)
        if length == 0:
            return header, None
        # lump data
        self.file.seek(offset)
        data = self.file.read(length)
        return header, data
