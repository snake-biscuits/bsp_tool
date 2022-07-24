# https://github.com/zturtleman/spearmint/blob/master/code/qcommon/bsp_mohaa.c
# https://github.com/openmoh/openmohaa/blob/master/code/bspc/q3files.h
# https://github.com/wfowler/LibBsp
# TODO: finish copying implementation
import enum
from typing import List

from .. import base
from .. import shared
from ..id_software import quake
from . import fakk2


FILE_MAGIC = b"2015"

BSP_VERSION = 18

GAME_PATHS = {"Medal of Honor: Allied Assault (Demo)": "MoHAA/demo"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


# NOTE: these are assumptions built on the mapped MoH:AA release
# TODO: confirm against lump loads in MOHAADemo.exe (search for CM_LoadMap string to get started)
class LUMP(enum.Enum):
    SHADERS = 0
    PLANES = 1
    LIGHTMAPS = 2
    SURFACES = 3
    DRAW_VERTICES = 4
    DRAW_INDICES = 5
    LEAF_BRUSHES = 6
    LEAF_SURFACES = 7
    LEAVES = 8  # has 2 versions based on BSP_VERSION
    NODES = 9
    SIDE_EQUATIONS = 10
    BRUSH_SIDES = 11
    BRUSHES = 12
    MODELS = 13
    UNKNOWN_14 = 14  # not FOGS or VISIBILITY
    ENTITIES = 15
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


# Known changes from Ubertools -> Allied Assault Demo:
# New:
#   SIDE_EQUATIONS
#   LIGHT_GRID_PALETTE
#   LIGHT_GRID_OFFSETS
#   LIGHT_GRID -> LIGHT_GRID_DATA?
#   ENT_LIGHTS -> SPHERE_LIGHTS
#   ENT_LIGHTS_VIS -> SPHERE_LIGHTS_VIS
#   TERRAIN
#   TERRAIN_INDICES
#   STATIC_MODEL_DATA
#   STATIC_MODEL_DEFINITIONS
#   STATIC_MODEL_INDICES
#   UNKNOWN_27

# a rough map of the relationships between lumps:
#
#               /-> Shader
# Model -> Brush -> BrushSide
#      \-> Face -> MeshVertex
#             \--> Texture
#              \-> Vertex


# classes for lumps, in alphabetical order:
class BrushSide(base.MappedArray):
    plane: int  # index into Plane lump
    shader: int  # index into Shader lump
    equation: int  # index into SideEquation lump
    _mapping = ["plane", "shader", "equation"]
    _format = "3i"


class Leaf(base.Struct):  # LUMP 4
    cluster: int  # index into VisData
    area: int
    mins: List[float]  # Bounding box
    maxs: List[float]
    first_leaf_face: int  # index into LeafFace lump
    num_leaf_faces: int  # number of LeafFaces in this Leaf
    first_leaf_brush: int  # index into LeafBrush lump
    num_leaf_brushes: int  # number of LeafBrushes in this Leaf
    padding: List[int]
    first_static_model: int  # index into StaticModel lump
    num_static_models: int  # number of StaticModels in this Leaf
    __slots__ = ["cluster", "area", "mins", "maxs", "first_leaf_face",
                 "num_leaf_faces", "first_leaf_brush", "num_leaf_brushes",
                 "padding", "first_static_model", "num_static_models"]  # new
    _format = "16i"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"], "padding": 2}


class Shader(base.Struct):  # LUMP 0
    name: str
    flags: List[int]
    subdivisions: int
    fence_mask: str  # new
    __slots__ = ["name", "flags", "subdivisions", "fence_mask"]
    _format = "64s3i64s"
    _arrays = {"flags": ["surface", "contents"]}


class Unknown14(base.Struct):  # LUMP 14
    """reminds me of respawn.titanfall2.ShadowEnvironment"""
    mins: List[float]
    maxs: List[float]
    first_unknown_1: int
    num_unknown_1: int
    first_unknown_2: int
    num_unknown_2: int
    __slots__ = ["mins", "maxs", "first_unknown_1", "num_unknown_1",
                 "first_unknown_2", "num_unknown_2"]
    _format = "6f4i"
    _arrays = {"min": [*"xyz"], "max": [*"xyz"]}


# {"LUMP_NAME": LumpClass}
BASIC_LUMP_CLASSES = fakk2.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = fakk2.LUMP_CLASSES.copy()
LUMP_CLASSES.update({"BRUSH_SIDES": BrushSide,
                     "LEAVES":      Leaf,
                     "SHADERS":     Shader,
                     "UNKNOWN_14":  Unknown14})

SPECIAL_LUMP_CLASSES = fakk2.SPECIAL_LUMP_CLASSES.copy()

methods = [shared.worldspawn_volume]
