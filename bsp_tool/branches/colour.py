from typing import List

from . import base


class Rgb24(base.MappedArray):
    _mapping = [*"rgb"]
    _format = "3B"

    def as_floats(self) -> List[float]:
        return [getattr(self, x) / 255 for x in self._mapping]


class Rgb32(Rgb24):
    _mapping = [*"rgba"]
    _format = "4B"


class RgbExponent(Rgb32):
    _mapping = [*"rgb", "exponent"]

    def as_floats(self) -> List[float]:
        """HDR scaled values"""
        return [getattr(self, x) / 255 * self.exponent for x in (*"rgb")]
