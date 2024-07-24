# https://github.com/r-ex/LegionPlus/
from __future__ import annotations
import datetime
import enum
import io
import os
from typing import List, Tuple, Union

from ....branches.base import MappedArray
from ....utils.binary import read_struct
from .. import base


# enums
versions = {
    6: "Titanfall 2 Tech Test",
    7: "Titanfall 2",
    8: "Apex Legends"}
# ^ {version: game}


asset_type = {
    b"anir": "Unknown",  # in r2tt/r2 sp_training.rpak
    b"arig": "Animation rig",
    b"aseq": "Animation",
    b"dtbl": "DataTable",
    b"efct": "Effect",  # *.pcf ?
    b"font": "Font",  # only in ui.rpak
    b"hsys": "Highlight System?",  # only in highlight.rpak
    b"matl": "Material",
    b"mdl_": "Model",
    b"Ptch": "Patch",  # patches another asset
    b"rmap": "Map",
    b"rpsk": "Unknown",  # only in particle_scripts.rpak
    b"rson": "RSON",  # Respawn JSON
    b"rlcd": "Unknown",  # only in common.rpak
    b"shdr": "Shader",
    b"shds": "Shader set",  # e.g. {vertex_X, fragment_Y}
    b"stgs": "Settings",
    b"stlt": "Settings layout",
    b"subt": "Subtitles",
    b"txan": "Animated texture",
    b"txtr": "Texture",
    b"ui\0\0": "RUI",  # Respawn UI
    b"uiia": "UIIA",
    b"uimg": "UI image atlas",
    b"wrap": "Wrap",  # plain text or binary file
    b"vers": "Patch version"}  # assumed
# {b"magic": "description"


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

    # TODO: .from_datetime / .now @classmethod(s)


# other header data
class PatchHeader(MappedArray):
    data_size: int  # "total size of the patch edit stream data"
    virtual_segment: int  # index into VirtualSegments
    _mapping = ["data_size", "virtual_segment"]
    _format = "2I"


class CompressPair(MappedArray):
    _mapping = ["compressed_size", "decompressed_size"]
    _format = "2Q"


class VirtualSegment(MappedArray):
    flags: int  # if 64 is set, this virtual segment is in another file
    _mapping = ["flags", "type", "size"]
    _format = "2IQ"
    # TODO: flags & type enums


class MemoryPage(MappedArray):
    _mapping = ["virtual_segment", "flags", "size"]
    _format = "3I"
    # TODO: flags enum


class Descriptor(MappedArray):
    _mapping = ["index", "offset"]
    _format = "2I"


# versioned headers
class AssetEntryv6(MappedArray):  # also v7
    _mapping = [
        "name_hash", "unknown_1", "head_index", "head_offset", "cpu_index", "cpu_offset",
        "starpak_offset", "last_page", "unknown_2",
        "first_relation", "uses_start_index", "num_relations", "uses_count",
        "subheader_size", "version", "magic"]
    _format = "2Q4IQ2H6I4s"


class AssetEntryv8(MappedArray):
    _mapping = [
        "name_hash", "unknown", "head_index", "head_offset", "cpu_index", "cpu_offset",
        "starpak_offset", "optimal_starpak_offset", "last_page", "unknown",
        "first_relation", "uses_start_index", "num_relations", "uses_count",
        "subheader_size", "version", "magic"]
    _format = "2Q4i2q2h6I4s"


class RPakHeaderv6(MappedArray):
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


class RPakHeaderv7(MappedArray):
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


