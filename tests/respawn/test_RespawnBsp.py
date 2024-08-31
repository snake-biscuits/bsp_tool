from bsp_tool import RespawnBsp
from bsp_tool.branches.respawn import titanfall2

import pytest

from .. import files


bsps = files.local_bsps(
    RespawnBsp, {
        titanfall2: [
            "Titanfall 2"]})


@pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
def test_no_errors(bsp):
    assert len(bsp.loading_errors) == 0
    assert len(bsp.GAME_LUMP.loading_errors) == 0


@pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
def test_entities_loaded(bsp):
    assert bsp.ENTITIES[0]["classname"] == "worldspawn"
