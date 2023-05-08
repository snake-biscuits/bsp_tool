from bsp_tool import lumps

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
