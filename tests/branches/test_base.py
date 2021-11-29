import struct

from bsp_tool.branches import base


class Example(base.Struct):
    __slots__ = ["id", "position", "data"]
    _format = "i3f4i"
    _arrays = {"position": [*"xyz"], "data": 4}


class TestStruct:
    def test_unpack(self):
        raw_struct = b"\x00\x00\x00\x00" b"\xDE\xAD\xBE\xEF" \
                     b"\xDE\xAD\xBE\xEF" b"\xDE\xAD\xBE\xEF" \
                     b"\x04\x00\x00\x00" b"\x05\x00\x00\x00" \
                     b"\x06\x00\x00\x00" b"\x07\x00\x00\x00"
        raw_tuple = struct.unpack(Example._format, raw_struct)
        test_struct = Example.from_tuple(raw_tuple)
        assert test_struct.id == 0
        assert test_struct.position == base.MappedArray.from_bytes(b"\xDE\xAD\xBE\xEF" * 3,
                                                                   _mapping=[*"xyz"],
                                                                   _format="3f")
        assert test_struct.data == (4, 5, 6, 7)

    def test_pack(self):
        raw_struct = b"\x00\x00\x00\x00" b"\x00\x00\x00\x01" \
                     b"\x00\x00\x00\x02" b"\x00\x00\x00\x03" \
                     b"\x00\x00\x00\x04" b"\x00\x00\x00\x05" \
                     b"\x00\x00\x00\x06" b"\x00\x00\x00\x07"
        raw_tuple = struct.unpack(Example._format, raw_struct)
        test_struct = Example.from_tuple(raw_tuple)
        flattened_struct = test_struct.flat()
        recreated_struct = struct.pack(Example._format, *flattened_struct)
        assert raw_struct == recreated_struct


class TestMappedArray:
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
