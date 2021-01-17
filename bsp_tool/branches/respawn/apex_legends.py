import enum

from .. import base
from .. import shared  # special lumps


BSP_VERSION = 47  # Olympus is version 48
# how to load for 2 different .bsp versions?
# will need to tackle this to handle lump versions too...

# Apex Legends has b"rBSP" file-magic and 128 lumps
# ~72 of the 128 lumps appear in .bsp_lump files
# the naming convention for these files is: "<bsp.filename>.<LUMP_HEX_ID>.bsp_lump"
# where <LUMP_HEX_ID> is a lowercase four digit hexadecimal string
# e.g. mp_rr_canyonlands.004a.bsp_lump (Lump #74: VertexUnlitTS)
# entities are stored across 5 different .ent files per .bsp
# the 5 files are: env, fx, script, snd, spawn
# e.g. mp_rr_canyonlands_env.ent  # kings canyon lighting, fog etc.
# presumably all this file splitting has to do with streaming data into memory
# each .ent file has a header similar to: ENTITIES02 model_count=28
# model_count appears to be the same across all .ent files for a given .bsp


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
class MaterialSort(base.Struct):  # LUMP 82 (0052)
    __slots__ = ["texdata", "unknown", "vertex_offset"]
    _format = "2h2I"  # 12 bytes
    _arrays = {"unknown": [*"ab"]}


class Mesh(base.Struct):  # LUMP 80 (0050)
    __slots__ = ["start_index", "num_triangles", "unknown",
                 "material_sort", "flags"]
    # vertex type stored in flags
    _format = "IH3I2HI"  # 28 bytes
    _arrays = {"unknown": [*"abcd"]}


class MeshIndices(int):  # LUMP 79 (004F)
    _format = "H"


class Model(base.Struct):  # LUMP 14 (000E)
    __slots__ = ["big_negative", "big_positive", "small_int", "tiny_int"]
    _format = "8i"
    _arrays = {"big_negative": [*"abc"], "big_positive": [*"abc"]}


class ShadowMesh(base.Struct):  # LUMP 7F (0127)
    __slots__ = ["start_index", "num_triangles", "unknown"]
    _format = "2I2h"  # assuming 12 bytes
    _arrays = {"unknown": ["one", "negative_one"]}


class TextureData(base.Struct):  # LUMP 2 (0002)
    __slots__ = ["unknown", "string_table_index", "unknown2"]
    _format = "9i"  # WRONG SIZE (8384 / 36)
    _arrays = {"unknown": [*"abc"], "unknown2": [*"abcde"]}


class Vertex(base.MappedArray):  # LUMP 3 (0003)
    _mapping = [*"xyz"]
    _format = "3f"

    def flat(self):
        return [self.x, self.y, self.z]


class VertexBlinnPhong(base.Struct):  # LUMP 75 (004B)
    __slots__ = ["position_index", "normal_index", "uv", "uv2"]
    _format = "2I4f"  # 24 bytes
    _arrays = {"uv": [*"uv"], "uv2": [*"uv"]}


class VertexLitBump(base.Struct):  # LUMP 73 (0049)
    __slots__ = ["position_index", "normal_index", "uv", "negative_one", "unknown"]
    _format = "2I2fi3f"  # 32 bytes
    _arrays = {"uv": [*"uv"], "unknown": [*"abc"]}


class VertexLitFlat(base.Struct):  # LUMP 72 (0048)
    __slots__ = ["position_index", "normal_index", "uv", "unknown"]
    _format = "2I2fi"  # 20 bytes
    _arrays = {"uv": [*"uv"]}


class VertexUnlit(base.Struct):  # LUMP 71 (0047)
    __slots__ = ["position_index", "normal_index", "uv", "unknown"]
    _format = "2i2fi"  # 20 bytes
    _arrays = {"uv": [*"uv"]}


class VertexUnlitTS(base.Struct):  # LUMP 74 (004A)
    __slots__ = ["position_index", "normal_index", "uv", "uv2"]
    _format = "2I4f"  # 24 bytes
    _arrays = {"uv": [*"uv"], "uv2": [*"uv"]}


LUMP_CLASSES = {"MATERIAL_SORT": MaterialSort,
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

SPECIAL_LUMP_CLASSES = {"ENTIITES": shared.Entities}  # used on all 5 .ent files


# branch exclusive methods, in alphabetical order:
mesh_types = {0x600: "VERTS_UNLIT_TS",
              0x610: "VERTS_BLINN_PHONG",
              0x400: "VERTS_UNLIT",
              0x200: "VERTS_LIT_BUMP",
              0x210: "VERTS_LIT_FLAT"}
# a function mapping mesh.flags to vertex lumps would be better


def vertices_of_mesh(bsp, mesh_index: int):
    mesh = bsp.MESHES[mesh_index]
    mat = bsp.MATERIAL_SORT[mesh.material_sort]
    start = mesh.start_index
    finish = start + mesh.num_triangles * 3
    indices = bsp.MESH_INDICES[start:finish]
    indices = [mat.vertex_offset + i for i in indices]
    mesh_type = list(filter(lambda k: mesh.flags & k == k, mesh_types))[0]
    verts = getattr(bsp, mesh_types[mesh_type])  # get bsp.VERTS_* lump
    return [verts[i] for i in indices]


methods = [vertices_of_mesh]
