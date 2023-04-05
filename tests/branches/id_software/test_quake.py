from bsp_tool import QuakeBsp
from bsp_tool.branches.id_software import quake

import pytest


# NOTE: not grabbing all maps as ReMakeQuake maps are in the same folder
bsps = [QuakeBsp(quake, "tests/maps/Quake/mp_lobby.bsp")]


# TODO: test LumpClasses are valid
# TODO: test SpecialLumpClasses are valid
# TODO: verify assumptions about this branch_script
# TODO: verify lumps that index other lumps are in bounds

class TestMethods:
    @pytest.mark.parametrize("bsp", bsps)
    def test_vertices_of_face(self, bsp):
        for i, face in enumerate(bsp.FACES):
            vertices = bsp.vertices_of_face(i)
            # ^ [(pos.xyz, uv.xy)]
            # TODO: verify vertices
            assert len(vertices) >= 3  # the compiler would never
            # positions are on plane (or close enough)
            # uvs match texture vec projections (or close enough)
            # consistent winding order

    @pytest.mark.parametrize("bsp", bsps)
    def test_lightmap_of_face(self, bsp):
        for i, face in enumerate(bsp.FACES):
            data = bsp.lightmap_of_face(i)
            # ^ {"uvs": [uv.xy], "width": 0, "height": 0}
            # uvs are from vertices_of_face, used to derive width & height
            if (data["width"], data["height"]) == (0, 0):
                assert data["lightmap_offset"] == -1
                continue
            assert 0 <= data["lightmap_offset"] < len(bsp.LIGHTING)
            assert len(data["lightmap_bytes"]) != b""

    # TODO: test_as_lightmapped_obj
    # TODO: test_parse_vis
    # TODO: test_vertices_of_model
