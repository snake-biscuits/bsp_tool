# based on notes by Cra0kalo; developer of titanfall VPK tool and CSGO hacks
# http://dev.cra0kalo.com/?p=202 (bsp) & https://dev.cra0kalo.com/?p=137 (vpk)

import enum

from . import common
from . import team_fortress2


bsp_version = 37

class LUMP(enum.Enum):
    ENTITIES = 0 # entities are stored across multiple text files
    PLANES = 1 # version 1
    TEXDATA = 2 # version 1
    VERTICES = 3
    UNKNOWN_4 = 4 # source VISIBILITY
    UNKNOWN_5 = 5 # source NODES
    UNKNOWN_6 = 6 # source TEXINFO
    UNKNOWN_7 = 7 # source FACES
    UNKNOWN_8 = 8
    UNKNOWN_9 = 9
    UNUSED_10 = 10
    UNKNOWN_11 = 11
    UNKNOWN_12 = 12
    UNKNOWN_13 = 13
    MODELS = 14
    UNUSED_16 = 16
    UNKNOWN_17 = 17
    UNKKOWN_18 = 18
    UNKNOWN_19 = 19
    UNUSED_20 = 20
    UNUSED_21 = 21
    UNUSED_22 = 22
    UNUSED_23 = 23
    ENTITY_PARTITIONS = 24
    UNKNOWN_25 = 25
    UNKNOWN_26 = 26
    UNKNOWN_27 = 27
    UNKNOWN_28 = 28
    PHYS_COLLIDE = 29
    VERTEX_NORMALS = 30
    UNKNOWN_31 = 31
    UNKNOWN_32 = 32
    UNKNOWN_33 = 33
    UNKNOWN_34 = 34
    GAME_LUMP = 35
    LEAF_WATERDATA = 36
    UNKNOWN_37 = 37
    UNKNOWN_38 = 38
    UNKNOWN_39 = 39
    PAKFILE = 40 # zip file, contains cubemaps
    UNKNOWN_41 = 41
    CUBEMAPS = 42
    TEXDATA_STRING_DATA = 43
    TEXDATA_STRING_TABLE = 44
    UNKNOWN_45 = 45
    UNKNOWN_46 = 46
    UNKNOWN_47 = 47
    UNKNOWN_48 = 48
    UNKNOWN_49 = 49
    UNKNOWN_50 = 50
    UNKNOWN_51 = 51
    UNKNOWN_52 = 52
    UNUSED_53 = 53
    WORLDLIGHTS_HDR = 54
    UNKNOWN_59 = 59 # version 3
    PHYS_LEVEL = 62
    UNKNOWN_63 = 63
    UNKNOWN_64 = 64
    UNKNOWN_65 = 65
    TRICOLL_TRIS = 66
    UNKNOWN_67 = 67
    TRICOLL_NODES = 68
    TRICOLL_HEADERS = 69
    PHYSTRIS = 70
    VERTS_UNLIT = 71 # VERTS_RESERVED_0 - 7
    VERTS_LIT_FLAT = 72
    VERTS_LIT_BUMP = 73 # version 2
    VERTS_UNLIT_TS = 74
    VERTS_BLINN_PHONG = 75 # version 1
    VERTS_RESERVED_5 = 76 # version 1
    VERTS_RESERVED_6 = 77
    VERTS_RESERVED_7 = 78
    MESH_INDICES = 79 # version 1
    MESHES = 80 # version 1
    MESH_BOUNDS = 81
    MATERIAL_SORT = 82
    LIGHTMAP_HEADERS = 83
    LIGHTMAP_DATA_DXT5 = 84
    CM_GRID = 85
    CM_GRIDCELLS = 86
    CM_GEO_SETS = 87
    CM_GEO_SET_BOUNDS = 88
    CM_PRIMS = 89
    CM_PRIM_BOUNDS = 90 # version 1
    CM_UNIQUE_CONTENTS = 91
    CM_BRUSHES = 92
    CM_BRUSH_SIDE_PLANE_OFFSETS = 93
    CM_BRUSH_SIDE_PROPS = 94
    CM_BRUSH_TEX_VECS = 95
    TRICOLL_BEVEL_STARTS = 96
    TRICOLL_BEVEL_INDICES = 97
    LIGHTMAP_DATA_SKY = 98
    CSM_AABB_NODES = 99
    CSM_OBJ_REFS = 100
    LIGHTPROBES = 101
    STATIC_PROP_LIGHTPROBE_INDEX = 102
    LIGHTPROBE_TREE = 103
    LIGHTPROBE_REFS = 104
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
    OCCLUSION_MESH_VERTS = 117
    OCCLUSION_MESH_INDICES = 118
    CELL_AABB_NODES = 119
    OBJ_REFS = 120
    OBJ_REF_BOUNDS = 121
    UNKNOWN_122 = 122
    LEVEL_INFO = 123
    SHADOW_MESH_OPAQUE_VERTS = 124
    SHADOW_MESH_ALPHA_VERTS = 125
    SHADOW_MESH_INDICES = 126
    SHADOW_MESH_MESHES = 127

