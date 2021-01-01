import struct

from bsp_tool import IdTechBsp
from bsp_tool.branches.id_software import quake3


def test_face_struct():  # most complex branches.base.Mappedarray
    bigbox_bsp = IdTechBsp(quake3, "tests/maps/test_bigbox.bsp")
    header = bigbox_bsp.HEADERS["FACES"]
    with open(bigbox_bsp.file.name, "rb") as file:
        file.seek(header.offset)
        raw_faces = file.read(header.length)

    faces = [*map(quake3.Face, struct.iter_unpack(quake3.Face._format, raw_faces))]
    print(*faces, sep="\n")  # error in __repr__?
    return faces
