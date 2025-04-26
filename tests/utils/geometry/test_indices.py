from bsp_tool.utils import geometry
from bsp_tool.utils import vector


def test_triangle_fan():
    expected = [0, 1, 2, 0, 2, 3, 0, 3, 4]
    actual = geometry.triangle_fan(5)
    assert actual == expected


def test_triangle_soup():
    normal = vector.vec3(0, 0, 0)
    vertices = [
        geometry.Vertex(vector.vec3(i, i, i), normal)
        for i in range(9)]
    soup = geometry.triangle_soup(vertices)
    assert len(soup) == 3
    assert len(soup[0].vertices) == 3
    assert soup[0].vertices == vertices[0:3]
    assert len(soup[1].vertices) == 3
    assert soup[1].vertices == vertices[3:6]
    assert len(soup[2].vertices) == 3
    assert soup[2].vertices == vertices[6:9]
