from __future__ import annotations
import collections
import itertools
from typing import Any, List, Union

from . import vector


def triangle_fan(num_vertices: int) -> List[int]:
    assert num_vertices >= 3
    return itertools.chain([(0, 1, 2), *[(0, i - 1, i) for i in range(3, num_vertices)]])


class Vertex:
    position: vector.vec3
    normal: vector.vec3  # should be normalised
    uv: List[vector.vec2]
    # uv0: vector.vec2  # albedo
    # uv1: vector.vec2  # lightmap

    def __init__(self, position, normal, *uvs):
        self.position = position
        self.normal = normal
        self.uv = uvs

    def __eq__(self, other: Vertex) -> bool:
        if isinstance(other, Vertex):
            return hash(self) == hash(other)
        return False

    def __getattr__(self, attr: str) -> Any:
        if attr.startswith("uv") and attr[2:].isnumeric():  # uv0 etc.
            index = int(attr[2:])
            return self.uv[index]
        else:
            raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{attr}'")

    def __hash__(self) -> int:
        return hash((self.position, self.normal, *self.uv))

    def __repr__(self) -> str:
        args = ", ".join(map(str, [self.position, self.normal, *self.uv]))
        return f"{self.__class__.__name__}({args})"


class Polygon:
    vertices: List[Vertex]
    normal: vector.vec3
    # TODO: CW / CCW check based on normal
    # TODO: keep normals, force CW / CCW (check ? reversed(...) : ...)

    def __init__(self, vertices=list()):
        assert len(vertices) >= 3
        self.vertices = vertices

    def __iter__(self):
        return iter(self.vertices)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.vertices!r})"

    @property
    def normal(self) -> vector.vec3:
        return sum([v.normal for v in self.vertices]) / len(self.vertices)

    @normal.setter
    def normal(self, new_normal: vector.vec3):
        for i, vertex in enumerate(self.vertices):
            self.vertices[i].normal = new_normal


class Material:
    """base class"""
    name: str

    def __init__(self, name=""):
        self.name = name

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
    translation: vector.vec3
    rotation: vector.vec3  # degrees for each axis
    # TODO: alternate rotations (e.g. Quaternion)
    scale: Union[float, vector.vec3]  # uniform or per-axis

    def __init__(self, meshes=list(), origin=vector.vec3(), angles=vector.vec3(), scale=1):
        self.meshes = self.merge_meshes(meshes)
        self.translation = origin
        self.rotation = angles
        if isinstance(scale, (float, int)):
            scale = vector.vec3(scale, scale, scale)
        self.scale = scale

    def __repr__(self) -> str:
        origin = self.translation
        angles = self.rotation
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
        vertex.position = vertex.position.rotated(*self.rotation)
        vertex.normal = vertex.normal.rotated(*self.rotation)
        # translate
        vertex.position += self.translation
        return vertex

    @property
    def transform_matrix(self) -> List[List[float]]:
        """for .gltf"""
        # | a b c d |
        # | e f g h |
        # | i j k l |
        # | m n o p |
        raise NotImplementedError()
