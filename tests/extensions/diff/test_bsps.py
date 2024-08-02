from bsp_tool import ValveBsp
from bsp_tool.branches.valve import orange_box
from bsp_tool.extensions import diff

import pytest


old_bsp = ValveBsp.from_file(orange_box, "tests/maps/Team Fortress 2/test_displacement_decompile.bsp")
new_bsp = ValveBsp.from_file(orange_box, "tests/maps/Team Fortress 2/test_physcollide.bsp")
# >>> old_lumps = {L for L, h in old_bsp.headers.items() if h.length > 0}
# >>> new_lumps = {L for L, h in new_bsp.headers.items() if h.length > 0}
# >>> old_lumps.difference(new_lumps)
# {'DISPLACEMENT_TRIS', 'DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS', 'DISPLACEMENT_VERTICES', 'DISPLACEMENT_INFO'}
# >>> new_lumps.difference(old_lumps)
# {'VISIBILITY'}


class TestBspDiff:
    diff = diff.bsps.BspDiff(old_bsp, new_bsp)
    # TODO: diff.bsps.BspDiff(old_bsp, old_bsp) & verify no changes

    def test_invalid_lump(self):
        with pytest.raises(AttributeError):
            print(self.diff.NONEXISTANT_LUMP)

    def test_lump_added(self):
        lump_diff = self.diff.VISIBILITY
        assert isinstance(lump_diff, diff.lumps.NoneDiff)

    def test_lump_removed(self):
        lump_diff = self.diff.DISPLACEMENT_INFO
        assert isinstance(lump_diff, diff.lumps.NoneDiff)

    # TODO: save
    # TODO: has_no_changes
    # TODO: what_changed
