"""Pi Studios Quake Arena Arcade .bpk format"""
from __future__ import annotations
import io
import struct
from typing import List

from .. import core
from ..utils import binary
from . import base


class Bpk(base.Archive):
    ext = "*.bpk"
    headers: List[CentralHeader]
    files: List[(LocalHeader, bytes)]

    def __init__(self):
        self.headers = list()
        self.files = list()

    def __repr__(self) -> str:
        descriptor = f"{len(self.headers)} files"
        return f"<{self.__class__.__name__} {descriptor} @ {id(self):016X}>"

    def namelist(self) -> List[str]:
        # TODO: get filenames somehow
        # -- reverse hashes in CentralHeader?
        raise NotImplementedError()

    def read(self, filename: str) -> bytes:
        raise NotImplementedError()

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Bpk:
        out = cls()
        one, num_headers = binary.read_struct(stream, ">2I")
        out.headers = [
            CentralHeader.from_stream(stream)
            for i in range(num_headers)]
        assert all(ch.one == 1 for ch in out.headers)
        for header in out.headers:
            assert header.size >= 0x48
            stream.seek(header.offset)
            local_header = LocalHeader.from_stream(stream)
            data = stream.read(header.size - 0x48)[1:-5]
            # NOTE: trimmed bytes are always 0
            out.files.append((local_header, data))
        return out


class CentralHeader(core.Struct):
    key: int  # filename hash?
    offset: int
    data_size: int  # matches text length if uncompressed plaintext
    one: int  # always 1
    size: int
    __slots__ = ["key", "offset", "data_size", "one", "size"]
    _format = ">Q4I"

    def __repr__(self) -> str:
        attrs = ", ".join([
            f"key=0x{self.key:016X}",
            f"offset=0x{self.offset:08X}",
            f"data_size=0x{self.data_size:06X}",
            f"one={self.one}",
            f"size=0x{self.size:06X}"])
        return f"EntryHeader({attrs})"


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
        assert binary.read_struct(stream, ">5I") == (0, 0, 0x8000, 0x8000, 0)
        uncompressed_size = binary.read_struct(stream, ">I")
        assert binary.read_struct(stream, ">I") == 0
        unknown_1 = binary.read_struct(stream, ">I")
        assert binary.read_struct(stream, ">I") == 0x8000
        unknown_2 = binary.read_struct(stream, ">7I")
        return cls(uncompressed_size, unknown_1, *unknown_2)
