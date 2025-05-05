from __future__ import annotations
import io
from typing import Dict, List

from .. import core
from ..utils import binary
from . import base


class Apk(base.Archive):
    ext = "*.apk"
    _file: io.BytesIO
    header: ApkHeader
    entries: Dict[str, ApkEntry]

    def __init__(self):
        self.entries = dict()

    def __repr__(self) -> str:
        descriptor = f"{len(self.entries)} files"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def namelist(self) -> List[str]:
        return sorted(self.entries.keys())

    def read(self, filename: str) -> bytes:
        if filename not in self.namelist():
            raise FileNotFoundError()
        entry = self.entries[filename]
        self._file.seek(entry.offset)
        return self._file.read(entry.length)

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Apk:
        out = cls()
        out.header = ApkHeader.from_stream(stream)
        assert out.header.magic == b"\x57\x23\x00\x00", "not a valid .apk file"
        stream.seek(out.header.dir_offset)
        for i in range(out.header.num_files):
            entry = ApkEntry.from_stream(stream)
            out.entries[entry.filename] = entry
            stream.seek(entry.next_entry_offset)
        out._file = stream
        return out


class ApkEntry:
    filename: str
    offset: int
    length: int
    next_entry_offset: int
    unknown: int  # checksum?

    def __repr__(self) -> str:
        descriptor = f"{self.filename!r} 0x{self.offset:08X}"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> ApkEntry:
        out = cls()
        filename_length = binary.read_struct(stream, "I")
        filename = stream.read(filename_length + 1).decode()
        assert len(filename) == filename_length + 1, "filename ends prematurely"
        assert filename[-1] == "\0", "filename is not zero terminated"
        out.filename = filename[:-1].replace("\\", "/")
        out.offset, out.length, out.next_entry_offset, out.unknown = binary.read_struct(stream, "4I")
        return out


class ApkHeader(core.Struct):
    magic: bytes
    files_offset: int
    num_files: int
    dir_offset: int
    __slots__ = ["magic", "files_offset", "num_files", "dir_offset"]
    _format = "4s3I"
