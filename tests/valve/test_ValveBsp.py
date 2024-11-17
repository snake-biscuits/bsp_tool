import collections
import os

from bsp_tool.valve import ValveBsp
from bsp_tool.branches.strata import strata
from bsp_tool.branches.valve import orange_box
from bsp_tool.branches.valve import orange_box_x360
from bsp_tool.branches.valve import source

import pytest

from .. import files


# PC
bsps = files.local_bsps(
    ValveBsp, {
        orange_box: [
            "Team Fortress 2"],
        strata: [
            "Momentum Mod"]})

branch_dirs = {
    source: {
        "Steam": {
            "Half-Life 2": ["Half-Life 2/hl2/maps"],
            "Half-Life 2: Episode 1": ["Half-Life 2/episodic/maps"],
            "Half-Life 2: Episode 2": ["Half-Life 2/ep2/maps"],
            "Half-Life 2: Lost Coast": ["Half-Life 2/lostcoast/maps"]}}}

library = files.game_library()

bsps.update({
    f"{section} | {game} | {short_path}": ValveBsp.from_file(branch, full_path)
    for branch, bsp_dirs in branch_dirs.items()
    for section, game, paths in library.scan(bsp_dirs, "*.bsp")
    for short_path, full_path in paths
    if not os.path.getsize(full_path) == 0})

bsps = collections.OrderedDict(sorted(bsps.items()))

# lump headers are totally incorrect
if "Steam | Half-Life 2: Episode 1 | ep1_citadel_00_demo.bsp" in bsps:
    bsps.pop("Steam | Half-Life 2: Episode 1 | ep1_citadel_00_demo.bsp")


@pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
def test_no_errors(bsp):
    assert len(bsp.loading_errors) == 0
    assert len(bsp.GAME_LUMP.loading_errors) == 0


@pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
def test_entities_loaded(bsp):
    assert "ENTITIES" not in bsp.loading_errors
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
    assert "GAME_LUMP" not in bsp.loading_errors
    assert len(bsp.GAME_LUMP.loading_errors) == 0
