"""Titanfall Engine .stbsp file parser"""
from __future__ import annotations
import collections
import enum
import struct
from typing import Any, Dict, List


def read_struct(file, format_: str) -> List[Any]:
    return struct.unpack(format_, file.read(struct.calcsize(format_)))


BlockIndex = collections.namedtuple("BlockIndex", ["offset", "size"])


class BlockType(enum.Enum):
    MATERIALS = 0  # zero-terminated strings
    # TODO: do other lumps index first byte of each material?
    UNKNOWN_1 = 1  # 24 byte structs; size >= len(materials)
    UNKNOWN_2 = 2  # 4 byte structs
    UNKNOWN_3 = 3  # 2 byte structs
    UNKNOWN_4 = 4  # 24 byte structs
    UNKNOWN_5 = 5  # mip pixels?
# observed order: 1, 2, 3, 0, 4, 5


class FlatStruct:
    __slots__: List[str]
    _format: str

    def __init__(self, *args):
        assert len(args) == len(self.__slots__)
        for attr, value in zip(self.__slots__, args):
            setattr(self, attr, value)

    def __repr__(self) -> str:
        args = ", ".join([str(getattr(self, a)) for a in self.__slots__])
        return f"{self.__class__.__name__}({args})"

    @classmethod
    def from_bytes(cls, raw_bytes: bytes) -> FlatStruct:
        return cls(*struct.unpack(cls._format, raw_bytes))

    @classmethod
    def from_stream(cls, stream) -> FlatStruct:
        return cls.from_bytes(stream.read(struct.calcsize(cls._format)))


class Block1(FlatStruct):  # UNKNOWN_1
    material: int  # index into raw_materials (first byte of string)
    # stbsp.materials[stbsp.material_index[block_1.material]]
    unknown_1: int  # flags?
    hash: int  # indexes rpak; 0 if .vmt
    unknown_2: int  # = previous unknown_3
    unknown_3: int  # += 1 if .vmt
    __slots__ = ["material", "unknown_1", "hash", "unknown_2", "unknown_3"]
    _format = "2IQ2I"


class Block4(FlatStruct):  # UNKNOWN_4
    offset: int  # index into UNKNOWN_5?
    length: int
    flags: int  # maybe asset type?
    first_x: int  # stbsp.block_4[0].first_x == stbsp.unknown[0]
    first_y: int  # stbsp.block_4[0].first_y == stbsp.unknown[1]
    last_x: int  # stbsp.block_4[-1].first_x + last_x == stbsp.unknown[3]
    last_y: int  # stbsp.block_4[-1].first_y + last_y == stbsp.unknown[4]
    __slots__ = [
        "offset", "length", "flags",
        "first_x", "first_y", "last_x", "last_y"]
    _format = "Q2I4h"


class StreamBsp:
    # header
    unknown: List[int]
    block_indices: List[BlockIndex]
    # data
    materials: Dict[int, str]
    # ^ {first_byte: material}
    block_1: List[Block1]
    block_2: List[int]
    block_3: List[int]
    block_4: List[Block4]
    block_5: bytes

    def __repr__(self) -> str:
        return f"<StreamBsp {len(self.materials)} materials @ 0x{id(self):016X}>"

    @classmethod
    def from_file(cls, filename: str) -> StreamBsp:
        with open(filename, "rb") as file:
            magic = file.read(4)
            assert magic == b"\xB5\xCB\x00\xCB"
            version = read_struct(file, "2H")
            assert version == (8, 0)  # r2 only; r5 s3 is (8, 1)
            out = cls()
            out.unknown = read_struct(file, "2i3I")
            assert read_struct(file, "2I") == (0x43000000,) * 2
            assert read_struct(file, "33I") == (0,) * 33
            out.block_indices = [BlockIndex(*read_struct(file, "2Q")) for i in range(6)]
            assert read_struct(file, "16Q") == (0,) * 16
            assert file.tell() == min(bi.offset for bi in out.block_indices)
            # Block0: materials
            materials_block = out.block_indices[0]
            file.seek(materials_block.offset)
            raw_materials = file.read(materials_block.size)
            assert raw_materials.endswith(b"\0")
            material_strings = [s.decode() for s in raw_materials[:-1].split(b"\0")]
            out.materials, i = {0: material_strings[0]}, 0
            while len(out.materials) < raw_materials.count(b"\0"):
                i = raw_materials.find(b"\0", i) + 1
                out.materials[i] = material_strings[len(out.materials)]
            # Block1
            file.seek(out.block_indices[1].offset)
            out.block_1 = [Block1.from_stream(file) for i in range(out.block_indices[1].size)]
            # Block2
            file.seek(out.block_indices[2].offset)
            out.block_2 = read_struct(file, f"{out.block_indices[2].size}I")
            # Block3
            file.seek(out.block_indices[3].offset)
            out.block_3 = read_struct(file, f"{out.block_indices[3].size}H")
            # Block4
            file.seek(out.block_indices[4].offset)
            out.block_4 = [Block4.from_stream(file) for i in range(out.block_indices[4].size)]
            # Block5
            file.seek(out.block_indices[5].offset)
            out.block_5 = file.read(out.block_indices[5].size)
            # TODO: assert EOF
        return out
