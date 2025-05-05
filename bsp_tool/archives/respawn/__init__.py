from __future__ import annotations
import io
from typing import Dict, List

from ... import core
from ...utils import binary
from .. import valve
from .rpak import RPak


__all__ = ["RPak", "Vpk", "VpkHeader", "VpkEntry", "VpkFilePart"]


class VpkHeader(core.Struct):
    magic: int  # should always be 0x55AA1234
    version: List[int]  # should always be (2, 3)
    tree_length: int
    data_length: int
    __slots__ = ["magic", "version", "tree_length", "data_length"]
    _format = "I2H2I"
    _arrays = {"version": ["major", "minor"]}


class VpkEntry:
    crc: int
    preload_offset: int
    preload_length: int
    file_parts: List[VpkFilePart]
    # properties
    is_compressed: bool = property(lambda s: any(fp.is_compressed for fp in s.file_parts))

    def __init__(self):
        self.file_parts = list()

    def __repr__(self):
        descriptor = f"{len(self.file_parts)} parts crc=0x{self.crc:08X}"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> VpkEntry:
        out = cls()
        out.crc, out.preload_length = binary.read_struct(stream, "IH")
        # file parts
        file_part = VpkFilePart.from_stream(stream)
        while not file_part.is_terminator:
            out.file_parts.append(file_part)
            file_part = VpkFilePart.from_stream(stream)
        out.preload_offset = stream.tell()
        stream.seek(out.preload_length, 1)  # skip preload data
        return out


class VpkFilePart:
    archive_index: int
    load_flags: int  # TODO: enum.IntFlag
    texture_flags: int  # TODO: enum.IntFlag
    offset: int
    compressed_length: int
    length: int
    # properties
    is_terminator: bool = property(lambda s: s.archive_index == 0xFFFF)
    is_compressed: bool = property(lambda s: s.compressed_length != s.length)

    def __repr__(self) -> str:
        descriptor = f"{self.length} bytes"
        if self.is_compressed:
            descriptor += " (compressed)"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> VpkFilePart:
        out = cls()
        out.archive_index = binary.read_struct(stream, "H")
        if out.archive_index == 0xFFFF:  # terminator
            return out  # don't read any further!
        out.load_flags = binary.read_struct(stream, "H")
        out.texture_flags = binary.read_struct(stream, "I")
        out.offset = binary.read_struct(stream, "Q")
        out.compressed_length = binary.read_struct(stream, "Q")
        out.length = binary.read_struct(stream, "Q")
        return out


class Vpk(valve.Vpk):
    """*_dir.vpk only!"""
    ext = "*_dir.vpk"
    base_filename: str
    _file: io.BytesIO
    filename: str
    header: VpkHeader
    entries: Dict[str, VpkEntry]
    # NOTE: 'versions' is unused; only v2.3 is supported

    def __init__(self, filename: str = "untitled_dir.vpk"):
        super().__init__(filename)
        # "<language>client_*_dir.vpk" -> "client_*"
        assert self.filename.endswith("_dir.vpk")
        language_length = filename.find("client_")
        assert language_length != -1
        self.base_filename = self.filename[language_length:-len("_dir.vpk")]

    def extra_patterns(self) -> str:
        return [f"{self.base_filename}_*.vpk"]
        # NOTE: accurate, but very slow
        # return [
        #     f"{self.base_filename}_{index:03d}.vpk"
        #     for index in {
        #         file_part.archive_index
        #         for entry in self.entries.values()
        #         for file_part in entry.file_parts}]

    def read(self, filename: str) -> bytes:
        assert filename in self.namelist()
        entry = self.entries[filename]
        if entry.is_compressed:
            raise NotImplementedError("cannot decompress, yet.")
            # TODO: lzham decompress the compressed file_parts
        parts = list()
        for file_part in entry.file_parts:
            stream = self.archive_vpk(file_part.archive_index)
            stream.seek(file_part.offset)
            data = stream.read(file_part.length)
            assert len(data) == file_part.length, "unexpected EOF"
            parts.append(data)
        return b"".join(parts)

    def sizeof(self, filename: str) -> int:
        return sum(fp.length for fp in self.entries[filename].file_parts)

    @classmethod
    def from_stream(cls, stream: io.BytesIO, filename: str = "untitled_dir.vpk") -> Vpk:
        out = cls(filename)
        out._file = stream
        # header
        out.header = VpkHeader.from_stream(out._file)
        assert out.header.magic == 0x55AA1234
        version = tuple(out.header.version)
        if version != (2, 3):
            version_str = ".".join(map(str, version))
            raise NotImplementedError(f"Vpk v{version_str} is not supported")
        # tree
        assert out.header.tree_length != 0, "no files?"
        while True:
            extension = binary.read_str(out._file, encoding="latin_1")
            if extension == "":
                break  # end of tree
            while True:
                folder = binary.read_str(out._file, encoding="latin_1")
                if folder == "":
                    break  # end of extension
                while True:
                    filename = binary.read_str(out._file, encoding="latin_1")
                    if filename == "":
                        break  # end of folder
                    if folder != " ":  # not in root folder
                        entry_path = f"{folder}/{filename}.{extension}"
                    else:
                        entry_path = f"{filename}.{extension}"
                    out.entries[entry_path] = VpkEntry.from_stream(out._file)
                    # NOTE: we don't save preload, unlike valve.Vpk
        assert out._file.tell() == 16 + out.header.tree_length, "overshot tree"
        return out
