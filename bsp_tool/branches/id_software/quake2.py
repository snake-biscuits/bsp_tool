# https://www.flipcode.com/archives/Quake_2_BSP_File_Format.shtml
# https://github.com/id-Software/Quake-2/blob/master/qcommon/qfiles.h#L214
import enum
from typing import List

from . import quake
from .. import base
from .. import shared


FILE_MAGIC = b"IBSP"

BSP_VERSION = 38

GAME_PATHS = ["Anachronox", "Quake II", "Heretic II"]

GAME_VERSIONS = {GAME_PATH: BSP_VERSION for GAME_PATH in GAME_PATHS}


class LUMP(enum.Enum):
    ENTITIES = 0
    PLANES = 1
    VERTICES = 2
    VISIBILITY = 3
    NODES = 4
    TEXTURE_INFO = 5
    FACES = 6
    LIGHTMAPS = 7
    LEAVES = 8
    LEAF_FACES = 9
    LEAF_BRUSHES = 10
    EDGES = 11
    SURFEDGES = 12
    MODELS = 13
    BRUSHES = 14
    BRUSH_SIDES = 15
    POP = 16  # ?
    AREAS = 17
    AREA_PORTALS = 18


# struct Quake2BspHeader { char file_magic[4]; int version; QuakeLumpHeader headers[19]; };
lump_header_address = {LUMP_ID: (8 + i * 8) for i, LUMP_ID in enumerate(LUMP)}

# TODO: MAX & Contents enums

# A rough map of the relationships between lumps:
# ENTITIES -> MODELS -> NODES -> LEAVES -> LEAF_FACES -> FACES
#                                      \-> LEAF_BRUSHES

# FACES -> SURFEDGES -> EDGES -> VERTICES
#    \--> TEXTURE_INFO -> MIP_TEXTURES
#     \--> LIGHTMAPS
#      \-> PLANES

# LEAF_FACES -> FACES
# LEAF_BRUSHES -> BRUSHES


# classes for lumps, in alphabetical order:
class Brush(base.MappedArray):  # LUMP 14
    first_side: int
    num_sides: int
    contents: int
    _mapping = ["first_side", "num_sides", "contents"]
    _format = "3i"


class BrushSide(base.MappedArray):  # LUMP 15
    plane: int
    texture_info: int
    _format = "Hh"


class Leaf(base.Struct):  # LUMP 10
    type: int  # see LeafType enum
    cluster: int  # index into the VISIBILITY lump
    area: int
    bounds: List[int]
    first_leaf_face: int  # index to this Leaf's first LeafFace
    num_leaf_faces: int  # the number of LeafFaces after first_face in this Leaf
    first_leaf_brush: int  # index to this Leaf's first LeafBrush
    num_leaf_brushes: int  # the number of LeafBrushes after first_brush in this Leaf
    __slots__ = ["type", "cluster", "area", "bounds", "first_leaf_face",
                 "num_leaf_faces", "first_leaf_brush", "num_leaf_brushes"]
    _format = "I12H"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}


class Model(base.Struct):  # LUMP 13
    bounds: List[float]  # mins & maxs
    origin: List[float]
    first_node: int  # first node in NODES lumps
    first_face: int
    num_faces: int
    __slots__ = ["bounds", "origin", "first_node", "first_face", "num_faces"]
    _format = "9f3i"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}, "origin": [*"xyz"]}


class Node(base.Struct):  # LUMP 4
    plane_index: int
    children: List[int]  # +ve Node, -ve Leaf
    # NOTE: -1 (leaf 0) is a dummy leaf & terminates tree searches
    bounds: List[int]
    # NOTE: bounds are generous, rounding up to the nearest 16 units
    first_face: int
    num_faces: int
    _format = "I2i8h"
    _arrays = {"children": ["front", "back"],
               "bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}


class TextureInfo(base.Struct):  # LUMP 5
    U: List[float]
    V: List[float]
    flags: int  # "miptex flags & overrides"
    value: int  # "light emission etc."
    name: bytes  # texture name
    next: int  # index into TextureInfo lump for animations (-1 = last frame)
    __slots__ = ["U", "V", "flags", "value", "name", "next"]
    _format = "8f2I32sI"
    _arrays = {"U": [*"xyzw"], "V": [*"xyzw"]}


# {"LUMP": LumpClass}
BASIC_LUMP_CLASSES = {"LEAF_FACES": shared.Shorts,
                      "SURFEDGES":  shared.Ints}

LUMP_CLASSES = {"BRUSHES":      Brush,
                "BRUSH_SIDES":  BrushSide,
                "EDGES":        quake.Edge,
                "FACES":        quake.Face,
                "LEAVES":       Leaf,
                "MODELS":       Model,
                "NODES":        Node,
                "PLANES":       quake.Plane,
                "TEXTURE_INFO": TextureInfo,
                "VERTICES":     quake.Vertex}

SPECIAL_LUMP_CLASSES = {"ENTITIES": shared.Entities}
# TODO: Visibility


methods = [shared.worldspawn_volume]
