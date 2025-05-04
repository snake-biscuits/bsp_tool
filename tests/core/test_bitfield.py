import enum
import struct

import pytest

from bsp_tool.core import bitfield


class ExampleFlags(enum.IntFlag):
    FOO = 0x01
    BAR = 0x02


class TestBitField:
    # TODO: parametrise __init__ tests
    # TODO: test_init_kwargs
    # TODO: test_init_mixed (args & kwargs)
    def test_init_args(self):
        sample = bitfield.BitField(
            0xAA, 0xBBBB, 0xCC,
            _format="I",
            _fields={"AA": 8, "BBBB": 16, "CC": 8})
        assert sample.AA == 0xAA
        assert sample.BBBB == 0xBBBB
        assert sample.CC == 0xCC
        assert sample.as_int() == 0xAABBBBCC

    def test_init_subclass_from_int(self):
        class Test_BitField(bitfield.BitField):
            _fields = dict(foo=4, bar=12)
            _format = "H"

        sample = Test_BitField.from_int(0xDEEE)
        assert sample.foo == 0xD
        assert sample.bar == 0xEEE

    def test_init_one_arg(self):
        """should work the same as .from_int"""
        sample = bitfield.BitField(
            0xF0,
            _format="B",
            _fields={"alpha": 4, "omega": 4})
        assert sample.alpha == 0xF
        assert sample.omega == 0x0

    def test_overflow(self):
        sample = bitfield.BitField(
            0xFFFFFFFF,
            _format="I",
            _fields={"red": 8, "green": 16, "blue": 8})
        with pytest.raises(OverflowError):
            sample.red = 0xFF + 1

    def test_as_bytes(self):
        """wraps .as_int()"""

        class AllChildTypes(bitfield.BitField):
            _fields = {"flags": 2, "unknown": 6}
            _format = "B"
            _classes = {"flags": ExampleFlags}

        sample = AllChildTypes(ExampleFlags.BAR, 42)
        actual = sample.as_bytes()

        expected = sum([
            ExampleFlags.BAR.value << 0,
            42 << 2
            ]).to_bytes(1, "little")

        actual_size = len(actual)
        expected_size = struct.calcsize(AllChildTypes._format)

        assert actual_size == expected_size
        assert actual == expected
