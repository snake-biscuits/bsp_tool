# https://users.cs.jmu.edu/buchhofp/forensics/formats/pkzip-printable.html
from __future__ import annotations
from typing import Dict, List

import binascii
import enum
import io
import os
import struct

from ... import lumps
from .. import base


class MAGIC(enum.Enum):
    LocalFile = b"CS\x03\x04"
    CentralDirectory = b"CS\x01\x02"
    EOCD = b"CS\x05\x06"


class LocalFile:
    # header
    unused: int
    crc32: int
    compressed_size: int
    uncompressed_size: int
    path_size: int
    # data
    path: str
    data: bytes
    # TODO: use a property for data so we can decompress & keep track of edits

    # TODO: __init__(self, path, data):

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} "{self.path}" @ 0x{id(self):016X}>'

    def as_bytes(self) -> bytes:
        # TODO: compress data (optional)
        data = lumps.decompress_valve_LZMA(self.data) if self.compressed_size != 0 else self.data
        # rebuild header
        crc32 = binascii.crc32(data)
        compressed_size = 0
        uncompressed_size = len(data)
        path_size = len(self.path)
        # assemble bytes
        return b"".join([
            self.unused.to_bytes(2, "little"),
            struct.pack("4I", crc32, compressed_size, uncompressed_size, path_size),
            self.path.encode("ascii", "strict"),
            data])

    @classmethod
    def from_stream(cls, stream) -> LocalFile:
        out = cls()
        # header
        out.unused = int.from_bytes(stream.read(2), "little")
        out.crc32, out.compressed_size, out.uncompressed_size, out.path_size = struct.unpack("4I", stream.read(16))
        # data
        out.path = stream.read(out.path_size).decode()
        if out.compressed_size == 0:
            out.data = stream.read(out.uncompressed_size)
        else:  # grab compressed bytes
            out.data = stream.read(out.compressed_size)  # decompress later
        return out


class CentralDirectory:
    """preceded by magic CS\x01\x02"""
    # NOTE: byte alignment sucks, would try base.Struct otherwise
    # header
    unused: int  # always 0
    crc32: int
    uncompressed_size: int
    compressed_size: int
    path_size: int
    unknown: int
    header_offset: int
    # data
    path: str

    # TODO: __init__(self, local_file: LocalFile, offset: int):

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} "{self.path}" @ 0x{id(self):016X}>'

    def as_bytes(self) -> bytes:
        return b"".join([
            self.unused.to_bytes(2, "little"),
            self.crc32.to_bytes(4, "little"),
            self.uncompressed_size.to_bytes(4, "little"),
            self.compressed_size.to_bytes(4, "little"),
            self.path_size.to_bytes(4, "little"),
            self.unknown.to_bytes(2, "little"),
            self.header_offset.to_bytes(4, "little"),
            self.path.encode()])

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> CentralDirectory:
        out = cls()
        out.unused = int.from_bytes(stream.read(2), "little")
        out.crc32 = int.from_bytes(stream.read(4), "little")
        out.uncompressed_size = int.from_bytes(stream.read(4), "little")
        out.compressed_size = int.from_bytes(stream.read(4), "little")
        out.path_size = int.from_bytes(stream.read(4), "little")
        out.unknown = int.from_bytes(stream.read(2), "little")
        out.header_offset = int.from_bytes(stream.read(4), "little")
        out.path = stream.read(out.path_size).decode()
        return out


class EOCD(base.Struct):  # End of Central Directory
    """preceded by magic CS\x05\x06"""
    unused_1: int  # always 0
    num_local_files: int
    num_central_directories: int
    sizeof_central_directories: int  # 28 * num_central_directories + sum(len(cd.path) for cd in central_directories)
    sizeof_local_files: int  # 22 * num_local_files + sum(len(lf.path) + len(lf.data) for lf in local_files)
    # sizeof_central_directories + sizeof_local_files + 25 == len(raw_lump)
    one: int  # always 1
    unused_2: int  # always 0
    __slots__ = [
        "unused_1", "num_local_files", "num_central_directories",
        "sizeof_central_directories", "sizeof_local_files", "one",
        "unused_2"]
    _format = "I2H3IB"


class PakFile:
    local_files: Dict[str, LocalFile]
    # metadata
    central_directories: Dict[str, CentralDirectory]  # zipfile.ZipInfo equivalent?
    eocd: EOCD

    def __init__(self):
        self.local_files = dict()
        self.central_directories = dict()
        self.eocd = EOCD()  # placeholder; not nessecarily a valid 0 file PakFile

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} with {len(self.local_files)} files @ 0x{id(self):016X}>"

    def extract(self, filename: str, dest_folder: str = "./") -> str:
        if filename not in self.local_files:
            raise FileNotFoundError()
        out_path = os.path.join(dest_folder, filename)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "wb") as out_file:
            out_file.write(self.read(filename))
        return out_path

    def extractall(self, dest_folder: str = "./"):
        for filename in self.local_files:
            self.extract(filename, dest_folder)

    def namelist(self) -> List[str]:
        return sorted(self.local_files.keys())

    def read(self, path: str) -> bytes:
        local_file = self.local_files[path]
        if local_file.compressed_size == 0:
            return local_file.data
        else:  # decompress
            return lumps.decompress_valve_LZMA(local_file.data)

    @classmethod
    def from_bytes(cls, raw_lump: bytes) -> PakFile:
        raw_len = len(raw_lump)
        out = cls()
        stream = io.BytesIO(raw_lump)
        magic = MAGIC(stream.read(4))
        while magic == MAGIC.LocalFile:
            local_file = LocalFile.from_stream(stream)
            out.local_files[local_file.path] = local_file
            magic = MAGIC(stream.read(4))
        while magic == MAGIC.CentralDirectory:
            cd = CentralDirectory.from_stream(stream)
            out.central_directories[cd.path] = cd
            magic = MAGIC(stream.read(4))
        assert magic == MAGIC.EOCD
        out.eocd = EOCD.from_stream(stream)
        assert len(out.local_files) == out.eocd.num_local_files
        assert len(out.central_directories) == out.eocd.num_central_directories
        assert stream.tell() == raw_len, "unexpected tail"
        return out

    def as_bytes(self):
        # TODO: preserve local_files order (if unedited)
        # TODO: generate new CentralDirectories
        # TODO: generate new EOCD
        return b"".join([
            *[lf.as_bytes() for lf in self.local_files.values()],
            *[cd.as_bytes() for cd in self.central_directories.values()],
            self.eocd.as_bytes()])
