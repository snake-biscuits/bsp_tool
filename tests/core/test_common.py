from bsp_tool.core import common


def test_subgroup():
    mapping = {
        "id": None,
        "plane.vector": [*"xyz"],
        "plane.distance": None}
    actual = common.subgroup(mapping, "plane")
    expected = {"vector": [*"xyz"], "distance": None}
    assert actual == expected


class TestSchool():
    class ParentClass:
        _classes = {"child": float}

    def test_defined(self):
        base = 6
        actual = common.school(self.ParentClass, "child", base)
        expected = float(base)

        assert actual == expected
        assert isinstance(actual, float)

    def test_undefined(self):
        base = 53
        actual = common.school(self.ParentClass, "stranger", base)
        expected = base

        assert actual == expected
        assert isinstance(actual, int)


def test_split_format():
    # TODO: test all possible format chars
    example = "iI3f16sh"
    expected = ("i", "I", "f", "f", "f", "16s", "h")
    actual = common.split_format(example)
    assert actual == expected
