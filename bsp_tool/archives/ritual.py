from __future__ import annotations
import io
import struct
from typing import Dict, List

from ..utils import binary
from . import base


# NOTE: can't use branches.base.Struct without making a circular import
class SPakEntry:
    filename: bytes  # plaintext
    offset: int
    length: int
    __slots__ = ["filename", "offset", "length"]
    _format = "120s2I"

    def __init__(self, filename: str, offset: int, length: int):
        self.filename = filename
        self.offset = offset
        self.length = length

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{attr}={getattr(self, attr)!r}"
            for attr in ("filename", "offset", "length"))
        return f"PakFileEntry({attrs})"

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> SPakEntry:
        return cls(*struct.unpack(cls._format, stream.read(0x80)))


class Sin(base.Archive):
    ext = "*.sin"
    _file: io.BytesIO
    entries: Dict[str, SPakEntry]

    def __init__(self):
        self.entries = dict()

    def read(self, filename: str) -> bytes:
        assert filename in self.entries
        entry = self.entries[filename]
        self._file.seek(entry.offset)
        return self._file.read(entry.length)

    def namelist(self) -> List[str]:
        return sorted(self.entries.keys())

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Sin:
        out = cls()
        out._file = stream
        assert out._file.read(4) == b"SPAK", "not a .pak file"
        # file table
        offset, length = binary.read_struct(out._file, "2I")
        sizeof_entry = 0x80
        assert length % sizeof_entry == 0, "unexpected file table size"
        out._file.seek(offset)
        out.entries = {
            entry.filename.partition(b"\0")[0].decode("ascii"): entry
            for entry in [
                SPakEntry.from_stream(out._file)
                for i in range(length // sizeof_entry)]}
        return out
