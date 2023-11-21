from __future__ import annotations
from collections.abc import Iterable
import math
from typing import Union

from . import vector


# TODO: ivec variants (not yet implemented)

class AABB:
    # NOTE: no internal validity checks (mins <= maxs; extents >= 0)
    mins: vector.vec3 = property(lambda s: s._mins)
    maxs: vector.vec3 = property(lambda s: s._maxs)
    origin: vector.vec3 = property(lambda s: s._origin)
    extents: vector.vec3 = property(lambda s: s._extents)  # should be positive

    def __init__(self):
        self._origin = vector.vec3(*[0] * 3)
        self._extents = vector.vec3(*[math.inf] * 3)
        self._mins = vector.vec3(*[math.inf] * 3)
        self._maxs = vector.vec3(*[-math.inf] * 3)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {tuple(self.mins)} -> {tuple(self.maxs)}>"

    def __add__(self, other: Union[vector.vec3, AABB]) -> AABB:
        out = self.__class__()
        if isinstance(other, Iterable) and len(other) == 3:
            other = vector.vec3(*other)
        if isinstance(other, vector.vec3):  # expand bounds to contain point
            out.mins = vector.vec3(*[min(s, o) for s, o in zip(self.mins, other)])
            out.maxs = vector.vec3(*[max(s, o) for s, o in zip(self.maxs, other)])
        elif isinstance(other, AABB):  # expand bounds around other AABB
            out.mins = vector.vec3(*[min(s, o) for s, o in zip(self.mins, other.mins)])
            out.maxs = vector.vec3(*[max(s, o) for s, o in zip(self.maxs, other.maxs)])
        else:
            raise TypeError(f"Cannot add type '{type(other)}' to {self.__class__.__name__}")
        return out

    def __eq__(self, other: AABB) -> bool:
        if isinstance(other, AABB):
            return self.mins == other.mins and self.maxs == other.maxs
        else:
            return False

    def __contains__(self, other: Union[vector.vec3, AABB]) -> bool:
        if isinstance(other, Iterable) and len(other) == 3:
            other = vector.vec3(*other)
        if isinstance(other, vector.vec3):
            for min_, axis, max_ in zip(self.mins, other, self.maxs):
                if not min_ <= axis <= max_:  # include edges
                    return False
            else:
                return True
        # elif isinstance(other, AABB):
        else:
            raise NotImplementedError()

    # TODO: partial intersection; the "any" to __contains__' "all"

    @classmethod
    def from_mins_maxs(cls, mins: vector.vec3, maxs: vector.vec3) -> AABB:
        out = cls()
        assert len(mins) == 3
        assert len(maxs) == 3
        out._mins = vector.vec3(*mins)
        out._maxs = vector.vec3(*maxs)
        out._origin = (out.mins + out.maxs) / 2
        out._extents = out.maxs - out.origin
        return out

    @classmethod
    def from_origin_extents(cls, origin: vector.vec3, extents: vector.vec3) -> AABB:
        out = cls()
        assert len(origin) == 3
        assert len(extents) == 3
        out.origin = vector.vec3(*origin)
        out.extents = vector.vec3(*extents)
        return out

    @mins.setter
    def mins(self, new_mins: vector.vec3):
        """expand bounds"""
        self._mins = new_mins
        self._origin = (self.mins + self.maxs) / 2
        self._extents = self.mins + self.origin

    @maxs.setter
    def maxs(self, new_maxs: vector.vec3):
        """expand bounds"""
        self._maxs = new_maxs
        self._origin = (self.mins + self.maxs) / 2
        self._extents = self.maxs - self.origin

    @origin.setter
    def origin(self, new_origin: vector.vec3):
        """move the center, keep dimensions"""
        self._origin = new_origin
        self._mins = self.origin - self.extents
        self._maxs = self.origin + self.extents

    @extents.setter
    def extents(self, new_extents: vector.vec3):
        """keep the center, change dimensions"""
        self._extents = new_extents
        self._mins = self.origin - self.extents
        self._maxs = self.origin + self.extents
