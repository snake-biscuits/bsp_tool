import math
# from typing import Dict, List

from bsp_tool.utils.physics import AABB, Brush, Plane
from bsp_tool.utils.vector import vec3

import pytest


half_sqrt_2 = math.sqrt(2) / 2


aabbs = {"centered": AABB.from_origin_extents([0] * 3, [1] * 3)}


class TestInit():
    @pytest.mark.parametrize("aabb", aabbs.values(), ids=aabbs.keys())
    def test_from_bounds(self, aabb: AABB):
        brush = Brush.from_bounds(aabb)
        assert len(brush.planes) == 6
        # test axial sides
        axial_normals = {
            f"{s}{a}": vec3(**{a: v})
            for s, v in (("+", 1), ("-", -1))
            for a in "xyz"}
        axial_distances = {
            **{f"-{a}": getattr(-aabb.mins, a) for a in "xyz"},
            **{f"+{a}": getattr(aabb.maxs, a) for a in "xyz"}}
        axial_planes = {
            n: p
            for n in axial_normals.values()
            for p in brush.planes
            if p.normal == n}
        for axis, normal in axial_normals.items():
            assert axial_planes[normal].distance == axial_distances[axis]

    # @pytest.mark.parametrize("planes", ..., ids=...)
    # def test_from_planes(self, planes: List[Plane]):
    #     ...

    # @pytest.mark.parametrize("ent", ..., ids=...)
    # def test_from_entity(self, ent: Dict[str, str]):
    #     ...


# class TestInvalidInit:


# test_equality


# class TestCollision:
# def test_contains():
#     ...
