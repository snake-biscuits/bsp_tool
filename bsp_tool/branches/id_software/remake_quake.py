# https://ericwa.github.io/ericw-tools/doc/qbsp.html
# https://github.com/ericwa/ericw-tools
# https://quakewiki.org/wiki/BSP2
# https://github.com/xonotic/darkplaces/blob/master/model_brush.c
# NOTE: FAILING; built from deprectaed 2PSB spec, do not have samples to test
from typing import List

from .. import base
from . import quake


FILE_MAGIC = b"BSP2"

BSP_VERSION = None

GAME_PATHS = {"Alkaline": "Quake/alk1",
              "Darkplaces": "Darkplaces",
              # Nexuiz?
              "Quake Re-release": "Quake/rerelease"}  # Dimension of the Past

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = quake.LUMP

LumpHeader = quake.LumpHeader


# A rough map of the relationships between lumps:

# ENTITIES -> MODELS -> NODES -> LEAVES -> LEAF_FACES -> FACES
#                   \-> CLIP_NODES -> PLANES

#      /-> TEXTURE_INFO -> MIP_TEXTURES
# FACES -> SURFEDGES -> EDGES -> VERTICES
#     \--> LIGHTMAPS
#      \-> PLANES


# TODO: MAXS


# classes for lumps, in alphabetical order:
class ClipNode(base.Struct):  # LUMP 9
    plane: int  # index of the Plane that splits this ClipNode
    children: List[int]
    __slots__ = ["plane", "children"]
    _format = "3i"
    _arrays = {"children": ["front", "back"]}


class Edge(list):  # LUMP 12
    _format = "2I"  # List[int]

    def flat(self):
        return self  # HACK

    @classmethod
    def from_tuple(cls, _tuple):
        return cls(_tuple)


class Face(base.Struct):  # LUMP 7
    plane: int
    side: int  # 0 or 1 for side of plane
    first_edge: int
    num_edges: int
    texture_info: int  # index of this face's TextureInfo
    lighting_type: int  # 0x00=lightmap, 0xFF=no-lightmap, 0x01=fast-pulse, 0x02=slow-pulse, 0x03-0x10 other
    base_light: int  # 0x00 bright - 0xFF dark (lowest possible light level)
    light: int
    lightmap: int  # index into lightmap lump, or -1
    __slots__ = ["plane", "side", "first_edge", "num_edges", "texture_info",
                 "lighting_type", "base_light", "light", "lightmap"]
    _format = "5i4Bi"
    _arrays = {"light": 2}


class Leaf(base.Struct):  # LUMP 10
    leaf_type: int  # see LeafType enum
    cluster: int  # index into the VISIBILITY lump
    bounds: List[int]
    first_leaf_face: int  # MarkSurface?
    num_leaf_faces: int
    sound: List[int]  # ambient master of all 4 elements (0x00 - 0xFF)
    __slots__ = ["leaf_type", "cluster", "bounds", "first_leaf_face",
                 "num_leaf_faces", "sound"]
    _format = "2i6h2I4B"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]},
               "sound": ["water", "sky", "slime", "lava"]}


class Node(base.Struct):  # LUMP 5
    plane: int  # index of the Plane that splits this Node
    children: List[int]  # indices of child Nodes either side of plane
    bounds: List[List[int]]
    # bounds.mins: List[int]
    # bounds.maxs: List[int]
    first_face: int  # index of the first Face in this Node
    num_faces: int  # number of Faces after first_face in this Node (counts both sides)
    __slots__ = ["plane"]
    _format = "3i6h2I"
    _arrays = {"children": ["front", "back"], "bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}


# {"LUMP": LumpClass}
BASIC_LUMP_CLASSES = quake.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = quake.LUMP_CLASSES.copy()
LUMP_CLASSES.update({"CLIP_NODES": ClipNode,
                     "EDGES":      Edge,
                     "FACES":      Face,
                     "LEAVES":     Leaf,
                     "NODES":      Node})

SPECIAL_LUMP_CLASSES = quake.SPECIAL_LUMP_CLASSES.copy()


methods = [*quake.methods]
