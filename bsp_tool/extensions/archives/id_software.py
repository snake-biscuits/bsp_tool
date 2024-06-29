from __future__ import annotations
import io
import struct
from typing import Dict, List
import zipfile

from . import base


class PakFileEntry:
    def __init__(self, filepath: str, offset: int, size: int):
        self.filepath = filepath
        self.offset = offset
        self.size = size

    def __repr__(self) -> str:
        return f"PakFileEntry(filepath={self.filepath}, offset={self.offset}, size={self.size})"

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> PakFileEntry:
        return cls(*struct.unpack("56s2I", stream.read(64)))


class Pak(base.Archive):
    # https://quakewiki.org/wiki/.pak
    ext = "*.pak"
    files: Dict[str, PakFileEntry]

    def __init__(self, filepath: str = None):
        self.files = dict()
        if filepath is not None:
            self._from_file(filepath)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {len(self.files)} files @ 0x{id(self):016X}>"

    def __del__(self):
        self.file.close()

    def __exit__(self):
        self.file.close()

    def _from_file(self, filepath: str):
        self.file = open(filepath, "rb")
        assert self.file.read(4) == b"PACK", "not a .pak file"
        # file table
        offset, size = struct.unpack("2I", self.file.read(8))
        assert size % 64 == 0, "unexpected file table size"
        self.file.seek(offset)
        self.files = {
            e.filepath.split(b"\0")[0].decode(): e
            for e in [
                PakFileEntry.from_stream(self.file)
                for i in range(size // 64)]}

    def read(self, filepath: str) -> bytes:
        assert filepath in self.files
        entry = self.files[filepath]
        self.file.seek(entry.offset)
        return self.file.read(entry.size)

    def namelist(self) -> List[str]:
        return sorted(self.files.keys())


class Pk3(zipfile.ZipFile, base.Archive):
    """IdTech .bsps are stored in .pk3 files, which are basically .zip archives"""
    ext = "*.pk3"
