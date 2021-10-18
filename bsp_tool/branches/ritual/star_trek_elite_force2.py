# ef2GameSource3/Shared/qcommon/qfiles.h
# https://github.com/zturtleman/spearmint/blob/master/code/qcommon/bsp_ef2.c
# TODO: finish copying implementation
import enum
from typing import List

from .. import base
from .. import shared
from . import fakk2


FILE_MAGIC = b"EF2!"

BSP_VERSION = 20

GAME_PATHS = ["Star Trek: Elite Force II"]

GAME_VERSIONS = {GAME: BSP_VERSION for GAME in GAME_PATHS}


class LUMP(enum.Enum):
    SHADERS = 0
    PLANES = 1
    LIGHTMAPS = 2
    BASE_LIGHTMAPS = 3
    CONT_LIGHTMAPS = 4
    SURFACES = 5
    DRAW_VERTICES = 6
    DRAW_INDICES = 7
    LEAF_BRUSHES = 8
    LEAF_SURFACES = 9
    LEAFS = 10
    NODES = 11
    BRUSH_SIDES = 12
    BRUSHES = 13
    FOGS = 14
    MODELS = 15
    ENTITIES = 16
    VISIBILITY = 17
    LIGHT_GRID = 18
    ENTITY_LIGHTS = 19
    ENTITY_LIGHTS_VISIBILITY = 20
    LIGHT_DEFINITIONS = 21
    BASE_LIGHTING_VERTICES = 22
    CONT_LIGHTING_VERTICES = 23
    BASE_LIGHTING_SURFACES = 24
    LIGHTING_SURFACES = 25
    LIGHTING_VERTEX_SURFACES = 26
    LIGHTING_GROUPS = 27
    STATIC_LOD_MODELS = 28
    BSP_INFO = 29


# RitualBspHeader { char file_magic[4]; int version, checksum; QuakeLumpHeader headers[20]; };
lump_header_address = {LUMP_ID: (12 + i * 8) for i, LUMP_ID in enumerate(LUMP)}


# classes for lumps, in alphabetical order:
class DrawVertex(base.Struct):  # LUMP 10
    position: List[float]
    # uv.texture: List[float]
    # uv.lightmap: List[float]
    normal: List[float]
    colour: bytes  # 1 RGBA32 pixel / texel
    lod_extra: float  # ???
    lightmap: List[float]  # union { float lightmap[2]; int collapse_map;}
    __slots__ = ["position", "uv", "normal", "colour", "lod_extra", "lightmap"]
    _format = "8f4B3f"
    _arrays = {"position": [*"xyz"], "uv": [*"uv"], "normal": [*"xyz"],
               "colour": [*"rgba"], "lightmap": [*"uv"]}


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
    base_lighting_surface: int  # index into BaseLightingSurface lump
    terrain: List[int]
    __slots__ = ["texture", "fog", "surface_type", "first_vertex", "num_vertices",
                 "first_index", "num_indices", "lightmap", "normal", "size",
                 "subdivisions", "base_lighting_surface", "terrain"]
    _format = "12i12f2if6i"
    _arrays = {"lightmap": {"index": None, "top_left": [*"xy"],
               "size": ["width", "height"], "origin": [*"xyz"],
               "vector": {"s": [*"xyz"], "t": [*"xyz"]}},
               "normal": [*"xyz"], "patch": ["width", "height"],
               "terrain": {"inverted": None, "face_flags": 4}}


BASIC_LUMP_CLASSES = fakk2.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = fakk2.LUMP_CLASSES.copy()
LUMP_CLASSES.update({"DRAW_VERTICES": DrawVertex,
                     "SURFACES":      Surface})

SPECIAL_LUMP_CLASSES = fakk2.SPECIAL_LUMP_CLASSES.copy()


methods = [shared.worldspawn_volume]
