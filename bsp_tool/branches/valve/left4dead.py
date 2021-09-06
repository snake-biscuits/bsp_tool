# https://developer.valvesoftware.com/wiki/Left_4_Dead_(engine_branch)
import collections
import enum

from . import orange_box


BSP_VERSION = 20  # L4D = 20, L4D2 = 21

GAMES = ["Left 4 Dead", "Left 4 Dead 2"]


class LUMP(enum.Enum):
    ENTITIES = 0
    PLANES = 1
    TEXTURE_DATA = 2
    VERTICES = 3
    VISIBILITY = 4
    NODES = 5
    TEXTURE_INFO = 6
    FACES = 7
    LIGHTING = 8
    OCCLUSION = 9
    LEAVES = 10
    FACE_IDS = 11
    EDGES = 12
    SURFEDGES = 13
    MODELS = 14
    WORLD_LIGHTS = 15
    LEAF_FACES = 16
    LEAF_BRUSHES = 17
    BRUSHES = 18
    BRUSH_SIDES = 19
    AREAS = 20
    AREA_PORTALS = 21
    PROP_COLLISION = 22
    PROP_HULLS = 23
    PROP_HULL_VERTS = 24
    PROP_HULL_TRIS = 25
    DISPLACEMENT_INFO = 26
    ORIGINAL_FACES = 27
    PHYSICS_DISPLACEMENT = 28
    PHYSICS_COLLIDE = 29
    VERTEX_NORMALS = 30
    VERTEX_NORMAL_INDICES = 31
    DISPLACEMENT_LIGHTMAP_ALPHAS = 32
    DISPLACEMENT_VERTICES = 33
    DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS = 34
    GAME_LUMP = 35
    LEAF_WATER_DATA = 36
    PRIMITIVES = 37
    PRIMITIVE_VERTICES = 38
    PRIMITIVE_INDICES = 39
    PAKFILE = 40
    CLIP_PORTAL_VERTICES = 41
    CUBEMAPS = 42
    TEXTURE_DATA_STRING_DATA = 43
    TEXTURE_DATA_STRING_TABLE = 44
    OVERLAYS = 45
    LEAF_MIN_DIST_TO_WATER = 46
    FACE_MACRO_TEXTURE_INFO = 47
    DISPLACEMENT_TRIS = 48
    PROP_BLOB = 49
    WATER_OVERLAYS = 50
    LEAF_AMBIENT_INDEX_HDR = 51
    LEAF_AMBIENT_INDEX = 52
    LIGHTING_HDR = 53
    WORLD_LIGHTS_HDR = 54
    LEAF_AMBIENT_LIGHTING_HDR = 55
    LEAF_AMBIENT_LIGHTING = 56
    XZIP_PAKFILE = 57
    FACES_HDR = 58
    MAP_FLAGS = 59
    OVERLAY_FADES = 60
    LUMP_OVERLAY_SYSTEM_LEVELS = 61  # overlay CPU & GPU limits
    LUMP_PHYSLEVEL = 62
    UNUSED_63 = 63

# Known lump changes from Orange Box -> Alien Swarm:
# New (L4D):
#   UNUSED_61 -> LUMP_OVERLAY_SYSTEM_LEVELS
# New (L4D2):
#   UNUSED_22 -> PROP_COLLISION
#   UNUSED_23 -> PROP_HULLS
#   UNUSED_24 -> PROP_HULL_VERTS
#   UNUSED_25 -> PROP_HULL_TRIS
#   PHYSICS_COLLIDE_SURFACE -> PROP_BLOB
#   UNUSED_62 -> LUMP_PHYSLEVEL


lump_header_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}
Left4Dead2LumpHeader = collections.namedtuple("Left4DeadLumpHeader", ["length", "offset", "version", "fourCC"])
# length and offset are swapped for L4D2


read_lump_header = orange_box.read_lump_header


# classes for lumps (alphabetical order):
# TODO: (L4D2) PropHull, PropHullTri

# classes for special lumps (alphabetical order):
# TODO: (L4D2) PropCollision, PropBlob

# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = orange_box.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = orange_box.LUMP_CLASSES.copy()
LUMP_CLASSES.update({"PROP_HULL_VERTS": orange_box.Vertex})

SPECIAL_LUMP_CLASSES = orange_box.SPECIAL_LUMP_CLASSES.copy()

# TODO: GAME_LUMP_CLASSES = {"sprp": {8: lambda raw_lump: shared.GameLump_SPRP(raw_lump, StaticPropv8),


# branch exclusive methods, in alphabetical order:
methods = [*orange_box.methods]
