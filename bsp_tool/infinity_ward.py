import collections
import enum
import struct

from . import base


LumpHeader = collections.namedtuple("LumpHeader", ["length", "offset"])


class D3DBsp(base.Bsp):
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_1:_d3dbsp
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_2:_d3dbsp
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_4:_d3dbsp
    FILE_MAGIC = b"IBSP"
    # NOTE: Call of Duty 1 has .bsp files in .pk3 archives
    # -- later games instead use .d3dbsp in .iwd archives

    def read_lump(self, LUMP: enum.Enum) -> (LumpHeader, bytes):
        # header
        self.file.seek(self.branch.lump_header_address[LUMP])
        length, offset = struct.unpack("2i", self.file.read(8))
        header = LumpHeader(length, offset)
        if length == 0:
            return header, None
        # data
        self.file.seek(header.offset)
        data = self.file.read(header.length)
        return header, data
