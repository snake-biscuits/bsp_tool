from bsp_tool import ValveBsp
from bsp_tool.branches.strata import strata

import pytest

from ... import files


bsps = files.local_bsps(
    ValveBsp, {
        strata: [
            "Momentum Mod"]})


# TODO: test LumpClasses are valid
# TODO: test SpecialLumpClasses are valid
# TODO: verify assumptions about this branch_script
# TODO: verify lumps that index other lumps are in bounds


@pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
def test_spec(bsp: ValveBsp):
    assert bsp.file_magic == strata.FILE_MAGIC
    assert bsp.version == strata.BSP_VERSION


class TestDisplacements:
    # TODO: a bunch of checks (index bounds, neighbours, valid enums etc.)
    # need at least one map with a displacement
    ...
    # TODO: test_physics_displacement
