from ... import files
from bsp_tool import QuakeBsp
from bsp_tool.branches.id_software import quake

import pytest


bsps = files.local_bsps(
    QuakeBsp, {
        quake: [
            "Quake"]})


# TODO: test LumpClasses are valid
# TODO: test SpecialLumpClasses are valid
# TODO: verify assumptions about this branch_script
# TODO: verify lumps that index other lumps are in bounds


class TestMethods:
    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_face_mesh(self, bsp: QuakeBsp):
        for i, face in enumerate(bsp.FACES):
            mesh = bsp.face_mesh(i)
            assert len(mesh.polygons) == 1
            polygon = mesh.polygons[0]
            assert len(polygon.vertices) >= 3
            # TODO: vertex positions are on plane (or close enough)
            assert polygon.normal == bsp.PLANES[face.plane].normal
            # TODO: uvs match texture vec projections (or close enough)
            # TODO: consistent winding order

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_lightmap_of_face(self, bsp: QuakeBsp):
        for i, face in enumerate(bsp.FACES):
            data = bsp.lightmap_of_face(i)
            assert set(data.keys()) == {"width", "height", "lightmap_bytes"}
            # FAILING: assert len(data["lightmap_bytes"]) == data["width"] * data["height"]

    # TODO: test_model
    # TODO: test_parse_vis
