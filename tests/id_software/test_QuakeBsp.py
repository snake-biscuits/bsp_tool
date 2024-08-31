from bsp_tool import QuakeBsp
from bsp_tool.branches.id_software import quake

import pytest

from .. import files


bsps = files.local_bsps(
    QuakeBsp, {
        quake: [
            "Quake"]})


@pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
def test_no_errors(bsp):
    assert len(bsp.loading_errors) == 0


@pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
def test_entities_loaded(bsp):
    assert bsp.ENTITIES[0]["classname"] == "worldspawn"
