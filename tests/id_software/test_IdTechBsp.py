from bsp_tool import IdTechBsp
from bsp_tool.branches.id_software import quake2
from bsp_tool.branches.id_software import quake3

import pytest

from .. import files


bsps = files.local_bsps(
    IdTechBsp, {
        quake2: [
            "Quake 2"],
        quake3: [
            "Quake 3 Arena"]})


@pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
def test_no_errors(bsp):
    assert len(bsp.loading_errors) == 0


@pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
def test_entities_loaded(bsp):
    assert bsp.ENTITIES[0]["classname"] == "worldspawn"


@pytest.mark.xfail(reason="ADVERTISEMENTS header")
@pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
def test_get_signature(bsp):
    signature = bsp.signature.rstrip(b"\0").decode("ascii", errors="strict")
    assert "q3map2" in signature.lower()
