# https://github.com/ValveSoftware/halflife/blob/master/utils/common/bspfile.h
# http://hlbsp.sourceforge.net/index.php?content=bspdef
# TODO: list games this branch supports
import enum

from .. import shared
from ..id_software import quake  # GoldSrc was forked from IdTech 2 during Quake II development

BSP_VERSION = 30

GAMES = [*[f"Half-Life/{mod}" for mod in [
                       "bshift",    # Half-Life: Blue Shift
                       "cstrike",   # Counter-Strike
                       "czero",     # Counter-Strike: Condition Zero
                       "czeror",    # Counter-Strike: Condition Zero - Deleted Scenes
                       "dmc",       # Deathmatch Classic
                       "dod",       # Day of Defeat
                       "gearbox",   # Half-Life: Opposing Force
                       "ricochet",  # Ricochet
                       "tfc",       # Team Fortress Classic
                       "valve"]],   # Half-Life
         "Halfquake Trilogy", "Sven Co-op"]


# lump names & indices:
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
    MODELS = 14


# engine limits:
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
class Contents(enum.IntFlag):
    """Brush flags"""
    # src/public/bspflags.h
    # NOTE: compiler gets these flags from a combination of all textures on the brush
    # e.g. any non opaque face means this brush is non-opaque, and will not block vis
    # visible
    EMPTY = -1
    SOLID = -2
    WATER = -3
    SLIME = -4
    LAVA = -5
    SKY = -6
    ORIGIN = -7  # remove when compiling from .map to .bsp
    CLIP = -8  # "changed to contents_solid"
    CURRENT_0 = -9
    CURRENT_90 = -10
    CURRENT_180 = -11
    CURRENT_270 = -12
    CURRENT_UP = -13
    CURRENT_DOWN = -14
    TRANSLUCENT = -15


lump_header_address = {LUMP_ID: (4 + i * 8) for i, LUMP_ID in enumerate(LUMP)}
# NOTE: according to github, GoldSrc has a checksum for each lump?


# classes for lumps (alphabetical order):


# classes for special lumps (alphabetical order):


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = {"EDGES": quake.Edge}

LUMP_CLASSES = {"PLANES": quake.Plane}

SPECIAL_LUMP_CLASSES = {"ENTITIES": shared.Entities}
# TODO: make a special LumpCLass for MipTextures
# -- any lump containing offsets needs it's own BspLump subclass
# {"TEXTURES": lambda raw_lump: lump.MipTextures(quake.MipTexture, raw_lump)}


# branch exclusive methods, in alphabetical order:
methods = []
