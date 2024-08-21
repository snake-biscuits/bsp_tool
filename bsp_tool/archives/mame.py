# https://github.com/mamedev/mame/blob/master/src/lib/util/chd.h
from __future__ import annotations
import enum
import io
from typing import Dict, List

from . import base
from ..branches.base import Struct
from ..utils import binary


# from src/lib/util/chdcodec.cpp (codec_entry f_codec_list[])
compressor_codecs = {
    b"avhu": "A/V Huffman",
    b"cdfl": "CD FLAC",
    b"cdlz": "CD LZMA",  # in test GD-ROM
    b"cdzl": "CD Deflate",  # in test GD-ROM
    b"cdzs": "CD Zstandatd",  # in test GD-ROM
    b"flac": "FLAC",
    b"huff": "Huffman",
    b"lzma": "LZMA",
    b"zlib": "Deflate",
    b"zstd": "Zstandard"}


class ChdHeaderv5(Struct):
    compressors: List[bytes]
    logical_bytes: int
    map_offset: int
    meta_offset: int
    hunk_bytes: int
    unit_bytes: int
    sha1: List[bytes]
    # sha1.raw: bytes  # SHA1 of raw data
    # sha1.combined: bytes  # SHA1 of raw data + metadata
    # sha1.parent: bytes  # SHA1 of parent's raw data + metadata; 0 if no parent

    __slots__ = [
        "compressors", "logical_bytes", "map_offset", "meta_offset",
        "hunk_bytes", "unit_bytes", "sha1"]
    _format = ">4s4s4s4s3Q2I20s20s20s"
    _arrays = {"compressors": 4, "sha1": ["raw", "combined", "parent"]}


# from src/lib/util/chd.h
metadata_type = {
    b"AVAV": "A/V",
    b"AVLD": "A/V Laserdisc",
    b"CHCD": "CD-ROM (Old)",
    b"CHGD": "GD-ROM Track",
    b"CHGT": "GD-ROM (Old)",
    b"CHT2": "CD-ROM Track (2)",
    b"CHTR": "CD-ROM Track",
    b"CIS ": "PCMIA CIS",
    b"DVD ": "DVD",
    b"GDDD": "Hard Disk",
    b"IDNT": "Hard Disk Identifier",
    b"KEY ": "Hard Disk Key"}


class MetadataFlag(enum.IntFlag):
    NONE = 0x00
    CHECKSUM = 0x01  # data is checksummed


class Metadata:
    magic: bytes
    flags: MetadataFlag
    next: int  # offset to next metadata entry?
    keyvalues: Dict[str, str]

    def __repr__(self) -> str:
        descriptor = f"[{metadata_type[self.magic]}]"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Metadata:
        out = cls()
        out.magic = binary.read_struct(stream, "4s")
        assert out.magic in metadata_type, f"Unknown magic: {out.magic!r}"
        flags_and_length, out.next = binary.read_struct(stream, ">IQ")
        # big-endian support in BitField would be great rn...
        out.flags = MetadataFlag(flags_and_length >> 24)
        length = flags_and_length & 0x00FFFFFF
        text = stream.read(length)
        assert text.endswith(b"\x00")
        text = text[:-1].decode()
        out.keyvalues = dict([kv.split(":") for kv in text.split(" ")])
        return out


class CompressedMapv5:
    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> CompressedMapv5:
        raise NotImplementedError()
        out = cls()
        # [  0] uint32_t  length;          // length of compressed map
        # [  4] UINT48    datastart;       // offset of first block
        # [ 10] uint16_t  crc;             // crc-16 of the map
        # [ 12] uint8_t   lengthbits;      // bits used to encode complength
        # [ 13] uint8_t   hunkbits;        // bits used to encode self-refs
        # [ 14] uint8_t   parentunitbits;  // bits used to encode parent unit refs
        # [ 15] uint8_t   reserved;        // future use
        # Huffman Decompress Map Entries
        return out


class CompressedMapEntryv5:
    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> CompressedMapEntryv5:
        raise NotImplementedError()
        out = cls()
        # [  0] uint8_t   compression;  // compression type
        # [  1] UINT24    complength;   // compressed length
        # [  4] UINT48    offset;       // offset
        # [ 10] uint16_t  crc;          // crc-16 of the data
        return out


class Chd(base.Archive):
    """Compressed Hunks of Data"""
    ext = "*.chd"
    header: ChdHeaderv5
    metadata: List[Metadata]

    def __init__(self):
        self.metadata = list()

    # TODO: __repr__
    # TODO: namelist
    # TODO: read

    @classmethod
    def from_file(cls, filename: str) -> Chd:
        return cls.from_stream(open(filename, "rb"))

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Chd:
        magic, header_length, header_version = binary.read_struct(stream, ">8s2I")
        assert magic == b"MComprHD"
        assert header_version == 5, "only supporting v5"
        assert header_length == 124, "incorrect header size for v5"
        out = cls()
        out.header = ChdHeaderv5.from_stream(stream)
        # metadata
        stream.seek(out.header.meta_offset)
        metadata = Metadata.from_stream(stream)
        while metadata.next != 0:
            out.metadata.append(metadata)
            metadata = Metadata.from_stream(stream)
        # TODO: if out.header.compressors[0] != b"\x00" * 4:  # data is compressed
        # NOTE: https://github.com/mamedev/mame/blob/master/src/lib/util/chd.cpp#L2489
        # -- get map (m_rawmap)
        # NOTE: https://github.com/mamedev/mame/blob/master/src/lib/util/chd.cpp#L2168
        # -- decompress_v5_map
        # --- seek to map offset
        ...
        # INITIALISE DECOMPRESSORS
        # NOTE: https://github.com/mamedev/mame/blob/master/src/lib/util/chdcodec.cpp#L406
        # -- cdrom_file::MAX_SECTOR_DATA = 2352
        # -- cdrom_file::MAX_SUBCODE_DATA = 96
        # -- chd_cd_compressor needs a BaseCompressor & SubcodeCompressor for it's template
        # --- cdlz: (LZMA, Deflate), cdzl: (Deflate,) * 2, cdzs: (Zstandard,) * 2
        # -- chd_lzma_decompressor::decompress | lzma/C/LzmaDec.h | import lzma
        # -- chd_zlib_decompressor::decompress | <zlib.h> | import zlib
        # -- chd_zstd_decompressor::decompress | <zstd.h>  | pip install zstandard (+ cffi) => import zstandard
        ...
        return out

    @property
    def is_gdrom(self) -> bool:
        metadata_magics = {md.magic for md in self.metadata}
        return any(magic in metadata_magics for magic in (b"CHGD", b"CHGT"))
