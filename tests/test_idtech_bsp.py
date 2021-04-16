# import os
import struct

from bsp_tool import IdTechBsp
from bsp_tool.branches.id_software import quake3


bigbox = IdTechBsp(quake3, "tests/maps/test_bigbox.bsp")


def test_no_errors():
    assert len(bigbox.loading_errors) == 0


def test_entities_loaded():
    assert bigbox.ENTITIES[0]["classname"] == "worldspawn"


def test_face_struct():  # most complex branches.base.MappedArray
    # TODO: add some asserts, be thorough
    header = bigbox.HEADERS["FACES"]
    with open(bigbox.file.name, "rb") as file:
        file.seek(header.offset)
        raw_faces = file.read(header.length)

    faces = [*map(quake3.Face, struct.iter_unpack(quake3.Face._format, raw_faces))]
    print(*faces, sep="\n")  # error in __repr__?
    return faces


# def test_save_as():  # Not implemented
#     with open("tests/maps/test_bigbox.bsp", "rb") as file:
#         original = file.read()
#     bigbox.save_as("tests/maps/bigbox_save_test.bsp")
#     with open("tests/maps/bigbox_save_test.bsp", "rb") as file:
#         saved = file.read()
#     os.remove("tests/maps/bigbox_save_test.bsp")
#     assert original == saved
