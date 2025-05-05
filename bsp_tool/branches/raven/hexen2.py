# https://github.com/ericwa/ericw-tools/blob/master/include/common/bspfile.hh
import enum
from typing import List

from ... import core
from ...utils import vector
from ..id_software import quake


FILE_MAGIC = None

BSP_VERSION = 29

GAME_PATHS = {"Hexen II": "Hexen 2"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = quake.LUMP


LumpHeader = quake.LumpHeader


# A rough map of the relationships between lumps:

# ENTITIES -> MODELS -> NODES -> LEAVES -> LEAF_FACES -> FACES
#                   \-> CLIP_NODES -> PLANES

# VISIBILITY -> NODES -> LEAVES -> LEAF_FACES -> FACES
#                    \-> PLANES

#      /-> TEXTURE_INFO -> MIP_TEXTURES
# FACES -> SURFEDGES -> EDGES -> VERTICES
#     \--> LIGHTMAPS
#      \-> PLANES


# Engine limits:
class MAX(enum.Enum):
    ENTITIES = 1024
    PLANES = 32767
    MIP_LEVELS = 4  # affects MipTexture LumpClass
    MIP_TEXTURES = 512
    MIP_TEXTURES_SIZE = 0x200000  # in bytes
    VERTICES = 65535
    VISIBILITY_SIZE = 0x100000  # in bytes
    NODES = 32767  # "because negative shorts are contents"
    TEXTURE_INFO = 4096
    FACES = 65535
    LIGHTING_SIZE = 0x100000  # in bytes
    LIGHTMAPS = 4  # affects Face LumpClass
    CLIP_NODES = 32767
    LEAVES = 8192
    LEAF_FACES = 65535
    EDGES = 256000
    MODELS = 256
    BRUSHES = 4096  # for radiant / q2map ?
    ENTITY_KEY = 32
    ENTITY_STRING = 65536
    ENTITY_VALUE = 1024
    PORTALS = 65536  # related to leaves
    SURFEDGES = 512000
    MAP_HULLS = 8  # double Quake's limit; affects Model LumpClass


# classes for lumps, in alphabetical order:
class Model(core.Struct):  # LUMP 14
    bounds: List[List[float]]
    # bounds.mins: List[float]
    # bounds.maxs: List[float]
    origin: List[float]
    head_nodes: List[int]  # unsure of exact use
    # TODO: split up like Quake's Model nodes
    num_leaves: int
    first_leaf_face: int
    num_leaf_faces: int
    __slots__ = ["bounds", "origin", "head_nodes", "num_leaves", "first_face", "num_faces"]
    _format = "9f11i"
    _arrays = {
        "bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]},
        "origin": [*"xyz"], "head_nodes": 8}
    _classes = {
        "bounds.mins": vector.vec3, "bounds.maxs": vector.vec3,
        "origin": vector.vec3}


BASIC_LUMP_CLASSES = quake.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = quake.LUMP_CLASSES.copy()
LUMP_CLASSES.update({
    "MODELS": Model})

SPECIAL_LUMP_CLASSES = quake.SPECIAL_LUMP_CLASSES.copy()


methods = quake.methods.copy()
