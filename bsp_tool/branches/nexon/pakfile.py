# https://users.cs.jmu.edu/buchhofp/forensics/formats/pkzip-printable.html
from __future__ import annotations
from typing import Any, Dict, List

# import binascii  # crc32 for as_bytes
import io
import struct

from ... import lumps


# NOTE: can't use base.Struct because 2-byte aligned structs


def read_struct(format_: str, stream: io.BytesIO) -> List[Any]:
    return struct.unpack(format_, stream.read(struct.calcsize(format_)))


class FileHeader:
    """preceded by magic CS\x03\x04"""
    unused: int  # always 0
    crc32: int
    compressed_size: int
    uncompressed_size: int
    path_size: int

    def __init__(self, unused, crc32, compressed_size, uncompressed_size, path_size):
        self.unused = unused
        self.crc32 = crc32
        self.compressed_size = compressed_size
        self.uncompressed_size = uncompressed_size
        self.path_size = path_size

    def __repr__(self) -> str:
        args = [
            str(self.unused), f"0x{self.crc32:08X}",
            *map(str, [self.compressed_size, self.uncompressed_size, self.path_size])]
        return f"{self.__class__.__name__}({', '.join(args)})"

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> FileHeader:
        return cls(*read_struct("H", stream), *read_struct("4I", stream))


class File:
    header: FileHeader
    path: str
    data: bytes

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} "{self.path}" @ 0x{id(self):016X}>'

    @classmethod
    def from_stream(cls, stream) -> File:
        out = cls()
        out.header = FileHeader.from_stream(stream)
        out.path = stream.read(out.header.path_size).decode()
        if out.header.compressed_size == 0:
            out.data = stream.read(out.header.uncompressed_size)
        else:
            compressed_data = stream.read(out.header.compressed_size)
            out.data = lumps.decompress_valve_LZMA(compressed_data)
        return out


# TODO: b"CS\x05\x06" EndOfCentralDirectoryRecord  (magic + 21 bytes)
# TODO: b"CS\x01\x02" CentralDirectorFileHeader  (magic + XX bytes + filename)


class PakFile:
    entries: Dict[str, bytes]

    def __init__(self):
        self.entries = dict()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} with {len(self.entries)} files @ 0x{id(self):016X}>"

    def namelist(self) -> List[str]:
        return sorted(self.entries.keys())

    def read(self, path: str) -> bytes:
        return self.entries[path].data

    @classmethod
    def from_bytes(cls, raw_lump: bytes) -> PakFile:
        # raw_len = len(raw_lump)
        out = cls()
        stream = io.BytesIO(raw_lump)
        magic = stream.read(4)
        while magic == b"CS\x03\x04":
            entry = File.from_stream(stream)
            out.entries[entry.path] = entry
            magic = stream.read(4)
        # print(f"{magic=}, {stream.tell()=}, {raw_len=}")
        # TODO: CS\x01\x02 entries (should be just as many as CS\x03\x04)
        # TODO: CS\x05\06 entry (one; should contain number of entries)
        return out

    def as_bytes(self):
        raise NotImplementedError()
