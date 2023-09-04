# https://valvedev.info/tools/bspfix/
import enum

from ..id_software import quake
from ..valve import goldsrc


FILE_MAGIC = None

BSP_VERSION = 30

GAME_PATHS = {"Half-Life: Blue Shift": "Half-Life/blue_shift"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    PLANES = 0
    ENTITIES = 1
    MIP_TEXTURES = 2
    VERTICES = 3
    VISIBILITY = 4
    NODES = 5
    TEXTURE_INFO = 6
    FACES = 7
    LIGHTING = 8
    CLIP_NODES = 9
    LEAVES = 10
    LEAF_FACES = 11
    EDGES = 12
    SURFEDGES = 13
    MODELS = 14


LumpHeader = quake.LumpHeader


# known lump changes from GoldSrc -> Blue Shift:
# ENTITIES -> PLANES
# PLANES -> ENTITIES


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = goldsrc.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = goldsrc.LUMP_CLASSES.copy()

SPECIAL_LUMP_CLASSES = goldsrc.SPECIAL_LUMP_CLASSES.copy()


methods = goldsrc.methods.copy()
