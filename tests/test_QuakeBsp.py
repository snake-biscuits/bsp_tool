from . import utils
from bsp_tool import QuakeBsp
from bsp_tool.branches.id_software import quake

import pytest


bsps = utils.get_test_maps(QuakeBsp, {quake: ["Quake"]})


@pytest.mark.parametrize("bsp", bsps, ids=[b.filename for b in bsps])
def test_no_errors(bsp):
    assert len(bsp.loading_errors) == 0


@pytest.mark.parametrize("bsp", bsps, ids=[b.filename for b in bsps])
def test_entities_loaded(bsp):
    assert bsp.ENTITIES[0]["classname"] == "worldspawn"


# TODO: test methods
# TODO: .save_as() with no edits should copy file byte-for-byte
