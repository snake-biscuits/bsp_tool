from bsp_tool.valve import ValveBsp
from bsp_tool.branches.strata import strata
from bsp_tool.branches.valve import orange_box
from bsp_tool.branches.valve import orange_box_x360

import pytest

from .. import files


# PC
bsps = files.local_bsps(
    ValveBsp, {
        orange_box: [
            "Team Fortress 2"],
        strata: [
            "Momentum Mod"]})


@pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
def test_no_errors(bsp):
    assert len(bsp.loading_errors) == 0
    assert len(bsp.GAME_LUMP.loading_errors) == 0


@pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
def test_entities_loaded(bsp):
    assert bsp.ENTITIES[0]["classname"] == "worldspawn"


# XBOX 360
x360_bsps = files.local_bsps(
    ValveBsp, {
        orange_box_x360: [
            "Xbox360/The Orange Box"]})


@pytest.mark.parametrize("bsp", x360_bsps.values(), ids=x360_bsps.keys())
def test_x360(bsp):
    assert len(bsp.loading_errors) == 0


# NOTE: Official X360/OrangeBox maps don't have this issue
@pytest.mark.xfail(raises=AssertionError, reason="invalid GAME_LUMP.sprp")
@pytest.mark.parametrize("bsp", x360_bsps.values(), ids=x360_bsps.keys())
def test_x360_failing(bsp):
    assert len(bsp.GAME_LUMP.loading_errors) == 0
