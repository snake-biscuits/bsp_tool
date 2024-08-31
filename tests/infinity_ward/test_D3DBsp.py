from bsp_tool import D3DBsp
from bsp_tool.branches.infinity_ward import modern_warfare

import pytest

from .. import files


bsps = files.local_bsps(
    D3DBsp, {
        modern_warfare: [
            "Call of Duty 4",
            "Call of Duty 4/mp"]},
    pattern="*.d3dbsp")


@pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
def test_no_errors(bsp):
    assert len(bsp.loading_errors) == 0


@pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
def test_entities_loaded(bsp):
    assert bsp.ENTITIES[0]["classname"] == "worldspawn"