# rBSP header structure:
# int b"rBSP"
# int bsp_version
# int map_revision
# int 127
# 128 lump headers
lump_header_address = {LUMP_ID: (16 + i * 16) for i, LUMP_ID in enumerate(LUMP)}

# https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Titanfall
# Titanfall 2 has rBSP file-magic, 127 lumps & uses bsp_lump files:
# <bsp filename>.<ID>.bsp_lump
# where <ID> is a four digit hexadecimal string (lowercase)
# entities are stored in 5 different .ent files per bsp
## mp_drydock.bsp has .bsp_lump files for the following:
# 0000 ENTITIES               0  (SPECIAL)
# 0001 PLANES                 1
# 0002 TEXDATA                2
# 0003 VERTICES               3
# 0004 UNKNOWN_4              4  source VISIBILITY
# 0005 UNKNOWN_5              5  source NODES
# 0006 UNKNOWN_6              6  source TEXINFO
# 0007 UNKNOWN_7              7  source FACES
# ...
# 000E MODELS                14
# ...
# 0018 ENTITIY_PARTITIONS    24
# ...
# 001D PHYS_COLLIDE          29
# 001E VERTEX_NORMALS        30
# ...
# 0023 GAME_LUMP             35
# ...
# 0028 PAKFILE               40 [zip with PK file-magic] (contains cubemaps)
# ...
# 002A CUBEMAPS              42
# 002B TEXDATA_STRING_DATA   43
# 002C TEXDATA_STRING_TABLE  44
# ...
# 0036 WORLDLIGHTS_HDR       54
# ...
# 0042 PHYSCOLL_TRIS         66
# ...
# 0044 PHYSCOLL_NODES        68
# 0045 PHYSCOLL_HEADERS      69
# ...
# 0047 VERTS_UNLIT           71
# ...
# 0049 VERTS_LIT_BUMP        73
# 004A VERTS_UNLIT_TS        74
# ...
# 004F MESH_INDICES          79
# 0050 MESHES                80
# 0051 MESH_BOUNDS           81
# 0052 MATERIAL_SORT         82
# 0053 LIGHTMAP_HEADERS      83
# ...
# 0055 CM_GRID                          85
# 0056 CM_GRIDCELLS                     86
# 0057 CM_GEO_SETS                      87
# 0058 CM_GEO_SET_BOUNDS                88
# 0059 CM_PRIMS                         89
# 005A CM_PRIM_BOUNDS                   90
# 005B CM_UNIQUE_CONTENTS               91
# 005C CM_BRUSHES                       92
# 005D CM_BRUSH_SIDE_PLANE_OFFSETS      93
# 005E CM_BRUSH_SIDE_PROPS              94
# 005F CM_BRUSH_TEX_VECS                95
# 0060 TRICOLL_BEVEL_STARTS             96
# 0061 TRICOLL_BEVEL_INDICES            97
# 0062 LIGHTMAP_DATA_SKY                98
# 0063 CSM_AABB_NODES                   99
# 0064 CSM_OBJ_REFS                    100
# 0065 LIGHTPROBES                     101
# 0066 STATIC_PROP_LIGHTPROBE_INDEX    102
# 0067 LIGHTPROBE_TREE                 103
# 0068 LIGHTPROBE_REFS                 104
# 0069 LIGHTMAP_DATA_REAL_TIME_LIGHTS  105
# 006A CELL_BSP_NODES                  106
# 006B CELLS                           107
# 006C PORTALS                         108
# 006D PORTAL_VERTS                    109
# 006E PORTAL_EDGES                    110
# 006F PORTAL_VERT_EDGES               111
# 0070 PORTAL_VERT_REFS                112
# 0071 PORTAL_EDGE_REFS                113
# 0072 PORTAL_EDGE_ISECT_EDGE          114
# 0073 PORTAL_EDGE_ISECT_AT_VERT       115
# 0074 PORTAL_EDGE_ISECT_HEADER        116
# 0075 OCCLUSION_MESH_VERTICES         117
# 0076 OCCLUSION_MESH_INDICES          118
# 0077 CELL_AABB_NODES                 119
# 0078 OBJ_REFS                        120
# 0079 OBJ_REF_BOUNDS                  121
# 007A UNKNOWN_122                     122
# 007B LEVEL_INFO                      123
# 007C SHADOW_MESH_OPAQUE_VERTS        124
# 007D SHADOW_MESH_ALPHA_VERTS         125
# 007E SHADOW_MESH_INDICES             126
# 007F SHADOW_MESH_MESHES              127
# some of the other lumps appear within the .bsp itself


