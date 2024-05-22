"""Pi Studios Quake Arena Arcade .bpk format"""
from __future__ import annotations
import struct
from typing import List

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
    # -- also matches len(data) for some binary files
    size: int

    def __init__(self, key, offset, data_size, size):
        self.key = key
        self.offset = offset
        self.data_size = data_size
        self.size = size

    def __repr__(self) -> str:
        return f"EntryHeader(0x{self.key:016X}, 0x{self.offset:08X}, 0x{self.data_size:06X}, 0x{self.size:06X})"

    @classmethod
    def from_bytes(cls, raw: bytes) -> CentralHeader:
        key, offset, data_size, one, size = struct.unpack(">Q4I", raw)
        assert one == 1
        return cls(key, offset, data_size, size)

    @classmethod
    def from_stream(cls, stream) -> CentralHeader:
        return cls.from_bytes(stream.read(24))


class LocalHeader:
    unknown: List[int]
    # 0..4: ?
    # 5: data_size (len uncompressed ascii / CentralHeader.data_size)
    # 6-15: ?

    def __init__(self, *unknown):
        self.unknown = unknown

    def __repr__(self) -> str:
        return f"LocalHeader({', '.join(map(str, self.unknown))})"

    @classmethod
    def from_bytes(cls, raw: bytes) -> LocalHeader:
        assert len(raw) == 0x48
        assert raw[:0x08] == b"\x0F\xF5\x12\xEE\x01\x03\x00\x00"
        out = cls(*struct.unpack(">16I", raw[0x08:]))
        return out

    @classmethod
    def from_stream(cls, stream) -> LocalHeader:
        return cls.from_bytes(stream.read(0x48))
