"""2013-2017 format"""
# https://git.sr.ht/~leite/cso2-bsp-converter/tree/master/item/src/bsptypes.hpp
import enum
import io
import zipfile

from .. import base
from ..valve import source
from . import vindictus


FILE_MAGIC = b"VBSP"

BSP_VERSION = 100

GAME_PATHS = {"Counter-Strike: Online 2": "CSO2"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    ENTITIES = 0
    PLANES = 1
    TEXTURE_DATA = 2
    VERTICES = 3
    VISIBILITY = 4
    NODES = 5
    TEXTURE_INFO = 6
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
    PHYSICS_COLLIDE = 29
    VERTEX_NORMALS = 30
    VERTEX_NORMAL_INDICES = 31
    DISPLACEMENT_LIGHTMAP_ALPHAS = 32
    DISPLACEMENT_VERTICES = 33
    DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS = 34
    GAME_LUMP = 35
    LEAF_WATER_DATA = 36
    PRIMITIVES = 37
    PRIMITIVE_VERTICES = 38
    PRIMITIVE_INDICES = 39
    PAKFILE = 40
    CLIP_PORTAL_VERTICES = 41
    CUBEMAPS = 42
    TEXTURE_DATA_STRING_DATA = 43
    TEXTURE_DATA_STRING_TABLE = 44
    OVERLAYS = 45
    LEAF_MIN_DIST_TO_WATER = 46
    FACE_MARCO_TEXTURE_INFO = 47
    DISPLACEMENT_TRIS = 48
    PHYSICS_COLLIDE_SURFACE = 49
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
    UNKNOWN_61 = 61  # version 1; related to cubemaps?
    UNUSED_62 = 62
    UNUSED_63 = 63


class LumpHeader(base.MappedArray):
    offset: int  # index in .bsp file where lump begins
    length: int
    version: int
    compressed: int  # 2 byte bool?
    fourCC: int  # uncompressed size (big endian for some reason)
    _mapping = ["offset", "length", "version", "compressed", "fourCC"]
    _format = "2I2HI"


# classes for each lump, in alphabetical order:
# NOTE: dcubemap_t: 160 bytes


# special lump classes, in alphabetical order:
class PakFile(zipfile.ZipFile):  # WIP
    """CSO2 PakFiles have a custom .zip format"""
    # NOTE: it's not as simple as changing the FILE_MAGIC
    # -- this appears to be a unique implementation of .zip
    # b"CS" file magic & different header format?
    def __init__(self, raw_zip: bytes):
        # TODO: translate header to b"PK\x03\x04..."
        raw_zip = b"".join([b"PK", raw_zip[2:]])  # not that easy
        self._buffer = io.BytesIO(raw_zip)
        super(PakFile, self).__init__(self._buffer)

    def as_bytes(self) -> bytes:
        # TODO: translate header to b"CS\x03\x04..."
        raw_zip = self._buffer.getvalue()
        raw_zip = b"".join([b"CS", raw_zip[2:]])  # not that easy
        return raw_zip


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = vindictus.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = vindictus.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("BRUSH_SIDES")
LUMP_CLASSES.pop("CUBEMAPS")
LUMP_CLASSES.pop("DISPLACEMENT_INFO")
LUMP_CLASSES.pop("FACES")
LUMP_CLASSES.pop("LEAVES")
LUMP_CLASSES.pop("ORIGINAL_FACES")
LUMP_CLASSES.pop("OVERLAYS")
LUMP_CLASSES.pop("TEXTURE_INFO")
LUMP_CLASSES.pop("WORLD_LIGHTS")
LUMP_CLASSES.pop("WORLD_LIGHTS_HDR")

SPECIAL_LUMP_CLASSES = vindictus.SPECIAL_LUMP_CLASSES.copy()
SPECIAL_LUMP_CLASSES.pop("PAKFILE")

GAME_LUMP_HEADER = source.GameLumpHeader

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = dict()


methods = [*vindictus.methods]
