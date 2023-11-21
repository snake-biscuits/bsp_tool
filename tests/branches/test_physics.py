from bsp_tool.branches import physics
# from bsp_tool.branches import vector


class TestAABB:
    def test_init_origin_extents(self):
        x = physics.AABB.from_origin_extents([-1.5] * 3, [0.5] * 3)
        assert x.mins == [-2] * 3
        assert x.maxs == [-1] * 3

    def test_init_mins_maxs(self):
        x = physics.AABB.from_mins_maxs([-2] * 3, [-1] * 3)
        assert x.origin == [-1.5] * 3
        assert x.extents == [0.5] * 3

    def test_contains(self):
        x = physics.AABB.from_mins_maxs([-1] * 3, [1] * 3)
        # NOTE: y = physics.AABB.from_origin_extents(x.origin, x.extents + float_delta)
        assert [2] * 3 not in x
        assert [-2] * 3 not in x
        assert [0] * 3 in x
        # right on the edge
        assert [1] * 3 in x
        assert [-1] * 3 in x
