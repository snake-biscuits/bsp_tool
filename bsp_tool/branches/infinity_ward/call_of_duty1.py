# https://wiki.zeroy.com/index.php?title=Call_of_Duty_1:_d3dbsp
import enum

from ... import core
from . import call_of_duty1_demo


FILE_MAGIC = b"IBSP"

BSP_VERSION = 59

GAME_PATHS = {
    "Call of Duty": "Call of Duty",
    "Call of Duty: United Offensive": "Call of Duty"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    TEXTURES = 0
    LIGHTMAPS = 1
    PLANES = 2
    BRUSH_SIDES = 3
    BRUSHES = 4
    TRIANGLE_SOUPS = 6
    VERTICES = 7
    INDICES = 8
    CULL_GROUPS = 9
    CULL_GROUP_INDICES = 10
    PORTAL_VERTICES = 11
    OCCLUDERS = 12
    OCCLUDER_PLANES = 13
    OCCLUDER_EDGES = 14
    OCCLUDER_INDICES = 15
    AABB_TREES = 16
    CELLS = 17
    PORTALS = 18
    LIGHT_INDICES = 19
    NODES = 20
    LEAVES = 21
    LEAF_BRUSHES = 22
    LEAF_FACES = 23
    PATCH_COLLISION = 24
    COLLISION_VERTICES = 25
    COLLISION_INDICES = 26
    MODELS = 27
    VISIBILITY = 28
    ENTITIES = 29
    LIGHTS = 30
    UNKNOWN_31 = 31  # EFFECTS / FOGS ?
    # big "32nd lump" at end of file, not in header?


class LumpHeader(core.MappedArray):
    _mapping = ["length", "offset"]
    _format = "2I"


# {"LUMP_NAME": LumpClass}
BASIC_LUMP_CLASSES = call_of_duty1_demo.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = call_of_duty1_demo.LUMP_CLASSES.copy()

SPECIAL_LUMP_CLASSES = call_of_duty1_demo.SPECIAL_LUMP_CLASSES.copy()


methods = call_of_duty1_demo.methods.copy()
