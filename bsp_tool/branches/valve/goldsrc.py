# https://github.com/ValveSoftware/halflife/blob/master/utils/common/bspfile.h
# http://hlbsp.sourceforge.net/index.php?content=bspdef
# https://valvedev.info/tools/bsptwomap/
import enum

from ..id_software import quake
# NOTE: GoldSrc was forked from IdTech 2 during Quake II development
# -- so some elements of both quake & quake2 formats are present


FILE_MAGIC = None

BSP_VERSION = 30

GAME_PATHS = {"Counter Strike": "Half-Life/cstrike",
              "Counter-Strike: Condition Zero": "Half-Life/czero",
              "Counter-Strike: Condition Zero - Deleted Scenes": "Half-Life/czeror",
              "Cry of Fear": "Cry of Fear/cryoffear",
              "Day of Defeat": "Half-Life/dod",
              "Deathmatch Classic": "Half-Life/dmc",
              "Half-Life": "Half-Life/valve",
              "Half-Life: Opposing Force": "Half-Life/gearbox",
              "Halfquake Trilogy": "Halfquake Trilogy/valve",
              "Ricochet": "Half-Life/ricochet",
              "Sven Co-op": "Sven Co-op/svencoop",
              "Team Fortress Classic": "Half-Life/tfc"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    ENTITIES = 0
    PLANES = 1
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

# Known lump changes from Quake II -> GoldSrc:
# New:
#   MARK_SURFACES


# struct QuakeBspHeader { int version; QuakeLumpHeader headers[15]; };
lump_header_address = {LUMP_ID: (4 + i * 8) for i, LUMP_ID in enumerate(LUMP)}


# Engine limits:
class MAX(enum.Enum):
    ENTITIES = 1024
    PLANES = 32767
    MIP_TEXTURES = 512
    MIP_TEXTURES_SIZE = 0x200000  # in bytes
    VERTICES = 65535
    VISIBILITY_SIZE = 0x200000  # in bytes
    NODES = 32767  # "because negative shorts are contents"
    TEXTURE_INFO = 8192
    FACES = 65535
    LIGHTING_SIZE = 0x200000  # in bytes
    CLIP_NODES = 32767
    LEAVES = 8192
    MARK_SURFACES = 65535
    EDGES = 256000
    MODELS = 400
    BRUSHES = 4096  # for radiant / q2map ?
    ENTITY_KEY = 32
    ENTITY_STRING = 128 * 1024
    ENTITY_VALUE = 1024
    PORTALS = 65536  # related to leaves
    SURFEDGES = 512000


# flag enums
class Contents(enum.IntFlag):  # src/public/bspflags.h
    """Brush flags"""
    # NOTE: compiler gets these flags from a combination of all textures on the brush
    # e.g. any non opaque face means this brush is non-opaque, and will not block vis
    # visible
    EMPTY = -1
    SOLID = -2
    WATER = -3
    SLIME = -4
    LAVA = -5
    SKY = -6
    ORIGIN = -7  # removed when compiling from .map / .vmf to .bsp
    CLIP = -8  # "changed to contents_solid"
    CURRENT_0 = -9
    CURRENT_90 = -10
    CURRENT_180 = -11
    CURRENT_270 = -12
    CURRENT_UP = -13
    CURRENT_DOWN = -14
    TRANSLUCENT = -15


# classes for lumps, in alphabetical order:
# TODO: Model
# TODO: Node

# classes for special lumps, in alphabetical order:
# TODO: make a special LumpCLass for MipTextures
# -- any lump containing offsets needs it's own BspLump subclass
# {"TEXTURES": lambda raw_lump: lump.MipTextures(quake.MipTexture, raw_lump)}

# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = quake.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = quake.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("MODELS")
LUMP_CLASSES.pop("NODES")

SPECIAL_LUMP_CLASSES = quake.SPECIAL_LUMP_CLASSES.copy()


methods = [*quake.methods]
