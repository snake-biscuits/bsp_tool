import collections
import io

from bsp_tool import lumps
from bsp_tool.branches import base

import pytest


class TestRemapNegativeIndex:
    def test_guess(self):
        assert lumps._remap_negative_index(-1, 50) == 49

    def test_range(self):
        arr = [*range(128)]
        for i in range(-128, 0):
            positive_i = lumps._remap_negative_index(i, 128)
            assert arr[i] == arr[positive_i]

    def test_negative_out_of_range(self):
        with pytest.raises(IndexError):
            [*range(8)][lumps._remap_negative_index(-16, 8)]


class TestRemapSlice:
    def test_lazy(self):
        assert lumps._remap_slice(slice(None, None, None), 50) == slice(0, 50, 1)
        assert lumps._remap_slice(slice(0, None, None), 50) == slice(0, 50, 1)
        assert lumps._remap_slice(slice(0, 50, None), 50) == slice(0, 50, 1)
        assert lumps._remap_slice(slice(0, 50, 1), 50) == slice(0, 50, 1)
        assert lumps._remap_slice(slice(0, 69, 1), 50) == slice(0, 50, 1)


class TestDecompress:
    # TODO: test decompression on a repacked ValveBsp
    ...


LumpHeader_basic = collections.namedtuple("basic", ["offset", "length"])


class LumpClass_basic(base.MappedArray):
    _mapping = [*"xyz"]
    _format = "3H"


class TestBspLump:
    @pytest.mark.xfail(reason="not yet implemented")
    def test_implicit_change(self):
        header = LumpHeader_basic(offset=0, length=6)
        stream = io.BytesIO(b"\x01\x00\x02\x00\x03\x00")
        lump = lumps.BspLump.from_header(stream, header, LumpClass_basic)
        assert lump[0].x == 1
        lump[0].x += 1
        assert lump[0].x == 2
