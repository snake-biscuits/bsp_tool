from __future__ import annotations
from collections import namedtuple
import io
from typing import Dict, List

from . import base
from ..utils import binary


ApkHeader = namedtuple("ApkHeader", ["id", "files_offset", "file_count", "dir_offset"])


class Apk(base.Archive):
    ext = "*.apk"
    _file: io.BufferedReader  # keep file open for extraction
    files: Dict[str, ApkEntry]

    def __init__(self, apk_filename: str):
        self.files = dict()

    def __del__(self):
        self._file.close()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._file.name}>"

    def namelist(self) -> List[str]:
        return sorted(self.files.keys())

    def read(self, filename: str) -> bytes:
        if filename not in self.files:
            raise FileNotFoundError()
        entry = self.files[filename]
        self._file.seek(entry.data_offset)
        return self._file.read(entry.data_size)

    @classmethod
    def from_file(cls, filename: str) -> Apk:
        out = cls()
        out._file = open(filename, "rb")
        out.header = ApkHeader(*binary.read_struct(out._file, "4s3I"))
        assert out.header.id == b"\x57\x23\x00\x00", "not a valid .apk file"
        out._file.seek(out.header.dir_offset)
        for i in range(out.header.file_count):
            entry = ApkEntry.from_stream(out._file)
            out.files[entry.path] = entry
            out._file.seek(entry.next_entry_offset)
        return out


class ApkEntry:
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.path} @ 0x{self.data_offset:016X}>"

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> int:
        out = cls()
        path_len = binary.read_struct(stream, "I")
        path = stream.read(path_len + 1).decode()
        assert len(path) == path_len + 1, "path string ends prematurely"
        assert path[-1] == "\0", "path string is not zero terminated"
        out.path = path[:-1].replace("\\", "/")
        out.data_offset, out.data_size, out.next_entry_offset, out.unknown = binary.read_struct(stream, "4I")
        return out
