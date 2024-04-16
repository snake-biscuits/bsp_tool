"""Titanfall Engine .stbsp file parser"""
from __future__ import annotations
import enum
import os
import struct
from typing import Any, Dict, List, Tuple


def read_struct(file, format_: str) -> List[Any]:
    return struct.unpack(format_, file.read(struct.calcsize(format_)))


def write_struct(file, format_: str, *args):
    file.write(struct.pack(format_, *args))


class Block(enum.Enum):
    MATERIALS = 0  # bytes
    MATERIAL_INFOS = 1  # MaterialInfo
    VTFS = 2  # uint32_t
    VMTS = 3  # uint16_t
    COLUMNS = 4  # Column
    COLUMN_DATA = 5  # bytes


block_sizes = {
    Block.MATERIALS: 1,
    Block.MATERIAL_INFOS: 24,
    Block.VTFS: 4,
    Block.VMTS: 2,
    Block.COLUMNS: 24,
    Block.COLUMN_DATA: 1}


class FlatStruct:
    __slots__: List[str]
    _format: str

    def __init__(self, *args):
        assert len(args) == len(self.__slots__)
        for attr, value in zip(self.__slots__, args):
            setattr(self, attr, value)

    def __iter__(self):
        return iter(getattr(self, a) for a in self.__slots__)

    def __repr__(self) -> str:
        args = ", ".join([f"{a}={getattr(self, a)}" for a in self.__slots__])
        return f"{self.__class__.__name__}({args})"

    @classmethod
    def from_bytes(cls, raw_bytes: bytes) -> FlatStruct:
        return cls(*struct.unpack(cls._format, raw_bytes))

    @classmethod
    def from_stream(cls, stream) -> FlatStruct:
        return cls.from_bytes(stream.read(struct.calcsize(cls._format)))

    def as_bytes(self) -> bytes:
        return struct.pack(self._format, *self)


class BlockIndex(FlatStruct):
    offset: int
    count: int  # num_structs / num_bytes
    __slots__ = ["offset", "count"]
    _format = "2Q"


class MaterialInfo(FlatStruct):
    """rpak assets & vmts?"""
    material: int  # index materials
    unknown: int  # flags?
    guid: int  # indexes rpak
    # NOTE: only index vmt & vtf if guid == 0
    vmt: int  # index into vmts
    vtf: int  # index into vtfs
    __slots__ = ["material", "unknown", "guid", "vmt", "vtf"]
    _format = "2IQ2I"

    def __repr__(self) -> str:
        args = [f"{a}={getattr(self, a)}" for a in self.__slots__]
        args[self.__slots__.index("unknown")] = f"unknown=0x{self.unknown:08X}"
        args[self.__slots__.index("guid")] = f"guid=0x{self.guid:016X}"
        return f"MaterialInfo({', '.join(args)})"


class Column(FlatStruct):
    """grid tile data?"""
    offset: int  # index into ColumnData
    length: int
    coverage_scale: int  # also works as average histogram colour (RGBA32)
    mins_x: int
    mins_y: int
    maxs_x: int
    maxs_y: int
    __slots__ = [
        "offset", "length", "coverage_scale",
        "mins_x", "mins_y", "maxs_x", "maxs_y"]
    _format = "QIf4h"


# TODO: ColumnData
# -- some nulls, uint16_t count, 0xFFFF, short pairs
# -- short pair is mip:material bitfield & coverage
# NOTE: v8.0 & 8.1 have different bitfields for column_data
# -- r2: 10 bits material (& 0x3FF), 6 bits mip (>> 10)
# -- r5: 12 bits material (& 0xFFF), 4 bits mip (>> 12)


