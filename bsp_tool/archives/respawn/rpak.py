# https://github.com/r-ex/LegionPlus/
from __future__ import annotations
import datetime
import enum
import io
from typing import Dict, List, Tuple, Union

from ... import core
from ... import external
from ...utils import binary
from .. import base


# enums
versions = {
    6: "Titanfall 2 Tech Test",
    7: "Titanfall 2",
    8: "Apex Legends"}
# ^ {version: game}


asset_type = {
    b"anir": "Animation Recording",  # in r2tt/r2 sp_training.rpak
    b"arig": "Animation Rig",  # similar to include models, for sharing animations between multiple models
    b"aseq": "Animation Sequence",  # contains animation data
    b"dtbl": "DataTable",  # compiled csv file
    b"efct": "Effect",  # compiled .pcf file
    b"font": "Font",  # RUI font face
    b"hcxt": "Highlight Context",
    b"hsys": "Highlight System",  # only in highlight.rpak
    b"impa": "Impact Definition",
    b"matl": "Material",
    b"mdl_": "Model",
    b"Ptch": "Pak Patch",  # describes the highest patch number of each included rpak file for the game to load
    b"rlcd": "LCD screen effect",  # only in common.rpak
    b"rmap": "Map",  # currently unused/nulled data
    b"rpsk": "Particle Script",  # only in particle_scripts.rpak
    b"rson": "RSON",  # Respawn JSON
    b"rtk\0": "RTK File",  # RTK UI script
    b"shdr": "Shader",
    b"shds": "Shader Set",  # references a pixel shader and a vertex shader
    b"stgs": "Settings",
    b"stlt": "Settings Layout",
    b"subt": "Subtitles",  # rpak version of source's "closedcaption_%language%.dat" files
    # https://developer.valvesoftware.com/wiki/Closed_Captions
    b"txan": "Texture Animation",
    b"txtr": "Texture",
    b"ui\0\0": "RUI",  # Respawn UI
    b"uiia": "UI image",  # streamable ui image asset type added in season 11 apex
    b"uimg": "UI image atlas",  # describes locations of ui images in an associated atlas texture asset
    b"wepn": "Weapon Definition",  # rpak version of .txt weapon scripts
    b"wrap": "Wrapped File",  # text or binary file
    b"vers": "Patch Version"}
# ^ {b"magic": "description"}


class Compression(enum.Enum):
    NONE = 0x00
    RESPAWN = 0x01  # Proprietary "rtech"
    OODLE = 0x02


class HeaderFlags(enum.IntFlag):
    """all guesses"""
    # NOTE: R5 flags only use the bottom byte
    # TODO: r2tt
    # r2
    SKIN = 0x0000  # haven't checked r5 for exceptions
    UI = 0x0001
    COMMON_R2 = 0x0100
    # r5
    UNKNOWN_1 = 0x04  # entities & rendered geo + startup.rpak
    UNKNOWN_2 = 0x08  # lobby & firing range temp & materials
    R5 = 0x20  # always present (for season 21 anyway)


# utility classes
class FileTime:
    # NOTE: FILETIME epoch is 1601-01-01
    epoch_offset = 0x019DB1DED53E8000  # 1970-01-01 as FILETIME

    def __init__(self, value):
        self.value = value

    def __repr__(self) -> str:
        time_string = self.as_datetime().strftime("%Y/%m/%d (%a) %H:%M:%S.%f")
        return f"<{self.__class__.__name__} {time_string}>"

    def __iter__(self):  # for struct.as_bytes
        return iter([self.value])

    def as_datetime(self) -> datetime.datetime:
        timestamp = (self.value - self.epoch_offset) / (10 ** 7)  # 100s of ns -> seconds
        return datetime.datetime.utcfromtimestamp(timestamp)

    # TODO: .from_datetime & .now @classmethod(s)


# other header data
class PatchHeader(core.MappedArray):
    data_size: int  # "total size of the patch edit stream data"
    virtual_segment: int  # index into VirtualSegments
    _mapping = ["data_size", "virtual_segment"]
    _format = "2I"


class CompressPair(core.MappedArray):
    _mapping = ["compressed_size", "decompressed_size"]
    _format = "2Q"


class VirtualSegment(core.MappedArray):
    flags: int  # if 64 is set, this virtual segment is in another file
    _mapping = ["flags", "type", "size"]
    _format = "2IQ"
    # TODO: flags & type enums


class MemoryPage(core.MappedArray):
    _mapping = ["virtual_segment", "flags", "size"]
    _format = "3I"
    # TODO: flags enum


class Descriptor(core.MappedArray):
    _mapping = ["index", "offset"]
    _format = "2I"


# versioned headers
class AssetEntryv6(core.MappedArray):  # also v7
    _mapping = [
        "name_hash", "unknown_1", "head_index", "head_offset", "cpu_index", "cpu_offset",
        "starpak_offset", "last_page", "unknown_2",
        "first_relation", "uses_start_index", "num_relations", "uses_count",
        "subheader_size", "version", "magic"]
    _format = "2Q4IQ2H6I4s"


