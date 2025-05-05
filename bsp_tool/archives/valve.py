# https://github.com/ValvePython/vpk
from __future__ import annotations
import fnmatch
import io
import os
from typing import Dict, List, Union

from .. import core
from .. import external
from ..utils import binary
from . import base


class VpkHeader(core.Struct):
    magic: int  # should always be 0x55AA1234
    version: List[int]  # should always be (1, 0)
    tree_length: int
    __slots__ = ["magic", "version", "tree_length"]
    _format = "I2HI"
    _arrays = {"version": ["major", "minor"]}


class VpkHeaderv2(core.Struct):
    # attributed to http://forum.xentax.com/viewtopic.php?f=10&t=11208
    magic: int  # should always be 0x55AA1234
    version: List[int]  # should always be (1, 0)
    tree_length: int
    # new in v2.0
    embed_chunk_length: int
    chunk_hashes_length: int
    self_hashes_length: int  # always 48
    signature_length: int
    __slots__ = [
        "magic", "version", "tree_length",
        "embed_chunk_length", "chunk_hashes_length",
        "self_hashes_length", "signature_length"]
    _format = "I2H5I"
    _arrays = {"version": ["major", "minor"]}
    # NOTE: v2 has embed_chunk & chunk hashes after tree
    # -- followed by MD5 char[16] checksums for tree, chunk_hashes & file


class VpkEntry(core.Struct):
    crc: int  # CRC32 hash
    preload_length: int  # length of preload data
    archive_index: int
    archive_offset: int  # if archive_index == 0x7FFF: + end of tree
    file_length: int
    __slots__ = [
        "crc", "preload_length", "archive_index",
        "archive_offset", "file_length"]
    _format = "I2H2I"


class Vpk(base.Archive):
    ext = "*.vpk"
    _file: io.BytesIO
    header: Union[VpkHeader, VpkHeaderv2]
    entries: Dict[str, VpkEntry]
    extras: Dict[str, external.File]
    filename: str
    preload_offset: Dict[str, int]
    versions = {
        (1, 0): VpkHeader,
        (2, 0): VpkHeaderv2}

    def __init__(self, filename: str = "untitiled.vpk"):
        self.entries = dict()
        self.extras = dict()
        self.filename = filename
        self.preload_offset = dict()
        # "*_dir.vpk" -> "*"
        if self.filename.endswith("_dir.vpk"):
            self.base_filename = self.filename[:-len("_dir.vpk")]
        else:
            self.base_filename = None

    def __repr__(self) -> str:
        descriptor = f"{len(self.entries)} files"
        return f"<{self.__class__.__name__} '{self.filename}' {descriptor} @ 0x{id(self):016X}>"

    def extra_patterns(self) -> str:
        if self.filename.endswith("_dir.vpk"):
            return [
                f"{self.base_filename}_{index:03d}.vpk"
                for index in {
                    e.archive_index
                    for e in self.entries.values()
                    if e.archive_index != 0x7FFF}]
        else:
            return list()

    def namelist(self) -> List[str]:
        return sorted(self.entries)

    def read(self, filename: str) -> bytes:
        assert filename in self.namelist()
        # raise NotImplementedError("Need to know if this .vpk is a _dir.vpk")
        entry = self.entries[filename]
        if entry.archive_index != 0x7FFF:
            assert self.filename.endswith("_dir.vpk")
            stream = self.archive_vpk(entry.archive_index)
        else:
            stream = self._file
        stream.seek(entry.archive_offset)
        data = stream.read(entry.file_length)
        assert len(data) == entry.file_length, "unexpected EOF"
        return data

    def archive_vpk(self, index: int) -> external.File:
        assert self.filename.endswith("_dir.vpk"), "not a _dir.vpk"
        return self.extras[f"{self.base_filename}_{index:03d}.vpk"]

    @classmethod
    def from_archive(cls, parent_archive: base.Archive, filename: str) -> Vpk:
        """for ArchiveClasses composed of multiple files"""
        folder, short_filename = os.path.split(filename)
        archive = cls.from_bytes(parent_archive.read(filename), short_filename)
        extras = [
            filename
            for filename in parent_archive.listdir(folder)
            for pattern in archive.extra_patterns()
            if fnmatch.fnmatch(filename.lower(), pattern.lower())]
        for filename in extras:
            full_filename = os.path.join(folder, filename)
            external_file = external.File.from_archive(full_filename, parent_archive)
            archive.mount_file(filename, external_file)
        return archive

    @classmethod
    def from_bytes(cls, raw_archive: bytes, filename: str = "untitled.vpk") -> Vpk:
        return cls.from_stream(io.BytesIO(raw_archive), filename)

    @classmethod
    def from_file(cls, filename: str) -> Vpk:
        folder, short_filename = os.path.split(filename)
        archive = cls.from_stream(open(filename, "rb"), short_filename)
        extras = [
            filename
            for filename in os.listdir(folder)
            for pattern in archive.extra_patterns()
            if fnmatch.fnmatch(filename.lower(), pattern.lower())]
        for filename in extras:
            full_filename = os.path.join(folder, filename)
            external_file = external.File.from_file(full_filename)
            archive.mount_file(filename, external_file)
        return archive

    @classmethod
    def from_stream(cls, stream: io.BytesIO, filename: str = "untitled.vpk") -> Vpk:
        out = cls(filename)
        out._file = stream
        # verify magic
        magic = binary.read_struct(out._file, "I")
        assert magic == 0x55AA1234
        # get structs for this version
        version = binary.read_struct(out._file, "2H")
        if version not in cls.versions:
            version_str = ".".join(map(str, version))
            raise NotImplementedError(f"Vpk v{version_str} is not supported")
        HeaderClass = cls.versions[version]
        # header
        out._file.seek(0)
        out.header = HeaderClass.from_stream(out._file)
        end_of_tree = len(out.header.as_bytes()) + out.header.tree_length
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
                    # entry
                    if folder != " ":  # not in root folder
                        entry_path = f"{folder}/{filename}.{extension}"
                    else:
                        entry_path = f"{filename}.{extension}"
                    entry = VpkEntry.from_stream(out._file)
                    assert binary.read_struct(out._file, "H") == 0xFFFF
                    if entry.archive_index == 0x7FFF:
                        entry.archive_offset += end_of_tree
                    out.entries[entry_path] = entry
                    out.preload_offset[entry_path] = out._file.tell()
                    out._file.seek(entry.preload_length, 1)
        assert out._file.tell() == end_of_tree, "overshot tree"
        return out
