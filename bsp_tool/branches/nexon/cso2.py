"""2013-2017 format"""
# https://git.sr.ht/~leite/cso2-bsp-converter/tree/master/item/src/bsptypes.hpp
import enum
from typing import List, Tuple

from ... import core
from ...archives import nexon
from ...utils import vector
from .. import shared
from ..valve import source
from . import vindictus


FILE_MAGIC = b"VBSP"

BSP_VERSION = 100

GAME_PATHS = {
    "Counter-Strike: Online 2": "CSO2"}

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
    FACE_MACRO_TEXTURE_INFO = 47
    DISPLACEMENT_TRIANGLES = 48
    PHYSICS_COLLIDE_SURFACE = 49
    WATER_OVERLAYS = 50
    LEAF_AMBIENT_INDEX_HDR = 51
    LEAF_AMBIENT_INDEX = 52
    LIGHTING_HDR = 53  # version 1
    WORLD_LIGHTS_HDR = 54
    LEAF_AMBIENT_LIGHTING_HDR = 55  # version 1
    LEAF_AMBIENT_LIGHTING = 56  # version 1
    XZIP_PAKFILE = 57
    FACES_HDR = 58  # version 1
    MAP_FLAGS = 59
    OVERLAY_FADES = 60
    UNKNOWN_61 = 61  # version 1; related to cubemaps?
    UNUSED_62 = 62
    UNUSED_63 = 63


class LumpHeader(core.MappedArray):
    offset: int  # index in .bsp file where lump begins
    length: int
    version: int
    compressed: int  # 2 byte bool?
    fourCC: int  # uncompressed size; big-endian for some reason
    _mapping = ["offset", "length", "version", "compressed", "fourCC"]
    _format = "2I2HI"


# classes for each lump, in alphabetical order:
class BrushSide(core.Struct):  # LUMP 19
    plane: int  # index into Planes
    texture_info: int  # index into TextureInfo
    displacement_info: int  # index into DisplacementInfo; -1 if None
    bevel: int  # bool? indicates if side is a bevel plane (BSPVERSION 7)
    __slots__ = ["plane", "texture_info", "displacement_info", "bevel"]
    _format = "Ii2h"


class Face(core.Struct):  # LUMP 7, 27 & 58
    plane: int  # index into Planes
    side: int  # always 1 or 0? bool?
    on_node: int  # always 0? bool?
    padding_1: int  # alignment mistake?
    first_edge: int  # index into the SurfEdges
    num_edges: int
    texture_info: int  # index into TextureInfo
    displacement_info: int  # index into DisplacementInfo; -1 if None
    padding_2: int
    surface_fog_volume_id: int  # for water surfaces?
    styles: List[int]  # -1 for None
    light_offset: int  # index into Lighting
    area: float
    lightmap: List[vector.vec2]
    # lightmap.mins: vector.vec2  # dimensions of lightmap segment
    # lightmap.size: vector.vec2  # scalars for lightmap segment
    original_face: int  # index into OriginalFaces; -1 if OriginalFace
    primitives: Tuple[int, bool]
    # primitives.allow_dynamic_shadows: bool
    # primitives.count: int  # limit of 2^31 - 1
    first_primitive: int  # index of Primitive (if primitives.count != 0)
    smoothing_groups: int  # lightmap smoothing group
    __slots__ = [
        "plane", "side", "on_node", "padding_1", "first_edge", "num_edges",
        "texture_info", "displacement_info", "padding_2", "surface_fog_volume_id",
        "styles", "light_offset", "area", "lightmap", "original_face",
        "primitives", "first_primitive", "smoothing_groups"]
    _format = "I2BH3I2hi4bif5i3I"
    _arrays = {"styles": 4, "lightmap": {"mins": [*"xy"], "size": [*"xy"]}}
    _bitfields = {"primitives": {"allow_dynamic_shadows": 1, "count": 31}}
    # TODO: ivec2 for lightmap vectors
    _classes = {"lightmap.mins": vector.vec2, "lightmap.size": vector.vec2}


class Primitive(core.Struct):  # LUMP 37
    type: source.PrimitiveType
    first_index: int  # index into PrimitiveIndices
    num_indices: int
    first_vertex: int  # index into PrimitiveVertices
    num_vertices: int
    __slots__ = ["type", "first_index", "num_indices", "first_vertex", "num_vertices"]
    _format = "5I"
    _classes = {"type": source.PrimitiveType}


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = vindictus.BASIC_LUMP_CLASSES.copy()
BASIC_LUMP_CLASSES.update({
    "PRIMITIVE_INDICES":         {0: shared.UnsignedInts},
    "TEXTURE_DATA_STRING_TABLE": {0: shared.UnsignedInts}})

LUMP_CLASSES = vindictus.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("CUBEMAPS")
LUMP_CLASSES.pop("LEAVES")
LUMP_CLASSES.pop("OVERLAYS")
# LUMP_CLASSES.pop("TEXTURE_INFO")  # organnerx maps: source.TextureInfo
LUMP_CLASSES.pop("WORLD_LIGHTS")
LUMP_CLASSES.pop("WORLD_LIGHTS_HDR")
LUMP_CLASSES.update({
    "BRUSH_SIDES":       {0: BrushSide},
    "DISPLACEMENT_INFO": {0: source.DisplacementInfo},
    "FACES":             {1: Face},
    "FACES_HDR":         {1: Face},
    "ORIGINAL_FACES":    {0: Face},
    "PRIMITIVES":        {0: Primitive}})

SPECIAL_LUMP_CLASSES = vindictus.SPECIAL_LUMP_CLASSES.copy()
SPECIAL_LUMP_CLASSES.update({
    "PAKFILE": {0: nexon.PakFile}})

GAME_LUMP_HEADER = source.GameLumpHeader

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = dict()


methods = vindictus.methods.copy()
