import os
import struct
from typing import Dict

from . import id_software
from . import lumps


class RitualBsp(id_software.IdTechBsp):
    _file_magics = (b"RBSP", b"FAKK", b"2015", b"EF2!", b"EALA")
    checksum: int  # how is this calculated / checked?

    def _preload(self):  # big copy-paste, should use super + dheader_t
        """Loads filename using the format outlined in this .bsp's branch defintion script"""
        local_files = os.listdir(self.folder)
        def is_related(f): return f.startswith(os.path.splitext(self.filename)[0])
        self.associated_files = [f for f in local_files if is_related(f)]
        # open .bsp
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        # struct LumpHeader { int offset, length; };
        # struct { int file_magic, bsp_version, checksum; LumpHeader headers[]; };
        self.file_magic = self.file.read(4)
        assert self.file_magic in self._file_magics, f"{self.file} is not a valid .bsp!"
        assert self.file_magic == self.branch.FILE_MAGIC, f"{self.file} is not from {self.branch.GAME_PATHS[0]}!"
        self.bsp_version = int.from_bytes(self.file.read(4), "little")
        self.checksum = int.from_bytes(self.file.read(4), "little")
        self.file.seek(0, 2)  # move cursor to end of file
        self.bsp_file_size = self.file.tell()

        self.headers = dict()
        self.loading_errors: Dict[str, Exception] = dict()
        for LUMP in self.branch.LUMP:
            self.file.seek(12 + struct.calcsize(self.branch.LumpHeader._format) * LUMP.value)
            lump_header = self.branch.LumpHeader.from_stream(self.file)
            self.headers[LUMP.name] = lump_header
            if lump_header.length == 0:
                continue
            try:
                if LUMP.name in self.branch.LUMP_CLASSES:
                    LumpClass = self.branch.LUMP_CLASSES[LUMP.name]
                    BspLump = lumps.BspLump(self.file, lump_header, LumpClass)
                elif LUMP.name in self.branch.SPECIAL_LUMP_CLASSES:
                    SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP.name]
                    self.file.seek(lump_header.offset)
                    lump_data = self.file.read(lump_header.length)
                    BspLump = SpecialLumpClass(lump_data)
                elif LUMP.name in self.branch.BASIC_LUMP_CLASSES:
                    LumpClass = self.branch.BASIC_LUMP_CLASSES[LUMP.name]
                    BspLump = lumps.BasicBspLump(self.file, lump_header, LumpClass)
                else:
                    BspLump = lumps.RawBspLump(self.file, lump_header)
            except Exception as exc:
                self.loading_errors[LUMP.name] = exc
                BspLump = lumps.RawBspLump(self.file, lump_header)
            setattr(self, LUMP.name, BspLump)
