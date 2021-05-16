"""Counter-Strike: Online 2.  Appears to be similar to Vindictus"""
import collections
import enum
import io
import struct
import zipfile

from . import vindictus
from .. import base


# NOTE: there are two variants with identical version numbers
# -- 2013era & 2017era
BSP_VERSION = 100  # 1.00?


class LUMP(enum.Enum):
    ENTITIES = 0
    PLANES = 1
    TEXDATA = 2
    VERTICES = 3
    VISIBILITY = 4
    NODES = 5
    TEXINFO = 6
    FACES = 7  # version 1
    LIGHTING = 8  # version 1
    OCCLUSION = 9  # version 2
    LEAVES = 10  # version 1
    FACEIDS = 11
    EDGES = 12
    SURFEDGES = 13
    MODELS = 14
    WORLD_LIGHTS = 15
    LEAF_FACES = 16
    LEAF_BRUSHES = 17
    BRUSHES = 18
    BRUSH_SIDES = 19
    AREAS = 20
    AREA_PORTALS = 21
    UNUSED_22 = 22
    UNUSED_23 = 23
    UNUSED_24 = 24
    UNUSED_25 = 25
    DISPLACEMENT_INFO = 26
    ORIGINAL_FACES = 27
    PHYSICS_DISPLACEMENT = 28
    PHYSICSCOLLIDE = 29
    VERT_NORMALS = 30
    VERT_NORMAL_INDICES = 31
    DISPLACEMENT_LIGHTMAP_ALPHAS = 32
    DISPLACEMENT_VERTS = 33
    DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS = 34
    GAME_LUMP = 35
    LEAF_WATER_DATA = 36
    PRIMITIVES = 37
    PRIM_VERTS = 38
    PRIM_INDICES = 39
    PAKFILE = 40
    CLIP_PORTAL_VERTICES = 41
    CUBEMAPS = 42
    TEXDATA_STRING_DATA = 43
    TEXDATA_STRING_TABLE = 44
    OVERLAYS = 45
    LEAF_MIN_DIST_TO_WATER = 46
    FACE_MARCO_TEXTURE_INFO = 47
    DISPLACEMENT_TRIS = 48
    PHYSICSCOLLIDE_SURFACE = 49
    WATER_OVERLAYS = 50
    LEAF_AMBIENT_INDEX_HDR = 51
    LEAF_AMBIENT_INDEX = 52
    LIGHTING_HDR = 53  # version 1
    WORLD_LIGHTS_HDR = 54
    LEAF_AMBIENT_LIGHTING_HDR = 55  # version 1
    LEAF_AMBIENT_LIGHTING = 56  # version 1
    XZIP_PAKFILE = 57
    FACES_HDR = 58
    MAP_FLAGS = 59
    OVERLAY_FADES = 60
    UNKNOWN_61 = 61  # version 1
    UNUSED_62 = 62
    UNUSED_63 = 63


lump_header_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}
CSOLumpHeader = collections.namedtuple("LumpHeader", ["offset", "length", "version", "compressed", "fourCC"])
# NOTE: looking at headers, a half int of value 0x0001 seemed attached to version seemed to make sense


def read_lump_header(file, LUMP: enum.Enum):
    file.seek(lump_header_address[LUMP])
    offset, length, version, compressed = struct.unpack("2I2H", file.read(12))
    fourCC = int.from_bytes(file.read(4), "big")  # fourCC is big endian for some reason
    header = CSOLumpHeader(offset, length, version, bool(compressed), fourCC)
    return header
# NOTE: lump header formats could easily be a:  LumpClass(base.Struct)


# classes for each lump, in alphabetical order: [XX / 64]
class DisplacementInfo(base.Struct):  # LUMP 26
    __slots__ = [f"unknown{i + 1}" for i in range(61)]  # not yet used
    _format = "60IH"  # 242 bytes, 10 bytes more than Vindictus

# NOTE: dcubemap_t varies (160 bytes 2013era, 164 bytes 2017era)
# NOTE: if lighting settings are not Medium, maps from 2013 era crash


# special lump classes, in alphabetical order
class PakFile(zipfile.ZipFile):  # WIP
    """CSO2 PakFiles have a custom .zip format"""
    # b"CS" file magic & different header format?
    def __init__(self, raw_zip: bytes):
        # TODO: translate header to b"PK\x03\x04..."
        raw_zip = b"".join([b"PK", raw_zip[2:]])
        self._buffer = io.BytesIO(raw_zip)
        super(PakFile, self).__init__(self._buffer)

    def as_bytes(self) -> bytes:
        # TODO: translate header to b"CS\x03\x04..."
        raw_zip = self._buffer.getvalue()
        raw_zip = b"".join([b"CS", raw_zip[2:]])
        return raw_zip


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = vindictus.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = vindictus.LUMP_CLASSES.copy()
# NOTE: 2013 maps use orange_box DisplacementInfo (176 byte)
# NOTE: 2017era maps use the same version numbers etc as 2013era
# -- this is a nightmare for autodetecting
# however, since 2013 is no longer supported by CSO2, supporting just 2017 should work
# supporting 2013era maps should only require a tweak of orange_box

SPECIAL_LUMP_CLASSES = vindictus.SPECIAL_LUMP_CLASSES.copy()
SPECIAL_LUMP_CLASSES.update({"PAKFILE": {0: PakFile}})  # WIP

methods = vindictus.methods
