# https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
from __future__ import annotations
import math
from typing import Iterable

from . import vector


class Quaternion:
    x: float
    y: float
    z: float
    w: float

    def __init__(self, x=0, y=0, z=0, w=0):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __repr__(self) -> str:
        args = ", ".join([
            f"{a}={getattr(self, a)}"
            for a in "xyzw"])
        return f"{self.__class__.__name__}({args})"

    def __eq__(self, other: Quaternion) -> bool:
        if isinstance(other, Quaternion):
            return all(
                math.isclose(a, b)
                for a, b in zip(self, other))
        return False

    def __hash__(self) -> int:
        return hash(tuple(self))

    def __iter__(self) -> Iterable:
        return iter((self.x, self.y, self.z, self.w))

    def __len__(self) -> int:
        return 4

    # TODO: __mul__ vector.vec3 to apply rotation?

    # TODO: Quaterion -> Euler xyz

    @classmethod
    def from_euler(cls, angles: vector.vec3) -> Quaternion:
        # NOTE: assuming a specific rotation order; idk which
        # -- haven't broken down the matrix math myself
        out = cls()
        cos_x = math.cos(math.radians(angles.x) / 2)  # roll
        sin_x = math.sin(math.radians(angles.x) / 2)
        cos_y = math.cos(math.radians(angles.y) / 2)  # pitch
        sin_y = math.sin(math.radians(angles.y) / 2)
        cos_z = math.cos(math.radians(angles.z) / 2)  # yaw
        sin_z = math.sin(math.radians(angles.z) / 2)
        out.x = math.fsum([sin_x * cos_y * cos_z, -(cos_x * sin_y * sin_z)])
        out.y = math.fsum([cos_x * sin_y * cos_z, +(sin_x * cos_y * sin_z)])
        out.z = math.fsum([cos_x * cos_y * sin_z, -(sin_x * sin_y * cos_z)])
        out.w = math.fsum([cos_x * cos_y * cos_z, +(sin_x * sin_y * sin_z)])
        return out
