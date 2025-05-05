"""based on Anachronox DAT File Extractor Version 2 by John Rittenhouse"""
# https://archive.thedatadungeon.com/anachronox_2001/community/datextract2.zip
from __future__ import annotations
import io
from typing import Dict, List
import zlib

from .. import core
from ..utils import binary
from . import base
from . import id_software


class DatHeader(core.Struct):
    magic: bytes  # always b"ADAT"
    fileinfo_offset: int  # offset to fileinfo list
    fileinfo_length: int  # length (in bytes) of fileinfo list
    unknown: int  # always 9? version number?
    __slots__ = ["magic", "fileinfo_offset", "fileinfo_length", "unknown"]
    _format = "4s3I"


class DatFileInfo(core.Struct):
    filename: bytes
    offset: int
    length: int  # length of uncompressed data
    compressed_length: int  # uncompressed if 0
    unknown: int  # checksum?
    __slots__ = ["filename", "offset", "length", "compressed_length", "unknown"]
    _format = "128s4I"


class Dat(base.Archive):
    """Used by Anachronox"""
    ext = "*.dat"
    _file: io.BytesIO
    header: DatHeader
    entries: Dict[str, DatFileInfo]

    def __init__(self):
        self.entries = dict()

    def __repr__(self) -> str:
        descriptor = f"{len(self.entries)} files"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def namelist(self) -> List[str]:
        return sorted(self.entries.keys())

    def read(self, filename: str) -> bytes:
        entry = self.entries[filename]
        self._file.seek(entry.offset)
        if entry.compressed_length == 0:
            data = self._file.read(entry.length)
        else:
            data = zlib.decompress(self._file.read(entry.compressed_length))
        assert len(data) == entry.length
        return data

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Dat:
        out = cls()
        out._file = stream
        out.header = DatHeader.from_stream(out._file)
        assert out.header.magic == b"ADAT", "not a dat file"
        assert out.header.unknown == 9
        assert out.header.fileinfo_length % 144 == 0, "invalid fileinfo_size"
        out._file.seek(out.header.fileinfo_offset)
        for i in range(out.header.fileinfo_length // 144):
            file_info = DatFileInfo.from_stream(out._file)
            filename = file_info.filename.partition(b"\0")[0].decode()
            out.entries[filename] = file_info
        return out


class PakFileEntry(core.Struct):
    filename: bytes  # can contain multiple filenames
    # for maps, looks to be attached scripts
    # use filename.strip(b"\0").split(b"\0") to get the list
    offset: int
    length: int
    compressed_length: int
    is_compressed: int
    __slots__ = [
        "filename", "offset", "length",
        "compressed_length", "is_compressed"]
    _format = "56s4I"
    _classes = {"is_compressed": bool}


class Pak(id_software.Pak):
    # https://github.com/yquake2/pakextract
    ext = "*.pak"
    _file: io.BytesIO
    entries: Dict[str, PakFileEntry]

    def decompress(self, entry: PakFileEntry) -> bytes:
        """average time to decompress is ~1min per MB"""
        # https://github.com/yquake2/pakextract/blob/master/pakextract.c#L254
        out = b""
        self._file.seek(entry.offset)
        while self._file.tell() < entry.offset + entry.compressed_length:
            x = int.from_bytes(self._file.read(1))
            if x < 64:
                out += self._file.read(x + 1)
            elif x < 128:
                out += b"\x00" * (x - 62)
            elif x < 192:
                out += self._file.read(1) * (x - 126)
            elif x < 255:
                ptr = int.from_bytes(self._file.read(1)) + 1
                out += out[-ptr].to_bytes(1) * (x - 190)
            else:  # x == 255
                break  # terminator
        else:
            raise RuntimeError("no terminator at end of compressed data")
        assert len(out) == entry.length
        return out

    def read(self, filename: str) -> bytes:
        if filename not in self.entries:
            raise FileNotFoundError(f"{filename!r} is not in this Pak")
        entry = self.entries[filename]
        self._file.seek(entry.offset)
        if not entry.is_compressed:
            return self._file.read(entry.length)
        else:
            return self.decompress(entry)

    def namelist(self) -> List[str]:
        return sorted(self.entries.keys())

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Pak:
        out = cls()
        out._file = stream
        assert out._file.read(4) == b"PACK", "not a .pak file"
        # file table
        offset, length = binary.read_struct(out._file, "2I")
        sizeof_entry = len(PakFileEntry().as_bytes())
        assert length % sizeof_entry == 0, "unexpected file table size"
        out._file.seek(offset)
        out.entries = {
            entry.filename.partition(b"\0")[0].decode("ascii"): entry
            for entry in [
                PakFileEntry.from_stream(out._file)
                for i in range(length // sizeof_entry)]}
        return out
