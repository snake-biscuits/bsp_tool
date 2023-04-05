import fnmatch
import os

from bsp_tool import ValveBsp
from bsp_tool.branches.valve import orange_box

import pytest


bsps = []
map_dir = os.path.join(os.getcwd(), "tests/maps/Team Fortress 2")
for map_name in fnmatch.filter(os.listdir(map_dir), "*[Bb][Ss][Pp]"):
    bsps.append(ValveBsp(orange_box, os.path.join(map_dir, map_name)))


# TODO: ensure no floats are NaN
# TODO: check all enums are in-range
# TODO: check for unnamed unknown flags (100% unused & not listed is OK)
# TODO: check all paddings are 0
# TODO: check all [+ve or -1] domain ints are valid


class TestMethods:
    # TODO: def test_vertices_of_face(bsp):

    @pytest.mark.parametrize("bsp", bsps)
    def test_vertices_of_displacement(self, bsp):
        for disp_info in getattr(bsp, "DISPLACEMENT_INFO", list()):
            face_index = disp_info.face
            bsp.vertices_of_displacement(face_index)  # failing when the function can't be called is good enough for now
            # TODO: interrogate results

    # TODO: def test_textures_of_brush(bsp):
