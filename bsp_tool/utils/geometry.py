from __future__ import annotations
from typing import List

from . import vector


# TODO: Mesh, Material, Model
# -- Transform (matrix | position, rotation, scale)


class Vertex:
    position: vector.vec3
    normal: vector.vec3  # should be normalised
    uv: List[vector.vec2]
    # uv[0] = albedo
    # uv[1] = lightmap

    def __init__(self, position, normal, *uvs):
        self.position = position
        self.normal = normal
        self.uv = uvs

    def __repr__(self) -> str:
        args = ", ".join([self.position, self.normal, *self.uv])
        return f"{self.__class__.__name__}({args})"


class Polygon:
    vertices: List[Vertex]
    normal: vector.vec3

    def __init__(self, vertices: List[Vertex]):
        assert len(vertices) >= 3
        self.vertices = vertices

    def __iter__(self):
        return iter(self.vertices)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.vertices!r})"

    @property
    def normal(self) -> vector.vec3:
        return [v.normal for v in self.vertices] / len(self.vertices)

    @normal.setter
    def normal(self, new_normal: vector.vec3):
        for i, vertex in enumerate(self.vertices):
            self.vertices[i].normal = new_normal
