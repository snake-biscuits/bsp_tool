from __future__ import annotations
import math
import struct

from .. import core


class Float32(core.BitField):
    _fields = {"sign": 1, "exponent": 8, "mantissa": 23}
    _format = "I"

    @classmethod
    def from_float(cls, float_: float) -> Float32:
        return cls.from_int(int.from_bytes(struct.pack("f", float_), "little"))

    def as_float(self) -> float:
        # NOTE: if NaN: data will be lost (returns generic math.nan)
        sign = -1 if self.sign else 1
        mantissa = sum(
            2 ** -i
            for i, c in enumerate(reversed(f"{self.mantissa:023b}"))
            if c == "1")
        if self.exponent == 0:  # subnormal
            return float(sign * 2 ** -126 * mantissa) if self.mantissa else sign * 0.0
        elif self.exponent == 0xFF:
            return math.nan if self.mantissa else sign * math.inf
        else:  # normal
            return float(sign * 2 ** (self.exponent - 127) * (1 + mantissa))
