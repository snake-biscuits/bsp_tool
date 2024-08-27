# https://github.com/ValvePython/vpk
from __future__ import annotations
import io
from typing import Dict, List, Union

from ..branches.base import Struct
from ..utils import binary
from . import base


class VpkHeader(Struct):
    magic: int  # should always be 0x55AA1234
    version: List[int]  # should always be (1, 0)
    tree_length: int
    __slots__ = ["magic", "version", "tree_length"]
    _format = "I2HI"
    _arrays = {"version": ["major", "minor"]}


class VpkHeaderv2(Struct):
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


class VpkEntry(Struct):
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
    versions = {
        (1, 0): VpkHeader,
        (2, 0): VpkHeaderv2}
    _file: io.BytesIO
    header: Union[VpkHeader, VpkHeaderv2]
    entries: Dict[str, VpkEntry]
    preload_offset: Dict[str, int]
    # TODO: is_dir property

    def __init__(self):
        self.entries = dict()
        self.preload_offset = dict()

    def __repr__(self) -> str:
        descriptor = f"{len(self.entries)} files"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def namelist(self) -> List[str]:
        return sorted(self.entries)

    def read(self, filename: str) -> bytes:
        assert filename in self.namelist()
        raise NotImplementedError("Need to know if this .vpk is a _dir.vpk")
        # if self.is_dir:
        #     raise NotImplementedError("cannot read files inside *_dir.vpk yet")
        #     # TODO: need access to f"{filename}_000.vpk" etc.
        # else:
        #     raise NotImplementedError("cannot read files inside *.vpk yet")

    # TODO: failing to parse "The Ship | depot_2402_dir.vpk"
    # -- which contains maps & loads just fine in GCFScape
    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Vpk:
        out = cls()
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
                    entry_path = f"{folder}/{filename}.{extension}"
                    entry = VpkEntry.from_stream(out._file)
                    assert binary.read_struct(out._file, "H") == 0xFFFF
                    if entry.archive_index == 0x7FFF:
                        entry.archive_offset += end_of_tree
                    out.entries[entry_path] = entry
                    out.preload_offset[entry_path] = out._file.tell()
                    out._file.seek(entry.preload_length, 1)
        assert out._file.tell() == end_of_tree, "overshot tree"
        return out
