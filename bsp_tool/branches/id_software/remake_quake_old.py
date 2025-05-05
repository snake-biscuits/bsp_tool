# superceded by remake_quake; but still supported by some compile tools
# https://quakewiki.org/wiki/BSP2
# https://github.com/xonotic/darkplaces/blob/master/model_brush.c
from typing import List

from . import quake


FILE_MAGIC = b"2PSB"

BSP_VERSION = None

GAME_PATHS = {"DEPRECATED": ""}  # No known mods use this format

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
# -- https://quakewiki.org/wiki/Engine_Limits


# classes for lumps, in alphabetical order:
class ClipNode(quake.ClipNode):  # LUMP 9
    _format = "3i"


class Edge(quake.Edge):  # LUMP 12
    _format = "2I"  # List[int]


class Face(quake.Face):  # LUMP 7
    _format = "I4i4Bi"


class Leaf(quake.Leaf):  # LUMP 10
    bounds: List[List[int]]
    # bounds.mins: List[int]
    # bounds.maxs: List[int]
    _format = "2i6h2I4B"


class Node(quake.Node):  # LUMP 5
    bounds: List[List[int]]
    # bounds.mins: List[int]
    # bounds.maxs: List[int]
    _format = "3i6h2I"


# {"LUMP": LumpClass}
BASIC_LUMP_CLASSES = quake.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = quake.LUMP_CLASSES.copy()
LUMP_CLASSES.update({
    "CLIP_NODES": ClipNode,
    "EDGES":      Edge,
    "FACES":      Face,
    "LEAVES":     Leaf,
    "NODES":      Node})

SPECIAL_LUMP_CLASSES = quake.SPECIAL_LUMP_CLASSES.copy()


methods = quake.methods.copy()
