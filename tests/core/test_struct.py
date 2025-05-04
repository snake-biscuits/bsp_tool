import enum
import struct
from typing import List

from bsp_tool import core
from bsp_tool.utils import vector


# TODO: test_mapping_length
# - list
# - dict
# - int
# - None (dict key)
# - recursion


# TODO: test everything fails correctly when fed invalid inputs

class ExampleFlags(enum.IntFlag):
    FOO = 0x01
    BAR = 0x02


class Example(core.Struct):
    __slots__ = ["id", "position", "data", "flags", "bitfield"]
    _format = "i3f3iI"
    _arrays = {"position": [*"xyz"], "data": 2}
    _classes = {"position": vector.vec3, "flags": ExampleFlags}
    _bitfields = {"bitfield": {"foo": 24, "bar": 8}}


class TestStruct:
    def test_init(self):
        # no args, no kwargs
        test_Struct = Example()
        assert test_Struct.id == 0
        assert isinstance(test_Struct.position, vector.vec3)
        assert test_Struct.position == (0,) * 3
        # assert core.struct.attr_formats[Example]["data"] == "i" * 2
        assert tuple(test_Struct.data) == (0,) * 2
        assert isinstance(test_Struct.flags, ExampleFlags)
        assert test_Struct.flags == 0
        assert isinstance(test_Struct.bitfield, core.BitField)
        assert test_Struct.bitfield._fields == test_Struct._bitfields["bitfield"]
        assert test_Struct.bitfield.as_int() == 0
        # TODO: args
        # TODO: kwargs

    def test_unpack(self):
        raw_struct = b"\x00\x00\x00\x00" b"\xDE\xAD\xBE\xEF" \
                     b"\xDE\xAD\xBE\xEF" b"\xDE\xAD\xBE\xEF" \
                     b"\x04\x00\x00\x00" b"\x05\x00\x00\x00" \
                     b"\x06\x00\x00\x00" b"\x07\x00\x00\x00"
        raw_tuple = struct.unpack(Example._format, raw_struct)
        test_Struct = Example.from_tuple(raw_tuple)
        assert test_Struct.id == 0
        assert isinstance(test_Struct.position, vector.vec3)
        position = core.MappedArray.from_bytes(
            b"\xDE\xAD\xBE\xEF" * 3,
            _mapping=[*"xyz"],
            _format="3f")
        assert test_Struct.position == vector.vec3(*position)
        assert test_Struct.data == (4, 5)
        assert isinstance(test_Struct.flags, ExampleFlags)
        assert test_Struct.flags == 6
        assert isinstance(test_Struct.bitfield, core.BitField)
        assert test_Struct.bitfield.as_int() == 7

    def test_pack(self):
        raw_struct = b"\x00\x00\x00\x00" b"\x00\x00\x00\x01" \
                     b"\x00\x00\x00\x02" b"\x00\x00\x00\x03" \
                     b"\x00\x00\x00\x04" b"\x00\x00\x00\x05" \
                     b"\x00\x00\x00\x06" b"\x00\x00\x00\x07"
        raw_tuple = struct.unpack(Example._format, raw_struct)
        test_Struct = Example.from_tuple(raw_tuple)
        flattened_struct = test_Struct.as_tuple()
        recreated_struct = struct.pack(Example._format, *flattened_struct)
        assert raw_struct == recreated_struct

    def test_as_bytes(self):

        class AllChildTypes(core.Struct):
            a: core.MappedArray  # struct { float x, y; };
            b: str               # char[4];
            c: core.BitField     # uint32_t hi: 16, lo: 16;
            d: ExampleFlags      # int16_t;
            e: List[int]         # int16_t[2];
            __slots__ = [*"abcde"]
            _format = "2f4sI3h"
            _arrays = {"a": [*"xy"], "e": 2}
            _bitfields = {"c": {"hi": 16, "lo": 16}}
            _classes = {"d": ExampleFlags}

        bf = core.BitField.from_int(
            0x05000600,
            _fields={"hi": 16, "lo": 16},
            _format="I")
        test_Struct = AllChildTypes(
            a=(1.2, 3.4),
            b="test",
            c=bf,
            d=ExampleFlags.FOO,
            e=[7, 8])

        assert isinstance(test_Struct.a, core.MappedArray)
        assert isinstance(test_Struct.b, str)
        assert isinstance(test_Struct.c, core.BitField)
        assert isinstance(test_Struct.d, enum.IntFlag)
        assert isinstance(test_Struct.e, list)

        assert len(test_Struct.as_bytes()) == struct.calcsize(AllChildTypes._format)
