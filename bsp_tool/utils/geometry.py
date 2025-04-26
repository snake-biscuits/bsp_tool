from __future__ import annotations
import collections
import itertools
from typing import Any, List, Tuple

from . import vector


def triangle_fan(num_vertices: int) -> List[int]:
    assert num_vertices >= 3
    return list(itertools.chain(*[
        (0, 1, 2),
        *[
            (0, i - 1, i)
            for i in range(3, num_vertices)]]))


def triangle_soup(vertices: List[Vertex]) -> List[Polygon]:
    vertices = tuple(vertices)  # no generators, we need len
    assert len(vertices) % 3 == 0
    return [
        Polygon([
            vertices[i + j]
            for j in (0, 1, 2)])
        for i in range(0, len(vertices), 3)]


class Vertex:
    position: vector.vec3
    normal: vector.vec3  # should be normalised
    uv: List[vector.vec2]
    # uv0: vector.vec2  # albedo
    # uv1: vector.vec2  # lightmap
    colour: Tuple[float, float, float, float]  # rgba [0.0 -> 1.0]

    def __init__(self, position, normal, *uvs, colour=(0.0,) * 4):
        self.position = vector.vec3(*position)
        self.normal = vector.vec3(*normal)
        self.uv = [vector.vec2(*uv) for uv in uvs]
        self.colour = tuple(colour)

    def __repr__(self) -> str:
        args = ", ".join(map(str, [self.position, self.normal, *self.uv]))
        return f"{self.__class__.__name__}({args}, colour={self.colour})"

    def __add__(self, other: Vertex) -> Vertex:
        if not isinstance(other, Vertex):
            raise TypeError(f"TypeError: unsupported operand type(s) for +: 'Vertex' and '{other.__class__.__name__}'")
        assert len(self.uv) == len(other.uv)
        return Vertex(
            self.position + other.position,
            self.normal + other.normal,
            *[s + o for s, o in zip(self.uv, other.uv)],
            colour=[s + o for s, o in zip(self.colour, other.colour)])

    def __eq__(self, other: Vertex) -> bool:
        if isinstance(other, Vertex):
            return hash(self) == hash(other)
        return False

    def __getattr__(self, attr: str) -> Any:
        if attr.startswith("uv") and attr[2:].isnumeric():  # uv0 etc.
            index = int(attr[2:])
            if index >= len(self.uv):
                raise AttributeError(
                    f"'{self.__class__.__name__}' has no attribute '{attr}'")
            return self.uv[index]
        else:
            raise AttributeError(
                f"'{self.__class__.__name__}' has no attribute '{attr}'")

    def __hash__(self) -> int:
        return hash((self.position, self.normal, *self.uv, self.colour))

    def __mul__(self, other: float) -> Vertex:
        if not isinstance(other, float):
            raise TypeError(f"TypeError: unsupported operand type(s) for *: 'Vertex' and '{other.__class__.__name__}'")
        return Vertex(
            self.position * other,
            self.normal * other,
            *[uv * other for uv in self.uv],
            colour=[x * other for x in self.colour])

    def __sub__(self, other: Vertex) -> Vertex:
        if not isinstance(other, Vertex):
            raise TypeError(f"TypeError: unsupported operand type(s) for -: 'Vertex' and '{other.__class__.__name__}'")
        assert len(self.uv) == len(other.uv)
        return Vertex(
            self.position - other.position,
            self.normal - other.normal,
            *[s - o for s, o in zip(self.uv, other.uv)],
            colour=[s - o for s, o in zip(self.colour, other.colour)])

    def lerp(self, other: Vertex, t: float) -> Vertex:
        """t should be in range 0.0 -> 1.0"""
        assert isinstance(other, Vertex)
        assert len(self.uv) == len(other.uv)
        return self + ((other - self) * t)


class Polygon:
    vertices: List[Vertex]
    normal: vector.vec3
    # TODO: CW / CCW check based on normal
    # TODO: keep normals, force CW / CCW (check ? reversed(...) : ...)

    def __init__(self, vertices=list()):
        assert len(vertices) >= 3
        self.vertices = vertices

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.vertices!r})"

    def __len__(self) -> int:
        return len(self.vertices)

    def __iter__(self):
        return iter(self.vertices)

    @property
    def normal(self) -> vector.vec3:
        return sum([v.normal for v in self.vertices], start=vector.vec3()) / len(self.vertices)

    @normal.setter
    def normal(self, new_normal: vector.vec3):
        for i, vertex in enumerate(self.vertices):
            self.vertices[i].normal = new_normal


