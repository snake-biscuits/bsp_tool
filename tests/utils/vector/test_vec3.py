import math

from bsp_tool import core
from bsp_tool.utils import vector

import pytest

# TODO: look at using pytest.fixture to reduce duplicate code


class TestInit:
    args = {
        "all three": [(1, 2, 3)] * 2,
        "just two": [(4, 5), (4, 5, 0)],
        "no args": [tuple(), (0, 0, 0)]}

    @pytest.mark.parametrize("args,expected", args.values(), ids=args.keys())
    def test_args(self, args, expected):
        v = vector.vec3(*args)
        assert (v.x, v.y, v.z) == tuple(expected)

    # TODO: test_invalid_args

    kwargs = {"just x": [dict(x=1), (1, 0, 0)],
              "just y": [dict(y=1), (0, 1, 0)],
              "just z": [dict(z=1), (0, 0, 1)],
              "no x": [dict(y=2, z=3), (0, 2, 3)],
              "no y": [dict(x=2, z=3), (2, 0, 3)],
              "no z": [dict(x=2, y=3), (2, 3, 0)],
              "all three": [dict(x=4, y=5, z=6), (4, 5, 6)]}

    @pytest.mark.parametrize("kwargs,expected", kwargs.values(), ids=kwargs.keys())
    def test_kwargs(self, kwargs, expected):
        v = vector.vec3(**kwargs)
        assert (v.x, v.y, v.z) == tuple(expected)

    # TODO: test_invalid_kwargs


class TestEqual:
    # TODO: undefined / unwanted behaviour
    # -- iterable longer than 3
    # -- iterable containing non-numbers (int / float)

    def test_true_equality(self):
        A = vector.vec3(0.1, 0.2, 0.3)
        assert A == A
        B = vector.vec3(0.1, 0.2, 0.3)
        assert A is not B
        assert A == B

    def test_close_enough(self):
        A = vector.vec3(0.1, 0.2, 0.3)
        assert 0.1 + 0.2 != 0.3  # floating point error
        assert math.isclose(0.3, 0.1 + 0.2)
        C = vector.vec3(0.1, 0.2, 0.1 + 0.2)
        assert A == C

    def test_list(self):
        A = vector.vec3(0.1, 0.2, 0.3)
        assert A == [0.1, 0.2, 0.3]

    def test_tuple(self):
        A = vector.vec3(0.1, 0.2, 0.3)
        assert A == (0.1, 0.2, 0.3)

    @pytest.mark.xfail(reason="random order")  # shroedinger's unittest
    def test_set(self):
        A = vector.vec3(0.1, 0.2, 0.3)
        assert A != {0.1, 0.2, 0.3}

    @pytest.mark.xfail(reason="random order")  # might pass, might not
    def test_dict_view(self):
        A = vector.vec3(0.1, 0.2, 0.3)
        d = {a: a for a in (0.1, 0.2, 0.3)}
        assert A != d.keys()
        assert A != d.values()

    def test_MappedArray(self):
        A = vector.vec3(0.1, 0.2, 0.3)
        assert A == core.MappedArray(
            0.1, 0.2, 0.3,
            _mapping=[*"xyz"],
            _format="3f")


class TestSequence:
    # TODO: test __getitem__(s, slice(...))

    def test_iter(self):
        xyz = [1, 2, 3]
        v = vector.vec3(*xyz)
        for a, b in zip(v, xyz):
            assert a == b

    def test_len(self):
        assert len(vector.vec3()) == 3

    def test_indexable(self):
        xyz = [1, 2, 3]
        v = vector.vec3(*xyz)
        for i in range(3):
            assert v[i] == xyz[i]


class TestMath:
    def test_magnitude(self):
        assert vector.vec3(1, 1, 0).magnitude() == math.sqrt(2)

    def test_add(self):
        A = vector.vec3(0.1, 0.2, 0.3)
        B = vector.vec3(0.9, 0.8, 0.7)
        C = A + B
        assert (C.x, C.y, C.z) == (1.0, 1.0, 1.0)
