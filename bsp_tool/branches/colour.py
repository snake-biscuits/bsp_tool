from typing import List

from .. import core


# TODO: colorsys HSV translation


class RGB24(core.MappedArray):
    _mapping = [*"rgb"]
    _format = "3B"

    def as_floats(self) -> List[float]:
        return [getattr(self, c) / 255 for c in self._mapping]


class RGBA32(RGB24):
    _mapping = [*"rgba"]
    _format = "4B"


class RGBExponent(RGB24):
    _mapping = [*"rgb", "exponent"]

    def as_floats(self) -> List[float]:
        """HDR scaled values"""
        return [(getattr(self, c) / 255) * self.exponent for c in "rgb"]
