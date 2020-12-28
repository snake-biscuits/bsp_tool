import struct

from bsp_tool.branches import base


class Example(base.Struct):
    __slots__ = ["id", "position", "data"]
    _format = "i3f4i"
    _arrays = {"position": [*"xyz"], "data": 4}


class TestBase:
    def test_unpack(self):
        raw_struct = b"\x00\x00\x00\x00" b"\xDE\xAD\xBE\xEF" \
                     b"\xDE\xAD\xBE\xEF" b"\xDE\xAD\xBE\xEF" \
                     b"\x00\x00\x00\x04" b"\x00\x00\x00\x05" \
                     b"\x00\x00\x00\x06" b"\x00\x00\x00\x07"
        raw_tuple = struct.unpack(self.Example._format, raw_struct)
        test_struct = Example(raw_tuple)

        assert test_struct.id == 0
        # assert test_struct.position == base.MappedArray([*"xyz"])

    def test_pack(self):
        raw_struct = b"\x00\x00\x00\x00" b"\x00\x00\x00\x01" \
                     b"\x00\x00\x00\x02" b"\x00\x00\x00\x03" \
                     b"\x00\x00\x00\x04" b"\x00\x00\x00\x05" \
                     b"\x00\x00\x00\x06" b"\x00\x00\x00\x07"
        raw_tuple = struct.unpack(self.Example._format, raw_struct)
        test_struct = Example(raw_tuple)
        flattened_struct = test_struct.flat()
        recreated_struct = struct.pack(self.Example._format, *flattened_struct)
        assert raw_struct == recreated_struct


class TestMappedArray:
    def test_init(self):
        sample_A = base.MappedArray([0, 1, 2])
        sample_B = base.MappedArray([3, 4, 5], ["a", "b", "c"])
        sample_C = base.MappedArray([6, 7, 8, 9], {"D": ["i", "ii"],
                                                   "E": ["iii", " iv"]})
        assert (sample_A, sample_B, sample_C) != (None, None, None)
