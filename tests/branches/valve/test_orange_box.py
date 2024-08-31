from bsp_tool import ValveBsp
from bsp_tool.branches.valve import orange_box

import pytest

from ... import files


bsps = files.local_bsps(
    ValveBsp, {
        orange_box: [
            "Team Fortress 2"]})


class TestMethods:
    displacement_bsps = {m: b for m, b in bsps.items() if b.headers["DISPLACEMENT_INFO"].length != 0}

    # TODO: def test_face_mesh(bsp: ValveBsp):
    # TODO: def test_model(bsp: ValveBsp):
    # TODO: def test_textures_of_brush(bsp: ValveBsp):

    @pytest.mark.parametrize("bsp", displacement_bsps.values(), ids=displacement_bsps.keys())
    def test_displacement_mesh(self, bsp: ValveBsp):
        for disp_info in getattr(bsp, "DISPLACEMENT_INFO", list()):
            face_index = disp_info.face
            bsp.displacement_mesh(face_index)  # failing when the function can't be called is good enough for now
            # TODO: interrogate results
