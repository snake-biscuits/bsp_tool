import math

from bsp_tool.utils.physics import Plane
from bsp_tool.utils.vector import vec3

import pytest


planes = {"floor": (vec3(z=1), 0)}

half_sqrt_2 = math.sqrt(2) / 2
# third_sqrt_3 = math.sqrt(3) / 3

bevel_axes = {
    "NW": (-1, 1), "NE": (1, 1),
    "SW": (-1, -1), "SE": (1, -1)}

bevel_normals = {k: vec3(*v) * half_sqrt_2 for k, v in bevel_axes.items()}


class TestInit:
    @pytest.mark.parametrize("normal,distance", planes.values(), ids=planes.keys())
    def test_init(self, normal: vec3, distance: float):
        plane = Plane(normal, distance)
        assert plane.normal == normal
        assert plane.distance == distance

    def test_invalid(self):
        with pytest.raises(AssertionError):
            Plane(vec3(z=2), 0)


# def test_negation(plane, inverse):
#     assert -Plane(*plane) == Plane(*inverse)


class TestCollision:
    def test_point(self):
        plane = Plane(vec3(z=1), 0)
        assert plane.test(vec3(z=1)) == 1  # above
        assert plane.test(vec3(z=-1)) == -1  # below

    # def test_intersects(self):
    #     ...


# TODO:
# class TestBrushInteraction:
#     def test_is_axial_of(self, brush, planes):
#     def test_is_bevel_of(self, brush, planes):
