from ... import utils
from bsp_tool import RespawnBsp
from bsp_tool.branches.respawn import titanfall2

import pytest


bsps = utils.get_test_maps(RespawnBsp, {titanfall2: ["Titanfall 2"]})


# TODO: test LumpClasses are valid
# TODO: test SpecialLumpClasses are valid
# TODO: verify lumps that index other lumps are in bounds


class TestAssumptions:
    # TODO: verify more assumptions about this branch_script
    @pytest.mark.parametrize("bsp", bsps, ids=[b.filename for b in bsps])
    def test_grid_cells_count(self, bsp: RespawnBsp):
        assert len(bsp.CM_GRID_CELLS) == bsp.CM_GRID.count.x * bsp.CM_GRID.count.y + len(bsp.MODELS)
