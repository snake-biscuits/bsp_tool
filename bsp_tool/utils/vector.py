"""2D & 3D vector classes"""
from __future__ import annotations

import itertools
import math
from typing import Iterable, Union


# TODO: swizzle __getattr__ methods
# TODO: move silent type casting out of individual methods
# -- so we can keep it consistent
# -- _compatible_type(other) -> bool

class vec2:
    """2D vector class"""
    __slots__ = ["x", "y"]
    x: float
    y: float

    def __init__(self, x: float = 0, y: float = 0):
        self.x, self.y = float(x), float(y)

    def __abs__(self) -> float:
        return self.magnitude()

    def __add__(self, other: Iterable) -> vec2:
        if isinstance(other, (vec2, vec3, Iterable)):
            return vec2(*map(math.fsum, zip(self, other)))
        else:
            raise TypeError(f"cannot add '{type(other).__name__}' to '{type(self).__name__}'")

    def __eq__(self, other: Union[vec2, vec3, Iterable]) -> bool:
        # TODO: Sequences
        if isinstance(other, (vec2, vec3, Iterable)):
            return all([
                math.isclose(s, o)
                for s, o in itertools.zip_longest(self, other, fillvalue=0)])
        return False

    def __format__(self, format_spec: str = "") -> str:
        return " ".join([format(i, format_spec) for i in self])

    def __floordiv__(self, other: float) -> vec2:
        return vec2(self.x // other, self.y // other)

    def __getitem__(self, key: int) -> float:
        return (self.x, self.y)[key]

    def __hash__(self) -> int:
        return hash(tuple(self))

    def __iter__(self) -> Iterable:
        return iter((self.x, self.y))

    def __len__(self) -> int:
        return 2

    def __mul__(self, other: float) -> vec2:
        return vec2(self.x * other, self.y * other)

    def __neg__(self) -> vec2:
        return vec2(-self.x, -self.y)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{(self.x, self.y)}"

    def __rmul__(self, other: float) -> vec2:
        return self.__mul__(other)

    def __setitem__(self, key: Union[int, slice], value: float):
        if isinstance(key, slice):
            for k, v in zip("xy"[key], value[key]):
                setattr(self, k, v)
        else:
            setattr(self, "xy"[key], value)

    def __sub__(self, other: Iterable) -> vec2:
        return vec2(*[math.fsum((s, -o)) for s, o in zip(self, other)])

    def __truediv__(self, other: float) -> vec2:
        return vec2(self.x / other, self.y / other)

    def magnitude(self) -> float:
        """length of vector"""
        return math.sqrt(self.sqrmagnitude())

    def normalise(self):
        """scale this vector into a unit vector"""
        self.x, self.y = self.normalised()

    def normalised(self) -> vec2:
        """returns this vector if length was 1 (unless length is 0), does not mutate"""
        m = self.sqrmagnitude()
        return vec2(self.x/m, self.y/m) if m != 0 else self

    def rotated(self, degrees: float) -> vec2:
        """returns this vector rotated clockwise on Z-axis"""
        theta = math.radians(degrees)
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)
        x = round(math.fsum([self[0] * cos_theta, self[1] * sin_theta]), 6)
        y = round(math.fsum([self[1] * cos_theta, -self[0] * sin_theta]), 6)
        return vec2(x, y)

    def sqrmagnitude(self) -> float:
        """for quick comparisions"""
        return math.fsum([a ** 2 for a in self])


