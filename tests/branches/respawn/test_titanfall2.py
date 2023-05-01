import fnmatch
import os

from bsp_tool import RespawnBsp
from bsp_tool.branches.respawn import titanfall2

import pytest


bsps = list()
map_dir = os.path.join(os.getcwd(), "tests/maps/Titanfall 2")
# TODO: add more Titanfall 2 dirs from maplist.installed_games & make it optional
for map_name in fnmatch.filter(os.listdir(map_dir), "*.bsp"):
    bsps.append(RespawnBsp(titanfall2, os.path.join(map_dir, map_name)))


# TODO: test LumpClasses are valid
# TODO: test SpecialLumpClasses are valid
# TODO: verify lumps that index other lumps are in bounds


class TestAssumptions:
    # TODO: verify more assumptions about this branch_script
    @pytest.mark.parametrize("bsp", bsps)
    def test_grid_cells_count(self, bsp: RespawnBsp):
        assert len(bsp.CM_GRID_CELLS) == bsp.CM_GRID.count.x * bsp.CM_GRID.count.y + len(bsp.MODELS)
