from bsp_tool import D3DBsp
from bsp_tool.branches.infinity_ward import modern_warfare

import pytest

from ... import files


bsps = files.local_bsps(
    D3DBsp, {
        modern_warfare: [
            "Call of Duty 4",
            "Call of Duty 4/mp"]},
    pattern="*.d3dbsp")


# TODO: test LumpClasses are valid
# TODO: test SpecialLumpClasses are valid
# TODO: verify assumptions about this branch_script


class TestBounds:
    """verify lumps that index other lumps are in bounds"""
    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_simple_indices(self, bsp: D3DBsp):
        assert all([
            i <= len(bsp.SIMPLE_VERTICES)
            for i in bsp.SIMPLE_INDICES])

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_layered_indices(self, bsp: D3DBsp):
        assert all([
            i <= len(bsp.LAYERED_VERTICES)
            for i in bsp.LAYERED_INDICES])
