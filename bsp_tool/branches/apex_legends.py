import enum

from . import common


bsp_version = 47

# Apex Legends has rBSP file-magic, ~128 lumps & uses .bsp_lump files:
#   <bsp filename>.<ID>.bsp_lump
#   where <ID> is a four digit hexadecimal string (lowercase)
# entities are stored in 5 different .ent files per bsp

# note which lumps appear in the .bsp, which have .bsp_lump files,
# and which have both

# mp_rr_canyonlands_mu2.bsp has .bsp_lump files for the following:
# 0000 ENTITIES               0
# 0001 PLANES                 1
# 0002 TEXDATA                2
# 0003 VERTICES               3
# 0004 UNKNOWN_4              4
# 0005 UNKNOWN_5              5
# ...
# 000E MODELS                14
# 000F UNKNOWN_15            15
# 0010 UNKNOWN_16            16
# 0011 UNKNOWN_17            17
# 0012 UNKNOWN_18            18
# 0013 UNKNOWN_19            19
# 0014 UNKNOWN_20            20
# ...
# 0018 ENTITIY_PARTITIONS    24
# ...
# 001E VERTEX_NORMALS        30
# ...
# 0023 GAME_LUMP             35
# ...
# 0025 UNKNOWN_37            37
# 0026 UNKNOWN_38            38
# 0027 UNKNOWN_39            39
# 0028 PAKFILE               40 [zip with PK file-magic] (contains cubemaps)
# ...
# 002A CUBEMAPS              42
# ...
# 0036 WORLDLIGHTS_HDR       54
# 0037 UNKNOWN_55            55
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
# ...
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


class LUMP(enum.Enum):
    ENTITIES = 0  # there are more entities in external .ent files
    PLANES = 1
    TEXDATA = 2
    VERTICES = 3
    UNKNOWN_4 = 4  #
    UNKNOWN_5 = 5  #
    UNUSED_6 = 6
    UNUSED_7 = 7
    UNUSED_8 = 8
    UNUSED_9 = 9
    UNUSED_10 = 10
    UNUSED_11 = 11
    UNUSED_12 = 12
    UNUSED_13 = 13
    MODELS = 14
    UNKNOWN_16 = 16  #
    UNKNOWN_17 = 17  #
    UNKNOWN_18 = 18  #
    UNKNOWN_19 = 19  #
    UNKNOWN_20 = 20  #
    UNKNOWN_21 = 21  #
    UNUSED_22 = 22
    UNUSED_23 = 23
    ENTITY_PARTITIONS = 24
    UNKNOWN_25 = 25  #
    UNUSED_26 = 26
    UNUSED_27 = 27
    UNUSED_28 = 28
    UNUSED_29 = 29
    VERTEX_NORMALS = 30
    UNKNOWN_31 = 31  #
    UNUSED_32 = 32
    UNUSED_33 = 33
    UNUSED_34 = 34
    GAME_LUMP = 35
    LEAF_WATERDATA = 36  # leaf? does apex have visleaves?
    UNKNOWN_37 = 37  #
    UNKNOWN_38 = 38  #
    UNKNOWN_39 = 39  #
    PAKFILE = 40  # zip file, contains cubemaps [citation needed]
    UNKNOWN_41 = 41  #
    CUBEMAPS = 42
    TEXDATA_STRING_DATA = 43
    UNUSED_44 = 44
    UNUSED_45 = 45
    UNUSED_46 = 46
    UNUSED_47 = 47
    UNUSED_48 = 48
    UNUSED_49 = 49
    UNUSED_50 = 50
    UNUSED_51 = 51
    UNUSED_52 = 52
    UNUSED_53 = 53
    WORLDLIGHTS_HDR = 54  # does apex have LDR?
    UNKNOWN_55 = 55  #
    UNKNOWN_66 = 56  #
    UNUSED_57 = 57
    UNUSED_58 = 58
    UNKNOWN_59 = 59  #
    UNUSED_60 = 60
    UNUSED_61 = 61
    PHYS_LEVEL = 62
    UNUSED_63 = 63
    UNUSED_64 = 64
    UNUSED_65 = 65
    UNUSED_66 = 66
    UNUSED_67 = 67
    UNUSED_68 = 68
    UNUSED_69 = 69
    UNUSED_70 = 70
    VERTS_UNLIT = 71
    VERTS_LIT_FLAT = 72
    VERTS_LIT_BUMP = 73
    VERTS_UNLIT_TS = 74
    VERTS_BLINN_PHONG = 75
    UNUSED_76 = 76
    UNUSED_77 = 77
    VERTS_RESERVED_7 = 78  # may not be
    MESH_INDICES = 79
    MESHES = 80
    MESH_BOUNDS = 81
    MATERIAL_SORT = 82  # MATERIAL_SORT
    LIGHTMAP_HEADERS = 83
    LIGHTMAP_DATA_DXT5 = 84  #
    CM_GRID = 85
    CM_GRIDCELLS = 86
    CM_GEO_SETS = 87
    CM_GEO_SET_BOUNDS = 88
    CM_PRIMS = 89
    CM_PRIM_BOUNDS = 90
    UNUSED_91 = 91
    CM_BRUSHES = 92
    UNUSED_93 = 93
    UNUSED_94 = 94
    UNUSED_95 = 95
    UNUSED_96 = 96
    UNUSED_97 = 97
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