class Material:
    # NOTE: name must be unique within a file
    # -- will need variation if we have multiple materials per-path
    # -- might want to include arbitrary metadata like cubemap indices
    # NOTE: ApexLegends links cubemap indices to meshes, not MaterialSorts
    name: str

    def __init__(self, name=""):
        self.name = name.lower().replace("\\", "/")
        # TODO: shorten name
        # TODO: path
        # TODO: asset type (rpak.matl.wld, .vmt, .wad, .shader etc.)

    def __eq__(self, other: Material) -> bool:
        if isinstance(other, Material):
            return hash(self) == hash(other)
        return False

    def __hash__(self) -> int:
        return hash((self.name,))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r})"


class Mesh:
    material: Material
    polygons: List[Polygon]

    def __init__(self, material=Material("default"), polygons=list()):
        self.material = material
        self.polygons = polygons

    def __repr__(self) -> str:
        material = self.material
        return f"<{self.__class__.__name__} {len(self.polygons)} polygons, {material=!r}>"


class Model:
    meshes: List[Mesh]
    origin: vector.vec3
    angles: vector.vec3  # degrees for each axis
    # TODO: angles from QAngle / Quaternion
    scale: vector.vec3

    def __init__(self, meshes=list(), origin=vector.vec3(), angles=vector.vec3(), scale=1):
        self.meshes = self.merge_meshes(meshes)
        self.origin = vector.vec3(*origin)
        self.angles = vector.vec3(*angles)
        # NOTE: scale must be vec3, but can be a float when passed into __init__
        if isinstance(scale, (float, int)):
            scale = vector.vec3(scale, scale, scale)
        self.scale = scale

    def __repr__(self) -> str:
        origin = self.origin
        angles = self.angles
        scale = self.scale
        return f"<{self.__class__.__name__} {len(self.meshes)} meshes, {origin=!r}, {angles=!r}, {scale=!r}>"

    @staticmethod
    def merge_meshes(meshes: List[Mesh]) -> List[Mesh]:
        sort = collections.defaultdict(list)
        for mesh in meshes:
            sort[mesh.material].extend(mesh.polygons)
        return [Mesh(material, polygons) for material, polygons in sort.items()]

    def apply_transforms(self, vertex: Vertex) -> Vertex:
        # scale
        vertex.position.x *= self.scale.x
        vertex.position.y *= self.scale.y
        vertex.position.z *= self.scale.z
        # rotate
        vertex.position = vertex.position.rotated(*self.angles)
        vertex.normal = vertex.normal.rotated(*self.angles)
        # translate
        vertex.position += self.origin
        return vertex

    @property
    def transform_matrix(self) -> List[List[float]]:
        """for .gtlf/.glb & .usd/.usda"""
        # TODO: apply scale & rotation
        translation = [
            (1, 0, 0, self.origin.x),
            (0, 1, 0, self.origin.y),
            (0, 0, 1, self.origin.z),
            (0, 0, 0, 1)]
        # scale = [
        #     (self.scale.x, 0, 0, 0),
        #     (0, self.scale.y, 0, 0),
        #     (0, 0, self.scale.z, 0),
        #     (0, 0, 0, 1)]
        return translation


def generate_cube(mins: vector.vec3, maxs: vector.vec3) -> Model:
    assert len(mins) == 3
    assert len(maxs) == 3
    x, y, z = zip(mins, maxs)
    vertices = [vector.vec3(x[i >> 2], y[i >> 1 & 1], z[i & 1]) for i in range(8)]
    quads = [
        ((0b010, 0b011, 0b001, 0b000), vector.vec3(x=-1)),
        ((0b000, 0b001, 0b101, 0b100), vector.vec3(y=-1)),
        ((0b000, 0b100, 0b110, 0b010), vector.vec3(z=-1)),
        ((0b100, 0b101, 0b111, 0b110), vector.vec3(x=1)),
        ((0b110, 0b111, 0b011, 0b010), vector.vec3(y=1)),
        ((0b011, 0b111, 0b101, 0b001), vector.vec3(z=1))]
    polygons = [Polygon([Vertex(vertices[i], n) for i in idxs]) for idxs, n in quads]
    return Model([Mesh(polygons=polygons)])
