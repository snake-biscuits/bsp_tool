from __future__ import annotations
from collections.abc import Iterable
import math
from typing import Dict, List, Union

from . import geometry
from . import vector


# TODO: ivec3 variants (not yet implemented)
# TODO: YawOBB (Yaw-Oriented Bounding Box)
# TODO: Sphere, Cylinder, Capsule (Sphere + Cylinder)
# TODO: SlicedBrush(brush, plane) -> (front: Brush, back: Brush)


class AABB:
    """Axis-Aligned Bounding Box"""
    # NOTE: no internal validity checks (mins <= maxs; extents >= 0)
    mins: vector.vec3 = property(lambda s: s._mins)
    maxs: vector.vec3 = property(lambda s: s._maxs)
    origin: vector.vec3 = property(lambda s: s._origin)
    extents: vector.vec3 = property(lambda s: s._extents)  # should be positive
    # NOTE: you can add a delta to extents before testing for collision

    def __init__(self):
        self._origin = vector.vec3(*[0] * 3)
        self._extents = vector.vec3(*[math.inf] * 3)
        self._mins = vector.vec3(*[math.inf] * 3)
        self._maxs = vector.vec3(*[-math.inf] * 3)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {tuple(self.mins)} -> {tuple(self.maxs)}>"

    def __add__(self, other: Union[vector.vec3, AABB]) -> AABB:
        out = self.__class__()
        if (isinstance(other, Iterable) and len(other) == 3) or isinstance(other, vector.vec2):
            other = vector.vec3(*other)
        if isinstance(other, vector.vec3):  # expand bounds to contain point
            out.mins = vector.vec3(*[min(s, o) for s, o in zip(self.mins, other)])
            out.maxs = vector.vec3(*[max(s, o) for s, o in zip(self.maxs, other)])
        elif isinstance(other, AABB):  # expand bounds around other AABB
            out.mins = vector.vec3(*[min(s, o) for s, o in zip(self.mins, other.mins)])
            out.maxs = vector.vec3(*[max(s, o) for s, o in zip(self.maxs, other.maxs)])
        else:
            raise TypeError(f"{self.__class__.__name__} cannot contain '{type(other).__name__}'")
        return out

    def __eq__(self, other: AABB) -> bool:
        if isinstance(other, AABB):
            return (self.mins, self.maxs) == (other.mins, other.maxs)
        else:
            return False

    def __contains__(self, other: Union[vector.vec3, AABB]) -> bool:
        # type coersion
        if isinstance(other, Iterable) and len(other) == 3:
            other = vector.vec3(*other)
        elif isinstance(other, Brush):
            other = other.bounds
        # tests
        if isinstance(other, vector.vec3):
            return all([m <= a <= M for m, a, M in zip(self.mins, other, self.maxs)])
        elif isinstance(other, AABB):
            mins_inside = all([s <= o for s, o in zip(self.mins, other.mins)])
            maxs_inside = all([s >= o for s, o in zip(self.maxs, other.maxs)])
            return mins_inside and maxs_inside
        else:
            raise TypeError(f"{self.__class__.__name__} cannot contain '{type(other).__name__}'")

    def intersects(self, other: AABB) -> bool:
        return all([sm <= oM and sM >= om for sm, oM, sM, om in zip(self.mins, other.maxs, self.maxs, other.mins)])

    def as_model(self) -> geometry.Model:
        signs = [
            vector.vec3(
                (-1, 1)[i >> 2],
                (-1, 1)[i >> 1 & 1],
                (-1, 1)[i & 1])
            for i in range(8)]
        vertices = [
            vector.vec3(
                sign.x * self.extents.x,
                sign.y * self.extents.y,
                sign.z * self.extents.z)
            for sign in signs]
        quads = [
            ((0b000, 0b010, 0b011, 0b001), vector.vec3(x=-1)),
            ((0b000, 0b001, 0b101, 0b100), vector.vec3(y=-1)),
            ((0b000, 0b100, 0b110, 0b010), vector.vec3(z=-1)),
            ((0b100, 0b101, 0b111, 0b110), vector.vec3(x=1)),
            ((0b010, 0b110, 0b111, 0b011), vector.vec3(y=1)),
            ((0b001, 0b011, 0b111, 0b101), vector.vec3(z=1))]
        polygons = [
            geometry.Polygon([
                geometry.Vertex(vertices[i], normal)
                for i in indices])
            for indices, normal in quads]
        return geometry.Model(meshes=[geometry.Mesh(polygons=polygons)], origin=self.origin)

    # INITIALISERS

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

    @classmethod
    def from_points(cls, points: List[vector.vec3]) -> AABB:
        return sum({vector.vec3(*p) for p in points}, start=cls())

    # SETTERS

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


