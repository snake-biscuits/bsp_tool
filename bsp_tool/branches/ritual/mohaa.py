# https://github.com/zturtleman/spearmint/blob/master/code/qcommon/bsp_mohaa.c
# https://github.com/openmoh/openmohaa/blob/master/code/bspc/q3files.h
# https://github.com/wfowler/LibBsp
# TODO: finish copying implementation
import enum

from ..id_software import quake
from . import mohaa_demo


FILE_MAGIC = b"2015"

BSP_VERSION = 19

GAME_PATHS = {"Medal of Honor: Allied Assault": "MoHAA/main",
              "Medal of Honor: Allied Assault - Spearhead": "MoHAA/mainta"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    TEXTURES = 0
    PLANES = 1
    LIGHTMAPS = 2
    FACES = 3
    VERTICES = 4
    INDICES = 5
    LEAF_BRUSHES = 6
    LEAF_FACES = 7
    LEAVES = 8
    NODES = 9
    SIDE_EQUATIONS = 10
    BRUSH_SIDES = 11
    BRUSHES = 12
    MODELS = 13
    ENTITIES = 14
    VISIBILITY = 15
    LIGHT_GRID_PALETTE = 16
    LIGHT_GRID_OFFSETS = 17
    LIGHT_GRID_DATA = 18
    SPHERE_LIGHTS = 19
    SPHERE_LIGHT_VIS = 20
    LIGHT_DEFINITIONS = 21
    TERRAIN = 22
    TERRAIN_INDICES = 23
    STATIC_MODEL_DATA = 24
    STATIC_MODEL_DEFINITIONS = 25
    STATIC_MODEL_INDICES = 26
    UNKNOWN_27 = 27


LumpHeader = quake.LumpHeader

# known lump changes from Allied Assault Demo -> Allied Assault:
# new:
#   VISIBILITY
# deprecated:
#   UNKNOWN_14

# a rough map of the relationships between lumps:

# Entity -> Model -> Node -> Leaf -> LeafFace -> Face
#                                \-> LeafBrush -> Brush

# Visibility -> Node -> Leaf -> LeafFace -> Face
#                   \-> Plane

#               /-> Texture  /-> Texture
# Model -> Brush -> BrushSide -> Plane
#      \-> Face              \-> Face
# NOTE: Brush's indexed Texture is just used for Contents flags

#     /-> Texture
# Face -> Index -> Vertex
#    \--> Vertex
#     \-> Effect


# {"LUMP_NAME": LumpClass}
BASIC_LUMP_CLASSES = mohaa_demo.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = mohaa_demo.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("UNKNOWN_14")

SPECIAL_LUMP_CLASSES = mohaa_demo.SPECIAL_LUMP_CLASSES.copy()

methods = mohaa_demo.methods.copy()
