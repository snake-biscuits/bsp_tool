# https://github.com/mamedev/mame/blob/master/src/lib/util/chd.h
from __future__ import annotations
import enum
import io
from typing import Dict, List

from .. import core
from ..utils import binary
from . import base


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


class ChdHeaderv5(core.Struct):
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


class CompressedMapHeaderv5:
    length: int  # size of compressed map data

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> CompressedMapHeaderv5:
        out = cls()
        out.length, offset_crc = binary.read_struct(stream, ">IQ")
        out.first_block_offset = offset_crc >> 16
        out.crc = offset_crc & (2 ** 16 - 1)
        bits = binary.read_struct(stream, ">4B")
        out.length_bits = bits[0]
        out.hunk_bits = bits[1]
        out.parent_unit_bits = bits[2]
        assert bits[3] == 0  # reserved
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


class Chd(base.DiscImage):
    """Compressed Hunks of Data"""
    ext = "*.chd"
    header: ChdHeaderv5
    metadata: List[Metadata]

    def __init__(self):
        self.extras = dict()
        self.metadata = list()
        self.tracks = list()
        self._cursor = (0, 0)

    def extra_patterns(self) -> List[str]:
        return list()

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
        # TODO: CHGD & CHTR -> Track
        # TODO: track data -> extras
        # NOTE: https://github.com/mamedev/mame/blob/master/src/lib/util/chd.cpp#L2489
        # -- get map (m_rawmap)
        # NOTE: https://github.com/mamedev/mame/blob/master/src/lib/util/chd.cpp#L2168
        # -- decompress_v5_map
        # --- seek to map offset
        stream.seek(out.header.map_offset)
        if out.header.compressors[0] != b"\x00" * 4:  # data is compressed
            out.map_header = CompressedMapHeaderv5.from_stream(stream)
            out.raw_map = stream.read(out.map_header.length)
            assert len(out.raw_map) == out.map_header.length  # should hit EOF exactly
            # TODO: decompress Huffman encoded CompressedMapEntryv5 etc.
        # INITIALISE DECOMPRESSORS
        # NOTE: https://github.com/mamedev/mame/blob/master/src/lib/util/chdcodec.cpp#L406
        # -- cdrom_file::MAX_SECTOR_DATA = 2352
        # -- cdrom_file::MAX_SUBCODE_DATA = 96
        # -- chd_cd_compressor needs a BaseCompressor & SubcodeCompressor for it's template
        # --- cdlz: (LZMA, Deflate), cdzl: (Deflate,) * 2, cdzs: (Zstandard,) * 2
        # -- chd_lzma_decompressor::decompress | lzma/C/LzmaDec.h | import lzma
        # -- chd_zlib_decompressor::decompress | <zlib.h> | import zlib
        # -- chd_zstd_decompressor::decompress | <zstd.h> | pip install zstandard (+ cffi) => import zstandard
        else:
            # TODO: need an uncompressed .chd to test
            raise NotImplementedError("Cannot parse uncompressed Map")
        return out

    @property
    def is_gdrom(self) -> bool:
        metadata_magics = {md.magic for md in self.metadata}
        return any(magic in metadata_magics for magic in (b"CHGD", b"CHGT"))
