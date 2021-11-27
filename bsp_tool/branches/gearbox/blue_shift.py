# https://valvedev.info/tools/bspfix/
import enum

from ..valve import goldsrc


FILE_MAGIC = None

BSP_VERSION = 30

GAME_PATHS = ["Half-Life/blue_shift"]  # Half-Life: Blue Shift

GAME_VERSIONS = {GAME_PATH: BSP_VERSION for GAME_PATH in GAME_PATHS}


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
    MARK_SURFACES = 11
    EDGES = 12
    SURFEDGES = 13
    MODELS = 14


# struct QuakeBspHeader { int version; QuakeLumpHeader headers[15]; };
lump_header_address = {LUMP_ID: (4 + i * 8) for i, LUMP_ID in enumerate(LUMP)}

# Known lump changes from GoldSrc -> Blue Shift:
# ENTITIES -> PLANES
# PLANES -> ENTITIES


BASIC_LUMP_CLASSES = goldsrc.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = goldsrc.LUMP_CLASSES.copy()

SPECIAL_LUMP_CLASSES = goldsrc.SPECIAL_LUMP_CLASSES.copy()


methods = [*goldsrc.methods]
