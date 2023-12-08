from __future__ import annotations
from typing import List

from ..branches import vector


# TODO: Mesh, Material, Model
# -- Transform (matrix | position, rotation, scale)


class Vertex:
    position: vector.vec3
    normal: vector.vec3  # should be normalised
    uv: List[vector.vec2]
    # uv[0] = albedo
    # uv[1] = lightmap


class Polygon:
    vertices: List[Vertex]
    normal: vector.vec3

    def __init__(self, vertices: List[Vertex]):
        assert len(vertices) >= 3
        self.vertices = vertices

    def __iter__(self):
        return iter(self.vertices)

    @property
    def normal(self) -> vector.vec3:
        return [v.normal for v in self.vertices] / len(self.vertices)

    @normal.setter
    def normal(self, new_normal: vector.vec3):
        for i, vertex in enumerate(self.vertices):
            self.vertices[i].normal = new_normal