class StreamBsp:
    filename: str
    # header
    version: Tuple[int, int]  # r2 = (8, 0), r5 = (8, 1)
    mins_x: int
    mins_y: int
    maxs_x: int
    maxs_y: int
    stride: int  # width / height of each column
    scale: List[float]  # width, height
    blocks: Dict[Block, BlockIndex]
    # data
    materials: Dict[int, str]
    # ^ {first_byte: material}
    material_infos: List[MaterialInfo]
    vtfs: List[int]  # indexes materials
    vmts: List[int]  # indexes vtfs
    columns: List[Column]
    column_data: bytes

    def __init__(self, filename: str = "./untitled.stbsp"):
        self.filename = filename

    # TODO: init from probes (folder of cubemaps / .json)
    # -- list of materials
    # -- generate material info (need rpak uuids)
    # -- generate vmt & vtf tables
    # -- columns (only need populated)
    # --- {(*origin.xy,): [{(material, mip): coverage}, ...]
    # ---- {column: [probe]}; probe = {(material, mip): coverage}
    # --- generate empty columns, sort into correct grid order
    # --- calculate self width & height from column bounds
    # ---- (width, height) -> (mins.xy, maxs.xy)
    # -- stride & scale
    # -- calculate block lengths & offsets

    def __repr__(self) -> str:
        major, minor = self.version
        version = f"v{major}.{minor}"
        filename = os.path.basename(self.filename)
        return f"<StreamBsp {version} '{filename}' ({len(self.material_infos)} materials) @ 0x{id(self):016X}>"

    def read(self, offset: int, length: int) -> bytes:
        with open(self.filename, "wb") as file:
            file.seek(offset)
            return file.read(length)

    @classmethod
    def from_file(cls, filename: str) -> StreamBsp:
        out = cls()
        with open(filename, "rb") as file:
            # header
            magic = file.read(4)
            assert magic == b"\xB5\xCB\x00\xCB"  # float: -8440757.0?
            out.version = read_struct(file, "2H")
            assert out.version[0] == 8
            assert out.version[1] in (0, 1)  # 0: r2, 1: r5
            out.mins_x, out.mins_y, out.maxs_x, out.maxs_y, out.stride = read_struct(file, "4iI")
            out.scale = read_struct(file, "2f")
            assert read_struct(file, "33I") == (0,) * 33
            out.blocks = {
                Block(i): BlockIndex.from_stream(file)
                for i in range(6)}
            assert read_struct(file, "16Q") == (0,) * 16
            assert file.tell() == min(b.offset for b in out.blocks.values())
            # data
            offset, count = out.blocks[Block.MATERIALS]
            file.seek(offset)
            raw_materials = file.read(count)
            assert raw_materials.endswith(b"\0")
            material_strings = [s.decode() for s in raw_materials[:-1].split(b"\0")]
            out.materials, i = {0: material_strings[0]}, 0
            while len(out.materials) < raw_materials.count(b"\0"):
                i = raw_materials.find(b"\0", i) + 1
                out.materials[i] = material_strings[len(out.materials)]
            offset, count = out.blocks[Block.MATERIAL_INFOS]
            file.seek(offset)
            out.material_infos = [MaterialInfo.from_stream(file) for i in range(count)]
            offset, count = out.blocks[Block.VTFS]
            file.seek(offset)
            out.vtfs = read_struct(file, f"{count}I")
            offset, count = out.blocks[Block.VMTS]
            file.seek(offset)
            out.vmts = read_struct(file, f"{count}H")
            offset, count = out.blocks[Block.COLUMNS]
            file.seek(offset)
            out.columns = [Column.from_stream(file) for i in range(count)]
            offset, count = out.blocks[Block.COLUMN_DATA]
            file.seek(offset)
            out.column_data = file.read(count)
            # TODO: assert EOF
        return out

    def save(self):
        self.save_as(self.filename)

    def save_as(self, filename: str):
        # NOTE: assumes offsets are valid
        # -- doesn't verify / override anything
        assert self.version[0] == 8
        assert self.version[1] in (0, 1)  # 0: r2, 1: r5
        # recalculate block counts
        self.blocks[Block.MATERIALS].count = sum(len(m) for m in self.materials.values()) + len(self.materials)
        # USER: make sure ALL indices are correct before saving!
        assert all(mi.material in self.materials for mi in self.material_infos), "bad material index in material_infos"
        self.blocks[Block.MATERIAL_INFOS].count = len(self.material_infos)
        assert all(i in self.materials for i in self.vtfs), "bad material index in vtfs"
        self.blocks[Block.VTFS].count = len(self.vtfs)
        assert all(0 <= i < len(self.vtfs) for i in self.vmts), "bad vtf index in vmts"
        self.blocks[Block.VMTS].count = len(self.vmts)
        self.blocks[Block.COLUMNS].count = len(self.columns)
        self.blocks[Block.COLUMN_DATA].count = len(self.column_data)
        # recalculate block offsets
        offset = 188
        for i in (1, 2, 3, 0, 4, 5):  # observed block order
            block = Block(i)
            self.blocks[block].offset = offset
            offset += self.blocks[block].count * block_sizes[block]
        # write
        with open(filename, "wb") as file:
            # header
            file.write(b"\xB5\xCB\x00\xCB")  # magic / -8440757.0
            write_struct(file, "2H", *self.version)
            write_struct(file, "4iI", self.mins_x, self.mins_y, self.maxs_x, self.maxs_y, self.stride)
            write_struct(file, "2f", *self.scale)
            file.write(b"\0" * 132)
            file.write(b"".join([self.blocks[b].as_bytes() for b in Block]))
            file.write(b"\0" * 96)
            # data
            file.write(b"".join([mi.as_bytes() for mi in self.material_infos]))
            write_struct(file, f"{len(self.vtfs)}I", *self.vtfs)
            write_struct(file, f"{len(self.vmts)}H", *self.vmts)
            materials_list = [self.materials[o] for o in sorted(self.materials)]  # maintain order
            file.write(b"\0".join(m.encode("ascii") for m in materials_list) + b"\0")
            file.write(b"".join([c.as_bytes() for c in self.columns]))
            file.write(self.column_data)

    def columns_as_obj(self, filename: str):
        x_scale, y_scale = self.scale
        with open(filename, "w") as obj_file:
            obj_file.write("# generated by bsp_tool.extensions.stbsp\n")
            for column in self.columns:
                colour = int.from_bytes(struct.pack("f", column.coverage_scale), "little")
                obj_file.write(f"usemtl {colour:08X}\n")
                obj_file.write(f"v {column.mins_x * x_scale} {column.mins_y * y_scale} 0\n")
                obj_file.write(f"v {column.mins_x * x_scale} {column.maxs_y * y_scale} 0\n")
                obj_file.write(f"v {column.maxs_x * x_scale} {column.maxs_y * y_scale} 0\n")
                obj_file.write(f"v {column.maxs_x * x_scale} {column.mins_y * y_scale} 0\n")
                obj_file.write("f -1 -2 -3 -4\n")
