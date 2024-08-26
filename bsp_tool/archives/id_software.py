from __future__ import annotations
import io
import struct
from typing import Dict, List

from . import base
from . import pkware


class PakFileEntry:
    def __init__(self, filepath: str, offset: int, size: int):
        self.filepath = filepath
        self.offset = offset
        self.size = size

    def __repr__(self) -> str:
        return f"PakFileEntry(filepath={self.filepath!r}, offset={self.offset}, size={self.size})"

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> PakFileEntry:
        return cls(*struct.unpack("56s2I", stream.read(64)))


class Pak(base.Archive):
    # https://quakewiki.org/wiki/.pak
    ext = "*.pak"
    files: Dict[str, PakFileEntry]

    def __init__(self):
        self.files = dict()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {len(self.files)} files @ 0x{id(self):016X}>"

    def read(self, filepath: str) -> bytes:
        assert filepath in self.files
        entry = self.files[filepath]
        self.file.seek(entry.offset)
        return self.file.read(entry.size)

    def namelist(self) -> List[str]:
        return sorted(self.files.keys())

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Pak:
        out = cls()
        out.file = stream
        assert out.file.read(4) == b"PACK", "not a .pak file"
        # file table
        offset, size = struct.unpack("2I", out.file.read(8))
        assert size % 64 == 0, "unexpected file table size"
        out.file.seek(offset)
        out.files = {
            entry.filepath.split(b"\0")[0].decode(): entry
            for entry in [
                PakFileEntry.from_stream(out.file)
                for i in range(size // 64)]}
        return out


class Pk3(pkware.Zip):
    """IdTech .bsps are stored in .pk3 files, which are basically .zip archives"""
    ext = "*.pk3"
