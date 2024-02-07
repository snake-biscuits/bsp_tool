from bsp_tool.utils import editor

import pytest


# TODO: test __str__ (and maybe __repr__)


inits = {
    "noargs": dict(),
    "classname": dict(classname="worldspawn"),
    "complex": dict(classname="info_player_start", origin="0 0 0", angles="0 90 0")}


@pytest.mark.parametrize("kwargs", inits.values(), ids=inits.keys())
def test_init(kwargs):
    entity = editor.Entity(**kwargs)
    assert set(entity._keys) == set(kwargs.keys())
    assert all([entity[k] == kwargs[k] for k in kwargs])


def test_init_invalid():
    with pytest.raises(AssertionError):
        editor.Entity(_keys=None)
    with pytest.raises(AssertionError):
        editor.Entity(brushes=None)
    with pytest.raises(TypeError):
        editor.Entity(**{2: None})
    # NOTE: setattr(..., "2", None) is valid, but evil
    # -- getattr still retrieves this, and it should appear in _keys


def test_getitem():
    entity = editor.Entity(classname="worldspawn")
    assert entity.classname == "worldspawn"
