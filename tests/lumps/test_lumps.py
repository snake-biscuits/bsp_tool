import collections
import io

from bsp_tool import lumps
from bsp_tool import core

import pytest


# TODO: more mutability & _changes testing
# TODO: merge with tests/test_BspLump.py (or divide concerns more clearly)


class TestRemapIndex:
    def test_guess(self):
        assert lumps._remap_index(-1, 50) == 49

    def test_range(self):
        arr = [*range(128)]
        for i in range(-128, 0):
            positive_i = lumps._remap_index(i, 128)
            assert arr[i] == arr[positive_i]

    def test_negative_out_of_range(self):
        with pytest.raises(IndexError):
            [*range(8)][lumps._remap_index(-16, 8)]


class TestRemapSliceToRange:
    def test_lazy(self):
        assert lumps._remap_slice_to_range(slice(None, None, None), 50) == range(0, 50, 1)
        assert lumps._remap_slice_to_range(slice(0, None, None), 50) == range(0, 50, 1)
        assert lumps._remap_slice_to_range(slice(0, 50, None), 50) == range(0, 50, 1)
        assert lumps._remap_slice_to_range(slice(0, 50, 1), 50) == range(0, 50, 1)
        assert lumps._remap_slice_to_range(slice(0, 69, 1), 50) == range(0, 50, 1)


LumpHeader_basic = collections.namedtuple("basic", ["offset", "length"])


class LumpClass_basic(core.MappedArray):
    _mapping = [*"xyz"]
    _format = "3H"


class TestRawBspLump:
    """test the changes system & bytearray-like behaviour"""
    # TODO: tests to ensure RawBspLump behaves like a bytearray
    ...


class TestBspLump:
    def test_implicit_change(self):
        header = LumpHeader_basic(offset=0, length=6)
        stream = io.BytesIO(b"\x01\x00\x02\x00\x03\x00")
        lump = lumps.BspLump.from_header(stream, header, LumpClass_basic)
        assert lump[0].x == 1
        lump[0].x += 1
        assert lump[0].x == 2


# TODO: external lump test files as part of test maps (Issue #16)
# TODO: TestGameLump
# TODO: TestDarkMessiahSPGameLump
