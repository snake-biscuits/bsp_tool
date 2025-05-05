# ef2GameSource3/Shared/qcommon/qfiles.h
# https://github.com/zturtleman/spearmint/blob/master/code/qcommon/bsp_ef2.c
# TODO: finish copying implementation
import enum
from typing import List

from ... import core
from ...utils import vector
from .. import colour
from ..id_software import quake
from ..id_software import quake3
from . import fakk2


FILE_MAGIC = b"FAKK"

BSP_VERSION = 19

GAME_PATHS = {
    "Star Trek Elite Force II Single Player Demo": "StarTrekEliteForceIIDemo"}

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


# Known lump changes from F.A.K.K. 2 -> Star Trek: Elite Force 2 Demo:
# New:
#   BASE_LIGHTMAPS
#   CONT_LIGHTMAPS
#   BASE_LIGHTING_VERTICES
#   CONT_LIGHTING_VERTICES
#   BASE_LIGHTING_FACES
#   LIGHTING_FACES
#   LIGHTING_VERTEX_FACES
#   LIGHTING_GROUPS
#   STATIC_LOD_MODELS
#   BSP_INFO


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


# classes for lumps, in alphabetical order:
class Face(core.Struct):  # LUMP 3
    texture: int  # index into Texture lump
    effect: int  # index into Effect lump; -1 for None?
    type: int  # see quake3.FaceType enum
    first_vertex: int  # index into Vertex lump
    num_vertices: int  # number of Vertices after first_vertex in this face
    first_index: int  # index into DrawIndices lump
    num_indices: int  # number of DrawIndices after first_index in this face
    # lightmap.index: int  # which of the 3 lightmap textures to use
    # lightmap.top_left: List[int]  # approximate top-left corner of visible lightmap segment
    # lightmap.size: List[int]  # size of visible lightmap segment
    # lightmap.origin: List[float]  # world space lightmap origin
    # lightmap.vector: List[List[float]]  # lightmap texture projection vectors
    # NOTE: lightmap.vector is used for patches; first 2 indices are LoD bounds?
    normal: vector.vec3
    patch: List[float]  # for patches (displacement-like)
    subdivisions: float  # ??? new
    base_lighting_face: int  # index into BaseLightingFace lump
    terrain: List[int]
    __slots__ = ["texture", "effect", "type", "first_vertex", "num_vertices",
                 "first_index", "num_indices", "lightmap", "normal", "patch",
                 "subdivisions", "base_lighting_face", "terrain"]
    _format = "12i12f2if6i"
    _arrays = {
        "lightmap": {
            "index": None,
            "top_left": [*"xy"],
            "size": [*"xy"],
            "origin": [*"xyz"],
            "vector": {"s": [*"xyz"], "t": [*"xyz"]}},
        "normal": [*"xyz"],
        "patch": [*"xy"],
        "terrain": {"inverted": None, "face_flags": 4}}
    _classes = {
        "type": quake3.FaceType,
        "lightmap.top_left": vector.vec2,
        "lightmap.size": vector.vec2,
        "lightmap.origin": vector.vec3,
        "lightmap.vector.s": vector.vec3,
        "lightmap.vector.t": vector.vec3,
        "normal": vector.vec3,
        "patch": vector.vec2}


class Vertex(core.Struct):  # LUMP 10
    position: vector.vec3
    uv: List[float]  # texture UV
    normal: vector.vec3
    colour: colour.RGBA32
    lod_extra: float  # ???
    lightmap: List[float]  # union { float lightmap[2]; int collapse_map;}
    __slots__ = ["position", "uv", "normal", "colour", "lod_extra", "lightmap"]
    _format = "8f4B3f"
    _arrays = {"position": [*"xyz"], "uv": [*"uv"], "normal": [*"xyz"],
               "colour": [*"rgba"], "lightmap": [*"uv"]}
    _classes = {"position": vector.vec3, "normal": vector.vec3, "colour": colour.RGBA32}
    # TODO: "uv": vec2.uv, "lightmap": vec2.uv


# {"LUMP": LumpClass}
BASIC_LUMP_CLASSES = fakk2.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = fakk2.LUMP_CLASSES.copy()
LUMP_CLASSES.update({
    "VERTICES": Vertex,
    "FACES":    Face})

SPECIAL_LUMP_CLASSES = fakk2.SPECIAL_LUMP_CLASSES.copy()


methods = fakk2.methods.copy()
