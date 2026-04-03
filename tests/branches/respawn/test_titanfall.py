from bsp_tool import RespawnBsp
from bsp_tool.branches.respawn import titanfall

import pytest

from ... import files


bsps = {
    **files.library_bsps(
        RespawnBsp, {
            titanfall: {"Mod": {
                    "Titanfall": ["Titanfall/maps/"],
                    "Titanfall: Online": ["TitanfallOnline/maps/"]}}})}
# NOTE: skipping depot/; should line up with results for maps/


# class TestConstant:
#     """some things never change"""
#     @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
#     def test_XYZ(self, bsp: RespawnBsp):
#         assert bsp.XYZ_LUMP[0] == constant_value


class TestIndex:
    """indices into lumps are in bounds"""

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_num_grid_cells(self, bsp: RespawnBsp):
        assert bsp.CM_GRID.count.x * bsp.CM_GRID.count.y + len(bsp.MODELS) == len(bsp.CM_GRID_CELLS)

    # TODO: Brush -> BrushSide
    # TODO: Portal -> Cell (and PortalType.SKY indexes len(Cells) + 1)


# class TestLogic:
#     @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
#     def test_behaviour(self, bsp: RespawnBsp):
#         ...  # if i do x with y, we get z


# class TestLumpClass:
#     ...


# class TestMethod:
#     @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
#     def test_method(self, bsp: RespawnBsp):
#         ...


# class TestParallel:
#     @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
#     def test_lumpA_lumpB(self, bsp: RespawnBsp):
#         assert len(bsp.LUMP_A) == len(bsp.LUMP_B)


# class TestSpecialLumpClass:
#     ...