class AssetEntryv8(core.MappedArray):
    _mapping = [
        "name_hash", "unknown", "head_index", "head_offset", "cpu_index", "cpu_offset",
        "starpak_offset", "optimal_starpak_offset", "last_page", "unknown",
        "first_relation", "uses_start_index", "num_relations", "uses_count",
        "subheader_size", "version", "magic"]
    _format = "2Q4i2q2h6I4s"


class RPakHeaderv6(core.MappedArray):
    """Titanfall 2 Tech Test"""
    magic: bytes  # always b"RPak"
    version: int  # always 6
    flags: HeaderFlags
    # notes
    num_unknown_1: int  # length of penultimate uint32_t header block
    num_unknown_2: int  # bytesize of final header block
    # defaults
    compression: Compression = Compression.NONE
    patch_index: int = 0

    _mapping = [
        "magic", "version", "flags", "created", "hash",
        "file_size", "padding_1", "padding_2",
        "len_starpak_ref", "num_virtual_segments", "num_memory_pages",
        "num_descriptors", "num_asset_entries", "num_guid_descriptors",
        "num_relations", "num_unknown_1", "num_unknown_2", "unknown"]
    _format = "4s2H5Q10I"
    _classes = {"flags": HeaderFlags, "created": FileTime}


class RPakHeaderv7(core.MappedArray):
    """Titanfall 2"""
    magic: bytes  # always b"RPak"
    version: int  # always 7
    flags: HeaderFlags
    # notes
    num_unknown_1: int  # length of penultimate uint32_t header block
    num_unknown_2: int  # bytesize of final header block
    # NOTE: compression is a @property

    _mapping = [
        "magic", "version", "flags", "created", "hash",
        "compressed_size", "padding_1", "decompressed_size", "padding_2",
        "len_starpak_ref", "num_virtual_segments", "num_memory_pages", "patch_index",
        "num_descriptors", "num_asset_entries", "num_guid_descriptors",
        "num_relations", "num_unknown_1", "num_unknown_2"]
    _format = "4s2H6Q4H6I"
    _classes = {"flags": HeaderFlags, "created": FileTime}

    @property
    def compression(self) -> Compression:
        return Compression.NONE if self.compressed_size == self.decompressed_size else Compression.RESPAWN


class RPakHeaderv8(core.MappedArray):
    """Apex Legends"""
    magic: bytes  # always b"RPak"
    version: int  # always 8
    flags: HeaderFlags
    compression: Compression

    _mapping = [
        "magic", "version", "flags", "compression", "created", "hash",
        "compressed_size", "starpak_offset", "padding_1",
        "decompressed_size", "starpak_size", "padding_2",
        "len_starpak_ref", "len_opt_starpak_ref", "num_virtual_segments", "num_memory_pages",
        "patch_index", "num_descriptors", "num_asset_entries", "num_guid_descriptors",
        "num_relations", "unknown"]
    # TODO: unknown -> {uint8_t unk1[10]; uint32_t page_offset; uint8_t unk2[8];}  // hidden alignment cost
    _format = "4sH2B8Q4H5I28s"
    _classes = {"flags": HeaderFlags, "compression": Compression, "created": FileTime}


