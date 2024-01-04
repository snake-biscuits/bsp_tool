from typing import Any

from bsp_tool.extensions.editor import base

import pytest


# SAMPLES

class Everything(base.Pattern):
    regex = r".*"
    ValueType = str


class Hexadecimal(base.Pattern):
    regex = r"[0-9a-fA-F]+"
    ValueType = int

    def __init__(self, string: str = "0"):
        self.value = int(string, base=16)

    def __str__(self) -> str:
        return f"{self.value:X}"


class Comment(base.MetaPattern):
    spec = "# comment"
    patterns = {"comment": Everything}


# TESTS

class TestPattern:
    inits = {"Everything": (Everything, *["hello world"] * 2),
             "Hexadecimal": (Hexadecimal, "7F", 0x7F)}

    # TODO: test __init__ passes *args & **kwargs down to ValueType
    # TODO: test __str__

    @pytest.mark.parametrize("cls,string,value", inits.values(), ids=inits.keys())
    def test_init(self, cls: base.Pattern, string: str, value: Any):
        sample = cls()
        assert isinstance(sample.value, sample.ValueType)
        assert sample.value == sample.ValueType()  # default value

    @pytest.mark.parametrize("cls,string,value", inits.values(), ids=inits.keys())
    def test_from_string(self, cls: base.Pattern, string: str, value: Any):
        assert cls.from_string(string).value == value

    @pytest.mark.parametrize("cls,string,value", inits.values(), ids=inits.keys())
    def test_as_string(self, cls: base.Pattern, string: str, value: Any):
        assert str(cls.from_string(string)) == string


def test_AttrMap():
    sample = base.AttrMap(key="value")
    assert sample._keys == ("key",)
    assert sample.key == "value"
    assert sample.as_dict() == dict(key="value")
    assert sample != dict(key="value")
    assert sample == sample


class TestMetaPattern:
    inits = {"Comment": (Comment, "# hello world", base.AttrMap(comment="hello world"))}

    @pytest.mark.parametrize("cls, string,value", inits.values(), ids=inits.keys())
    def test_from_string(self, cls: base.MetaPattern, string: str, value: Any):
        assert cls.from_string(string).value == value

    # NOTE: whitespace will always be reduced to a single space
    @pytest.mark.parametrize("cls,string,value", inits.values(), ids=inits.keys())
    def test_as_string(self, cls: base.Pattern, string: str, value: Any):
        assert str(cls.from_string(string)) == string
