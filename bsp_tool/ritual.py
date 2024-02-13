import os
from typing import Dict

from . import id_software


class RitualBsp(id_software.IdTechBsp):
    _file_magics = (b"RBSP", b"FAKK", b"2015", b"EF2!", b"EALA")
    checksum: int  # TODO: calculate / verify (CRC?)
    # struct LumpHeader { int offset, length; };
    # struct { int file_magic, version, checksum; LumpHeader headers[]; };

    def _preload(self):
        """Loads filename using the format outlined in this .bsp's branch defintion script"""
        # collect files
        local_files = os.listdir(self.folder)
        def is_related(f): return f.startswith(os.path.splitext(self.filename)[0])
        self.associated_files = [f for f in local_files if is_related(f)]
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        # collect metadata
        self.file_magic = self.file.read(4)
        assert self.file_magic in self._file_magics, f"{self.file} is not a valid .bsp!"
        assert self.file_magic == self.branch.FILE_MAGIC, f"{self.file} is not from {[*self.branch.GAME_PATHS][0]}!"
        self.version = int.from_bytes(self.file.read(4), "little")
        self.checksum = int.from_bytes(self.file.read(4), "little")
        self.file.seek(0, 2)  # move cursor to end of file
        self.filesize = self.file.tell()
        # collect headers
        self.headers = dict()
        self.loading_errors: Dict[str, Exception] = dict()
        for lump_name, lump_header in self._header_generator(offset=12):
            self._preload_lump(lump_name, lump_header)
