import enum

from .. import base
from .. import shared
from ..valve import orange_box
from . import titanfall2


BSP_VERSION = 29


class LUMP(enum.Enum):  # copy of Titanfall 2's lump names & ids
    ENTITIES = 0
    PLANES = 1  # version 1
    TEXDATA = 2  # version 1
    VERTICES = 3
    UNUSED_4 = 4
    UNUSED_5 = 5
    UNUSED_6 = 6
    UNUSED_7 = 7
    UNUSED_8 = 8
    UNUSED_9 = 9
    UNUSED_10 = 10
    UNUSED_11 = 11
    UNUSED_12 = 12
    UNUSED_13 = 13
    MODELS = 14
    UNUSED_15 = 15
    UNUSED_16 = 16
    UNUSED_17 = 17
    UNUSED_18 = 18
    UNUSED_19 = 19
    UNUSED_20 = 20
    UNUSED_21 = 21
    UNUSED_22 = 22
    UNUSED_23 = 23
    ENTITY_PARTITIONS = 24
    UNUSED_25 = 25
    UNUSED_26 = 26
    UNUSED_27 = 27
    UNUSED_28 = 28
    PHYS_COLLIDE = 29
    VERTEX_NORMALS = 30
    UNUSED_31 = 31
    UNUSED_32 = 32
    UNUSED_33 = 33
    UNUSED_34 = 34
    GAME_LUMP = 35
    LEAF_WATERDATA = 36
    UNUSED_37 = 37
    UNUSED_38 = 38
    UNUSED_39 = 39
    PAKFILE = 40  # zip file, contains cubemaps
    UNKNOWN_41 = 41
    CUBEMAPS = 42
    TEXDATA_STRING_DATA = 43
    TEXDATA_STRING_TABLE = 44
    UNUSED_45 = 45
    UNUSED_46 = 46
    UNUSED_47 = 47
    UNUSED_48 = 48
    UNUSED_49 = 49
    UNUSED_50 = 50
    UNUSED_51 = 51
    UNUSED_52 = 52
    UNUSED_53 = 53
    WORLDLIGHTS_HDR = 54
    UNUSED_55 = 55
    UNUSED_56 = 56
    UNUSED_57 = 57
    UNUSED_58 = 58
    UNUSED_59 = 59
    UNUSED_60 = 60
    UNUSED_61 = 61
    PHYS_LEVEL = 62  # length 0, version 6?
    UNUSED_63 = 63
    UNUSED_64 = 64
    UNUSED_65 = 65
    TRICOLL_TRIS = 66
    UNUSED_67 = 67
    TRICOLL_NODES = 68
    TRICOLL_HEADERS = 69
    PHYSTRIS = 70
    VERTS_UNLIT = 71  # VERTS_RESERVED_0 - 7
    VERTS_LIT_FLAT = 72
    VERTS_LIT_BUMP = 73  # version 2
    VERTS_UNLIT_TS = 74
    VERTS_BLINN_PHONG = 75  # version 1
    VERTS_RESERVED_5 = 76  # version 1
    VERTS_RESERVED_6 = 77
    VERTS_RESERVED_7 = 78
    MESH_INDICES = 79  # version 1
    MESHES = 80  # version 1
    MESH_BOUNDS = 81
    MATERIAL_SORT = 82
    LIGHTMAP_HEADERS = 83
    LIGHTMAP_DATA_DXT5 = 84
    CM_GRID = 85
    CM_GRIDCELLS = 86
    CM_GEO_SETS = 87
    CM_GEO_SET_BOUNDS = 88
    CM_PRIMS = 89
    CM_PRIM_BOUNDS = 90  # version 1
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


lump_header_address = {LUMP_ID: (16 + i * 16) for i, LUMP_ID in enumerate(LUMP)}


# classes for lumps (alphabetical order) [X / 128] + shared.Entites
LUMP_CLASSES = titanfall2.LUMP_CLASSES
LUMP_CLASSES["FACES"] = orange_box.Face
LUMP_CLASSES["TEXINFO"] = orange_box.TextureInfo
LUMP_CLASSES["NODES"] = orange_box.Node

SPECIAL_LUMP_CLASSES = {"ENTITIES": shared.Entities,
                        "TEXDATA_STRING_DATA": shared.TexDataStringData}
# VISIBILITY


# branch exclusive methods, in alphabetical order:
methods = [*titanfall2.methods]
