# https://users.cs.jmu.edu/buchhofp/forensics/formats/pkzip-printable.html
from __future__ import annotations
import binascii
import enum
import io
import struct
from typing import Dict, List

from .. import valve
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
        if self.compressed_size != 0:
            data = valve.decompress(self.data)
        else:
            data = self.data
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
    # header
    unused: int  # always 0
    crc32: int
    uncompressed_size: int
    compressed_size: int
    path_size: int
    unknown: int
    header_offset: int  # file offset of LocalFile
    # data
    path: str

    # TODO: __init__(self, local_file: LocalFile, offset: int):

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.path!r} @ 0x{id(self):016X}>'

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> PakCentralDirectory:
        out = cls()
        out.unused = binary.read_struct(stream, "H")
        out.crc32 = binary.read_struct(stream, "I")
        out.uncompressed_size = binary.read_struct(stream, "I")
        out.compressed_size = binary.read_struct(stream, "I")
        out.path_size = binary.read_struct(stream, "I")
        out.unknown = binary.read_struct(stream, "H")
        out.header_offset = binary.read_struct(stream, "I")
        out.path = stream.read(out.path_size).decode("latin_1")
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
            self.path.encode("latin_1")])


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

    def __repr__(self) -> str:
        attrs = ", ".join([
            f"{attr}={getattr(self, attr)!r}"
            for attr in self.__slots__])
        return f"{self.__class__.__name__}({attrs})"

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> PakEOCD:
        out = cls()
        for attr, val in zip(cls.__slots__, binary.read_struct(stream, cls._format)):
            setattr(out, attr, val)
        return out

    def as_bytes(self) -> bytes:
        return struct.pack(self._format, *[
            getattr(self, attr)
            for attr in self.__slots__])


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
            return valve.decompress(local_file.data)

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
        # NOTE: decompresses all data
        out = list()
        # TODO: preserve local_files order (if unedited)
        for local_file in self.local_files.values():
            out.append(PakMagic.LocalFile.value)
            out.append(local_file.as_bytes())
        # TODO: generate new CentralDirectories
        for central_directory in self.central_directories.values():
            out.append(PakMagic.CentralDirectory.value)
            out.append(central_directory.as_bytes())
        # TODO: generate new EOCD
        out.append(PakMagic.EOCD.value)
        out.append(self.eocd.as_bytes())
        # NOTE: no comment, unlike pkware.Zip
        return b"".join(out)


class Pkg(base.Archive):
    ext = "*.pkg"

    def __init__(self, filename: str):
        raise NotImplementedError()
