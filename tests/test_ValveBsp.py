from . import utils
from bsp_tool import ValveBsp
from bsp_tool.branches.strata import strata
from bsp_tool.branches.valve import orange_box

import pytest


bsps = utils.get_test_maps(ValveBsp, {orange_box: ["Team Fortress 2"], strata: ["Momentum Mod"]})


@pytest.mark.parametrize("bsp", bsps, ids=[b.filename for b in bsps])
def test_no_errors(bsp):
    assert len(bsp.loading_errors) == 0
    assert len(bsp.GAME_LUMP.loading_errors) == 0


@pytest.mark.parametrize("bsp", bsps, ids=[b.filename for b in bsps])
def test_entities_loaded(bsp):
    assert bsp.ENTITIES[0]["classname"] == "worldspawn"


# TODO: test methods
# TODO: .save_as() with no edits should copy file byte-for-byte
