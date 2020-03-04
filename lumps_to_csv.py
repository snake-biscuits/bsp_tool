of = open("mp_drydock.csv", "w")

# change to process multiple bsps
# find the common denominator of lump sizes
# as well as the common denominator of the differences -
# between each lump of the same type
# once split into these sizes "69B" etc. analysis can begin

def line(x, name):
    try:
        with open(f"mp_drydock.bsp.{x:04x}.bsp_lump", "rb") as lump:
            size = len(lump.read())
    except:
        return
    of.write(f"{x},{name},{x:04x},{size}\n")

class LUMP(enum.Enum):
    ENTITIES = 0 # entities are stored across multiple text files
    PLANES = 1
    TEXDATA = 2
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
    UNUSED_41 = 41
    CUBEMAPS = 42
    TEXDATA_STRING_DATA = 43
    TEXDATA_STRING_TABLE = 44
    UNUSED_45 = 45
    UNKNOWN_46 = 46
    UNKNOWN_47 = 47
    UNKNOWN_48 = 48
    UNKNOWN_49 = 49
    UNKNOWN_50 = 50
    UNKNOWN_51 = 51
    UNKNOWN_52 = 52
    UNUSED_53 = 53
    WORLDLIGHTS_HDR = 54
    UNUSED_59 = 59
    PHYS_LEVEL = 62
    UNKNOWN_63 = 63
    UNKNOWN_64 = 64
    UNKNOWN_65 = 65
    TRICOLL_TRIS = 66
    UNKNOWN_67 = 67
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

for e in LUMP:
    line(e.value, e.name)

of.close()

