from ... import utils
from bsp_tool import ValveBsp
from bsp_tool.branches.valve import orange_box

import pytest


bsps = utils.get_test_maps(ValveBsp, {orange_box: ["Team Fortress 2"]})


class TestMethods:
    displacement_bsps = [b for b in bsps if b.headers["DISPLACEMENT_INFO"].length != 0]

    # TODO: def test_vertices_of_face(bsp: ValveBsp):

    @pytest.mark.parametrize("bsp", displacement_bsps, ids=[b.filename for b in displacement_bsps])
    def test_vertices_of_displacement(self, bsp: ValveBsp):
        for disp_info in getattr(bsp, "DISPLACEMENT_INFO", list()):
            face_index = disp_info.face
            bsp.vertices_of_displacement(face_index)  # failing when the function can't be called is good enough for now
            # TODO: interrogate results

    # TODO: def test_textures_of_brush(bsp: ValveBsp):