# classes for lumps (alphabetical order)
class brush(common.base): # LUMP 92 (005C)
    __slots__ = ["normal", "unknown"] # origin, id?
    _format = "3fI"
    _arrays = {"normal": [*"xyz"]}

class bump_lit_vertex(common.base): # LUMP 71 (0047)
    __slots__ = ["position_index", "normal_index", "uv", "uv2", "uv3", "unknown"]
    # byte 8  - 12 = uv coords into albedo, normal, gloss, spec
    # byte 20 - 28 = uv coords into lightmap
    _format = "2I6f3I" # 44 bytes
    _arrays  = {"uv": [*"uv"], "uv2": [*"uv"], "uv3": [*"uv"],
                "unknown": [*"abc"]}

class material_sort(common.base): # LUMP 82 (0052)
    __slots__ = ["texdata", "unknown", "vertex_offset"]
    _format = "2h2I" # 12 bytes
    _arrays = {"unknown": [*"ab"]}

class mesh(common.base): # LUMP 80 (0050)
    __slots__ = ["start_index", "num_triangles", "unknown",
                 "material_sort", "flags"]
    # vertex type stored in flags
    _format = "IH3I2HI" # 28 Bytes
    _arrays = {"unknown": [*"abcd"]}

class mesh_indices(int): # LUMP 79 (004F)
    _format = "H"

class model(common.base): # LUMP 14 (000E)
    __slots__ = ["big_negative", "big_positive", "small_int", "tiny_int"]
    _format = "8i"
    _arrays = {"big_negative": [*"abc"], "big_positive": [*"abc"]}

class shadow_mesh(common.base): # LUMP 7F (0127)
    __slots__ = ["start_index", "num_triangles", "unknown"]
    _format = "2I2h" # assuming 12 bytes
    _arrays = {"unknown": ["one", "negative_one"]}

class texture_data(common.base): # LUMP 2 (0002)
    __slots__ = ["unknown", "string_table_index", "unknown2"]
    _format = "9i"
    _arrays = {"unknown": [*"abc"], "unknown2": [*"abcde"]}
    
class unlit_vertex(common.base): # LUMP 71 (0047)
    __slots__ = ["position_index", "normal_index", "uv", "unknown"]
    _format = "2i2fi" # 20 bytes
    _arrays = {"uv": [*"uv"]}

class unlit_ts_vertex(common.base): # LUMP 74 (004A)
    __slots__ = ["position_index", "normal_index", "uv", "unknown"]
    _format = "2i2f3i" # 28 bytes
    _arrays  = {"uv": [*"uv"], "unknown": [*"abc"]}

class vertex(common.mapped_array): # LUMP 3 (0003)
    _mapping = [*"xyz"]
    _format = "3f"
    flat = lambda self: [self.x, self.y, self.z]
    
lump_classes = {"CM_BRUSHES": brush, "MATERIAL_SORT": material_sort,
                "MODELS": model, "TEXDATA": texture_data,
                "VERTEX_NORMALS": vertex, "VERTICES": vertex,
                "VERTS_LIT_BUMP": bump_lit_vertex, "VERTS_UNLIT": unlit_vertex,
                "VERTS_UNLIT_TS": unlit_ts_vertex, "MESHES": mesh,
                "MESH_INDICES": mesh_indices}


# BSP METHODS EXCLUSIVE TO THIS MOD:
mesh_types = {0x600: "VERTS_UNLIT_TS",
              0x400: "VERTS_UNLIT",
              0x200: "VERTS_LIT_BUMP"}
# ^ a proper mapping of the flags would be nice

# https://raw.githubusercontent.com/Wanty5883/Titanfall2/master/tools/TitanfallMapExporter.py
def tris_of(bsp, mesh_index): # simplified from McSimp's exporter ^
    mesh = bsp.MESHES[mesh_index]
    mat = bsp.MATERIAL_SORT[mesh.material_sort]
    start = mesh.start_index
    finish = start + mesh.num_triangles * 3
    indices = bsp.MESH_INDICES[start:finish]
    indices = [mat.vertex_offset + i for i in indices]
    verts = getattr(bsp, mesh_types[mesh.flags & 0x600])
    return [verts[i] for i in indices]
