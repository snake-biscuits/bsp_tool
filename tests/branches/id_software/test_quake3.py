import struct

from bsp_tool import IdTechBsp
from bsp_tool.branches.id_software import quake3

import pytest

from ... import files


bsps = files.local_bsps(
    IdTechBsp, {
        quake3: [
            "Quake 3 Arena"]})


# TODO: test LumpClasses are valid
# TODO: test SpecialLumpClasses are valid
# TODO: verify assumptions about this branch_script
# TODO: verify lumps that index other lumps are in bounds


@pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
def test_face_struct(bsp: IdTechBsp):  # the most complex MappedArray
    # TODO: add more asserts, be thorough
    header = bsp.headers["FACES"]
    assert header.length % struct.calcsize(quake3.Face._format) == 0
    with open(bsp.file.name, "rb") as file:
        file.seek(header.offset)
        raw_faces = file.read(header.length)
    # just __init__ on some real-world bytes
    faces = [*map(quake3.Face.from_tuple, struct.iter_unpack(quake3.Face._format, raw_faces))]  # noqa F841


# class TestMethods:
#     @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
#     def test_vertices_of_face(self, bsp: IdTechBsp):
#         # TODO: write a real test once this method exists
#         ...

#     @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
#     def test_vertices_of_model(self, bsp: IdTechBsp):
#         # TODO: write a real test once this method exists
#         ...
