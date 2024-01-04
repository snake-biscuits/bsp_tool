from bsp_tool.utils import physics
from bsp_tool.utils import vector
from bsp_tool.extensions.editor import common

import pytest


# Patterns


filepaths = {"basic": "filename",
             "extension": "file.ext",
             "linux": "/dev/null",
             "windows": "C:/Windows/notepad.exe"}


@pytest.mark.parametrize("string", filepaths.values(), ids=filepaths.keys())
def test_filepath(string):
    val = common.Filepath.from_string(string).value
    assert isinstance(val, str)
    assert val == string


floats = {"basic": ("1.0", 1.0),
          "integer": ("2", 2.0),
          "exponent": ("1e1", 1e1),
          "negative": ("-1", -1.0),
          "signs": ("+5.4e-3", 5.4e-3)}
# TODO: ensure decimal point is escaped


@pytest.mark.parametrize("string,expected", floats.values(), ids=floats.keys())
def test_float(string, expected):
    val = common.Float.from_string(string).value
    assert isinstance(val, float)
    assert val == expected


ints = {"basic": ("1", 1),
        "zero": ("0", 0),
        "negative": ("-1", -1),
        "sign": ("+1", 1)}


@pytest.mark.parametrize("string,expected", ints.values(), ids=ints.keys())
def test_integer(string, expected):
    val = common.Integer.from_string(string).value
    assert isinstance(val, int)
    assert val == expected


# MetaPatterns


# TODO: Point

# NOTE: Plane is made up of points, testing all of `MetaPattern.regex` & `regex_groups`
def test_plane():
    plane = common.Plane.from_string("(0 0 0) (0 1 0) (1 0 0)")
    assert isinstance(plane.value, physics.Plane)
    assert plane.value.normal == vector.vec3(z=1)
    assert plane.value.distance == 0
    assert plane.value == physics.Plane(vector.vec3(z=1), 0)
