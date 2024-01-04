from typing import Dict

from ...utils import physics
from ...utils import vector
from . import base


class Comment(base.Pattern):
    regex = r"(\\\\|//) .*"
    ValueType = str


class Everything(base.Pattern):
    regex = r".*"
    ValueType = str


class TrailingComment(base.MetaPattern):
    spec = r"line \\ comment"
    patterns = {"line": Everything, "comment": Everything}


class Filepath(base.Pattern):
    regex = r"[A-Za-z0-9_\./\\:]*"
    ValueType = str


class Float(base.Pattern):
    regex = r"[+-]?[0-9]+(\.[0-9]+?(e[+-]?[0-9]+)?)?"
    ValueType = float


class Integer(base.Pattern):
    regex = r"[+-]?[0-9]+"
    ValueType = int


class KeyValuePair(base.MetaPattern):
    spec = r'" key " " value "'
    patterns = {"key": Everything, "value": Everything}


class Point(base.MetaPattern):
    spec = "( x y z )"
    patterns = {a: Float for a in "xyz"}
    ValueType = vector.vec3


class Plane(base.MetaPattern):
    spec = "A B C"
    patterns = {P: Point for P in "ABC"}

    class ValueType(physics.Plane):
        def __init__(self, **kwargs: Dict[str, Point]):
            if kwargs["A"] == kwargs["B"] == kwargs["C"]:
                # TODO: warning for invalid face
                self.normal, self.distance = vector.vec3(z=1), 0
            else:
                plane = physics.Plane.from_triangle(*[kwargs[P] for P in "ABC"])
                self.normal, self.distance = plane.normal, plane.distance

    def __str__(self) -> str:
        return " ".join([f"({P.x} {P.y} {P.z})" for P in self.value.as_triangle()])
