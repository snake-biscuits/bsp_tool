from bsp_tool.extensions.editor import generic

import pytest


# NOTE: editor.generic is mostly baseclasses / containers for map data
# -- MapFile implementations will populate with these entries

class TestEntity:
    inits = {
        "noargs": dict(),
        "classname": dict(classname="worldspawn"),
        "complex": dict(classname="info_player_start", origin="0 0 0", angles="0 90 0")}

    @pytest.mark.parametrize("kwargs", inits.values(), ids=inits.keys())
    def test_init(self, kwargs):
        entity = generic.Entity(**kwargs)
        assert set(entity._keys) == set(kwargs.keys())
        assert all([entity[k] == kwargs[k] for k in kwargs])

    def test_init_invalid(self):
        with pytest.raises(AssertionError):
            generic.Entity(_keys=None)
        with pytest.raises(AssertionError):
            generic.Entity(brushes=None)
        with pytest.raises(TypeError):
            generic.Entity(**{2: None})
        # NOTE: setattr(..., "2", None) is valid, but evil
        # -- getattr still retrieves this, and it should appear in _keys

    def test_getitem(self):
        entity = generic.Entity(classname="worldspawn")
        assert entity.classname == "worldspawn"

    # testing __repr__ & __str__ seems excessive...
    # -- __str__ is important for writing, but generic.Brush has no __str__
    # -- this is because each MapFile implementation will have it's own Brush / BrushSide spec
