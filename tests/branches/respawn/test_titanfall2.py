from bsp_tool import RespawnBsp
from bsp_tool.branches.respawn import titanfall2

import pytest

from ... import files


bsps = {
    **files.local_bsps(
        RespawnBsp, {
            titanfall2: [
                "Titanfall 2"]}),
    **files.library_bsps(
        RespawnBsp, {
            titanfall2: {
                "Mod": {
                    "Titanfall 2": [
                        "Titanfall2/maps/"]}}})}


# TODO: test LumpClasses are valid
# TODO: test SpecialLumpClasses are valid
# TODO: verify lumps that index other lumps are in bounds


class TestAssumptions:
    # TODO: verify more assumptions about this branch_script
    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_grid_cells_count(self, bsp: RespawnBsp):
        assert len(bsp.CM_GRID_CELLS) == bsp.CM_GRID.count.x * bsp.CM_GRID.count.y + len(bsp.MODELS)


# class TestMethods:
#     @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
#     def test_method(self, bsp: RespawnBsp):
#         ...
