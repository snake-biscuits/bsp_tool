import enum
import struct
from typing import List

from bsp_tool.core import common
from bsp_tool.core import bitfield
from bsp_tool.core import mapped_array
from bsp_tool.utils import vector


# TODO: test_mapping_length


class ExampleFlags(enum.IntFlag):
    FOO = 0x01
    BAR = 0x02


# TODO: test invalid inputs are caught
class TestMappedArray:
    # TODO: parametrise init tests
    def test_init_no_args(self):
        sample = mapped_array.MappedArray()
        assert isinstance(sample, mapped_array.MappedArray)
        # TODO: more checks

    def test_init_flat(self):
        sample = mapped_array.MappedArray(
            0, 1, 2,
            _mapping=[*"xyz"])
        assert sample.x == 0
        assert sample.y == 1
        assert sample.z == 2

    def test_init_nested(self):
        sample = mapped_array.MappedArray(
            [3, 4], [5, 6],
            _mapping={"C": ["i", "ii"], "D": ["iii", "iv"]})
        assert sample.C.i == 3
        assert sample.C.ii == 4
        assert sample.D.iii == 5
        assert sample.D.iv == 6

    def test_init_defaults(self):
        # _format & _defaults
        # NOTE: _format should match "".join(base.type_LUT.keys()) + "1s"
        # -- subsititing "byte" for "char" with "b" & "B"
        # NOTE: _mapping should match:
        # -- [t.replace(" ", "_") for t in base.type_LUT.keys()]
        sample = mapped_array.MappedArray(
            _format="c?bBhHiIfg1s",
            _mapping=[
                "char", "bool",
                "byte", "unsigned_byte",
                "short", "unsigned_short",
                "int", "unsigned_int",
                "float", "double",
                "string"])
        assert isinstance(sample.char, bytes)
        assert sample.char == common.type_defaults["c"]
        assert isinstance(sample.bool, bool)
        assert sample.bool == common.type_defaults["?"]
        assert isinstance(sample.byte, int)
        assert sample.byte == common.type_defaults["b"]
        assert isinstance(sample.unsigned_byte, int)
        assert sample.unsigned_byte == common.type_defaults["B"]
        assert isinstance(sample.byte, int)
        assert sample.short == common.type_defaults["h"]
        assert isinstance(sample.unsigned_byte, int)
        assert sample.unsigned_short == common.type_defaults["H"]
        assert isinstance(sample.byte, int)
        assert sample.int == common.type_defaults["i"]
        assert isinstance(sample.unsigned_byte, int)
        assert sample.unsigned_int == common.type_defaults["I"]
        assert isinstance(sample.float, float)
        assert sample.float == common.type_defaults["f"]
        assert isinstance(sample.double, float)
        assert sample.double == common.type_defaults["g"]
        # NOTE: both bytes & string are valid here
        assert isinstance(sample.string, (str, bytes))
        assert sample.string == common.type_defaults["s"]

    def test_init_kwargs(self):
        sample = mapped_array.MappedArray(
            z=1.0,
            _mapping=[*"xyz"],
            _format="3f")
        assert sample.x == common.type_defaults["f"]
        assert sample.y == common.type_defaults["f"]
        assert sample.z == 1.0

    # TODO: __init__ w/ _classes
    # TODO: __init__ w/ _bitfields
    # NOTE: both are touched on w/ test_as_bytes

    def test_attr_format_collision(self):
        """ensuring non-subclass MappedArrays don't have dict collision"""
        x = mapped_array.MappedArray(
            1, 2, 3,
            _mapping=[*"abc"],
            _format="3f")
        y = mapped_array.MappedArray(
            4, 5, 6,
            _mapping=[*"def"],
            _format="3b")
        assert x._attr_formats != y._attr_formats

        x = mapped_array.MappedArray(
            1, (2, 3),
            _mapping={"a": None, "b": 2},
            _format="3f")
        y = mapped_array.MappedArray(
            (4, 5), 6,
            _mapping={"c": 2, "d": None},
            _format="3b")
        assert x._attr_formats != y._attr_formats

    def test_as_bytes(self):

        class AllChildTypes(mapped_array.MappedArray):
            a: mapped_array.MappedArray  # struct { float x, y; };
            b: str                       # char[4];
            c: bitfield.BitField         # uint32_t hi: 16, lo: 16;
            d: ExampleFlags              # int16_t;
            e: List[int]                 # int16_t[2];
            _mapping = {"a": [*"xy"], "b": None, "c": None, "d": None, "e": 2}
            _format = "2f4sI3h"
            _bitfields = {"c": {"hi": 16, "lo": 16}}
            _classes = {"d": ExampleFlags}

        bf = bitfield.BitField.from_int(
            0x05000600,
            _fields={"hi": 16, "lo": 16},
            _format="I")

        sample = AllChildTypes(
            a=(1.2, 3.4),
            b="test",
            c=bf,
            d=ExampleFlags.FOO,
            e=[7, 8])

        assert isinstance(sample.a, mapped_array.MappedArray)
        assert isinstance(sample.b, str)
        assert isinstance(sample.c, bitfield.BitField)
        assert isinstance(sample.d, enum.IntFlag)
        assert isinstance(sample.e, list)

        actual = sample.as_bytes()
        # TODO: expected bytes
        expected = b"".join([
            struct.pack("2f", 1.2, 3.4),
            b"test",
            b"\x00\x06\x00\x05",  # little-endian 0x05000600
            ExampleFlags.FOO.value.to_bytes(2, "little"),
            struct.pack("2h", 7, 8)])

        actual_size = len(actual)
        expected_size = struct.calcsize(AllChildTypes._format)

        assert actual_size == expected_size
        assert actual == expected
