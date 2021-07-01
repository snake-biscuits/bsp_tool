import collections
import enum  # for type hints
import os
import struct
from typing import Dict

from . import base
from . import lumps


LumpHeader = collections.namedtuple("LumpHeader", ["offset", "length"])


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
        if file_magic != self.file_magic:
            raise RuntimeError(f"{self.file} is not a valid .bsp!")
        self.bsp_version = int.from_bytes(self.file.read(4), "little")
        self.file.seek(0, 2)  # move cursor to end of file
        self.bsp_file_size = self.file.tell()

        self.headers = dict()
        self.loading_errors: Dict[str, Exception] = dict()
        for LUMP_enum in self.branch.LUMP:
            # CHECK: is lump external? (are associated_files overriding)
            lump_header = self._read_header(LUMP_enum)
            LUMP_NAME = LUMP_enum.name
            self.HEADERS[LUMP_NAME] = lump_header
            if lump_header.length == 0:
                continue
            try:
                if LUMP_NAME in self.branch.LUMP_CLASSES:
                    LumpClass = self.branch.LUMP_CLASSES[LUMP_NAME]
                    BspLump = lumps.create_BspLump(self.file, lump_header, LumpClass)
                elif LUMP_NAME in self.branch.SPECIAL_LUMP_CLASSES:
                    SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP_NAME]
                    self.file.seek(lump_header.offset)
                    lump_data = self.file.read(lump_header.length)
                    BspLump = SpecialLumpClass(lump_data)
                elif LUMP_NAME in self.branch.BASIC_LUMP_CLASSES:
                    LumpClass = self.branch.BASIC_LUMP_CLASSES[LUMP_NAME]
                    BspLump = lumps.create_BasicBspLump(self.file, lump_header, LumpClass)
                else:
                    BspLump = lumps.create_RawBspLump(self.file, lump_header)
            except Exception as exc:
                self.loading_errors[LUMP_NAME] = exc
                BspLump = lumps.create_RawBspLump(self.file, lump_header)
            setattr(self, LUMP_NAME, BspLump)

    def _read_header(self, LUMP: enum.Enum) -> (LumpHeader, bytes):
        self.file.seek(self.branch.lump_header_address[LUMP])
        offset, length = struct.unpack("2i", self.file.read(8))
        header = LumpHeader(offset, length)
        return header
