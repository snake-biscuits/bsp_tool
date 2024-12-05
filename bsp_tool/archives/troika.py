# https://github.com/craftablescience/sourcepp/blob/main/src/vpkpp/format/VPK_VTMB.cpp
from __future__ import annotations
import io
from typing import Dict, List

from ..utils import binary
from . import base


class VpkEntry:
    filename: str
    offset: int
    length: int

    def __repr__(self) -> str:
        return f"<VpkEntry {self.filename!r} ({self.length} bytes)>"

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> VpkEntry:
        out = cls()
        filename_length = binary.read_struct(stream, "I")
        out.filename = stream.read(filename_length).decode(encoding="latin_1")
        # NOTE: no trailing \0
        out.offset, out.length = binary.read_struct(stream, "2I")
        return out


class Vpk(base.Archive):
    ext = "pack*.vpk"
    _file: io.BytesIO
    entries: Dict[str, VpkEntry]

    def __init__(self):
        self.entries = dict()

    def namelist(self) -> List[str]:
        return sorted(self.entries)

    def read(self, filename: str) -> bytes:
        entry = self.entries[filename]
        self._file.seek(entry.offset)
        data = self._file.read(entry.length)
        assert len(data) == entry.length, "unexpected EOF"
        return data

    def sizeof(self, filename: str) -> int:
        return self.entries[filename].length

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Vpk:
        out = cls()
        out._file = stream
        out._file.seek(-9, 2)
        num_entries, dir_offset, version = binary.read_struct(out._file, "2IB")
        assert version in (0, 1), f"unsupported version: {version}"
        # NOTE: if version == 1 the file is only entries, no data
        # -- version is only 1 for pack010.vpk
        # -- might be a flag, rather than a version, but idk
        out._file.seek(dir_offset)
        for i in range(num_entries):
            entry = VpkEntry.from_stream(out._file)
            out.entries[entry.filename] = entry
        return out
