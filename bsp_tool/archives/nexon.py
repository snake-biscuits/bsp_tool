# https://users.cs.jmu.edu/buchhofp/forensics/formats/pkzip-printable.html
from __future__ import annotations
import binascii
import enum
import io
import struct
from typing import Dict, List

from .. import lumps
from ..utils import binary
from . import base


class Hfs(base.Archive):
    ext = "*.hfs"

    def __init__(self, filename: str):
        raise NotImplementedError()


class PakMagic(enum.Enum):
    LocalFile = b"CS\x03\x04"
    CentralDirectory = b"CS\x01\x02"
    EOCD = b"CS\x05\x06"


class PakLocalFile:
    # header
    unused: int
    crc32: int
    compressed_size: int
    uncompressed_size: int
    path_size: int
    # data
    path: str
    data: bytes

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} "{self.path}" @ 0x{id(self):016X}>'

    @classmethod
    def from_stream(cls, stream) -> PakLocalFile:
        out = cls()
        # header
        out.unused = binary.read_struct(stream, "H")
        out.crc32, out.compressed_size, out.uncompressed_size, out.path_size = binary.read_struct(stream, "4I")
        # data
        out.path = stream.read(out.path_size).decode("latin_1")
        if out.compressed_size == 0:
            out.data = stream.read(out.uncompressed_size)
        else:  # grab compressed bytes
            out.data = stream.read(out.compressed_size)  # decompress later
        return out

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
            self.path.encode("latin_1", "strict"),
            data])


class PakCentralDirectory:
    """preceded by magic CS\x01\x02"""
    # NOTE: byte alignment sucks, would try Struct otherwise
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

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> PakCentralDirectory:
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


class PakEOCD:  # End of Central Directory
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

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> PakEOCD:
        out = cls()
        for attr, val in zip(cls.__slots__, binary.read_struct(stream, cls._format)):
            setattr(out, attr, val)
        return out


class PakFile(base.Archive):
    """Nexon's cursed custom pkware.Zip implementation"""
    ext = "*.zip"
    # NOTE: only exists inside .bsp; but it's based on pkware.Zip
    local_files: Dict[str, PakLocalFile]  # contains data
    # metadata
    central_directories: Dict[str, PakCentralDirectory]
    eocd: PakEOCD

    def __init__(self):
        self.local_files = dict()
        self.central_directories = dict()
        self.eocd = PakEOCD()
        # NOTE: these defaults won't nessecarily save to a valid empty PakFile

    def __repr__(self) -> str:
        descriptor = f"{len(self.local_files)} files"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def namelist(self) -> List[str]:
        return sorted(self.local_files.keys())

    def read(self, path: str) -> bytes:
        local_file = self.local_files[path]
        if local_file.compressed_size == 0:
            return local_file.data
        else:  # decompress
            return lumps.decompress_valve_LZMA(local_file.data)

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> PakFile:
        out = cls()
        magic = PakMagic(stream.read(4))
        while magic == PakMagic.LocalFile:
            local_file = PakLocalFile.from_stream(stream)
            out.local_files[local_file.path] = local_file
            magic = PakMagic(stream.read(4))
        while magic == PakMagic.CentralDirectory:
            cd = PakCentralDirectory.from_stream(stream)
            out.central_directories[cd.path] = cd
            magic = PakMagic(stream.read(4))
        assert magic == PakMagic.EOCD
        out.eocd = PakEOCD.from_stream(stream)
        assert len(out.local_files) == out.eocd.num_local_files
        assert len(out.central_directories) == out.eocd.num_central_directories
        return out

    def as_bytes(self):
        # TODO: preserve local_files order (if unedited)
        # TODO: generate new CentralDirectories
        # TODO: generate new EOCD
        return b"".join([
            *[lf.as_bytes() for lf in self.local_files.values()],
            *[cd.as_bytes() for cd in self.central_directories.values()],
            self.eocd.as_bytes()])


class Pkg(base.Archive):
    ext = "*.pkg"

    def __init__(self, filename: str):
        raise NotImplementedError()
