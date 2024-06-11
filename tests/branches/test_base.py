import enum
import struct
from typing import List

import pytest

from bsp_tool.branches import base
from bsp_tool.utils import vector


# TODO: test everything fails correctly when fed invalid inputs

class ExampleFlags(enum.IntFlag):
    FOO = 0x01
    BAR = 0x02


class Example(base.Struct):
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
        assert base.struct_attr_formats[Example]["data"] == "i" * 2
        assert tuple(test_Struct.data) == (0,) * 2
        assert isinstance(test_Struct.flags, ExampleFlags)
        assert test_Struct.flags == 0
        assert isinstance(test_Struct.bitfield, base.BitField)
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
        position = base.MappedArray.from_bytes(b"\xDE\xAD\xBE\xEF" * 3, _mapping=[*"xyz"], _format="3f")
        assert test_Struct.position == vector.vec3(*position)
        assert test_Struct.data == (4, 5)
        assert isinstance(test_Struct.flags, ExampleFlags)
        assert test_Struct.flags == 6
        assert isinstance(test_Struct.bitfield, base.BitField)
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

        class AllChildTypes(base.Struct):
            a: base.MappedArray  # struct { float x, y; };
            b: str               # char[4];
            c: base.BitField     # uint32_t hi: 16, lo: 16;
            d: ExampleFlags      # int16_t;
            e: List[int]         # int16_t[2];
            __slots__ = [*"abcde"]
            _format = "2f4sI3h"
            _arrays = {"a": [*"xy"], "e": 2}
            _bitfields = {"c": {"hi": 16, "lo": 16}}
            _classes = {"d": ExampleFlags}

        bf = base.BitField.from_int(0x05000600, _fields={"hi": 16, "lo": 16}, _format="I")
        test_Struct = AllChildTypes(a=(1.2, 3.4), b="test", c=bf, d=ExampleFlags.FOO, e=[7, 8])

        assert isinstance(test_Struct.a, base.MappedArray)
        assert isinstance(test_Struct.b, str)
        assert isinstance(test_Struct.c, base.BitField)
        assert isinstance(test_Struct.d, enum.IntFlag)
        assert isinstance(test_Struct.e, list)

        assert len(test_Struct.as_bytes()) == struct.calcsize(AllChildTypes._format)


