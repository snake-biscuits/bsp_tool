import os
from typing import Dict

from . import id_software
from . import lumps


class UberBsp(id_software.IdTechBsp):
    file_magic = b"FAKK"  # Ubertools 1.0.0; FAKK2 -> Alice
    checksum: int  # how is this calculated / checked?

    def _preload(self):  # big copy-paste, should use super + dheader_t
        """Loads filename using the format outlined in this .bsp's branch defintion script"""
        local_files = os.listdir(self.folder)
        def is_related(f): return f.startswith(os.path.splitext(self.filename)[0])
        self.associated_files = [f for f in local_files if is_related(f)]
        # open .bsp
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        # struct { int file_magic, bsp_version, checksum; lump_t lumps[20] };
        file_magic = self.file.read(4)
        assert file_magic == self.file_magic, f"{self.file} is not a valid .bsp!"
        self.bsp_version = int.from_bytes(self.file.read(4), "little")
        self.checksum = int.from_bytes(self.file.read(4), "little")
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