lump_header_address = {LUMP_ID: (16 + i * 16) for i, LUMP_ID in enumerate(LUMP)}


# classes for lumps (alphabetical order)
class MaterialSort(common.Base):  # LUMP 82 (0052)
    __slots__ = ["texdata", "unknown", "vertex_offset"]
    _format = "2h2I"  # 12 bytes
    _arrays = {"unknown": [*"ab"]}


class Mesh(common.Base):  # LUMP 80 (0050)
    __slots__ = ["start_index", "num_triangles", "unknown",
                 "material_sort", "flags"]
    # vertex type stored in flags
    _format = "IH3I2HI"  # 28 bytes
    _arrays = {"unknown": [*"abcd"]}


class MeshIndices(int):  # LUMP 79 (004F)
    _format = "H"


class Model(common.Base):  # LUMP 14 (000E)
    __slots__ = ["big_negative", "big_positive", "small_int", "tiny_int"]
    _format = "8i"
    _arrays = {"big_negative": [*"abc"], "big_positive": [*"abc"]}


class ShadowMesh(common.Base):  # LUMP 7F (0127)
    __slots__ = ["start_index", "num_triangles", "unknown"]
    _format = "2I2h"  # assuming 12 bytes
    _arrays = {"unknown": ["one", "negative_one"]}


class TextureData(common.Base):  # LUMP 2 (0002)
    __slots__ = ["unknown", "string_table_index", "unknown2"]
    _format = "9i"  # WRONG SIZE (8384 / 36)
    _arrays = {"unknown": [*"abc"], "unknown2": [*"abcde"]}


class Vertex(common.MappedArray):  # LUMP 3 (0003)
    _mapping = [*"xyz"]
    _format = "3f"

    def flat(self):
        return [self.x, self.y, self.z]


class VertexBlinnPhong(common.Base):  # LUMP 75 (004B)
    __slots__ = ["position_index", "normal_index", "uv", "uv2"]
    _format = "2I4f"  # 24 bytes
    _arrays = {"uv": [*"uv"], "uv2": [*"uv"]}


class VertexLitBump(common.Base):  # LUMP 73 (0049)
    __slots__ = ["position_index", "normal_index", "uv", "negative_one", "unknown"]
    _format = "2I2fi3f"  # 32 bytes
    _arrays = {"uv": [*"uv"], "unknown": [*"abc"]}


class VertexLitFlat(common.Base):  # LUMP 72 (0048)
    __slots__ = ["position_index", "normal_index", "uv", "unknown"]
    _format = "2I2fi"  # 20 bytes
    _arrays = {"uv": [*"uv"]}


class VertexUnlit(common.Base):  # LUMP 71 (0047)
    __slots__ = ["position_index", "normal_index", "uv", "unknown"]
    _format = "2i2fi"  # 20 bytes
    _arrays = {"uv": [*"uv"]}


class VertexUnlitTS(common.Base):  # LUMP 74 (004A)
    __slots__ = ["position_index", "normal_index", "uv", "uv2"]
    _format = "2I4f"  # 24 bytes
    _arrays = {"uv": [*"uv"], "uv2": [*"uv"]}


lump_classes = {"MATERIAL_SORT": MaterialSort,
                "MESHES": Mesh,
                "MESH_INDICES": MeshIndices,
                "MODELS": Model,
                "TEXDATA": TextureData,
                "VERTEX_NORMALS": Vertex,
                "VERTICES": Vertex,
                "VERTS_BLINN_PHONG": VertexBlinnPhong,
                "VERTS_LIT_BUMP": VertexLitBump,
                "VERTS_LIT_FLAT": VertexLitFlat,
                "VERTS_UNLIT": VertexUnlit,
                "VERTS_UNLIT_TS": VertexUnlitTS}


# METHODS EXCLUSIVE TO THIS MOD:
mesh_types = {0x600: "VERTS_UNLIT_TS",
              0x610: "VERTS_BLINN_PHONG",
              0x400: "VERTS_UNLIT",
              0x200: "VERTS_LIT_BUMP",
              0x210: "VERTS_LIT_FLAT"}
# a function mapping mesh.flags to vertex lumps would be better


def vertices_of_mesh(bsp, mesh_index):
    mesh = bsp.MESHES[mesh_index]
    mat = bsp.MATERIAL_SORT[mesh.material_sort]
    start = mesh.start_index
    finish = start + mesh.num_triangles * 3
    indices = bsp.MESH_INDICES[start:finish]
    indices = [mat.vertex_offset + i for i in indices]
    # select vertex lump from mesh.MAP_FLAGS
    mesh_type = list(filter(lambda k: mesh.flags & k == k, mesh_types))[0]
    verts = getattr(bsp, mesh_types[mesh_type])
    return [verts[i] for i in indices]

# look at bsp_tool_examples/visualise/render_bsp.py
# assembling vertex buffers in a requested format would be cool


methods = [vertices_of_mesh]
