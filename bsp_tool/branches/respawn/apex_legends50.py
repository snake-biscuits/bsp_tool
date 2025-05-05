"""Map format from season 10.1 to season 13"""
import enum

from ... import core
from ...utils import vector
from ..valve import source
from . import apex_legends


FILE_MAGIC = b"rBSP"

BSP_VERSION = 50

GAME_PATHS = {"Apex Legends": "ApexLegends/maps"}

GAME_VERSIONS = {
    "Apex Legends: Season 10 - Emergence": 50,
    "Apex Legends: Season 11 - Escape [19 Nov Patch]": (50, 1)}


class LUMP(enum.Enum):
    ENTITIES = 0x0000
    PLANES = 0x0001
    TEXTURE_DATA = 0x0002
    VERTICES = 0x0003
    LIGHTPROBE_PARENT_INFOS = 0x0004
    SHADOW_ENVIRONMENTS = 0x0005
    UNUSED_6 = 0x0006
    UNUSED_7 = 0x0007
    UNUSED_8 = 0x0008
    UNUSED_9 = 0x0009
    UNUSED_10 = 0x000A
    UNUSED_11 = 0x000B
    UNUSED_12 = 0x000C
    UNUSED_13 = 0x000D
    MODELS = 0x000E
    SURFACE_NAMES = 0x000F
    CONTENTS_MASKS = 0x0010
    SURFACE_PROPERTIES = 0x0011
    BVH_NODES = 0x0012
    BVH_LEAF_DATA = 0x0013
    PACKED_VERTICES = 0x0014
    HEIGHTFIELDS = 0x0015
    HEIGHTFIELD_SAMPLES = 0x0016
    UNUSED_23 = 0x0017
    ENTITY_PARTITIONS = 0x0018
    UNUSED_25 = 0x0019
    UNUSED_26 = 0x001A
    UNUSED_27 = 0x001B
    UNUSED_28 = 0x001C
    UNUSED_29 = 0x001D
    VERTEX_NORMALS = 0x001E
    UNUSED_31 = 0x001F
    UNUSED_32 = 0x0020
    UNUSED_33 = 0x0021
    UNUSED_34 = 0x0022
    GAME_LUMP = 0x0023
    UNUSED_36 = 0x0024
    UNKNOWN_37 = 0x0025  # connected to VIS lumps
    UNKNOWN_38 = 0x0026  # connected to CSM lumps
    UNKNOWN_39 = 0x0027  # connected to VIS lumps
    PAKFILE = 0x0028  # zip file, contains cubemaps
    UNUSED_41 = 0x0029
    CUBEMAPS = 0x002A
    CUBEMAPS_AMBIENT_RCP = 0x002B
    WATER_BODIES = 0x002C
    WATER_BODY_CENTERS = 0x002D
    WATER_BODY_VERTICES = 0x002E
    WATER_BODY_INDICES = 0x002F
    WAVE_DATA = 0x0030
    UNUSED_49 = 0x0031
    UNUSED_50 = 0x0032
    UNUSED_51 = 0x0033
    UNUSED_52 = 0x0034
    UNUSED_53 = 0x0035
    WORLD_LIGHTS = 0x0036
    WORLD_LIGHT_PARENT_INFOS = 0x0037
    UNUSED_56 = 0x0038
    UNUSED_57 = 0x0039
    UNUSED_58 = 0x003A
    UNUSED_59 = 0x003B
    UNUSED_60 = 0x003C
    UNUSED_61 = 0x003D
    UNUSED_62 = 0x003E
    UNUSED_63 = 0x003F
    UNUSED_64 = 0x0040
    UNUSED_65 = 0x0041
    UNUSED_66 = 0x0042
    UNUSED_67 = 0x0043
    UNUSED_68 = 0x0044
    UNUSED_69 = 0x0045
    UNUSED_70 = 0x0046
    VERTEX_UNLIT = 0x0047        # VERTEX_RESERVED_0
    VERTEX_LIT_FLAT = 0x0048     # VERTEX_RESERVED_1
    VERTEX_LIT_BUMP = 0x0049     # VERTEX_RESERVED_2
    VERTEX_UNLIT_TS = 0x004A     # VERTEX_RESERVED_3
    VERTEX_BLINN_PHONG = 0x004B  # VERTEX_RESERVED_4
    VERTEX_RESERVED_5 = 0x004C
    VERTEX_RESERVED_6 = 0x004D
    VERTEX_RESERVED_7 = 0x004E
    MESH_INDICES = 0x004F
    MESHES = 0x0050
    MESH_BOUNDS = 0x0051
    MATERIAL_SORTS = 0x0052
    LIGHTMAP_HEADERS = 0x0053
    UNUSED_84 = 0x0054
    TWEAK_LIGHTS = 0x0055
    UNUSED_86 = 0x0056
    UNUSED_87 = 0x0057
    UNUSED_88 = 0x0058
    UNUSED_89 = 0x0059
    UNUSED_90 = 0x005A
    UNUSED_91 = 0x005B
    UNUSED_92 = 0x005C
    UNUSED_93 = 0x005D
    UNUSED_94 = 0x005E
    UNUSED_95 = 0x005F
    UNUSED_96 = 0x0060
    LIGHTMAP_DATA_UNKNOWN = 0x0061
    LIGHTMAP_DATA_SKY = 0x0062
    CSM_AABB_NODES = 0x0063
    CSM_OBJ_REFERENCES = 0x0064
    LIGHTPROBES = 0x0065
    STATIC_PROP_LIGHTPROBE_INDICES = 0x0066
    LIGHTPROBE_TREE = 0x0067
    LIGHTPROBE_REFERENCES = 0x0068
    LIGHTMAP_DATA_REAL_TIME_LIGHTS = 0x0069
    CELL_BSP_NODES = 0x006A
    CELLS = 0x006B
    PORTALS = 0x006C
    PORTAL_VERTICES = 0x006D
    PORTAL_EDGES = 0x006E
    PORTAL_VERTEX_EDGES = 0x006F
    PORTAL_VERTEX_REFERENCES = 0x0070
    PORTAL_EDGE_REFERENCES = 0x0071
    PORTAL_EDGE_INTERSECT_AT_EDGE = 0x0072
    PORTAL_EDGE_INTERSECT_AT_VERTEX = 0x0073
    PORTAL_EDGE_INTERSECT_HEADER = 0x0074
    OCCLUSION_MESH_VERTICES = 0x0075
    OCCLUSION_MESH_INDICES = 0x0076
    CELL_AABB_NODES = 0x0077
    OBJ_REFERENCES = 0x0078
    OBJ_REFERENCE_BOUNDS = 0x0079
    LIGHTMAP_DATA_RTL_PAGES = 0x007A
    LEVEL_INFO = 0x007B
    SHADOW_MESH_OPAQUE_VERTICES = 0x007C
    SHADOW_MESH_ALPHA_VERTICES = 0x007D
    SHADOW_MESH_INDICES = 0x007E
    SHADOW_MESHES = 0x007F


LumpHeader = source.LumpHeader


# classes for lumps, in alphabetical order:
class CSMAABBNode(core.Struct):  # LUMP 99 (0063)
    mins: vector.vec3
    children: core.BitField  # indices into CSMAABBNodes
    maxs: vector.vec3
    unknown: core.BitField  # indices into Unknown38?
    __slots__ = ["mins", "children", "maxs", "unknown"]
    _format = "3fI3fI"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}
    _bitfields = {
        "children": {"first": 24, "count": 8},  # no flags; increased limit?
        "unknown": {"first": 24, "count": 8}}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}


# NOTE: all Apex lumps are version 0, except GAME_LUMP
# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = apex_legends.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = apex_legends.LUMP_CLASSES.copy()
LUMP_CLASSES.update({
    "CSM_AABB_NODES": {0: CSMAABBNode}})

SPECIAL_LUMP_CLASSES = apex_legends.SPECIAL_LUMP_CLASSES.copy()

GAME_LUMP_HEADER = source.GameLumpHeader

GAME_LUMP_CLASSES = {
    "sprp": {
        50: apex_legends.GameLump_SPRP}}


methods = apex_legends.methods.copy()
