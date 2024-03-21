from __future__ import annotations

from . import vector


# TODO: Image class (Issue #159)

class ProjectionAxis:
    axis: vector.vec3
    offset: float
    scale: float

    def __init__(self, axis: vector.vec3, offset: float = None, scale: float = None):
        self.axis = vector.vec3(*axis)
        self.offset = 0 if offset is None else offset
        self.scale = 1 if scale is None else scale

    def __repr__(self) -> str:
        return f"ProjectionAxis({self.axis!r}, {self.offset}, {self.scale})"

    def project(self, point: vector.vec3) -> float:
        return (vector.dot(point, self.axis) + self.offset) * self.scale


class TextureVector:
    s: ProjectionAxis
    t: ProjectionAxis
    # TODO: rotation (extensions.editor only)

    def __init__(self, s: ProjectionAxis = None, t: ProjectionAxis = None):
        self.s = ProjectionAxis([1, 0]) if s is None else s
        self.t = ProjectionAxis([0, 1]) if t is None else t

    def __iter__(self):
        return iter((self.s, self.t))

    def __repr__(self) -> str:
        return f"TextureAxis({self.s}, {self.t})"

    def uv_at(self, point: vector.vec3) -> vector.vec2:
        u = self.s.project(point)
        v = self.t.project(point)
        return vector.vec2(u, v)

    @classmethod
    def from_normal(cls, normal: vector.vec3) -> TextureVector:
        axes = [(vector.vec3(y=1), vector.vec3(z=-1)),  # X: east / west wall
                (vector.vec3(x=1), vector.vec3(z=-1)),  # Y: north / south wall
                (vector.vec3(x=1), vector.vec3(y=-1))]  # Z: floor / ceiling
        # defaults to floor / ceiling if equally on each axis
        best_axis = 2 if len(set(normal)) == 0 else list(normal).index(max(normal))
        s, t = axes[best_axis]
        return cls(*map(ProjectionAxis, [s, t]))