class TestMappedArray:
    # TODO: test non-Subclass MappedArrays do not overlap
    def test_init(self):
        # TODO: test invalid inputs are caught
        # no args; MappedArray defaults
        test_MappedArray = base.MappedArray()
        # basic __init__
        test_MappedArray = base.MappedArray(0, 1, 2, _mapping=[*"xyz"])
        assert test_MappedArray.x == 0
        assert test_MappedArray.y == 1
        assert test_MappedArray.z == 2
        # nesting
        test_MappedArray = base.MappedArray([3, 4], [5, 6],
                                            _mapping={"C": ["i", "ii"], "D": ["iii", "iv"]})
        assert test_MappedArray.C.i == 3
        assert test_MappedArray.C.ii == 4
        assert test_MappedArray.D.iii == 5
        assert test_MappedArray.D.iv == 6
        # _format & _defaults
        # NOTE: _format should match "".join(base.type_LUT.keys()) + "1s"
        # -- subsititing "byte" for "char" with "b" & "B"
        # NOTE: _mapping should match [t.replace(" ", "_") for t in base.type_LUT.keys()]
        test_MappedArray = base.MappedArray(_format="c?bBhHiIfg1s",
                                            _mapping=["char", "bool",
                                                      "byte", "unsigned_byte",
                                                      "short", "unsigned_short",
                                                      "int", "unsigned_int",
                                                      "float", "double",
                                                      "string"])
        assert isinstance(test_MappedArray.char, bytes)
        assert test_MappedArray.char == base.type_defaults["c"]
        assert isinstance(test_MappedArray.bool, bool)
        assert test_MappedArray.bool == base.type_defaults["?"]
        assert isinstance(test_MappedArray.byte, int)
        assert test_MappedArray.byte == base.type_defaults["b"]
        assert isinstance(test_MappedArray.unsigned_byte, int)
        assert test_MappedArray.unsigned_byte == base.type_defaults["B"]
        assert isinstance(test_MappedArray.byte, int)
        assert test_MappedArray.short == base.type_defaults["h"]
        assert isinstance(test_MappedArray.unsigned_byte, int)
        assert test_MappedArray.unsigned_short == base.type_defaults["H"]
        assert isinstance(test_MappedArray.byte, int)
        assert test_MappedArray.int == base.type_defaults["i"]
        assert isinstance(test_MappedArray.unsigned_byte, int)
        assert test_MappedArray.unsigned_int == base.type_defaults["I"]
        assert isinstance(test_MappedArray.float, float)
        assert test_MappedArray.float == base.type_defaults["f"]
        assert isinstance(test_MappedArray.double, float)
        assert test_MappedArray.double == base.type_defaults["g"]
        assert isinstance(test_MappedArray.string, (str, bytes))  # can be a decoded string
        assert test_MappedArray.string == base.type_defaults["s"]
        # kwargs only
        test_MappedArray = base.MappedArray(z=1.0, _mapping=[*"xyz"], _format="3f")
        assert test_MappedArray.x == base.type_defaults["f"]
        assert test_MappedArray.y == base.type_defaults["f"]
        assert test_MappedArray.z == 1.0
        # TODO: _classes & _bitfields

    def test_attr_format_collision(self):
        x = base.MappedArray(1, 2, 3, _mapping=[*"abc"], _format="3f")
        y = base.MappedArray(4, 5, 6, _mapping=[*"def"], _format="3b")
        assert x._attr_formats != y._attr_formats
        x = base.MappedArray(1, (2, 3), _mapping={"a": None, "b": 2}, _format="3f")
        y = base.MappedArray((4, 5), 6, _mapping={"c": 2, "d": None}, _format="3b")
        assert x._attr_formats != y._attr_formats

    def test_as_cpp(self):  # covers BitField & Struct .as_cpp pretty well too
        basic = "struct MappedArray { int32_t x, y, z; };"
        multi_list = "struct MappedArray {\n\tint16_t a[2];\n\tint8_t b;\n};"
        multi_sub = "struct MappedArray {\n\tstruct { float x, y; } a;\n\tbool b;\n};"
        multi_classes = "struct MappedArray {\n\tstruct { float x, y; } a;\n\tbool b;\n};"
        multi_bitfield = "struct MappedArray {\n\tdouble a;\n\tuint8_t b;\n};"
        c_structs = {basic: dict(_mapping=[*"xyz"], _format="3i"),
                     multi_list: dict(_mapping={"a": 2, "b": None}, _format="2hb"),
                     multi_sub: dict(_mapping={"a": [*"xy"], "b": None}, _format="2f?"),
                     multi_classes: dict(_mapping={"a": [*"xy"], "b": None}, _format="2f?",
                                         _classes={"a": vector.vec2}),
                     multi_bitfield: dict(_mapping=[*"ab"], _format="gB", _bitfields={"c": 2, "d": 6})}
        # ^ {"output": {**MappedArray_definition}}

        for answer, kwargs in c_structs.items():
            assert base.MappedArray(**kwargs).as_cpp() == answer

    def test_as_bytes(self):

        class AllChildTypes(base.MappedArray):
            a: base.MappedArray  # struct { float x, y; };
            b: str               # char[4];
            c: base.BitField     # uint32_t hi: 16, lo: 16;
            d: ExampleFlags      # int16_t;
            e: List[int]         # int16_t[2];
            _mapping = {"a": [*"xy"], "b": None, "c": None, "d": None, "e": 2}
            _format = "2f4sI3h"
            _bitfields = {"c": {"hi": 16, "lo": 16}}
            _classes = {"d": ExampleFlags}

        bf = base.BitField.from_int(0x05000600, _fields={"hi": 16, "lo": 16}, _format="I")
        test_MappedArray = AllChildTypes(a=(1.2, 3.4), b="test", c=bf, d=ExampleFlags.FOO, e=[7, 8])

        assert isinstance(test_MappedArray.a, base.MappedArray)
        assert isinstance(test_MappedArray.b, str)
        assert isinstance(test_MappedArray.c, base.BitField)
        assert isinstance(test_MappedArray.d, enum.IntFlag)
        assert isinstance(test_MappedArray.e, list)

        assert len(test_MappedArray.as_bytes()) == struct.calcsize(AllChildTypes._format)


class TestBitField:
    def test_init(self):
        # full *args
        test_bitfield = base.BitField(0xAA, 0xBBBB, 0xCC, _format="I", _fields={"AA": 8, "BBBB": 16, "CC": 8})
        assert test_bitfield.AA == 0xAA
        assert test_bitfield.BBBB == 0xBBBB
        assert test_bitfield.CC == 0xCC
        assert test_bitfield.as_int() == 0xAABBBBCC

        # TODO: full kwargs, mixed args & kwargs

        # subclass
        class Test_BitField(base.BitField):
            _fields = dict(foo=4, bar=12)
            _format = "H"

        # .from_int()
        test_bitfield = Test_BitField.from_int(0xDEEE)
        assert test_bitfield.foo == 0xD
        assert test_bitfield.bar == 0xEEE

        # single arg
        test_bitfield = base.BitField(0xF0, _format="B", _fields={"alpha": 4, "omega": 4})
        assert test_bitfield.alpha == 0xF
        assert test_bitfield.omega == 0x0

    def test_overflow(self):
        test_bitfield = base.BitField(0xFFFFFFFF, _format="I", _fields={"red": 8, "green": 16, "blue": 8})
        with pytest.raises(OverflowError):
            test_bitfield.red = 0xFF + 1

    def test_as_bytes(self):
        """wraps .as_int()"""

        class AllChildTypes(base.BitField):
            _fields = {"flags": 2, "unknown": 6}
            _format = "B"
            _classes = {"flags": ExampleFlags}

        assert len(AllChildTypes(ExampleFlags.BAR, 42).as_bytes()) == struct.calcsize(AllChildTypes._format)


def test_dict_subgroup():
    out = base.dict_subgroup({"attr.sub": 0, "attr": 1}, "attr")
    assert out == {"sub": 0}
