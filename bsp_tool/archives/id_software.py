from __future__ import annotations
import io
import struct
from typing import Dict, List

from ..utils import binary
from . import base
from . import pkware


# NOTE: can't use branches.base.Struct without making a circular import
class PakFileEntry:
    filename: bytes  # paintext
    offset: int
    length: int
    __slots__ = ["filename", "offset", "length"]
    _format = "56s2I"

    def __init__(self, filename: str, offset: int, length: int):
        self.filename = filename
        self.offset = offset
        self.length = length

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{attr}={getattr(self, attr)!r}"
            for attr in ("filename, offset, length"))
        return f"PakFileEntry({attrs})"

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> PakFileEntry:
        return cls(*struct.unpack("56s2I", stream.read(64)))


class Pak(base.Archive):
    # https://quakewiki.org/wiki/.pak
    ext = "*.pak"
    _file: io.BytesIO
    entries: Dict[str, PakFileEntry]

    def __init__(self):
        self.entries = dict()

    def __repr__(self) -> str:
        descriptor = f"{len(self.entries)} files"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def read(self, filepath: str) -> bytes:
        assert filepath in self.entries
        entry = self.entries[filepath]
        self._file.seek(entry.offset)
        return self._file.read(entry.length)

    def namelist(self) -> List[str]:
        return sorted(self.entries.keys())

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Pak:
        out = cls()
        out._file = stream
        assert out._file.read(4) == b"PACK", "not a .pak file"
        # file table
        offset, length = binary.read_struct(out._file, "2I")
        sizeof_entry = 64
        assert length % sizeof_entry == 0, "unexpected file table size"
        out._file.seek(offset)
        out.entries = {
            entry.filename.partition(b"\0")[0].decode("ascii"): entry
            for entry in [
                PakFileEntry.from_stream(out._file)
                for i in range(length // sizeof_entry)]}
        return out


class Pk3(pkware.Zip):
    ext = "*.pk3"
