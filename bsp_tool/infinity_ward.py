import collections
import enum
import os
import struct
from typing import Dict

from . import base
from . import lumps


LumpHeader = collections.namedtuple("LumpHeader", ["length", "offset"])


class D3DBsp(base.Bsp):
    file_magic = b"IBSP"
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_1:_d3dbsp
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_2:_d3dbsp
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_4:_d3dbsp
    # NOTE: Call of Duty 1 has .bsp files in .pk3 archives
    # NOTE: Call of Duty 2 has .d3dbsp in .iwd archives
    # NOTE: Call of Duty 4 has .d3dbsp in .ff archives

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
            LUMP_NAME = LUMP_enum.name
            self.headers[LUMP_NAME] = lump_header
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
        length, offset = struct.unpack("2i", self.file.read(8))
        header = LumpHeader(length, offset)
        return header
