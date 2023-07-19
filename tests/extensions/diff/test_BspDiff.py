from bsp_tool import ValveBsp
from bsp_tool.branches.valve import orange_box
from bsp_tool.extensions import diff

import pytest


old_bsp = ValveBsp(orange_box, "tests/maps/Team Fortress 2/test_displacement_decompile.bsp")
new_bsp = ValveBsp(orange_box, "tests/maps/Team Fortress 2/test_physcollide.bsp")
# >>> old_lumps = {L for L, h in old_bsp.headers.items() if h.length > 0}
# >>> new_lumps = {L for L, h in new_bsp.headers.items() if h.length > 0}
# >>> old_lumps.difference(new_lumps)
# {'DISPLACEMENT_TRIS', 'DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS', 'DISPLACEMENT_VERTICES', 'DISPLACEMENT_INFO'}
# >>> new_lumps.difference(old_lumps)
# {'VISIBILITY'}


class TestBspDiff:
    diff = diff.BspDiff(old_bsp, new_bsp)
    # TODO: diff.BspDiff(old_bsp, new_bsp) & verify no changes

    def test_invalid_lump(self):
        with pytest.raises(AttributeError):
            print(self.diff.NONEXISTANT_LUMP)

    def test_lump_added(self):
        lump_diff = self.diff.VISIBILITY
        assert isinstance(lump_diff, diff.NoneDiff)

    def test_lump_removed(self):
        lump_diff = self.diff.DISPLACEMENT_INFO
        assert isinstance(lump_diff, diff.NoneDiff)


# TODO: TestNoneDiff  (short_stats only)
# TODO: TestDiffLumps  (assigning diff class)
# -- branches.shared.Entities -> diff.shared.EntitiesDiff
# -- branches.valve.source.PakFile -> diff.valve.source.PakFileDiff
# -- branches.base.* -> diff.base.Diff
# -- RawBspLump -> NotImplementedError
# -- * -> diff.base.Diff