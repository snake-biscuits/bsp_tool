import fnmatch
import os

from bsp_tool import ValveBsp
from bsp_tool.branches.strata import strata

import pytest


bsps = list()
map_dir = os.path.join(os.getcwd(), "tests/maps/Momentum Mod")
# TODO: add more Strata dirs from maplist.installed_games & make it optional
for map_name in fnmatch.filter(os.listdir(map_dir), "*.bsp"):
    bsps.append(ValveBsp(strata, os.path.join(map_dir, map_name)))


# TODO: test LumpClasses are valid
# TODO: test SpecialLumpClasses are valid
# TODO: verify assumptions about this branch_script
# TODO: verify lumps that index other lumps are in bounds


@pytest.mark.parametrize("bsp", bsps)
def test_spec(bsp: ValveBsp):
    assert bsp.file_magic == strata.FILE_MAGIC
    assert bsp.bsp_version == strata.BSP_VERSION


class TestDisplacements:
    # TODO: a bunch of checks (index bounds, neighbours, valid enums etc.)
    # need at least one map with a displacement
    ...
    # TODO: test_physics_displacement