class vec3:
    """3D vector class"""
    __slots__ = ["x", "y", "z"]
    x: float
    y: float
    z: float

    def __init__(self, x=0, y=0, z=0):
        self.x, self.y, self.z = map(float, (x, y, z))

    def __abs__(self) -> float:
        return self.magnitude()

    def __add__(self, other: Iterable) -> vec3:
        if isinstance(other, (vec2, vec3)) or (isinstance(other, Iterable) and len(other) in (2, 3)):
            return vec3(*map(math.fsum, itertools.zip_longest(self, other, fillvalue=0)))
        else:
            raise TypeError(f"cannot add '{type(other).__name__}' to '{type(self).__name__}'")

    def __eq__(self, other: Union[float, Iterable]) -> bool:
        if isinstance(other, (vec2, vec3)) or (isinstance(other, Iterable) and len(other) in (2, 3)):
            return all([math.isclose(s, o) for s, o in itertools.zip_longest(self, other, fillvalue=0)])
        return False

    def __format__(self, format_spec: str = "") -> str:
        return " ".join([format(a, format_spec) for a in self])

    def __floordiv__(self, other: Union[float, Iterable]) -> vec3:
        return vec3(self.x // other, self.y // other, self.z // other)

    def __getitem__(self, key: int) -> float:
        return [self.x, self.y, self.z][key]

    def __hash__(self) -> int:
        return hash(tuple(self))

    def __iter__(self) -> Iterable:
        return iter((self.x, self.y, self.z))

    def __len__(self) -> int:
        return 3

    def __mul__(self, other: Union[float, Iterable]) -> vec3:
        if isinstance(other, (int, float)):
            return vec3(*[i * other for i in self])
        elif isinstance(other, Iterable):
            return vec3(math.fsum([self[1] * other[2], -self[2] * other[1]]),
                        math.fsum([self[2] * other[0], -self[0] * other[2]]),
                        math.fsum([self[0] * other[1], -self[1] * other[0]]))

    def __neg__(self) -> vec3:
        return vec3(-self.x, -self.y, -self.z)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{(self.x, self.y, self.z)}"

    def __rmul__(self, other: Union[float, Iterable]) -> vec3:
        return self.__mul__(other)

    def __setitem__(self, key: Union[int, slice], value: float):
        if isinstance(key, slice):
            for k, v in zip("xyz"[key], value[key]):
                setattr(self, k, v)
        else:
            setattr(self, "xyz"[key], value)

    def __sub__(self, other: Iterable) -> vec3:
        return vec3(*map(math.fsum, zip(self, -other)))

    def __truediv__(self, other: float) -> vec3:
        return vec3(self.x / other, self.y / other, self.z / other)

    def magnitude(self) -> float:
        """length of vector"""
        return math.sqrt(self.sqrmagnitude())

    def normalise(self):
        """scale this vector into a unit vector"""
        new = self.normalised()
        self.x, self.y, self.z = new.x, new.y, new.z

    def normalised(self) -> vec3:
        """returns vec3 as a unit vector"""
        m = self.magnitude()
        return vec3(self.x/m, self.y/m, self.z/m) if m != 0 else self

    def rotated(self, x: float = 0, y: float = 0, z: float = 0) -> vec3:
        """This method can be used on any iterable, inputs are degrees rotated around axis"""
        angles = [math.radians(i) for i in (x, y, z)]
        cos_x, sin_x = math.cos(angles[0]), math.sin(angles[0])
        cos_y, sin_y = math.cos(angles[1]), math.sin(angles[1])
        cos_z, sin_z = math.cos(angles[2]), math.sin(angles[2])
        out = vec3(self[0],
                   math.fsum([self[1] * cos_x, -self[2] * sin_x]),
                   math.fsum([self[1] * sin_x, self[2] * cos_x]))
        out = vec3(math.fsum([out.x * cos_y, out.z * sin_y]),
                   out.y,
                   math.fsum([out.z * cos_y, out.x * sin_y]))
        out = vec3(math.fsum([out.x * cos_z, -out.y * sin_z]),
                   math.fsum([out.x * sin_z, out.y * cos_z]),
                   out.z)
        out = vec3(*[round(i, 6) for i in out])
        return out

    def sqrmagnitude(self) -> float:
        """vec3.magnitude but without math.sqrt
        handy for comparing length quickly"""
        return math.fsum([i ** 2 for i in self])


def dot(a: Iterable, b: Iterable) -> float:
    """Returns the dot product of two vectors"""
    return math.fsum([i * j for i, j in itertools.zip_longest(a, b, fillvalue=0)])


def lerp(a: Union[float, Iterable], b: Union[float, Iterable], t: float) -> Union[float, list]:
    """Interpolates between two given points by t [0-1]"""
    if isinstance(a, Iterable) and isinstance(b, Iterable):
        r = [lerp(i, j, t) for i, j in itertools.zip_longest(a, b, fillvalue=0)]
        return r
    else:
        return math.fsum([a, t * math.fsum([b, -a])])


def angle_between(a: vec3, b: vec3) -> float:
    dot(a, b) / (a.magnitude() * b.magnitude())


def sort_clockwise(points: vec3, normal: Iterable) -> list:
    C = sum(points, vec3()) / len(points)
    def score(A, B): return dot(normal, (A - C) * (B - C))
    left = []
    right = []
    for index, point in enumerate(points[1:]):
        (left if score(points[0], point) >= 0 else right).append(index + 1)
    proximity = dict()  # number of points between self and start
    for i, p in enumerate(points[1:]):
        i += 1
        if i in left:
            proximity[i] = len(right)
            for j in left:
                if score(p, points[j]) >= 0:
                    proximity[i] += 1
        else:
            proximity[i] = 0
            for j in right:
                if score(p, points[j]) >= 0:
                    proximity[i] += 1
    sorted_vec3s = [points[0]] + [points[i] for i in sorted(proximity.keys(), key=lambda k: proximity[k])]
    return sorted_vec3s


# TODO: ivec2, ivec3, QAngle
