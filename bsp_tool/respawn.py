from collections import namedtuple
import os
import struct

from . import base
from .base import LumpHeader
from .branches import respawn


ExternalLumpHeader = namedtuple("ExternalLumpHeader", ["offset", "length", "version", "fourCC", "filename", "filesize"])


def read_lump(file, header_address: int) -> (LumpHeader, bytes):  # .bsp internal lumps only
    # header
    file.seek(header_address)
    offset, length, version, fourCC = struct.unpack("4i", file.read(16))
    header = LumpHeader(offset, length, version, fourCC)
    if length == 0:
        return header, None
    # lump data
    file.seek(offset)
    data = file.read(length)
    return header, data


class RespawnBsp(base.Bsp):
    # https://dev.cra0kalo.com/?p=202
    FILE_MAGIC = b"rBSP"
    branch = respawn.titanfall2  # default branch

    def __init__(self, branch=branch, filename="untitled.bsp"):
        super(base.Bsp, self).__init__(branch, filename)
        # NOTE: bsp revision appears before headers, not after (as in valve's variant)

    def read_lump(self, LUMP) -> (LumpHeader, bytes):
        return read_lump(self.file, self.branch.lump_header_address[LUMP])

    def load_lumps(self, file):
        for ID in self.branch.LUMP:
            lump_filename = f"{self.filename}.{ID.value:04x}.bsp_lump"
            if lump_filename in self.associated_files:
                with open(os.path.join(self.folder, lump_filename), "rb") as lump_file:
                    data = lump_file.read()
                # the .bsp_lump file has no header, this is just the matching header in the .bsp
                # unsure how / if headers for external .bsp_lump affect anything
                file.seek(self.branch.lump_header_address[ID])
                offset, length, version, fourCC = struct.unpack("4i", file.read(16))
                lump_filesize = len(data)
                header = ExternalLumpHeader(offset, length, version, fourCC, lump_filename, lump_filesize)
                # TODO: save contents of matching .bsp lump as INTERNAL_RAW_<LUMPNAME>
            else:  # internal lump
                header, data = self.read_lump(file, self.branch.lump_header_address[ID])
            self.HEADERS[ID] = header
            if data is not None:
                setattr(self, "RAW_" + ID.name, data)
        # TODO: load all 5 ENTITIES files
