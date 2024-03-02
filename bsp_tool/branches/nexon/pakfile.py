# https://users.cs.jmu.edu/buchhofp/forensics/formats/pkzip-printable.html
from __future__ import annotations
from typing import Any, Dict, List

# import binascii  # crc32 for as_bytes
import io
import os
import struct

from ... import lumps


# NOTE: can't use base.Struct much here, since structures are tight and unaligned


def read_struct(format_: str, stream: io.BytesIO) -> List[Any]:
    return struct.unpack(format_, stream.read(struct.calcsize(format_)))


class FileHeader:
    """preceded by magic CS\x03\x04"""
    unused: int  # always 0
    crc32: int  # of compressed data
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
    offset: int
    header: FileHeader
    path: str
    data: bytes

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} "{self.path}" @ 0x{id(self):016X}>'

    @classmethod
    def from_stream(cls, stream) -> File:
        out = cls()
        out.offset = stream.tell() - 4  # matches FileTailer
        out.header = FileHeader.from_stream(stream)
        out.path = stream.read(out.header.path_size).decode()
        if out.header.compressed_size == 0:
            out.data = stream.read(out.header.uncompressed_size)
        else:
            compressed_data = stream.read(out.header.compressed_size)
            out.data = lumps.decompress_valve_LZMA(compressed_data)
        return out


class Tailer:  # complements header
    """preceded by magic CS\x01\x02"""
    # header
    unknown_1: bytes
    # unused: 2 bytes
    # crc32: int
    # uncompressed_size: int
    # compressed_size: int
    path_size: int
    unknown_2: bytes
    header_offset: int
    # data
    path: str

    def __init__(self, unknown_1, path_size, unknown_2, header_offset, path):
        self.unknown_1 = unknown_1
        self.path_size = path_size
        self.unknown_2 = unknown_2
        self.header_offset = header_offset
        self.path = path

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} "{self.path}" @ 0x{id(self):016X}>'

    def as_bytes(self) -> bytes:
        return b"".join([
            self.unknown_1,
            self.path_size.to_bytes(4, "little"),
            self.unknown_2.to_bytes(2, "little"),
            self.header_offset.to_bytes(4, "little"),
            self.path.encode()])

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> FileHeader:
        unknown_1 = stream.read(14)
        path_size = int.from_bytes(stream.read(4), "little")
        unknown_2 = int.from_bytes(stream.read(2), "little")
        header_offset = int.from_bytes(stream.read(4), "little")
        path = stream.read(path_size).decode()
        return cls(unknown_1, path_size, unknown_2, header_offset, path)


class Terminator:
    """preceded by magic CS\x05\x06"""
    unknown_1: bytes  # always b"\0" * 4?
    num_entries: int
    num_tailers: int
    unknown_2: bytes

    def __init__(self, unknown_1, num_entries, num_tailers, unknown_2):
        self.unknown_1 = unknown_1
        self.num_entries = num_entries
        self.num_tailers = num_tailers
        self.unknown_2 = unknown_2

    def as_bytes(self) -> bytes:
        return b"".join([
            self.unknown_1,
            self.num_entries.to_bytes(2, "little"),
            self.num_tailers.to_bytes(2, "little"),
            self.unknown_2])

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Terminator:
        unknown_1 = stream.read(4)
        num_entries = int.from_bytes(stream.read(2), "little")
        num_tailers = int.from_bytes(stream.read(2), "little")
        unknown_2 = stream.read(13)
        return cls(unknown_1, num_entries, num_tailers, unknown_2)


class PakFile:
    # TODO: make extracted data private
    # TODO: work out system for writing
    entries: Dict[str, File]
    tailers: Dict[str, Tailer]
    terminator: Terminator

    def __init__(self):
        self.entries = dict()
        self.tailers = dict()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} with {len(self.entries)} files @ 0x{id(self):016X}>"

    def extract(self, filename: str, dest_filename: str = None):
        if filename not in self.entries:
            raise FileNotFoundError()
        dest = filename if dest_filename is None else dest_filename
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as out_file:
            out_file.write(self.entries[filename].data)

    def extractall(self, dest_folder: str = "./"):
        for filename in self.entries:
            self.extract(filename, os.path.join(dest_folder, filename))

    def namelist(self) -> List[str]:
        return sorted(self.entries.keys())

    def read(self, path: str) -> bytes:
        return self.entries[path].data

    @classmethod
    def from_bytes(cls, raw_lump: bytes) -> PakFile:
        raw_len = len(raw_lump)
        out = cls()
        stream = io.BytesIO(raw_lump)
        magic = stream.read(4)
        while magic == b"CS\x03\x04":
            entry = File.from_stream(stream)
            out.entries[entry.path] = entry
            magic = stream.read(4)
        while magic == b"CS\x01\x02":
            entry = Tailer.from_stream(stream)
            out.tailers[entry.path] = entry
            magic = stream.read(4)
        assert magic == b"CS\x05\x06"
        out.terminator = Terminator.from_stream(stream)
        assert len(out.entries) == out.terminator.num_entries
        assert len(out.tailers) == out.terminator.num_tailers
        assert stream.tell() == raw_len, "unexpected tail"
        return out

    def as_bytes(self):
        # TODO: preserve entries & tailers orders
        # TODO: generate new tailers
        # TODO: generate new terminator
        return b"".join([
            *[e.as_bytes() for e in self.entries.values()],
            *[t.as_bytes() for t in self.tailers.values()],
            self.terminator.as_bytes()])
