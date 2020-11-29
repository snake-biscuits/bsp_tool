import struct
import unittest

from bsp_tool.branches import common


class TestBaseMethods(unittest.TestCase):

    def setUp(self):
        class Example(common.Base):
            __slots__ = ["id", "position", "data"]
            _format = "i3f4i"
            _arrays = {"position": [*"xyz"], "data": 4}
        self.Example = Example

    def test_flat(self):
        # test_unpack
        raw_struct = b"\x00\x00\x00\x00" b"\x00\x00\x00\x01" \
                     b"\x00\x00\x00\x02" b"\x00\x00\x00\x03" \
                     b"\x00\x00\x00\x04" b"\x00\x00\x00\x05" \
                     b"\x00\x00\x00\x06" b"\x00\x00\x00\x07"
        raw_tuple = struct.unpack(self.Example._format, raw_struct)
        test_struct = self.Example(raw_tuple)
        # test_pack
        flattened_struct = test_struct.flat()
        recreated_struct = struct.pack(self.Example._format, *flattened_struct)
        self.assertEqual(raw_struct, recreated_struct)


class TestMappedArrayMethods(unittest.TestCase):

    def setUp(self):
        self.sample_A = common.MappedArray([0, 1, 2])
        self.sample_B = common.MappedArray([3, 4, 5], ["a", "b", "c"])
        self.sample_C = common.MappedArray([6, 7, 8, 9], {"D": ["i", "ii"],
                                                           "E": ["iii", " iv"]})
