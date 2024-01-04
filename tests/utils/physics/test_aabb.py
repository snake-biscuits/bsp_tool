from bsp_tool.utils import physics
from bsp_tool.utils import vector

import pytest


mmoes = {"centered": [[x] * 3 for x in (-1, 1, 0, 1)],
         "mixup": [(-1, -5, -3), (4, 2, 6), (1.5, -1.5, 1.5), (2.5, 3.5, 4.5)]}
# ^ {"test_name": [mins, maxs, origin, extents]}


# 8 AABBs for each +- axes quadrant possible in 3D space
def sign(point, pattern):
    return [[a, -a][p] for a, p in zip(point, pattern)]


def sign2(mins, maxs, pattern):
    return zip(*[([m, -M][p], [M, -m][p]) for m, M, p in zip(mins, maxs, pattern)])


mins = [1] * 3
maxs = [2] * 3
origin = [1.5] * 3
extents = [0.5] * 3

signs = [[i >> j & 1 for j in range(3)] for i in range(8)]
mmoes.update({f"quadrant{i}": (*sign2(mins, maxs, s), sign(origin, s), extents) for i, s in enumerate(signs)})


class TestInit:
    @pytest.mark.parametrize("mins,maxs,origin,extents", mmoes.values(), ids=mmoes.keys())
    def test_mins_maxs(self, mins, maxs, origin, extents):
        aabb = physics.AABB.from_mins_maxs(mins, maxs)
        assert aabb.mins == mins
        assert aabb.maxs == maxs
        assert aabb.origin == origin
        assert aabb.extents == extents

    @pytest.mark.parametrize("mins,maxs,origin,extents", mmoes.values(), ids=mmoes.keys())
    def test_origin_extents(self, mins, maxs, origin, extents):
        aabb = physics.AABB.from_origin_extents(origin, extents)
        assert aabb.mins == mins
        assert aabb.maxs == maxs
        assert aabb.origin == origin
        assert aabb.extents == extents

    # NOTE: from_points automatically determines mins & maxs; can't test that w/ mmoes
    @pytest.mark.parametrize("mins,maxs,origin,extents", mmoes.values(), ids=mmoes.keys())
    def test_from_points(self, mins, maxs, origin, extents):
        aabb = physics.AABB.from_points([mins, origin, maxs])
        assert aabb.mins == mins
        assert aabb.maxs == maxs
        assert aabb.origin == origin
        assert aabb.extents == extents


@pytest.mark.parametrize("mins,maxs,origin,extents", mmoes.values(), ids=mmoes.keys())
def test_add_points(mins, maxs, origin, extents):
    # single point
    aabb = physics.AABB() + mins
    assert aabb.mins == mins
    assert aabb.maxs == mins
    assert aabb.origin == mins
    assert aabb.extents == [0] * 3
    # full bounds
    aabb += maxs
    assert aabb.mins == mins
    assert aabb.maxs == maxs
    assert aabb.origin == origin
    assert aabb.extents == extents
    # no change
    aabb += origin
    assert aabb.mins == mins
    assert aabb.maxs == maxs
    assert aabb.origin == origin
    assert aabb.extents == extents


class TestCollision:
    @pytest.mark.parametrize("mins,maxs,origin,extents", mmoes.values(), ids=mmoes.keys())
    def test_contains_point(self, mins, maxs, origin, extents):
        mins, maxs, extents = [vector.vec3(*v) for v in (mins, maxs, extents)]
        aabb = physics.AABB.from_mins_maxs(mins, maxs)
        assert mins - extents not in aabb
        assert maxs + extents not in aabb
        assert origin in aabb
        assert mins in aabb
        assert maxs in aabb
        with pytest.raises(TypeError):
            "a string" in aabb

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
