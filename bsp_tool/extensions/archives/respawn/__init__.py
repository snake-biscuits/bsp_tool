from __future__ import annotations
import io
import os
from typing import Dict, List, Tuple

from ....utils.binary import read_str, read_struct
from .. import base
from .rpak import RPak


__all__ = ["RPak", "Vpk"]


class Vpk(base.Archive):
    """Titanfall _dir.vpk only!"""
    ext = "*_dir.vpk"
    header: VpkHeader
    files: Dict[str, VpkEntry]
    filename: str
    # TODO: file extraction, need to process LZHAM compression

    def __init__(self, dir_vpk_filename: str, input_stream: io.BytesIO = None) -> Vpk:
        """
        Arguments:

        - dir_vpk_filename -- name of the vpk directory file to parse

        - input_stream     -- IO stream for vpk directory file data (optional)
        """
        self.filename = dir_vpk_filename

        # if no provided input stream, check provided filename for sanity before reading
        if input_stream is None:
            assert os.path.isfile(dir_vpk_filename)
            assert os.path.splitext(dir_vpk_filename)[1] == ".vpk"

            with open(dir_vpk_filename, "rb") as vpk_file:
                self._from_stream(vpk_file)
        else:
            assert not input_stream.closed
            self._from_stream(input_stream)

    def _from_stream(self, vpk_stream: io.BytesIO) -> Vpk:
        # HEADER
        self.header = VpkHeader().from_stream(vpk_stream)
        assert self.header.tree_length != 0, "no files?"
        assert self.header.data_length == 0, "not a _dir.vpk"
        # TREE
        self.files = dict()
        while True:
            extension = read_str(vpk_stream)
            if extension == "":
                break  # end of tree
            while True:
                folder = read_str(vpk_stream)
                if folder == "":
                    break  # end of extension
                while True:
                    filename = read_str(vpk_stream)
                    if filename == "":
                        break  # end of folder
                    full_filename = f"{folder}/{filename}.{extension}"
                    # ENTRY
                    entry = VpkEntry.from_stream(vpk_stream)
                    self.files[full_filename] = entry
        assert vpk_stream.tell() == 16 + self.header.tree_length, "parser overshot tree"
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
            raise NotImplementedError("Cannot target an out folder yet")
        raise NotImplementedError()
        with open(os.path.join("" if path is None else path, filename), "w") as out_file:
            out_file.write(self.read(filename))

    def extractall(self, path=None):
        for file in self.files:
            self.extract(file, path)

    def namelist(self) -> List[str]:
        return sorted(self.files)


class VpkHeader:
    magic: int = 0x55AA1234
    version: Tuple[int, int] = (2, 3)  # major, minor
    tree_length: int
    data_length: int

    def __repr__(self):
        class_name = self.__class__.__name__
        major, minor = self.version
        version = f"v{major}.{minor}"
        return f"<{class_name} (version: {version}, tree_length: {self.tree_length}, data_length: {self.data_length})>"

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> VpkHeader:
        magic, major, minor, tree_length, data_length = read_struct(stream, "I2H2I")
        assert magic == cls.magic, "invalid file magic"
        assert major == cls.version[0], "unsupported major version"
        assert minor == cls.version[1], "unsupported minor version"
        out = cls()
        out.version = (major, minor)
        out.tree_length = tree_length
        out.data_length = data_length
        return out


class VpkEntry:
    crc: int
    preload_length: int
    preload_offset: int
    file_parts: List[VpkFilePart] = list()

    def __repr__(self):
        return f"<{self.__class__.__name__} ({len(self.file_parts)} parts; crc: {self.crc:08X})>"

    @classmethod
    def from_stream(cls, vpk_file: io.BytesIO) -> VpkEntry:
        out = cls()
        out.crc, out.preload_length = read_struct(vpk_file, "IH")
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
    def from_stream(cls, vpk_file: io.BytesIO) -> VpkFilePart:
        out = cls()
        out.archive_index = read_struct(vpk_file, "H")
        if out.archive_index == 0xFFFF:
            out.is_terminator = True
            return out
        out.load_flags = read_struct(vpk_file, "H")
        out.texture_flags = read_struct(vpk_file, "I")
        out.entry_offset, out.entry_length, out.entry_length_uncompressed = read_struct(vpk_file, "3Q")
        out.is_compressed = (out.entry_length != out.entry_length_uncompressed)
        return out
