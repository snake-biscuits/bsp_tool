# Chaos Initiative's Chaos Source Engine (closed source) v25 VBSP
# https://blog.momentum-mod.org/posts/changelog/0.9.2/#not-so-very-full-anymore
# https://github.com/momentum-mod/BSPConversionLib
import enum

from ..valve import sdk_2013
from ..valve import source


FILE_MAGIC = b"VBSP"

BSP_VERSION = 25

GAME_PATHS = {"Momentum Mod": "Momentum Mod/momentum"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):  # assumed
    ENTITIES = 0
    PLANES = 1
    TEXTURE_DATA = 2
    VERTICES = 3
    VISIBILITY = 4
    NODES = 5
    TEXTURE_INFO = 6
    FACES = 7
    LIGHTING = 8
    OCCLUSION = 9
    LEAVES = 10
    FACE_IDS = 11
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
    FACE_BRUSHES = 22  # infra
    FACE_BRUSH_LIST = 23  # infra
    UNUSED_24 = 24
    UNUSED_25 = 25
    DISPLACEMENT_INFO = 26
    ORIGINAL_FACES = 27
    PHYSICS_DISPLACEMENT = 28
    PHYSICS_COLLIDE = 29
    VERTEX_NORMALS = 30
    VERTEX_NORMAL_INDICES = 31
    DISPLACEMENT_LIGHTMAP_ALPHAS = 32  # deprecated / X360 ?
    DISPLACEMENT_VERTICES = 33
    DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS = 34
    GAME_LUMP = 35
    LEAF_WATER_DATA = 36
    PRIMITIVES = 37
    PRIMITIVE_VERTICES = 38  # deprecated / X360 ?
    PRIMITIVE_INDICES = 39
    PAKFILE = 40
    CLIP_PORTAL_VERTICES = 41
    CUBEMAPS = 42
    TEXTURE_DATA_STRING_DATA = 43
    TEXTURE_DATA_STRING_TABLE = 44
    OVERLAYS = 45
    LEAF_MIN_DIST_TO_WATER = 46
    FACE_MACRO_TEXTURE_INFO = 47
    DISPLACEMENT_TRIS = 48
    PROP_BLOB = 49  # left4dead
    WATER_OVERLAYS = 50  # deprecated / X360 ?
    LEAF_AMBIENT_INDEX_HDR = 51
    LEAF_AMBIENT_INDEX = 52
    LIGHTING_HDR = 53
    WORLD_LIGHTS_HDR = 54
    LEAF_AMBIENT_LIGHTING_HDR = 55
    LEAF_AMBIENT_LIGHTING = 56
    XZIP_PAKFILE = 57  # deprecated / X360 ?
    FACES_HDR = 58
    MAP_FLAGS = 59
    OVERLAY_FADES = 60
    OVERLAY_SYSTEM_LEVELS = 61  # left4dead
    PHYSICS_LEVEL = 62  # left4dead2
    DISPLACEMENT_MULTIBLEND = 63  # alienswarm


LumpHeader = source.LumpHeader

# Known lump changes from SDK 2013 -> Chaos
# TODO: figure out what changed


# engine limits:
# NOTE: max map coords are -131072 to 131072 (4^3x Source, 2^3x Apex Legends)
class MAX(enum.Enum):
    """https://blog.momentum-mod.org/posts/changelog/0.9.2/"""
    MODELS = 65536
    BRUSHES = 131072
    BRUSH_SIDES = 655360
    PLANES = 1048576
    VERTICES = 1048576
    NODES = 1048576
    # unlimited TEXTURE_INFO
    TEXTURE_DATA = 16384
    FACES = 1048576
    FACES_HDR = 1048576
    ORIGINAL_FACES = 1048576
    LEAVES = 1048576
    LEAF_FACES = 1048576
    LEAF_BRUSHES = 1048576
    AREAS = 65536
    SURFEDGES = 2097152
    EDGES = 1048576
    # unlimited WORLDLIGHTS
    # unlimited WORLDLIGHTS_HDR
    LEAF_WATER_DATA = 32768  # unchanged
    PRIMITIVES = 1048576
    PRIMITIVE_VERTICES = 1048576
    PRIMITIVE_INDICES = 1048576
    CUBEMAP_SAMPLES = 16384
    OVERLAYS = 16384
    DISPLACEMENTS = 262144
    # edicts limit quadrupled to 8192 (engine entity implementation)


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = sdk_2013.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = sdk_2013.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("ORIGINAL_FACES")

SPECIAL_LUMP_CLASSES = sdk_2013.SPECIAL_LUMP_CLASSES.copy()

GAME_LUMP_HEADER = sdk_2013.GAME_LUMP_HEADER

GAME_LUMP_CLASSES = {"sprp": sdk_2013.GAME_LUMP_CLASSES["sprp"].copy()}

methods = [*sdk_2013.methods]
