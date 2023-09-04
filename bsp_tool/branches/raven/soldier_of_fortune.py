# https://www.mobygames.com/game/1331/soldier-of-fortune/releases/#dreamcast
import enum

from ..id_software import quake
from ..id_software import quake2


FILE_MAGIC = b"IBSP"

BSP_VERSION = 46

GAME_PATHS = {"Soldier of Fortune": "SoF",
              "Soldier of Fortune (Dreamcast)": "Dreamcast/SoF"}

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
    UNKNOWN_19 = 19
    UNKNOWN_20 = 20
    UNKNOWN_21 = 21


LumpHeader = quake.LumpHeader


BASIC_LUMP_CLASSES = quake2.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = quake2.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("FACES")
LUMP_CLASSES.pop("LEAVES")

SPECIAL_LUMP_CLASSES = quake2.SPECIAL_LUMP_CLASSES.copy()


methods = quake2.methods.copy()
