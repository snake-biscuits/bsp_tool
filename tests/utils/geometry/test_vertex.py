from bsp_tool.utils import geometry
from bsp_tool.utils import vector


def test_init():
    v = geometry.Vertex([1, 2, 3], [4, 5, 6], [7, 8], [9, 10], colour=(0.11, 0.22, 0.33, 0.44))
    assert isinstance(v.position, vector.vec3)
    assert v.position == [1, 2, 3]
    assert isinstance(v.normal, vector.vec3)
    assert v.normal == [4, 5, 6]
    assert isinstance(v.uv[0], vector.vec2)
    assert v.uv[0] == [7, 8]
    assert isinstance(v.uv[1], vector.vec2)
    assert v.uv[1] == [9, 10]
    assert len(v.uv) == 2
    assert isinstance(v.colour, tuple)
    assert v.colour == (0.11, 0.22, 0.33, 0.44)


def test_getattr():
    v = geometry.Vertex([], [], [1, 2], [3, 4])
    assert isinstance(v.uv0, vector.vec2)
    assert v.uv0 == [1, 2] == v.uv[0]
    assert isinstance(v.uv1, vector.vec2)
    assert v.uv1 == [3, 4] == v.uv[1]
    assert len(v.uv) == 2