class Plane:
    normal: vector.vec3  # should always be normalised
    distace: float

    def __init__(self, normal: vector.vec3, distance: float):
        self.normal = vector.vec3(*normal)
        assert math.isclose(self.normal.magnitude(), 1, rel_tol=1e-6), "normal must be a unit vector"
        self.distance = distance

    def __eq__(self, other: Plane) -> bool:
        if isinstance(other, Plane):
            return self.normal == other.normal and math.isclose(self.distance, other.distance)
        else:
            return False

    def __neg__(self) -> Plane:
        return self.__class__(-self.normal, -self.distance)

    def __repr__(self) -> str:
        return f"Plane({self.normal!r}, {self.distance})"

    # COLLISION

    def test(self, point: vector.vec3) -> float:
        return vector.dot(self.normal, point) - self.distance

    def intersects(self, aabb: AABB) -> bool:
        # TODO: document how edge-cases are handled
        xs, ys, zs = zip(aabb.mins, aabb.maxs)
        vertices = [vector.vec3(x, y, z) for x in xs for y in ys for z in zs]
        side_checks = {self.test(v) > 0 for v in vertices}  # true: front, false: back
        return len(side_checks) > 0  # plane divides the aabb

    # BRUSH INTERACTIONS

    def is_axial_of(self, brush: Brush) -> bool:
        """axial normal & same distance as side of the same axis"""
        if math.isclose(self.normal.sqrmagnitude(), 1):
            sign = vector.dot(self.normal, [1] * 3)
            axes = (brush.bounds.mins, brush.bounds.maxs)[sign > 0]
            return math.isclose(vector.dot(self.normal, axes), self.distance)
        return False

    def is_bevel_of(self, brush: Brush) -> bool:
        """45 degree normal and distance lines up with matching brush corner / edge"""
        # sqrt(2) / 2 or sqrt(3) / 3 (2D / 3D 45 degrees)
        # on outward facing corners of aabb
        # use normal sign to identify edge / corner
        # use vector.dot to detect if normal is exactly on edge / corner
        raise NotImplementedError()

    # editor format 2-way conversion

    @classmethod
    def from_triangle(cls, A: vector.vec3, B: vector.vec3, C: vector.vec3) -> Plane:
        """normal faces clockwise direction"""
        normal = -((A - B) * (A - C)).normalised()
        return cls(normal, vector.dot(A, normal))

    def as_triangle(self, radius: float = 64) -> List[vector.vec3]:
        # TODO: verify orientation
        axis = "y" if math.isclose(abs(self.normal.z), 1) else "z"
        non_parallel = vector.vec3(**{axis: -1})
        local_y = (non_parallel * self.normal).normalised() * radius
        local_x = (local_y * self.normal).normalised() * radius
        A = self.normal * self.distance
        return A, A + local_y, A + local_x


class Brush:
    """AABB + Planes"""
    # NOTE: primarily focused on physics, not so much geo / metadata
    bounds: AABB
    planes: List[Plane]  # property
    # TODO: Brush.axial_planes() -> Generator[Plane, None, None]:
    # TODO: Brush.bevel_planes() -> Generator[Plane, None, None]:  # x & y only
    _planes: List[Plane]
    # TODO: convexity check
    # TODO: planes cancelling each other out
    # TODO: [extensions.editor / geometry] generate face per plane (side)

    def __init__(self):
        self.bounds = AABB()
        # NOTE: default bounds should be an invalid brush
        self._planes = list()
        # TODO: ensure all planes intersect bounds
        # TODO: initialise from just planes & calculate bounds
        # TODO: update bounds when sliced by plane (+/- for front/back slices)

    def __contains__(self, other: Union[vector.vec3, AABB]) -> bool:
        if other in self.bounds:
            return all([p.test(other) <= 0 for p in self._planes])  # behind all planes
        else:
            return False

    def __eq__(self, other: Brush) -> bool:
        if isinstance(other, Brush):
            if self.bounds == other.bounds:
                if len(self._planes) == len(other._planes):
                    return all([s == o for s, o in zip(self._planes, other._planes)])
        return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} with {6 + len(self._planes)} sides @ {self.bounds.origin}>"

    # PROPERTIES

    @property  # read-only
    def axial_planes(self) -> List[Plane]:
        return tuple(
            Plane(vector.vec3(**{a: s}), getattr(v, a))
            for s, v in ((1, self.bounds.maxs), (-1, -self.bounds.mins))
            for a in "xyz")

    @property  # read-only
    def planes(self) -> List[Plane]:
        return (*self.axial_planes, *self._planes)

    # TESTS

    # TODO: slice(self, plane) -> (Brush, Brush)
    # -- return front, back
    # -- return None, self  # self is behind plane
    # -- return self, None  # self is in front of plane

    # INITIALISERS

    @classmethod
    def from_bounds(cls, aabb: AABB) -> Brush:
        brush = cls()
        brush.bounds = aabb
        return brush

    @classmethod
    def from_planes(cls, planes: List[Plane]) -> Brush:
        # need initial space to slice
        # final brush must be convex & enclosed
        raise NotImplementedError()

    @classmethod  # maybe move to a subclass in respawn.titanfall2?
    def from_entity(cls, r2_entity: Dict[str, str]) -> List[Brush]:
        """Titanfall 2 trigger entity to physics"""
        # *trigger_brush_[0-9]+_plane_[0-9]+
        raise NotImplementedError()
