import enum

from .. import base
from .. import shared  # special lumps
from . import titanfall


BSP_VERSION = 37

# https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Titanfall
# TitanFall|2 has b"rBSP" file-magic and 128 lumps
# ~72 of the 128 lumps appear in .bsp_lump files
# the naming convention for these files is: "<bsp.filename>.<LUMP_HEX_ID>.bsp_lump"
# where <LUMP_HEX_ID> is a lowercase four digit hexadecimal string
# e.g. mp_drydock.004a.bsp_lump (Lump #74: VertexUnlitTS)
# entities are stored across 5 different .ent files per .bsp
# the 5 files are: env, fx, script, snd, spawn
# e.g. mp_drydock_env.ent
# presumably all this file splitting has to do with streaming data into memory


class LUMP(enum.Enum):
    ENTITIES = 0x0000
    PLANES = 0x0001
    TEXDATA = 0x0002
    VERTICES = 0x0003
    LIGHTPROBE_PARENT_INFOS = 0x0004
    SHADOW_ENVIRONMENTS = 0x0005
    LIGHTPROBE_BSP_NODES = 0x0006
    LIGHTPROBE_BSP_REF_IDS = 0x0007
    UNUSED_8 = 0x0008
    UNUSED_9 = 0x0009
    UNUSED_10 = 0x000A
    UNUSED_11 = 0x000B
    UNUSED_12 = 0x000C
    UNUSED_13 = 0x000D
    MODELS = 0x000E
    UNUSED_15 = 0x000F
    UNUSED_16 = 0x0010
    UNUSED_17 = 0x0011
    UNUSED_18 = 0x0012
    UNUSED_19 = 0x0013
    UNUSED_20 = 0x0014
    UNUSED_21 = 0x0015
    UNUSED_22 = 0x0016
    UNUSED_23 = 0x0017
    ENTITY_PARTITIONS = 0x0018
    UNUSED_25 = 0x0019
    UNUSED_26 = 0x001A
    UNUSED_27 = 0x001B
    UNUSED_28 = 0x001C
    PHYS_COLLIDE = 0x001D
    VERTEX_NORMALS = 0x001E
    UNUSED_31 = 0x001F
    UNUSED_32 = 0x0020
    UNUSED_33 = 0x0021
    UNUSED_34 = 0x0022
    GAME_LUMP = 0x0023
    LEAF_WATERDATA = 0x0024
    UNUSED_37 = 0x0025
    UNUSED_38 = 0x0026
    UNUSED_39 = 0x0027
    PAKFILE = 0x0028  # zip file, contains cubemaps
    UNUSED_41 = 0x0029
    CUBEMAPS = 0x002A
    TEXDATA_STRING_DATA = 0x002B
    TEXDATA_STRING_TABLE = 0x002C
    UNUSED_45 = 0x002D
    UNUSED_46 = 0x002E
    UNUSED_47 = 0x002F
    UNUSED_48 = 0x0030
    UNUSED_49 = 0x0031
    UNUSED_50 = 0x0032
    UNUSED_51 = 0x0033
    UNUSED_52 = 0x0034
    UNUSED_53 = 0x0035
    WORLDLIGHTS = 0x0036
    WORLDLIGHTS_PARENT_INFO = 0x0037
    UNUSED_56 = 0x0038
    UNUSED_57 = 0x0039
    UNUSED_58 = 0x003A
    UNUSED_59 = 0x003B
    UNUSED_60 = 0x003C
    UNUSED_61 = 0x003D
    PHYS_LEVEL = 0x003E  # length 0, version 6?
    UNUSED_63 = 0x003F
    UNUSED_64 = 0x0040
    UNUSED_65 = 0x0041
    TRICOLL_TRIS = 0x0042
    UNUSED_67 = 0x0043
    TRICOLL_NODES = 0x0044
    TRICOLL_HEADERS = 0x0045
    PHYSTRIS = 0x0046
    VERTS_UNLIT = 0x0047  # VERTS_RESERVED_0 - 7
    VERTS_LIT_FLAT = 0x0048
    VERTS_LIT_BUMP = 0x0049
    VERTS_UNLIT_TS = 0x004A
    VERTS_BLINN_PHONG = 0x004B
    VERTS_RESERVED_5 = 0x004C
    VERTS_RESERVED_6 = 0x004D
    VERTS_RESERVED_7 = 0x004E
    MESH_INDICES = 0x004F
    MESHES = 0x0050
    MESH_BOUNDS = 0x0051
    MATERIAL_SORT = 0x0052
    LIGHTMAP_HEADERS = 0x0053
    LIGHTMAP_DATA_DXT5 = 0x0054  # unused?
    CM_GRID = 0x0055
    CM_GRIDCELLS = 0x0056
    CM_GEO_SETS = 0x0057
    CM_GEO_SET_BOUNDS = 0x0058
    CM_PRIMS = 0x0059
    CM_PRIM_BOUNDS = 0x005A
    CM_UNIQUE_CONTENTS = 0x005B
    CM_BRUSHES = 0x005C
    CM_BRUSH_SIDE_PLANE_OFFSETS = 0x005D
    CM_BRUSH_SIDE_PROPS = 0x005E
    CM_BRUSH_TEX_VECS = 0x005F
    TRICOLL_BEVEL_STARTS = 0x0060
    TRICOLL_BEVEL_INDICES = 0x0061
    LIGHTMAP_DATA_SKY = 0x0062
    CSM_AABB_NODES = 0x0063
    CSM_OBJ_REFS = 0x0064
    LIGHTPROBES = 0x0065
    STATIC_PROP_LIGHTPROBE_INDEX = 0x0066
    LIGHTPROBE_TREE = 0x0067
    LIGHTPROBE_REFS = 0x0068
    LIGHTMAP_DATA_REAL_TIME_LIGHTS = 0x0069
    CELL_BSP_NODES = 0x006A
    CELLS = 0x006B
    PORTALS = 0x006C
    PORTAL_VERTS = 0x006D
    PORTAL_EDGES = 0x006E
    PORTAL_VERT_EDGES = 0x006F
    PORTAL_VERT_REFS = 0x0070
    PORTAL_EDGE_REFS = 0x0071
    PORTAL_EDGE_ISECT_EDGE = 0x0072
    PORTAL_EDGE_ISECT_AT_VERT = 0x0073
    PORTAL_EDGE_ISECT_HEADER = 0x0074
    OCCLUSION_MESH_VERTS = 0x0075
    OCCLUSION_MESH_INDICES = 0x0076
    CELL_AABB_NODES = 0x0077
    OBJ_REFS = 0x0078
    OBJ_REF_BOUNDS = 0x0079
    LIGHTMAP_DATA_REAL_TIME_LIGHT_PAGE = 0x007A
    LEVEL_INFO = 0x007B
    SHADOW_MESH_OPAQUE_VERTS = 0x007C
    SHADOW_MESH_ALPHA_VERTS = 0x007D
    SHADOW_MESH_INDICES = 0x007E
    SHADOW_MESH_MESHES = 0x007F


lump_header_address = {LUMP_ID: (16 + i * 16) for i, LUMP_ID in enumerate(LUMP)}


# classes for lumps (alphabetical order) [X / 128] + 2 special lumps
LUMP_CLASSES = titanfall.LUMP_CLASSES.copy()
# LUMP_CLASSES.update({})

SPECIAL_LUMP_CLASSES = titanfall.SPECIAL_LUMP_CLASSES.copy()


# branch exclusive methods, in alphabetical order:
methods = [*titanfall.methods]
