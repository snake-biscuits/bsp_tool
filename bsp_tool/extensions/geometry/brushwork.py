from typing import List

# from ...utils import physics
from ..editor import generic
from . import base


def polygons_of(brush: generic.Brush) -> List[base.Polygon]:
    # generate a Polygon for each Plane, such that they can be zipped
    raise NotImplementedError()
    # generic.Brush(...).as_physics()  # calculate AABB
    # AABB quads
    # slice edges w/ each non-axial plane
    # only respect in-bounds intersections
    # slice edge by replacing A-B w/ A-S;S-B if A & B on opposite sides
    # find the lerp(t) via plane.test(A) * -plane.normal
