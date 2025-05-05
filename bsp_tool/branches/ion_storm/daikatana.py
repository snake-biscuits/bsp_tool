# https://bitbucket.org/daikatana13/daikatana
# https://github.com/atsb/daikatana-restoration-project/blob/main/user/qfiles.h
import collections
import enum
from typing import Dict, List

from ... import core
from ...utils import vector
from .. import shared
from ..id_software import quake
from ..id_software import quake2


FILE_MAGIC = b"IBSP"

BSP_VERSION = 41

GAME_PATHS = {"Daikatana": "Daikatana"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    ENTITIES = 0
    PLANES = 1
    VERTICES = 2
    VISIBILITY = 3
    NODES = 4
    TEXTURE_INFO = 5
    FACES = 6
    LIGHTING = 7
    LEAVES = 8
    LEAF_FACES = 9
    LEAF_BRUSHES = 10
    EDGES = 11
    SURFEDGES = 12
    MODELS = 13
    BRUSHES = 14
    BRUSH_SIDES = 15
    POP = 16  # QuakeII/pak1 only (multiplayer / deathmatch?)
    AREAS = 17
    AREA_PORTALS = 18
    TEXTURE_INFO_COLOUR = 19
    PLANE_FACES = 20


LumpHeader = quake.LumpHeader

# known lump changes from Quake 2 -> Daikatana:
# new:
#   TEXTURE_INFO_COLOUR
#   PLANE_FACES

# A rough map of the relationships between lumps:
# PlaneFaces is parallel w/ Planes (kinda, off by one)
# TextureInfoColour is parallel w/ TextureInfo (appended to mtextureinfo_t)


# flag enums:
class Contents(enum.IntFlag):
    """https://github.com/atsb/daikatana-restoration-project/blob/main/user/qfiles.h"""
    SOLID = 0x00000001  # opaque & transparent
    WINDOW = 0x00000002
    AUX = 0x00000004
    LAVA = 0x00000008
    SLIME = 0x00000010
    WATER = 0x00000020
    MIST = 0x00000040
    CLEAR = 0x00000080
    NOT_SOLID = 0x00000100
    NO_SHOOT = 0x00000200
    FOG = 0x00000400
    NITRO = 0x00000800
    # non-visible "don't eat brushes"
    AREA_PORTAL = 0x00008000
    PLAYER_CLIP = 0x00010000
    MONSTER_CLIP = 0x00020000
    # bot hints
    CURRENT_0 = 0x00040000
    CURRENT_90 = 0x00080000
    CURRENT_180 = 0x00100000
    CURRENT_270 = 0x00200000
    CURRENT_UP = 0x00400000
    CURRENT_DOWN = 0x00800000
    # end bot hints
    ORIGIN = 0x01000000  # removed during compile
    MONSTER = 0x02000000
    DEAD_MONSTER = 0x04000000
    DETAIL = 0x08000000
    TRANSLUCENT = 0x10000000  # vis splitting brushes
    LADDER = 0x20000000
    NPC_CLIP = 0x40000000


# classes for lumps, in alphabetical order:
class Brush(quake2.Brush):  # LUMP 14
    _classes = {"contents": Contents}


class Leaf(core.Struct):  # LUMP 10
    contents: Contents  # bitwise OR of all brushes contents (not needed?)
    cluster: int  # index into VISIBILITY; -1 for always visible
    area: int
    bounds: List[int]
    first_leaf_face: int  # index into LeafFaces
    num_leaf_faces: int
    first_leaf_brush: int  # index into LeafBrushes
    num_leaf_brushes: int
    brush: int  # "brushnum"; rarely used
    __slots__ = ["contents", "cluster", "area", "bounds", "first_leaf_face",
                 "num_leaf_faces", "first_leaf_brush", "num_leaf_brushes", "brush"]
    _format = "Ih11Hi"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}
    _classes = {"contents": Contents, "bounds.mins": vector.vec3, "bounds.maxs": vector.vec3}


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = quake2.BASIC_LUMP_CLASSES.copy()
BASIC_LUMP_CLASSES.update({
    "PLANE_FACES": shared.Ints})

LUMP_CLASSES = quake2.LUMP_CLASSES.copy()
LUMP_CLASSES.update({
    "BRUSHES":             Brush,
    "TEXTURE_INFO_COLOUR": quake.Vertex,  # RGB floats (emissive textures only)
    "LEAVES":              Leaf})

SPECIAL_LUMP_CLASSES = quake2.SPECIAL_LUMP_CLASSES.copy()


def plane_faces(bsp) -> Dict[int, List[int]]:
    """base/ref_soft/r_model.cpp:Mod_LoadPlanePolys"""
    out = collections.defaultdict(list)
    cursor = 0
    for i, plane in enumerate(bsp.PLANES):
        num_faces = bsp.PLANE_FACES[cursor]
        cursor += 1
        if num_faces > 0:
            out[i] = bsp.PLANE_FACES[cursor:cursor+num_faces]
        cursor += num_faces
    assert cursor == len(bsp.PLANE_FACES)
    return out


methods = quake2.methods.copy()
methods.update({
    "plane_faces": plane_faces})
