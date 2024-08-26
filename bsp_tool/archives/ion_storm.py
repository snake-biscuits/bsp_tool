"""based on Anachronox DAT File Extractor Version 2 by John Rittenhouse"""
# https://archive.thedatadungeon.com/anachronox_2001/community/datextract2.zip
from __future__ import annotations
import io
from typing import Dict, List
import zlib

from ..branches.base import Struct
from . import base


class Header(Struct):
    magic: bytes  # always b"ADAT"
    fileinfo_offset: int  # offset to fileinfo list
    fileinfo_length: int  # length (in bytes) of fileinfo list
    unknown: int  # always 9? version number?
    __slots__ = ["magic", "fileinfo_offset", "fileinfo_length", "unknown"]
    _format = "4s3I"


class FileInfo(Struct):
    filename: bytes
    offset: int
    length: int  # length of uncompressed data
    compressed_length: int  # uncompressed if 0
    unknown: int  # checksum?
    __slots__ = ["filename", "offset", "length", "compressed_length", "unknown"]
    _format = "128s4I"


class Dat(base.Archive):
    """Used by Anachronox"""
    ext = "*.dat"
    _file: io.BytesIO
    header: Header
    entries: Dict[str, FileInfo]

    def __init__(self):
        self.entries = dict()

    def __repr__(self) -> str:
        descriptor = f"{len(self.entries)} files"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def namelist(self) -> List[str]:
        return sorted(self.entries.keys())

    def read(self, filename: str) -> bytes:
        entry = self.entries[filename]
        self._file.seek(entry.offset)
        if entry.compressed_length == 0:
            data = self._file.read(entry.length)
        else:
            data = zlib.decompress(self._file.read(entry.compressed_length))
        assert len(data) == entry.length
        return data

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Dat:
        out = cls()
        out._file = stream
        out.header = Header.from_stream(out._file)
        assert out.header.magic == b"ADAT", "not a dat file"
        assert out.header.unknown == 9
        assert out.header.fileinfo_length % 144 == 0, "invalid fileinfo_size"
        out._file.seek(out.header.fileinfo_offset)
        for i in range(out.header.fileinfo_length // 144):
            file_info = FileInfo.from_stream(out._file)
            filename = file_info.filename.partition(b"\0")[0].decode()
            out.entries[filename] = file_info
        return out
