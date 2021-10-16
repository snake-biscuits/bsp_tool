# https://github.com/zturtleman/spearmint/blob/master/code/qcommon/bsp_fakk.c
import enum
from typing import List

from .. import base
from .. import shared
from ..id_software import quake3

FILE_MAGIC = b"FAKK"

BSP_VERSION = 12

GAME_PATHS = ["Heavy Metal: F.A.K.K. 2", "American McGee's Alice"]

GAME_VERSIONS = {"Heavy Metal: F.A.K.K. 2": 12, "American McGee's Alice": 42}


class LUMP(enum.Enum):
    SHADERS = 0
    PLANES = 1
    LIGHTMAPS = 2
    SURFACES = 3
    DRAW_VERTICES = 4
    DRAW_INDICES = 5
    LEAF_BRUSHES = 6
    LEAF_SURFACES = 7
    LEAVES = 8
    NODES = 9
    BRUSH_SIDES = 10
    BRUSHES = 11
    FOGS = 12
    MODELS = 13
    ENTITIES = 14
    VISIBILITY = 15
    LIGHT_GRID = 16
    ENTITY_LIGHTS = 17
    ENTITY_LIGHTS_VISIBILITY = 18
    LIGHT_DEFINITIONS = 19


# RitualBspHeader { char file_magic[4]; int version, checksum; QuakeLumpHeader headers[20]; };
lump_header_address = {LUMP_ID: (12 + i * 8) for i, LUMP_ID in enumerate(LUMP)}

# Known lump changes from Quake 3 -> Ubertools:
# New:
#   FACES -> SURFACES
#   LEAF_FACES -> LEAF_SURFACES
#   TEXTURES -> SHADERS
#   VERTICES -> DRAW_VERTICES
#   MESH_VERTICES -> DRAW_INDICES

# a rough map of the relationships between lumps:
#
#               /-> Shader
# Model -> Brush -> BrushSide
#      \-> Face -> MeshVertex
#             \--> Texture
#              \-> Vertex


# classes for lumps, in alphabetical order:
class Shader(base.Struct):  # LUMP 0
    name: str
    flags: List[int]
    subdivisions: int  # ??? new
    __slots__ = ["name", "flags", "subdivisions"]
    _format = "64s3i"
    _arrays = {"flags": ["surface", "contents"]}


class Surface(base.Struct):  # LUMP 3
    shader: int  # index into Shader lump
    fog: int  # index into Fog lump
    surface_type: int  # see SurfaceType enum
    first_vertex: int  # index into DrawVertex lump
    num_vertices: int  # number of DrawVertices after first_vertex in this face
    first_index: int  # index into DrawIndices lump
    num_indices: int  # number of DrawIndices after first_index in this face
    # lightmap.index: int  # which of the 3 lightmap textures to use
    # lightmap.top_left: List[int]  # approximate top-left corner of visible lightmap segment
    # lightmap.size: List[int]  # size of visible lightmap segment
    # lightmap.origin: List[float]  # world space lightmap origin
    # lightmap.vector: List[List[float]]  # lightmap texture projection vectors
    # NOTE: lightmap.vector is used for patches; first 2 indices are LoD bounds?
    normal: List[float]
    patch: List[float]  # for patches (displacement-like)
    subdivisions: float  # ??? new
    __slots__ = ["texture", "fog", "surface_type", "first_vertex", "num_vertices",
                 "first_index", "num_indices", "lightmap", "normal", "size", "subdivisions"]
    _format = "12i12f2if"
    _arrays = {"lightmap": {"index": None, "top_left": [*"xy"], "size": ["width", "height"],
                            "origin": [*"xyz"], "vector": {"s": [*"xyz"], "t": [*"xyz"]}},
               "normal": [*"xyz"], "patch": ["width", "height"]}


BASIC_LUMP_CLASSES = {"LEAF_BRUSHES": shared.Ints,
                      "LEAF_SURFACES":   shared.Ints,
                      "DRAW_INDICES": shared.Ints}

LUMP_CLASSES = {"BRUSH_SIDES":   quake3.BrushSide,
                "DRAW_VERTICES": quake3.Vertex,
                "LEAVES":        quake3.Leaf,
                "MODELS":        quake3.Model,
                "NODES":         quake3.Node,
                "PLANES":        quake3.Plane,
                "SHADERS":       Shader,
                "SURFACES":      Surface}

SPECIAL_LUMP_CLASSES = quake3.SPECIAL_LUMP_CLASSES.copy()

# branch exclusive methods, in alphabetical order:
methods = [shared.worldspawn_volume]