class RPakHeaderv8(MappedArray):
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
    filepath: str
    filename: str
    version: int
    header: Union[RPakHeaderv6, RPakHeaderv7, RPakHeaderv8]
    starpaks: List[str]
    optimal_starpaks: List[str] = list()
    patch: Tuple[PatchHeader, List[CompressPair], List[int]] = None
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

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        with open(filepath, "rb") as rpak_file:
            self._from_stream(rpak_file)

    def __repr__(self) -> str:
        hash = f"{self.header.hash:016X}"
        num_assets = self.header.num_asset_entries
        # num_assets = len(self.asset_entries)  # can't use until we have decompression
        return f"<RPak v{self.version} ({hash}) {num_assets} assets @ 0x{id(self):016X}>"

    def _from_stream(self, stream: io.BytesIO):
        assert read_struct(stream, "4s") == b"RPak", "not a RPak file!"
        self.version = read_struct(stream, "H")
        assert self.version in versions, f"unknown version: {self.version}"
        stream.seek(-6, 1)  # back to the start
        HeaderClass = self.HeaderClasses[self.version]
        self.header = HeaderClass.from_stream(stream)
        assert self.header.patch_index < 16
        if self.header.patch_index > 0:
            self.patch = (
                PatchHeader.from_stream(stream),
                [CompressPair.from_stream(stream) for i in range(self.header.patch_index)],
                [read_struct(stream, "H") for i in range(self.header.patch_index)])  # "IndicesToFile"
        # TODO: decompress everything after the main header
        if self.header.compression is not Compression.NONE:
            # uncompressed_rpak = b"".join([
            #     self.header.as_bytes(),
            #     decompress(self.header, stream)])  # TODO
            # stream = io.BytesIO(uncompressed_rpak)
            # stream.seek(len(self.header.as_bytes()))
            return  # NotImplemented
        # StaRPak references
        self.starpaks = [
            fn.decode("utf-8", "strict")
            for fn in stream.read(self.header.len_starpak_ref).split(b"\0")][:-1]
        if self.version == 8:
            self.optimal_starpaks = [
                fn.decode("utf-8", "strict")
                for fn in stream.read(self.header.len_opt_starpak_ref).split(b"\0")][:-1]
        self.virtual_segments = [
            VirtualSegment.from_stream(stream)
            for i in range(self.header.num_virtual_segments)]
        self.memory_pages = [
            MemoryPage.from_stream(stream)
            for i in range(self.header.num_memory_pages)]
        self.descriptors = [
            Descriptor.from_stream(stream)
            for i in range(self.header.num_descriptors)]
        AssetEntryClass = self.AssetEntryClasses[self.version]
        self.asset_entries = [
            AssetEntryClass.from_stream(stream)
            for i in range(self.header.num_asset_entries)]
        self.guid_descriptors = [
            Descriptor.from_stream(stream)
            for i in range(self.header.num_guid_descriptors)]
        self.relations = read_struct(stream, f"{self.header.num_relations}I")
        # TODO: parse the rest of the file
        # virtual_segment data (unless flags & 0x40) & some other unknown data
        self.data = stream.read()

    def virtual_segment_data(self, index: int) -> bytes:
        assert index < len(self.virtual_segments)
        start = sum(vs.size for vs in self.virtual_segments[:index] if not vs.flags & 64)
        length = self.virtual_segments[index].size
        return self.data[start:start + length]

    # TODO: memory_page_data(self, index: int) -> bytes:
    # -- should be inside a virtual_segment, need relative offset

    def extract(self, filepath: str, path=None):
        assert filepath in self.namelist()
        if path is not None:
            raise NotImplementedError("Cannot target an out folder yet")
        raise NotImplementedError()
        with open(os.path.join("" if path is None else path, filepath), "w") as out_file:
            out_file.write(self.read(filepath))

    def namelist(self) -> List[str]:
        # we cannot reverse name hashes
        if self.header.compression is not Compression.NONE:
            raise NotImplementedError("cannot decompress asset_entries")
        elif any(vs.flags == 1 and vs.type == 1 for vs in self.virtual_segments):
            # TODO: catch in _from_stream & convert to Dict[str, AssetEntry]
            names_segment_index = [i for i, vs in enumerate(self.virtual_segments) if vs.flags == 1 and vs.type == 1][0]
            raw_names = self.virtual_segment_data(names_segment_index)
            names = [fn.decode() for fn in raw_names.split(b"\0")[:-1]]
            assert len(names) == len(self.asset_entries)
            return sorted(names)
        else:
            return sorted(f"{ae.magic.decode()}_{ae.name_hash:016X}" for ae in self.asset_entries)

    def read(self, filepath: str) -> bytes:
        assert filepath in self.namelist()
        raise NotImplementedError("cannot parse StaRPak")


# StaRPak
class StreamEntry(MappedArray):
    _mapping = ["offset", "size"]
    _format = "2Q"


class StaRPak:
    # NOTE: not an archive! just contains data for RPak
    # https://github.com/r-ex/LegionPlus/blob/main/Legion/src/RpakLib.cpp
    # -- RpakLib::MountStarpak
    ext = "*.starpak"  # or "*.opt.starpak"
    entries: List[StreamEntry] = list()

    @classmethod
    def from_file(cls, filepath: str) -> StaRPak:
        with open(filepath, "rb") as starpak_file:
            assert read_struct(starpak_file, "4s") == b"SRPk"
            assert read_struct(starpak_file, "I") == 1  # version?
            out = cls()
            starpak_file.seek(-8, 2)
            num_entries = read_struct(starpak_file, "Q")
            starpak_file.seek(-(8 + num_entries * 16), 2)
            out.entries = [StreamEntry.from_stream(starpak_file) for i in range(num_entries)]
            return out
