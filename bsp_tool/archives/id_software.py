from __future__ import annotations
import io
from typing import Dict, List

from .. import core
from ..utils import binary
from . import base
from . import pkware


class PakFileEntry(core.Struct):
    filename: bytes  # plaintext
    offset: int
    length: int
    __slots__ = ["filename", "offset", "length"]
    _format = "56s2I"


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
