# TODO: more in-depth tests
import fnmatch
import os
import pytest
import struct

from bsp_tool import IdTechBsp
from bsp_tool.branches.id_software import quake3

bsps = []
map_dir = os.path.join(os.getcwd(), "tests/maps/Quake 3 Arena")
# TODO: add more Quake 3 Arena dirs from maplist.installed_games & make it optional
for map_name in fnmatch.filter(os.listdir(map_dir), "*[Bb][Ss][Pp]"):
    bsps.append(IdTechBsp(quake3, os.path.join(map_dir, map_name)))


@pytest.mark.parametrize("bsp", bsps)
def test_no_errors(bsp: IdTechBsp):
    assert len(bsp.loading_errors) == 0


@pytest.mark.parametrize("bsp", bsps)
def test_entities_loaded(bsp: IdTechBsp):
    assert bsp.ENTITIES[0]["classname"] == "worldspawn", bsp.filename


# NOTE: WIP
@pytest.mark.parametrize("bsp", bsps)
def test_face_struct(bsp: IdTechBsp):  # the most complex MappedArray
    # TODO: add more asserts, be thorough
    header = bsp.headers["FACES"]
    assert header.length % struct.calcsize(quake3.Face._format) == 0, bsp.filename
    with open(bsp.file.name, "rb") as file:
        file.seek(header.offset)
        raw_faces = file.read(header.length)
    # just __init__ on some real-world bytes
    faces = [*map(quake3.Face.from_tuple, struct.iter_unpack(quake3.Face._format, raw_faces))]  # noqa F841


# TODO: implement .save_as method and test that uneditted saves match EXACTLY
# @pytest.mark.parametrize("bsp", d3dbsps)
# def test_save_as(bsp):  # NotImplemented
#     with open(bsp.filename, "rb") as file:
#         original = file.read()
#     test2.save_as(f"{bsp.filename}.copy")
#     with open(f"{bsp.filename}.copy", "rb") as file:
#         saved = file.read()
#     os.remove(f"{bsp.filename}.copy")
#     assert original == saved

# TODO: assert UNUSED lump names are accurate
# -- warn if a lump is unexpectedly empty across all maps (test_deprecated?)
