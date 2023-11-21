from bsp_tool.branches import physics

import pytest


class TestAABB:
    def test_init_origin_extents(self):
        x = physics.AABB.from_origin_extents([-1.5] * 3, [0.5] * 3)
        assert x.mins == [-2] * 3
        assert x.maxs == [-1] * 3
        assert x.origin == [-1.5] * 3
        assert x.extents == [0.5] * 3

    def test_init_mins_maxs(self):
        x = physics.AABB.from_mins_maxs([-2] * 3, [-1] * 3)
        assert x.mins == [-2] * 3
        assert x.maxs == [-1] * 3
        assert x.origin == [-1.5] * 3
        assert x.extents == [0.5] * 3

    def test_init_from_points(self):
        x = physics.AABB.from_points([[-1] * 3, [1] * 3])
        assert x.mins == [-1] * 3
        assert x.maxs == [1] * 3
        assert x.origin == [0] * 3
        assert x.extents == [1] * 3

    def test_add_points(self):
        x = physics.AABB() + (-1, 2, -3) + (4, -5, 6)
        assert x.mins == (-1, -5, -3)
        assert x.maxs == (4, 2, 6)
        assert x.origin == (1.5, -1.5, 1.5)
        assert x.extents == (2.5, 3.5, 4.5)

    # NOTE: y = physics.AABB.from_origin_extents(x.origin, x.extents + float_delta)  # test w/ delta

    def test_contains_point(self):
        x = physics.AABB.from_mins_maxs([-1] * 3, [1] * 3)
        assert [2] * 3 not in x
        assert [-2] * 3 not in x
        assert [0] * 3 in x
        # edge cases
        assert [1] * 3 in x
        assert [-1] * 3 in x
        with pytest.raises(TypeError):
            "a string" in x

    def test_contains_AABB(self):
        outer = physics.AABB.from_mins_maxs([-2] * 3, [2] * 3)
        inner = physics.AABB.from_mins_maxs([-1] * 3, [1] * 3)
        assert inner in outer
        assert outer not in inner
        # edge case
        left = physics.AABB.from_mins_maxs([-1] * 3, [0] * 3)
        right = physics.AABB.from_mins_maxs([0] * 3, [1] * 3)
        assert left not in right
        assert right not in left
        # overlap cases
        assert inner in inner  # perfect overlap
        assert left in inner
        assert right in inner
        # corner case
        intersecting = physics.AABB.from_mins_maxs([0] * 3, [2] * 3)
        assert intersecting not in inner
        assert inner not in intersecting

    def test_intersects_AABB(self):
        # NOTE: contained AABBS are a subset of intersections
        basic = physics.AABB.from_mins_maxs([-1] * 3, [1] * 3)
        assert basic.intersects(basic)  # perfect overlap
        left = physics.AABB.from_mins_maxs([-1] * 3, [0] * 3)
        assert left.intersects(basic)
        assert basic.intersects(left)
        right = physics.AABB.from_mins_maxs([0] * 3, [1] * 3)
        assert right.intersects(basic)
        assert basic.intersects(right)
        # edge case
        assert left.intersects(right)
        assert right.intersects(left)
        # corner case
        corner = physics.AABB.from_mins_maxs([0] * 3, [2] * 3)
        assert corner.intersects(basic)
        assert basic.intersects(corner)
        # negative case
        space_boy = physics.AABB.from_mins_maxs([5] * 3, [6] * 3)
        assert not basic.intersects(space_boy)
        assert not space_boy.intersects(basic)
