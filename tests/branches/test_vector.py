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

    def test_add(self):
        A = vector.vec3(0.1, 0.2, 0.3)
        B = vector.vec3(0.9, 0.8, 0.7)
        C = A + B
        assert (C.x, C.y, C.z) == (1.0, 1.0, 1.0)
        D = vector.vec3.__add__([1, 2, 3], [6, 5, 4])
        assert (D.x, D.y, D.z) == (7, 7, 7)
