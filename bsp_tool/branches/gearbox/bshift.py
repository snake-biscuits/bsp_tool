# https://valvedev.info/tools/bspfix/
import enum

from ..valve import goldsrc


BSP_VERSION = 30

GAMES = ["Half-Life/bshift"]  # Half-Life: Blue Shift


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
    MODELS = 14

# Known lump changes from Quake II -> GoldSrc:
# ENTITIES -> PLANES
# PLANES -> ENTITIES


lump_header_address = {LUMP_ID: (4 + i * 8) for i, LUMP_ID in enumerate(LUMP)}


BASIC_LUMP_CLASSES = goldsrc.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = goldsrc.LUMP_CLASSES.copy()
# PLANES lump failing

SPECIAL_LUMP_CLASSES = goldsrc.SPECIAL_LUMP_CLASSES.copy()
# ENTITIES lump failing


methods = [*goldsrc.methods]
