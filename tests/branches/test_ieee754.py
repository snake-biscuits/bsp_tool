import math
from typing import Tuple

from bsp_tool.branches.ieee754 import Float32

import pytest


test_floats = {
    "+2.0": +2.0,
    "+1.0": +1.0,
    "+0.0": +0.0,
    "-0.0": -0.0,
    "-1.0": -1.0,
    "-2.0": -2.0}


@pytest.mark.parametrize("float_", test_floats.values(), ids=test_floats.keys())
def test_accurate_enough(float_: float):
    x = Float32.from_float(float_)
    assert math.isclose(float_, x.as_float(), rel_tol=1e-7)


test_ints = {
    "3F80000": [0x3F800000, (0, 127, 0x000000)],  # 1.0
    "FLT_MIN": [0xFF7FFFFF, (1, 254, 0x7FFFFF)],
    "FLT_MAX": [0x7F7FFFFF, (0, 254, 0x7FFFFF)]}


@pytest.mark.parametrize("hex_,expected", test_ints.values(), ids=test_ints.keys())
def test_from_int(hex_: int, expected: Tuple[int, int, int]):
    x = Float32.from_int(hex_)
    sign, exponent, mantissa = expected
    assert x.sign == sign
    assert x.exponent == exponent
    assert x.mantissa == mantissa
