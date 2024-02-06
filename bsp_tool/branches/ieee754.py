from __future__ import annotations
import functools
import math
import struct

from . import base


class Float32(base.BitField):
    _fields = {"fraction": 23, "exponent": 8, "sign": 1}
    _format = "I"

    @classmethod
    def from_float(cls, float_: float) -> Float32:
        return cls.from_int(int.from_bytes(struct.pack("f", float_), "little"))

    def as_float(self) -> float:
        sign = -1 if self.sign else 1
        fraction = sum(2 ** -i for i, c in enumerate(reversed(f"{self.fraction:023b}")) if c == "1")
        # NOTE: generic NaN, data will be lost
        if self.exponent == 0:  # subnormal
            return float(sign * 2 ** -126 * fraction) if self.fraction else sign * 0.0
        elif self.exponent == 0xFF:  # normal
            return math.nan if self.fraction else sign * math.inf
        else:
            return float(functools.reduce(lambda a, b: a * b, [
                sign,
                2 ** (self.exponent - 127),
                1 + fraction]))
