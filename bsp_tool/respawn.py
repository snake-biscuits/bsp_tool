from collections import namedtuple
import enum  # for type hints
import os
import struct
from types import ModuleType

from . import base
from .base import LumpHeader
from .branches import respawn


ExternalLumpHeader = namedtuple("ExternalLumpHeader", ["offset", "length", "version", "fourCC", "filename", "filesize"])


class RespawnBsp(base.Bsp):
    # https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Titanfall
    # https://raw.githubusercontent.com/Wanty5883/Titanfall2/master/tools/TitanfallMapExporter.py
    FILE_MAGIC = b"rBSP"
    branch = respawn.titanfall2  # default branch

    def __init__(self, branch: ModuleType = branch, filename: str = "untitled.bsp", autoload: bool = True):
        super(base.Bsp, self).__init__(branch, filename)
        # NOTE: bsp revision appears before headers, not after (as in Valve's variant)

    def read_lump(self, LUMP: enum.Enum) -> (LumpHeader, bytes):  # just .bsp internal lumps
        # header
        self.file.seek(self.branch.lump_header_address[LUMP])
        offset, length, version, fourCC = struct.unpack("4i", self.file.read(16))
        header = LumpHeader(offset, length, version, fourCC)
        if length == 0:
            return header, None
        # lump data
        self.file.seek(offset)
        data = self.file.read(length)
        return header, data

    def load_lumps(self, file):
        for LUMP in self.branch.LUMP:
            lump_filename = f"{self.filename}.{LUMP.value:04x}.bsp_lump"
            if lump_filename in self.associated_files:  # .bsp_lump file exists
                with open(os.path.join(self.folder, lump_filename), "rb") as lump_file:
                    data = lump_file.read()
                # the .bsp_lump file has no header, this is just the matching header in the .bsp
                # unsure how / if headers for external .bsp_lump affect anything
                file.seek(self.branch.lump_header_address[LUMP])  # internal .bsp lump header
                offset, length, version, fourCC = struct.unpack("4i", file.read(16))
                lump_filesize = len(data)
                header = ExternalLumpHeader(offset, length, version, fourCC, lump_filename, lump_filesize)
                # TODO: save contents of matching .bsp lump as INTERNAL_<LUMPNAME> / RAW_INTERNAL_<LUMPNAME>
            else:  # .bsp internal lump
                header, data = self.read_lump(file, LUMP)
            self.HEADERS[LUMP] = header
            if data is not None:
                setattr(self, "RAW_" + LUMP.name, data)
        # TODO: load all 5 ENTITIES files
