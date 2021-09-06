from collections import namedtuple  # for type hints
import enum  # for type hints
import os
import struct
from types import ModuleType
from typing import Dict

from . import base
from . import lumps
from .id_software import IdTechBsp


GoldSrcLumpHeader = namedtuple("GoldSrcLumpHeader", ["offset", "length"])


class GoldSrcBsp(IdTechBsp):
    # https://github.com/ValveSoftware/halflife/blob/master/utils/common/bspfile.h
    # http://hlbsp.sourceforge.net/index.php?content=bspdef
    # NOTE: GoldSrcBsp has no file_magic!

    def __init__(self, branch: ModuleType, filename: str = "untitled.bsp", autoload: bool = True):
        super(GoldSrcBsp, self).__init__(branch, filename, autoload)

    def __repr__(self):
        version = f"(version {self.bsp_version})"  # no file_magic
        game = self.branch.__name__[len(self.branch.__package__) + 1:]
        return f"<{self.__class__.__name__} '{self.filename}' {game} {version} at 0x{id(self):016X}>"

    def _preload(self):
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        self.bsp_version = int.from_bytes(self.file.read(4), "little")
        self.file.seek(0, 2)  # move cursor to end of file
        self.bsp_file_size = self.file.tell()

        self.headers = dict()
        self.loading_errors: Dict[str, Exception] = dict()
        for LUMP_enum in self.branch.LUMP:
            LUMP_NAME = LUMP_enum.name
            self.file.seek(self.branch.lump_header_address[LUMP_enum])
            offset, length = struct.unpack("2I", self.file.read(8))
            lump_header = GoldSrcLumpHeader(offset, length)
            self.headers[LUMP_NAME] = lump_header
            if length == 0:
                continue  # empty lump
            try:
                if LUMP_NAME in self.branch.LUMP_CLASSES:
                    LumpClass = self.branch.LUMP_CLASSES[LUMP_NAME]
                    BspLump = lumps.create_BspLump(self.file, lump_header, LumpClass)
                elif LUMP_NAME in self.branch.SPECIAL_LUMP_CLASSES:
                    SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP_NAME]
                    self.file.seek(offset)
                    BspLump = SpecialLumpClass(self.file.read(length))
                elif LUMP_NAME in self.branch.BASIC_LUMP_CLASSES:
                    LumpClass = self.branch.BASIC_LUMP_CLASSES[LUMP_NAME]
                    BspLump = lumps.create_BasicBspLump(self.file, lump_header, LumpClass)
                else:
                    BspLump = lumps.create_RawBspLump(self.file, lump_header)
            except Exception as exc:
                self.loading_errors[LUMP_NAME] = exc
                BspLump = lumps.create_RawBspLump(self.file, lump_header)
                # NOTE: doesn't decompress LZMA, fix that
            setattr(self, LUMP_NAME, BspLump)

    def _read_header(self, LUMP: enum.Enum) -> GoldSrcLumpHeader:
        """Reads bytes of lump"""
        self.file.seek(self.branch.lump_header_address[LUMP])
        offset, length = struct.unpack("2I", self.file.read(8))
        header = GoldSrcLumpHeader(offset, length)
        return header


class ValveBsp(base.Bsp):
    # https://developer.valvesoftware.com/wiki/Source_BSP_File_Format
    file_magic = b"VBSP"

    def __init__(self, branch: ModuleType, filename: str = "untitled.bsp", autoload: bool = True):
        super(ValveBsp, self).__init__(branch, filename, autoload)

    def _read_header(self, LUMP: enum.Enum) -> namedtuple:  # LumpHeader
        """Get LUMP from self.branch.LUMP; e.g. self.branch.LUMP.ENTITIES"""
        # NOTE: each branch of VBSP has unique headers,
        # -- so branch.read_lump_header function is used
        # TODO: move to a system of using header LumpClasses instead of the above
        return self.branch.read_lump_header(self.file, LUMP)
