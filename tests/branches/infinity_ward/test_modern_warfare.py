import fnmatch
import os

from bsp_tool import D3DBsp
from bsp_tool.branches.infinity_ward import modern_warfare

import pytest


bsps = list()
map_dirs = [os.path.join(os.getcwd(), "tests/maps/Call of Duty 4"),
            os.path.join(os.getcwd(), "tests/maps/Call of Duty 4/mp")]
# TODO: add more Call of Duty 4 dirs from maplist.installed_games & make it optional
for map_dir in map_dirs:
    for map_name in fnmatch.filter(os.listdir(map_dir), "*.d3dbsp"):
        bsps.append(D3DBsp(modern_warfare, os.path.join(map_dir, map_name)))


# TODO: test LumpClasses are valid
# TODO: test SpecialLumpClasses are valid
# TODO: verify assumptions about this branch_script


class TestBounds:
    """verify lumps that index other lumps are in bounds"""
    @pytest.mark.parametrize("bsp", bsps)
    def test_simple_indices(self, bsp: D3DBsp):
        assert all([i <= len(bsp.SIMPLE_VERTICES) for i in bsp.SIMPLE_INDICES])

    @pytest.mark.parametrize("bsp", bsps)
    def test_layered_indices(self, bsp: D3DBsp):
        assert all([i <= len(bsp.LAYERED_VERTICES) for i in bsp.LAYERED_INDICES])
