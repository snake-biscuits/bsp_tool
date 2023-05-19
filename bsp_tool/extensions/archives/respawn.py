# https://github.com/barnabwhy/TFVPKTool
from __future__ import annotations
from collections import namedtuple
import os
import struct
from typing import Dict, List

from . import base


def read_str(binary_stream, encoding="utf-8", errors="strict") -> str:
    """for tree parsing"""
    out = b""
    c = binary_stream.read(1)
    while c != b"\0":
        out += c
        c = binary_stream.read(1)
    return out.decode(encoding, errors)


VpkHeader = namedtuple("VpkHeader", ["magic", "version_major", "version_minor", "tree_length", "data_length"])


class Vpk(base.Archive):
    """Titanfall .vpk only!"""
    header: VpkHeader
    files: Dict[str, VpkEntry]
    filename: str
    # TODO: file extraction, need to process LZHAM compression

    def __init__(self, dir_vpk_filename: str) -> Vpk:
        assert os.path.isfile(dir_vpk_filename)
        assert os.path.splitext(dir_vpk_filename)[1] == ".vpk"
        self.filename = dir_vpk_filename
        with open(dir_vpk_filename, "rb") as vpk_file:
            # HEADER
            self.header = VpkHeader(*struct.unpack("I2H2I", vpk_file.read(16)))
            assert self.header.magic == 0x55AA1234, "invalid file magic"
            assert self.header.version_major == 2, "unsupported major version"
            assert self.header.version_minor == 3, "unsupported minor version"
            assert self.header.tree_length != 0, "no files?"
            assert self.header.data_length == 0, "not a _dir.vpk"
            # TREE
            self.files = dict()
            while True:
                extension = read_str(vpk_file)
                if extension == "":
                    break  # end of tree
                while True:
                    folder = read_str(vpk_file)
                    if folder == "":
                        break  # end of extension
                    while True:
                        filename = read_str(vpk_file)
                        if filename == "":
                            break  # end of folder
                        full_filename = f"{folder}/{filename}.{extension}"
                        # ENTRY
                        entry = VpkEntry.from_stream(vpk_file)
                        self.files[full_filename] = entry
            assert vpk_file.tell() == 16 + self.header.tree_length, "parser overshot tree"
            # DATA
            # either locally stored, or in external numbered vpks
            # NOTE: we don't care about mapping OR extracting data, just here for the filelist

    def __repr__(self):
        return f'{self.__class__.__name__}.from_file("{self.filename}")'

    def read(self, filename: str) -> bytes:
        assert filename in self.files
        # TODO: look up data tied to this entry, patch it all together and return it
        raise NotImplementedError()

    def extract(self, filename: str, path=None):
        assert filename in self.files
        if path is not None:
            raise NotImplementedError("Cannot target a out folder yet")
        raise NotImplementedError()
        with open(os.path.join("" if path is None else path, filename), "w") as out_file:
            out_file.write(self.read(filename))

    def extractall(self, path=None):
        for file in self.files:
            self.extract(file, path)

    def namelist(self) -> List[str]:
        return sorted(self.files)


class VpkEntry:
    crc: int
    preload_length: int
    preload_offset: int
    file_parts: List[VpkFilePart] = list()

    def __repr__(self):
        return f"<{self.__class__.__name__} ({len(self.file_parts)} parts; crc: {self.crc:08X})>"

    @classmethod
    def from_stream(cls, vpk_file) -> VpkEntry:
        out = cls()
        out.crc, out.preload_length = struct.unpack("IH", vpk_file.read(6))
        # file parts
        file_part = VpkFilePart.from_stream(vpk_file)
        while not file_part.is_terminator:
            out.file_parts.append(file_part)
            file_part = VpkFilePart.from_stream(vpk_file)
        out.preload_offset = vpk_file.tell()
        vpk_file.seek(out.preload_length, 1)  # skip preload data
        return out


class VpkFilePart:
    is_terminator: bool = False
    archive_index: int
    load_flags: int = 0  # TODO: enum
    texture_flags: int = 0  # TODO: enum
    entry_offset: int = 0
    entry_length: int = 0
    entry_length_uncompressed: int = 0
    is_compressed: bool = False

    @classmethod
    def from_stream(cls, vpk_file) -> VpkFilePart:
        out = cls()
        out.archive_index = int.from_bytes(vpk_file.read(2), "little")
        if out.archive_index == 0xFFFF:
            out.is_terminator = True
            return out
        out.load_flags = int.from_bytes(vpk_file.read(2), "little")  # uint16_t
        out.texture_flags = int.from_bytes(vpk_file.read(4), "little")  # uint32_t
        out.entry_offset, out.entry_length, out.entry_length_uncompressed = struct.unpack("3Q", vpk_file.read(24))
        out.is_compressed = (out.entry_length != out.entry_length_uncompressed)
        return out