class RPak(base.Archive):
    ext = "*.rpak"
    extras: Dict[str, external.File]
    header: Union[RPakHeaderv6, RPakHeaderv7, RPakHeaderv8]
    starpaks: List[str]
    optimal_starpaks: List[str]
    patch: Tuple[PatchHeader, List[CompressPair], List[int]]
    version: int
    # versioned struct lookups
    HeaderClasses = {
        6: RPakHeaderv6,
        7: RPakHeaderv7,
        8: RPakHeaderv8}
    # ^ {version: RPakHeader}
    AssetEntryClasses = {
        6: AssetEntryv6,
        7: AssetEntryv6,
        8: AssetEntryv8}
    # ^ {version: AssetEntry}

    def __init__(self):
        self.extras = dict()
        self.optimal_starpaks = list()
        self.patch = None
        self.starpaks = list()

    def __repr__(self) -> str:
        hash_ = f"{self.header.hash:016X}"
        num_assets = self.header.num_asset_entries
        descriptor = f"v{self.version} ({hash_}) {num_assets} assets"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def extra_patterns(self) -> List[str]:
        # NOTE: assuming all starpaks are in the same folder
        # "paks\\Win64\\example.starpak" -> "example.starpak"
        return [
            filename.replace("\\", "/").split("/")[-1]
            for filename in (*self.optimal_starpaks, *self.starpaks)]

    def virtual_segment_data(self, index: int) -> bytes:
        assert index < len(self.virtual_segments)
        start = sum(vs.size for vs in self.virtual_segments[:index] if not vs.flags & 64)
        length = self.virtual_segments[index].size
        return self.data[start:start + length]

    # TODO: memory_page_data(self, index: int) -> bytes:
    # -- should be inside a virtual_segment, need relative offset

    def namelist(self) -> List[str]:
        # we cannot reverse name hashes
        if self.header.compression is not Compression.NONE:
            raise NotImplementedError("cannot decompress asset_entries")
        elif any(vs.flags == 1 and vs.type == 1 for vs in self.virtual_segments):
            # TODO: catch in .from_stream() & convert to Dict[str, AssetEntry]
            names_segment_index = [i for i, vs in enumerate(self.virtual_segments) if vs.flags == 1 and vs.type == 1][0]
            raw_names = self.virtual_segment_data(names_segment_index)
            try:
                names = [fn.decode() for fn in raw_names.split(b"\0")[:-1]]
            except UnicodeDecodeError:
                assert names_segment_index + 1 < len(self.virtual_segments)
                start = self.virtual_segment_data(names_segment_index).find(b"r2")
                raw_names = b"".join([
                    self.virtual_segment_data(names_segment_index + 0)[start:],
                    self.virtual_segment_data(names_segment_index + 1)[:start]])
                names = [fn.decode() for fn in raw_names.split(b"\0")[:-1]]
            assert len(names) == len(self.asset_entries)
            return sorted(names)
        else:
            return sorted(f"{ae.magic.decode()}_{ae.name_hash:016X}" for ae in self.asset_entries)

    def read(self, filepath: str) -> bytes:
        assert filepath in self.namelist()
        raise NotImplementedError("cannot parse StaRPak")

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> RPak:
        out = cls()
        assert binary.read_struct(stream, "4s") == b"RPak", "not a RPak file!"
        out.version = binary.read_struct(stream, "H")
        assert out.version in versions, f"unknown version: {out.version}"
        stream.seek(-6, 1)  # back to the start
        HeaderClass = cls.HeaderClasses[out.version]
        out.header = HeaderClass.from_stream(stream)
        assert out.header.patch_index < 16
        if out.header.patch_index > 0:
            out.patch = (
                PatchHeader.from_stream(stream),
                [CompressPair.from_stream(stream) for i in range(out.header.patch_index)],
                [binary.read_struct(stream, "H") for i in range(out.header.patch_index)])  # "IndicesToFile"
        if out.header.compression is not Compression.NONE:
            return out
            # TODO: decompress everything after the main header
            # uncompressed_rpak = b"".join([
            #     out.header.as_bytes(),
            #     decompress(out.header, stream)])
            # stream = io.BytesIO(uncompressed_rpak)
            # stream.seek(len(out.header.as_bytes()))
        # StaRPak references
        out.starpaks = [
            fn.decode("utf-8", "strict")
            for fn in stream.read(out.header.len_starpak_ref).split(b"\0")][:-1]
        if out.version == 8:
            out.optimal_starpaks = [
                fn.decode("utf-8", "strict")
                for fn in stream.read(out.header.len_opt_starpak_ref).split(b"\0")][:-1]
        out.virtual_segments = [
            VirtualSegment.from_stream(stream)
            for i in range(out.header.num_virtual_segments)]
        out.memory_pages = [
            MemoryPage.from_stream(stream)
            for i in range(out.header.num_memory_pages)]
        out.descriptors = [
            Descriptor.from_stream(stream)
            for i in range(out.header.num_descriptors)]
        AssetEntryClass = out.AssetEntryClasses[out.version]
        out.asset_entries = [
            AssetEntryClass.from_stream(stream)
            for i in range(out.header.num_asset_entries)]
        out.guid_descriptors = [
            Descriptor.from_stream(stream)
            for i in range(out.header.num_guid_descriptors)]
        out.relations = binary.read_struct(stream, f"{out.header.num_relations}I")
        # TODO: parse the rest of the file
        # virtual_segment data (unless flags & 0x40) & some other unknown data
        # TODO: around 200 bytes of non-virtual_segment data in some client_temp.rpak
        out.data = stream.read()
        out._file = stream
        return out


# StaRPak
class StreamEntry(core.MappedArray):
    _mapping = ["offset", "size"]
    _format = "2Q"


class StaRPak:
    # NOTE: not an archive! just contains data for RPak
    # https://github.com/r-ex/LegionPlus/blob/main/Legion/src/RpakLib.cpp
    # -- RpakLib::MountStarpak
    ext = "*.starpak"  # or "*.opt.starpak"
    entries: List[StreamEntry]
    _file: io.BytesIO

    def __init__(self):
        self.entries = list()

    @classmethod
    def from_bytes(cls, data: bytes) -> StaRPak:
        return cls.from_stream(io.BytesIO(data))

    @classmethod
    def from_file(cls, filename: str) -> StaRPak:
        return cls.from_stream(open(filename, "rb"))

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> StaRPak:
        assert binary.read_struct(stream, "4s") == b"SRPk"
        assert binary.read_struct(stream, "I") == 1  # version?
        out = cls()
        stream.seek(-8, 2)
        num_entries = binary.read_struct(stream, "Q")
        stream.seek(-(8 + num_entries * 16), 2)
        out.entries = [StreamEntry.from_stream(stream) for i in range(num_entries)]
        return out
