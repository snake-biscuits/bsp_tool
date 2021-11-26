# import os
import struct

from bsp_tool import IdTechBsp
from bsp_tool.branches.id_software import quake3


mp_lobby = IdTechBsp(quake3, "tests/maps/Quake 3 Arena/mp_lobby.bsp")


def test_no_errors():
    assert len(mp_lobby.loading_errors) == 0


def test_entities_loaded():
    assert mp_lobby.ENTITIES[0]["classname"] == "worldspawn"


# TODO: @pytest.mark.parametrize("LumpClass", ...)
def test_face_struct():  # most complex branches.base.MappedArray
    # TODO: add some asserts, be thorough
    header = mp_lobby.headers["FACES"]
    assert header.length % struct.calcsize(quake3.Face._format) == 0
    with open(mp_lobby.file.name, "rb") as file:
        file.seek(header.offset)
        raw_faces = file.read(header.length)

    faces = [*map(quake3.Face.from_tuple, struct.iter_unpack(quake3.Face._format, raw_faces))]
    print(*faces, sep="\n")  # error in __repr__?
    return faces
    # ^ what?


# def test_save_as():  # NotImplemented
#     with open("tests/maps/Quake 3 Arena/mp_lobby.bsp", "rb") as file:
#         original = file.read()
#     bigbox.save_as("tests/maps/Quake 3 Arena/mp_lobby_save_test.bsp")
#     with open("tests/maps/Quake 3 Arena/mp_lobby_save_test.bsp", "rb") as file:
#         saved = file.read()
#     os.remove("tests/maps/Quake 3 Arena/mp_lobby_save_test.bsp")
#     assert original == saved
