from __future__ import annotations
import io
from typing import Any
import zipfile

from . import base


class Zip(zipfile.ZipFile, base.Archive):
    ext = "*.zip"
    _buffer: io.BytesIO  # copy of raw data as a byte stream

    def __init__(self, file_: Any = None, mode: str = "a", **kwargs):
        # wrapping ZipFile.__init__ so we always have the raw bytes & can init w/ no args
        # this specific implementation is meant to comply w/ the needs of valve.source PAKFILE
        # since I only feel like implementing a zipfile w/ .from_bytes once
        if file_ is None:  # create an empty zipfile
            empty_zip = [b"PK\x05\x06", b"\x00" * 16, b"\x20\x00XZP1 0", b"\x00" * 26]
            self._buffer = io.BytesIO(b"".join(empty_zip))
        elif isinstance(file_, io.BytesIO):  # BspClass will take this route via .from_bytes()
            self._buffer = file_
        elif isinstance(file_, str):  # save a copy of source file bytes if initialising from file
            self._buffer = io.BytesIO(open(file_, "rb").read())
        else:
            raise TypeError(f"Cannot create {self.__class__.__name__} from type '{type(file_)}'")
        super().__init__(self._buffer, mode=mode, **kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {len(self.namelist())} files mode='{self.mode}' @ 0x{id(self):016X}>"

    def as_bytes(self) -> bytes:
        # write ending records if edits were made (adapted from ZipFile.close)
        if self.mode in "wxa" and self._didModify and self.fp is not None:
            with self._lock:
                if self._seekable:
                    self.fp.seek(self.start_dir)
                self._write_end_record()
        self._didModify = False  # don't double up when .close() is called
        # NOTE: .close() can get funky but it's OK because ._buffer isn't a real file
        return self._buffer.getvalue()

    def sizeof(self, filename: str) -> int:
        return self.getinfo(filename).file_size

    @classmethod
    def from_bytes(cls, raw_lump: bytes) -> Zip:
        return cls(io.BytesIO(raw_lump))

    @classmethod
    def from_file(cls, filename: str) -> Zip:
        return cls(filename)

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Zip:
        return cls(stream)
