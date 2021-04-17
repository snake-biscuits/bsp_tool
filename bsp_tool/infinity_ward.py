import collections
import enum
import struct

from . import base


LumpHeader = collections.namedtuple("LumpHeader", ["length", "offset"])


class D3DBsp(base.Bsp):
    FILE_MAGIC = b"IBSP"
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_1:_d3dbsp
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_2:_d3dbsp
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_4:_d3dbsp
    # NOTE: Call of Duty 1 has .bsp files in .pk3 archives
    # NOTE: Call of Duty 2 has .d3dbsp in .iwd archives
    # NOTE: Call of Duty 4 has .d3dbsp in .ff archives

    def _read_header(self, LUMP: enum.Enum) -> (LumpHeader, bytes):
        self.file.seek(self.branch.lump_header_address[LUMP])
        length, offset = struct.unpack("2i", self.file.read(8))
        header = LumpHeader(length, offset)
        return header
