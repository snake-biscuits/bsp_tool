import fnmatch
import os

from bsp_tool import IdTechBsp
from bsp_tool.branches.id_software import quake2

import pytest


bsps = list()
map_dir = os.path.join(os.getcwd(), "tests/maps/Quake 2")
# TODO: add more Quake 2 dirs from maplist.installed_games & make it optional
for map_name in fnmatch.filter(os.listdir(map_dir), "*.bsp"):
    bsps.append(IdTechBsp(quake2, os.path.join(map_dir, map_name)))


# TODO: test LumpClasses are valid
# TODO: verify assumptions about this branch_script
# TODO: verify lumps that index other lumps are in bounds


@pytest.mark.parametrize("bsp", bsps)
def test_visibility(bsp: IdTechBsp):
    num_clusters = len({leaf.cluster for leaf in bsp.LEAVES if leaf.cluster != -1})
    assert len(bsp.VISIBILITY.pvs) == num_clusters
    assert len(bsp.VISIBILITY.pas) == num_clusters
    # TODO: assert no out of bounds bits


# @pytest.mark.parametrize("bsp", bsps)
# def test_lighting(bsp: IdTechBsp):
#     # TODO: unmapped; like quake 1? quake 2 uses quake 1 faces...
#     ...
