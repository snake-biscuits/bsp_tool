# https://github.com/qbism/q2tools-220/blob/master/src/qfiles.h
import enum
from typing import List

from . import quake
from . import quake2
from . import remake_quake
from . import remake_quake_old


FILE_MAGIC = b"QBSP"

BSP_VERSION = 38

GAME_PATHS = {
    "Quake II Re-release": "Quake 2/rerelease"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = quake2.LUMP


LumpHeader = quake.LumpHeader


# engine limits:
class MAX(enum.Enum):
    # lumps
    BRUSHES = 1048576
    BRUSHSIDES = 4194304
    EDGES = 1048576
    ENTITIES = 131072  # warn at 32768
    ENTSTRING = 13631488
    FACES = 1048576
    LEAFBRUSHES = 1048576
    LEAFFACES = 1048576
    LEAFS = 1048576
    MODELS = 131072  # warn at 32768
    NODES = 1048576
    PLANES = 1048576
    PORTALS = 1048576
    SURFEDGES = 4194304
    TEXINFO = 1048576
    VERTS = 4194304
    LIGHTING_SIZE = 0x3400000  # bytesize
    VISIBILITY_SIZE = 0x8000000  # bytesize
    # other
    ENTITY_KEY = 32
    ENTITY_VALUE = 1024
    MAP_SIZE = 32768  # +/- bounds


# classes for lumps, in alphabetical order:
class BrushSide(quake2.BrushSide):
    _format = "Ii"


class Leaf(quake2.Leaf):
    # int16_t -> int32_t
    # int16_t bounds -> float bounds
    bounds: List[List[float]]
    _format = "3i6f4I"


# {"LUMP": LumpClass}
BASIC_LUMP_CLASSES = quake2.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = quake2.LUMP_CLASSES.copy()
LUMP_CLASSES.update({
    "BRUSH_SIDES": BrushSide,
    "EDGES": remake_quake_old.Edge,
    "FACES": remake_quake_old.Face,
    "LEAVES": Leaf,
    "NODES": remake_quake.Node})

SPECIAL_LUMP_CLASSES = quake2.SPECIAL_LUMP_CLASSES.copy()


methods = quake2.methods.copy()
