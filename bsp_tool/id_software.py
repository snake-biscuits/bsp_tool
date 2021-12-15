import collections
import enum  # for type hints
import os
import struct
from types import ModuleType
from typing import Dict

from . import base
from . import lumps


IdTechLumpHeader = collections.namedtuple("IdTechLumpHeader", ["offset", "length"])


class QuakeBsp(base.Bsp):
    file_magic = None

    def __init__(self, branch: ModuleType, filename: str = "untitled.bsp", autoload: bool = True):
        super(QuakeBsp, self).__init__(branch, filename, autoload)

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
            lump_header = IdTechLumpHeader(offset, length)
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

    def _read_header(self, LUMP: enum.Enum) -> IdTechLumpHeader:
        """Reads bytes of lump"""
        self.file.seek(self.branch.lump_header_address[LUMP])
        offset, length = struct.unpack("2I", self.file.read(8))
        header = IdTechLumpHeader(offset, length)
        return header


# TODO: BSP2 (Darkplaces / Alkaline)
# https://ericwa.github.io/ericw-tools/doc/qbsp.html
# https://github.com/ericwa/ericw-tools
# https://quakewiki.org/wiki/BSP2
# https://github.com/xonotic/darkplaces/blob/master/model_brush.c
# https://github.com/xonotic/darkplaces/


# TODO: FBSP (Warsow)
# https://quakewiki.org/wiki/FTEQW_Modding#FBSP_map_support


class IdTechBsp(base.Bsp):
    file_magic = b"IBSP"
    # https://www.mralligator.com/q3/
    # NOTE: Quake 3 .bsp are usually stored in .pk3 files

    def _preload(self):
        """Loads filename using the format outlined in this .bsp's branch defintion script"""
        local_files = os.listdir(self.folder)
        def is_related(f): return f.startswith(os.path.splitext(self.filename)[0])
        self.associated_files = [f for f in local_files if is_related(f)]
        # open .bsp
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        file_magic = self.file.read(4)
        assert file_magic == self.file_magic, f"{self.file} is not a valid .bsp!"
        self.bsp_version = int.from_bytes(self.file.read(4), "little")
        self.file.seek(0, 2)  # move cursor to end of file
        self.bsp_file_size = self.file.tell()

        self.headers = dict()
        self.loading_errors: Dict[str, Exception] = dict()
        for LUMP_enum in self.branch.LUMP:
            # CHECK: is lump external? (are associated_files overriding)
            lump_header = self._read_header(LUMP_enum)
            LUMP_name = LUMP_enum.name
            self.headers[LUMP_name] = lump_header
            if lump_header.length == 0:
                continue
            try:
                if LUMP_name in self.branch.LUMP_CLASSES:
                    LumpClass = self.branch.LUMP_CLASSES[LUMP_name]
                    BspLump = lumps.create_BspLump(self.file, lump_header, LumpClass)
                elif LUMP_name in self.branch.SPECIAL_LUMP_CLASSES:
                    SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP_name]
                    self.file.seek(lump_header.offset)
                    lump_data = self.file.read(lump_header.length)
                    BspLump = SpecialLumpClass(lump_data)
                elif LUMP_name in self.branch.BASIC_LUMP_CLASSES:
                    LumpClass = self.branch.BASIC_LUMP_CLASSES[LUMP_name]
                    BspLump = lumps.create_BasicBspLump(self.file, lump_header, LumpClass)
                else:
                    BspLump = lumps.create_RawBspLump(self.file, lump_header)
            except Exception as exc:
                self.loading_errors[LUMP_name] = exc
                BspLump = lumps.create_RawBspLump(self.file, lump_header)
            setattr(self, LUMP_name, BspLump)

    def _read_header(self, LUMP: enum.Enum) -> IdTechLumpHeader:
        self.file.seek(self.branch.lump_header_address[LUMP])
        offset, length = struct.unpack("2i", self.file.read(8))
        header = IdTechLumpHeader(offset, length)
        return header
