# structs for BSP version 29? (Titanfall 2)
import common
import enum

# https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Titanfall
# Titanfall 2 has rBSP file-magic, 127 lumps & uses bsp_lump files
# <bsp filename>.<ID>.bsp_lump
# where <ID> is a four digit hexadecimal string (lowercase)
# entities are stored in 5 different .ent files per bsp

# retro-fitting the bsp loader to read bsp_lump files will be handy
# but processing the alternate structure will need more

# based on notes by Cra0kalo; developer of titanfall VPK tool and CSGO hacks
# http://dev.cra0kalo.com/?p=202  (bsp)
# https://dev.cra0kalo.com/?p=137 (vpk)
class LUMP(enum.Enum):
    ENTITIES = 0 # unused, entities are stored across multiple files
    PLANES = 1
    TEXDATA = 2
    VERTICES = 3
    UNUSED_4 = 4
    UNUSED_5 = 5
    # 6-9 unknown
    UNUSED_10 = 10
    # 11-13 unknown
    MODELS = 14
    UNUSED_16 = 16
    UNUSED_20 = 20
    UNUSED_21 = 21
    UNUSED_22 = 22
    UNUSED_23 = 23
    ENTITYPARTITIONS = 24
    # 25-28 unknown
    PHYSCOLLIDE = 29
    VERTNORMALS = 30
    # 31-34 unknown
    GAME_LUMP = 35
    LEAFWATERDATA = 36
    # 37-39 unkown
    PAKFILE = 40 # zip file, contains cubemaps
    UNUSED_41 = 41
    CUBEMAPS = 42
    TEXDATA_STRING_DATA = 43
    TEXDATA_STRING_TABLE = 44
    UNUSED_46 = 45
    # 46-52 unknown
    UNUSED_53 = 53
    WORLDLIGHTS_HDR = 54
    UNUSED_59 = 59
    PHYSLEVEL = 62
    TRICOLL_TRIS = 66
    TRICOLL_NODES = 68
    TRICOLL_HEADERS = 69
    PHYSTRIS = 70
    VERTS_UNLIT = 71
    VERTS_LIT_FLAT = 72
    VERTS_LIT_BUMP = 73
    VERTS_UNLIT_TS = 74
    VERTS_BLINN_PHONG = 75
    VERTS_RESERVED_5 = 76
    VERTS_RESERVED_6 = 77
    VERTS_RESERVED_7 = 78
    MESH_INDICES = 79
    MESHES = 80
    MESH_BOUNDS = 81
    MATERIAL_SORT = 82
    LIGHTMAP_HEADERS = 83
    LIGHTMAP_DATA_DXT5 = 84
    CM_GRID = 85
    CM_GRIDCELLS = 86
    CM_GEO_SETS = 87
    CM_GEO_SET_BOUNDS = 88
    CM_PRIMS = 89
    CM_PRIM_BOUNDS = 90
    CM_UNIQUE_CONTENTS = 91
    CM_BRUSHES = 92
    CM_BRUSH_SIDE_PLANE_OFFSETS = 93
    CM_BRUSH_SIDE_PROPS = 94
    CM_BRUSH_TEX_VECS = 95
    TRICOLL_BEVEL_STARTS = 96
    TRICOLL_BEVEL_INDEXE = 97
    LIGHTMAP_DATA_SKY = 98
    CSM_AABB_NODES = 99
    CSM_OBJ_REFS = 100
    LIGHTPROBES = 101
    STATIC_PROP_LIGHTPROBE_INDEX = 102
    LIGHTPROBETREE = 103
    LIGHTPROBEREFS = 104
    LIGHTMAP_DATA_REAL_TIME_LIGHTS = 105
    CELL_BSP_NODES = 106
    CELLS = 107
    PORTALS = 108
    PORTAL_VERTS = 109
    PORTAL_EDGES = 110
    PORTAL_VERT_EDGES = 111
    PORTAL_VERT_REFS = 112
    PORTAL_EDGE_REFS = 113
    PORTAL_EDGE_ISECT_EDGE = 114
    PORTAL_EDGE_ISECT_AT_VERT = 115
    PORTAL_EDGE_ISECT_HEADER = 116
    OCCLUSIONMESH_VERTS = 117
    OCCLUSIONMESH_INDICES = 118
    CELL_AABB_NODES = 119
    OBJ_REFS = 120
    OBJ_REF_BOUNDS = 121
    UNUSED_122 = 122
    LEVEL_INFO = 123
    SHADOW_MESH_OPAQUE_VERTS = 124
    SHADOW_MESH_ALPHA_VERTS = 125
    SHADOW_MESH_INDICES = 126
    SHADOW_MESH_MESHES = 127

lump_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}
