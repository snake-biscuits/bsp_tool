from __future__ import annotations
import io
import os
from types import ModuleType
from typing import Dict

from . import base


class File:
    """read-only streamed binary file wrapper"""
    filename: str
    archive: object  # ArchiveClass
    size: int  # filesize in bytes
    _stream: io.BytesIO  # cached file handle

    def __init__(self, filename: str, archive=None):
        self.archive = archive
        self.filename = filename
        self._stream = None

    def __repr__(self) -> str:
        if self.archive is not None:
            descriptor = f"'{self.filename}' in {repr(self.archive)}"
        else:
            descriptor = f"'{self.filename}'"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @property
    def stream(self) -> io.BytesIO:
        """deferring opening the file until it's touched"""
        if self._stream is None:
            if self.archive is None:
                self._stream = open(self.filename, "rb")
            else:
                self._stream = io.BytesIO(self.archive.read(self.filename))
        return self._stream

    # exposed self.stream methods
    def read(self, length: int = -1) -> bytes:
        return self.stream.read(length)

    def readline(self, length: int = -1) -> bytes:
        return self.stream.readline(length)

    def seek(self, offset: int, whence: int = 0) -> int:
        return self.stream.seek(offset, whence)

    def tell(self) -> int:
        return self.stream.tell()

    @classmethod
    def from_archive(cls, filename: str, archive) -> File:
        out = cls(filename, archive)
        out.size = archive.sizeof(filename)
        return out

    @classmethod
    def from_bytes(cls, filename: str, raw_data: bytes) -> File:
        out = cls.from_stream(filename, io.BytesIO(raw_data))
        out.size = len(raw_data)
        return out

    @classmethod
    def from_file(cls, filename: str) -> File:
        out = cls(filename)
        out.size = os.path.getsize(filename)
        return out

    @classmethod
    def from_stream(cls, filename: str, stream: io.BytesIO) -> File:
        out = cls(filename)
        out._stream = stream
        out.size = out._stream.seek(0, 2)
        out._stream.seek(0)
        return out


class LumpOverrides:
    """Like a BspClass, but just for external lump data"""
    # TODO: a system to run bsp methods with specific external lumps mounted
    branch: ModuleType
    endianness: str = "little"
    loading_errors: Dict[str, Exception]
    # ^ {"LUMP_NAME": Error}
    lump_files: Dict[str, File]
    # ^ {"LUMP_NAME": File}  # bsp.extras copy

    def __init__(self):
        self.loading_errors = dict()
        self.lump_files = dict()

    def __repr__(self) -> str:
        descriptor = f"{self.branch.__name__} {len(self.lump_files)} lumps"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def file_lump(self, filename: str, file: File) -> str:
        """matches lump to LUMP.name in self.branch"""
        raise NotImplementedError("subclass has not defined .file_lump()")

    def mount_lump(self, name: str, header: object, file: File):
        """attach lumps with setattr"""
        raise NotImplementedError("subclass has not defined .mount_lump()")

    # TODO: lump_as_bytes
    # TODO: saving to external.File(s)

    @classmethod
    def from_bsp(cls, bsp: base.Bsp) -> LumpOverrides:
        out = cls()
        out.branch = bsp.branch
        out.endianness = bsp.endianness
        # match files to lumps
        out.lump_files = {
            out.file_lump(filename, file): file
            for filename, file in bsp.extras.items()}
        out.lump_files.pop(None)  # RespawnBsp .ent etc.
        # mount lumps
        for lump_name, file in out.lump_files.items():
            header = bsp.headers[lump_name]
            out.mount_lump(lump_name, header, file)
        return out
