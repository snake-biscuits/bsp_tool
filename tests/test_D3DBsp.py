from . import utils
from bsp_tool import D3DBsp
from bsp_tool.branches.infinity_ward import modern_warfare

import pytest


bsps = utils.get_test_maps(D3DBsp, {modern_warfare: ["Call of Duty 4", "Call of Duty 4/mp"]}, pattern="*.d3dbsp")


@pytest.mark.parametrize("bsp", bsps, ids=[b.filename for b in bsps])
def test_no_errors(bsp):
    assert len(bsp.loading_errors) == 0


@pytest.mark.parametrize("bsp", bsps, ids=[b.filename for b in bsps])
def test_entites_loaded(bsp):
    assert bsp.ENTITIES[0]["classname"] == "worldspawn"


# TODO: test methods
# TODO: .save_as() with no edits should copy file byte-for-byte
