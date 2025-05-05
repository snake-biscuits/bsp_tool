# https://github.com/Sporesirius/fakk2/blob/master/source/utils/common/qfiles.h
# https://github.com/zturtleman/spearmint/blob/master/code/qcommon/bsp_fakk.c
# https://github.com/zturtleman/bsp-sekai
import enum
from typing import List

from ... import core
from ...utils import vector
from .. import shared
from ..id_software import quake
from ..id_software import quake3

FILE_MAGIC = b"FAKK"

BSP_VERSION = 12

GAME_PATHS = {
    "Heavy Metal: F.A.K.K. 2": "FAKK2",
    "American McGee's Alice": "Alice"}

GAME_VERSIONS = {
    "Heavy Metal: F.A.K.K. 2": 12,
    "American McGee's Alice": 42}


class LUMP(enum.Enum):
    TEXTURES = 0  # SHADERS
    PLANES = 1
    LIGHTMAPS = 2
    FACES = 3  # SURFACES
    VERTICES = 4  # DRAWVERTICES
    INDICES = 5  # DRAWINDICES
    LEAF_BRUSHES = 6
    LEAF_FACES = 7  # LEAFSURFACES
    LEAVES = 8
    NODES = 9
    BRUSH_SIDES = 10
    BRUSHES = 11
    EFFECTS = 12  # FOGS
    MODELS = 13
    ENTITIES = 14
    VISIBILITY = 15
    LIGHT_GRID = 16  # LIGHTGRID
    ENTITY_LIGHTS = 17  # ENTLIGHTS
    ENTITY_LIGHTS_VISIBILITY = 18  # ENTLIGHTSVIS
    LIGHT_DEFINITIONS = 19  # LIGHTDEFS


LumpHeader = quake.LumpHeader


# known lump changes from Quake 3 -> F.A.K.K. 2:
# new:
#   ENTITY_LIGHTS
#   ENTITY_LIGHTS_VISIBILITY
#   LIGHT_DEFINITIONS


# a rough map of the relationships between lumps:
#
#               /-> Shader
# Model -> Brush -> BrushSide
#      \-> Face -> MeshVertex
#             \--> Texture
#              \-> Vertex


# classes for lumps, in alphabetical order:
class Face(core.Struct):  # LUMP 3
    texture: int  # index into Texture lump
    effect: int  # index into Effect lump
    type: quake3.FaceType
    first_vertex: int  # index into Vertex lump
    num_vertices: int  # number of Vertices after first_vertex in this face
    first_index: int  # index into Indices lump
    num_indices: int  # number of Indices after first_index in this face
    # lightmap.index: int  # which of the 3 lightmap textures to use
    # lightmap.top_left: List[int]  # approximate top-left corner of visible lightmap segment
    # lightmap.size: List[int]  # size of visible lightmap segment
    # lightmap.origin: vector.vec3  # world space lightmap origin
    # lightmap.vector: List[vector.vec3]  # lightmap texture projection vectors
    # NOTE: lightmap.vector is used for patches; first 2 indices are LoD bounds?
    normal: vector.vec3
    patch: List[float]  # control point dimentions?
    subdivisions: float  # patch subdivisions? dynamic lod?
    __slots__ = [
        "texture", "effect", "type", "first_vertex", "num_vertices",
        "first_index", "num_indices", "lightmap", "normal", "patch", "subdivisions"]
    _format = "12i12f2if"
    _arrays = {
        "lightmap": {
            "index": None, "top_left": [*"xy"], "size": [*"xy"],
            "origin": [*"xyz"], "vector": {"s": [*"xyz"], "t": [*"xyz"]}},
        "normal": [*"xyz"], "patch": [*"xy"]}
    _classes = {
        "type": quake3.FaceType, "lightmap.top_left": vector.vec2,
        "lightmap.size": vector.vec2, "lightmap.origin": vector.vec3,
        "lightmap.vector.s": vector.vec3, "lightmap.vector.t": vector.vec3,
        "normal": vector.vec3,
        "patch": vector.vec2}
    # TODO: vector.ivec2 where appropriate


class Texture(core.Struct):  # LUMP 0
    name: str
    flags: List[int]
    subdivisions: int  # new; for patches?
    __slots__ = ["name", "flags", "subdivisions"]
    _format = "64s3i"
    _arrays = {"flags": ["surface", "contents"]}
    _classes = {"flags.surface": quake3.Surface, "flags.contents": quake3.Contents}


# {"LUMP_NAME": LumpClass}
BASIC_LUMP_CLASSES = {
    "LEAF_BRUSHES": shared.Ints,
    "LEAF_FACES":   shared.Ints,
    "INDICES":      shared.Ints}

LUMP_CLASSES = {
    "BRUSH_SIDES": quake3.BrushSide,
    "VERTICES":    quake3.Vertex,
    "FACES":       Face,
    "LEAVES":      quake3.Leaf,
    "MODELS":      quake3.Model,
    "NODES":       quake3.Node,
    "PLANES":      quake3.Plane,
    "TEXTURES":    Texture}

SPECIAL_LUMP_CLASSES = quake3.SPECIAL_LUMP_CLASSES.copy()


# branch exclusive methods, in alphabetical order:


methods = [quake.leaves_of_node, shared.worldspawn_volume]
methods = {method.__name__: method for method in methods}
