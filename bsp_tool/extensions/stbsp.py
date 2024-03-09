"""Titanfall Engine .stbsp file parser"""
from __future__ import annotations
import collections
import enum
import struct
from typing import Any, Dict, List


def read_struct(file, format_: str) -> List[Any]:
    return struct.unpack(format_, file.read(struct.calcsize(format_)))


BlockIndex = collections.namedtuple("BlockIndex", ["offset", "size"])


class Block(enum.Enum):
    # observed order: 1, 2, 3, 0, 4, 5
    MATERIALS = 0
    MATERIAL_INFO = 1
    VTFS = 2  # uint32_t
    VMTS = 3  # uint16_t
    COLUMNS = 4  # columns
    COLUMN_DATA = 5  # column data


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


class MaterialInfo(FlatStruct):
    """rpak assets & vmts?"""
    material: int  # index materials
    unknown_1: int  # flags?
    guid: int  # indexes rpak?
    # NOTE: only index vmt & vtf if guid == 0
    vmt: int  # index into vmts
    vtf: int  # index into vtfs
    __slots__ = ["material", "unknown_1", "guid", "vmt", "vtf"]
    _format = "2IQ2I"

    def __repr__(self) -> str:
        args = ", ".join([
            str(self.material), str(self.unknown_1),
            f"0x{self.guid:016X}",
            str(self.vmt), str(self.vtf)])
        return f"MaterialInfo({args})"


class Column(FlatStruct):
    """grid tile data?"""
    offset: int  # index into ColumnData
    length: int
    colour: int  # average histogram colour (RGBA32)
    mins_x: int
    mins_y: int
    maxs_x: int
    maxs_y: int
    __slots__ = ["offset", "length", "colour", "mins_x", "mins_y", "maxs_x", "maxs_y"]
    _format = "Q2I4h"


class StreamBsp:
    # header
    mins_x: int
    mins_y: int
    maxs_x: int
    maxs_y: int
    stride: int  # width / height of each column
    scale: List[float]  # width, height
    block_indices: List[BlockIndex]
    # data
    materials: Dict[int, str]
    # ^ {first_byte: material}
    material_info: List[MaterialInfo]
    vtfs: List[int]  # indexes materials
    vmts: List[int]  # indexes vtfs
    columns: List[Column]
    column_data: bytes

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
            out.mins_x, out.mins_y, out.maxs_x, out.maxs_y, out.stride = read_struct(file, "4iI")
            out.scale = read_struct(file, "2f")
            assert read_struct(file, "33I") == (0,) * 33
            out.block_indices = [BlockIndex(*read_struct(file, "2Q")) for i in range(6)]
            assert read_struct(file, "16Q") == (0,) * 16
            assert file.tell() == min(bi.offset for bi in out.block_indices)
            # Block 0: Materials
            file.seek(out.block_indices[0].offset)
            raw_materials = file.read(out.block_indices[0].size)
            assert raw_materials.endswith(b"\0")
            material_strings = [s.decode() for s in raw_materials[:-1].split(b"\0")]
            out.materials, i = {0: material_strings[0]}, 0
            while len(out.materials) < raw_materials.count(b"\0"):
                i = raw_materials.find(b"\0", i) + 1
                out.materials[i] = material_strings[len(out.materials)]
            # Block 1: Material Info
            file.seek(out.block_indices[1].offset)
            out.material_info = [MaterialInfo.from_stream(file) for i in range(out.block_indices[1].size)]
            # Block 2: VTFs
            file.seek(out.block_indices[2].offset)
            out.vtfs = read_struct(file, f"{out.block_indices[2].size}I")
            # Block 3: VMTs
            file.seek(out.block_indices[3].offset)
            out.vmts = read_struct(file, f"{out.block_indices[3].size}H")
            # Block 4: Columns
            file.seek(out.block_indices[4].offset)
            out.columns = [Column.from_stream(file) for i in range(out.block_indices[4].size)]
            # Block 4: Column Data
            file.seek(out.block_indices[5].offset)
            out.column_data = file.read(out.block_indices[5].size)
            # TODO: assert EOF
        return out

    def as_obj(self, filename: str):
        x_scale, y_scale = self.scale
        with open(filename, "w") as obj_file:
            obj_file.write("# generated by bsp_tool.extensions.stbsp\n")
            for column in self.columns:
                obj_file.write(f"usemtl {column.colour:08X}\n")
                obj_file.write(f"v {column.mins_x * x_scale} {column.mins_y * y_scale} 0\n")
                obj_file.write(f"v {column.mins_x * x_scale} {column.maxs_y * y_scale} 0\n")
                obj_file.write(f"v {column.maxs_x * x_scale} {column.maxs_y * y_scale} 0\n")
                obj_file.write(f"v {column.maxs_x * x_scale} {column.mins_y * y_scale} 0\n")
                obj_file.write("f -1 -2 -3 -4\n")
