# https://quakewiki.org/wiki/BSP2
# https://github.com/xonotic/darkplaces/blob/master/model_brush.c
from typing import List

from . import quake
from . import remake_quake_old


FILE_MAGIC = b"BSP2"

BSP_VERSION = None

GAME_PATHS = {
    "Alkaline": "Quake/alkaline",
    "Alkaline DevKit": "Quake/alkaline_dk",
    "Alkaline v1.1": "Quake/alk1.1",
    "Dimension of the Past": "Quake/rerelease/dopa"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = quake.LUMP

LumpHeader = quake.LumpHeader


# a rough map of the relationships between lumps:

# Entity -> Model -> Node -> Leaf -> LeafFace -> Face
#                \-> ClipNode -> Plane

#      /-> TextureInfo -> MipTextures -> MipTexture
# Face -> SurfEdge -> Edge -> Vertex
#     \--> Lightmap
#      \-> Plane


# TODO: engine limits:
# -- class MAX(enum.Enum):
# --     """https://quakewiki.org/wiki/Engine_Limits"""


# classes for lumps, in alphabetical order:
class Leaf(remake_quake_old.Leaf):  # LUMP 10
    bounds: List[List[float]]
    # bounds.mins: List[float]
    # bounds.maxs: List[float]
    _format = "2i6f2I4B"


class Node(remake_quake_old.Node):  # LUMP 5
    bounds: List[List[float]]
    # bounds.mins: List[float]
    # bounds.maxs: List[float]
    _format = "3i6f2I"


# {"LUMP": LumpClass}
BASIC_LUMP_CLASSES = remake_quake_old.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = remake_quake_old.LUMP_CLASSES.copy()
LUMP_CLASSES.update({
    "LEAVES": Leaf,
    "NODES":  Node})

SPECIAL_LUMP_CLASSES = remake_quake_old.SPECIAL_LUMP_CLASSES.copy()


methods = remake_quake_old.methods.copy()
