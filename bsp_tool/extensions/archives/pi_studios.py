"""Pi Studios Quake Arena Arcade .bpk format"""
from __future__ import annotations
import io
import struct
from typing import List

from ...utils.binary import read_struct
from . import base


class Bpk(base.Archive):
    filename: str
    headers: List[CentralHeader]
    files: List[(LocalHeader, bytes)]

    def __init__(self, filename: str):
        self.filename = filename
        with open(filename, "rb") as bpk_file:
            one, num_headers = struct.unpack(">2I", bpk_file.read(8))
            self.headers = [
                CentralHeader.from_stream(bpk_file)
                for i in range(num_headers)]
            self.files = list()
            for header in self.headers:
                assert header.size >= 0x48
                bpk_file.seek(header.offset)
                local_header = LocalHeader.from_stream(bpk_file)
                data = bpk_file.read(header.size - 0x48)[1:-5]
                # NOTE: trimmed bytes are always 0
                self.files.append((local_header, data))

    def __repr__(self) -> str:
        return f"<BPK '{self.filename}' {len(self.headers)} files @ {id(self):016X}>"

    # TODO: requires filenames (reversing CentralHeader hashes?)

    def extract(self, filename: str, path: str = None) -> str:
        raise NotImplementedError()

    def namelist(self) -> List[str]:
        raise NotImplementedError()

    def read(self, filename: str) -> bytes:
        raise NotImplementedError()


class CentralHeader:
    key: int  # filename hash?
    offset: int
    data_size: int  # matches text length if uncompressed ascii
    size: int

    def __init__(self, key, offset, data_size, size):
        self.key = key
        self.offset = offset
        self.data_size = data_size
        self.size = size

    def __repr__(self) -> str:
        return f"EntryHeader(0x{self.key:016X}, 0x{self.offset:08X}, 0x{self.data_size:06X}, 0x{self.size:06X})"

    def as_bytes(self) -> bytes:
        return struct.pack(">Q4I", self.key, self.offset, self.data_size, 1, self.size)

    @classmethod
    def from_bytes(cls, raw: bytes) -> CentralHeader:
        key, offset, data_size, one, size = struct.unpack(">Q4I", raw)
        assert one == 1
        return cls(key, offset, data_size, size)

    @classmethod
    def from_stream(cls, stream) -> CentralHeader:
        return cls.from_bytes(stream.read(24))


class LocalHeader:
    uncompressed_size: int
    unknown: List[int]
    # 0, 1 & 2 usually all match
    # 3 always FF ?? ?? ??

    def __init__(self, uncompressed_size, *unknown):
        self.uncompressed_size = uncompressed_size
        self.unknown = unknown

    def __repr__(self) -> str:
        plain_args = ", ".join(map(str, [self.uncompressed_size, *self.unknown[:3]]))
        hex_args = ", ".join(f"0x{a:08X}" for a in self.unknown[3:])
        return f"LocalHeader({plain_args}, {hex_args})"

    def as_bytes(self) -> bytes:
        return b"".join([
            b"\x0F\xF5\x12\xEE\x01\x03\x00\x00",
            struct.pack(">5I", 0, 0, 0x8000, 0x8000, 0),
            struct.pack(">I", self.uncompressed_size),
            struct.pack(">I", 0),
            struct.pack(">I", self.unknown[0]),
            struct.pack(">I", 0x8000),
            struct.pack(">7I", *self.unknown[1:])])

    @classmethod
    def from_bytes(cls, raw: bytes) -> LocalHeader:
        assert len(raw) == 0x48
        return cls.from_stream(io.BytesIO(raw))

    @classmethod
    def from_stream(cls, stream) -> LocalHeader:
        assert stream.read(8) == b"\x0F\xF5\x12\xEE\x01\x03\x00\x00"
        assert read_struct(stream, ">5I") == (0, 0, 0x8000, 0x8000, 0)
        uncompressed_size = read_struct(stream, ">I")
        assert read_struct(stream, ">I") == 0
        unknown_1 = read_struct(stream, ">I")
        assert read_struct(stream, ">I") == 0x8000
        unknown_2 = read_struct(stream, ">7I")
        return cls(uncompressed_size, unknown_1, *unknown_2)
