import math

from bsp_tool.branches import vector


class TestVec3:
    def test_init(self):
        v = vector.vec3(1, 2, 3)
        assert (v.x, v.y, v.z) == (1, 2, 3)
        v = vector.vec3(4, 5)
        assert (v.x, v.y, v.z) == (4, 5, 0)
        # kwargs
        v = vector.vec3(x=1)
        assert (v.x, v.y, v.z) == (1, 0, 0)
        v = vector.vec3(y=1)
        assert (v.x, v.y, v.z) == (0, 1, 0)
        v = vector.vec3(z=1)
        assert (v.x, v.y, v.z) == (0, 0, 1)

    def test_magnitude(self):
        v = vector.vec3(x=1)
        assert v.magnitude() == 1
        v = vector.vec3(x=1, y=1)
        assert v.magnitude() == math.sqrt(2)
