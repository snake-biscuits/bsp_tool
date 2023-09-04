# ef2GameSource3/Shared/qcommon/qfiles.h
# https://github.com/zturtleman/spearmint/blob/master/code/qcommon/bsp_ef2.c
# TODO: finish copying implementation
import enum

from ..id_software import quake
from . import star_trek_elite_force2_demo


FILE_MAGIC = b"EF2!"

BSP_VERSION = 20

GAME_PATHS = {"Star Trek: Elite Force II": "StarTrekEliteForceII"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    TEXTURES = 0
    PLANES = 1
    LIGHTMAPS = 2
    BASE_LIGHTMAPS = 3
    CONT_LIGHTMAPS = 4
    FACES = 5
    VERTICES = 6
    INDICES = 7
    LEAF_BRUSHES = 8
    LEAF_FACES = 9
    LEAVES = 10
    NODES = 11
    BRUSH_SIDES = 12
    BRUSHES = 13
    EFFECTS = 14  # EFFECTS
    MODELS = 15
    ENTITIES = 16
    VISIBILITY = 17
    LIGHT_GRID = 18
    ENTITY_LIGHTS = 19
    ENTITY_LIGHTS_VISIBILITY = 20
    LIGHT_DEFINITIONS = 21
    BASE_LIGHTING_VERTICES = 22
    CONT_LIGHTING_VERTICES = 23
    BASE_LIGHTING_FACES = 24
    LIGHTING_FACES = 25
    LIGHTING_VERTEX_FACES = 26
    LIGHTING_GROUPS = 27
    STATIC_LOD_MODELS = 28
    BSP_INFO = 29
    # TODO: what is CONT short for?


LumpHeader = quake.LumpHeader


# known lump changes from Star Trek: Elite Force 2 Demo -> Star Trek: Elite Force 2:
# nothing yet

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


# {"LUMP": LumpClass}
BASIC_LUMP_CLASSES = star_trek_elite_force2_demo.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = star_trek_elite_force2_demo.LUMP_CLASSES.copy()

SPECIAL_LUMP_CLASSES = star_trek_elite_force2_demo.SPECIAL_LUMP_CLASSES.copy()


methods = star_trek_elite_force2_demo.methods.copy()
