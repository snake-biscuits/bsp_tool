import enum
from typing import List

from .. import base
from .. import shared
from . import titanfall, titanfall2


BSP_VERSION = 47  # Olympus is v48 & canyonlands_staging is v49

GAMES = ["Apex Legends"]

# Apex Legends has b"rBSP" file-magic and 128 lumps
# ~72 of the 128 lumps appear in .bsp_lump files
# the naming convention for these files is: "<bsp.filename>.<LUMP_HEX_ID>.bsp_lump"
# where <LUMP_HEX_ID> is a lowercase four digit hexadecimal string
# e.g. mp_rr_canyonlands.004a.bsp_lump (Lump #74: VertexUnlitTS)
# entities are stored across 5 different .ent files per .bsp
# the 5 files are: env, fx, script, snd, spawn
# NOTE: the ENTITY_PARTITIONS lump may define which of these a .bsp is to use
# e.g. mp_rr_canyonlands_env.ent  # kings canyon lighting, fog etc.
# presumably all this file splitting has to do with streaming data into memory
# each .ent file has a header similar to: ENTITIES02 model_count=28
# model_count appears to be the same across all .ent files for a given .bsp


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
    CONTENT_MASKS = 0x0010
    SURFACE_PROPERTIES = 0x0011
    BVH_NODES = 0x0012
    BVH_LEAF_DATA = 0x0013
    PACKED_VERTICES = 0x0014
    UNUSED_21 = 0x0015
    UNUSED_22 = 0x0016
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
    UNKNOWN_38 = 0x0026
    UNKNOWN_39 = 0x0027  # connected to VIS lumps
    PAKFILE = 0x0028  # zip file, contains cubemaps
    UNUSED_41 = 0x0029
    CUBEMAPS = 0x002A
    UNKNOWN_43 = 0x002B
    UNUSED_44 = 0x002C
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
    MATERIAL_SORT = 0x0052
    LIGHTMAP_HEADERS = 0x0053
    UNUSED_84 = 0x0054
    CM_GRID = 0x0055
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
    UNKNOWN_97 = 0x0061
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
    LIGHTMAP_DATA_RTL_PAGE = 0x007A
    LEVEL_INFO = 0x007B
    SHADOW_MESH_OPAQUE_VERTS = 0x007C
    SHADOW_MESH_ALPHA_VERTS = 0x007D
    SHADOW_MESH_INDICES = 0x007E
    SHADOW_MESH_MESHES = 0x007F

# Known lump changes from Titanfall 2 -> Apex Legends:
# New:
#   UNUSED_15 -> SURFACE_NAMES
#   UNUSED_16 -> CONTENT_MASKS
#   UNUSED_17 -> SURFACE_PROPERTIES
#   UNUSED_18 -> BVH_NODES
#   UNUSED_19 -> BVH_LEAF_DATA
#   UNUSED_20 -> PACKED_VERTICES
#   UNUSED_37 -> UNKNOWN_37
#   UNUSED_38 -> UNKNOWN_38
#   UNUSED_39 -> UNKNOWN_39
#   TEXTURE_DATA_STRING_DATA -> UNKNOWN_43
#   TRICOLL_BEVEL_INDICES -> UNKNOWN_97
# Deprecated:
#   LIGHTPROBE_BSP_NODES
#   LIGHTPROBE_BSP_REF_IDS
#   PHYSICS_COLLIDE
#   LEAF_WATER_DATA
#   TEXTURE_DATA_STRING_TABLE
#   PHYSICS_LEVEL
#   TRICOLL_TRIS
#   TRICOLL_NODES
#   TRICOLL_HEADERS
#   CM_GRID_CELLS
#   CM_GEO_SETS
#   CM_GEO_SET_BOUNDS
#   CM_PRIMITIVES
#   CM_PRIMITIVE_BOUNDS
#   CM_UNIQUE_CONTENTS
#   CM_BRUSHES
#   CM_BRUSH_SIDE_PLANE_OFFSETS
#   CM_BRUSH_SIDE_PROPS
#   CM_BRUSH_TEX_VECS
#   TRICOLL_BEVEL_STARTS

# Rough map of the relationships between lumps:
# Model -> Mesh -> MaterialSort -> TextureData -> SurfaceName
#                              |-> VertexReservedX
#                              |-> MeshIndex?
#
# MeshBounds & Mesh (must have equal number of each)
#
# VertexReservedX -> Vertex
#                |-> VertexNormal
#
# ??? -> ShadowMeshIndices -?> ShadowMesh -> ???
# ??? -> Brush -?> Plane
#
# LightmapHeader -> LIGHTMAP_DATA_SKY
#               |-> LIGHTMAP_DATA_REAL_TIME_LIGHTS
#
# Portal -?> PortalEdge -> PortalVertex
# PortalEdgeRef -> PortalEdge
# PortalVertRef -> PortalVertex
# PortalEdgeIntersect -> PortalEdge?
#                    |-> PortalVertex
#
# PortalEdgeIntersectHeader -> ???
# NOTE: there are always as many intersect headers as edges
# NOTE: there are also always as many vert refs as edge refs
#
# Grid probably defines the bounds of CM_GRID_CELLS, with CM_GRID_CELLS indexing other objects?


lump_header_address = {LUMP_ID: (16 + i * 16) for i, LUMP_ID in enumerate(LUMP)}


# # classes for lumps, in alphabetical order:
# NOTE: LightmapHeader.count doesn't look like a count, quite off in general

class MaterialSort(base.Struct):  # LUMP 82 (0052)
    texture_data: int  # index of this MaterialSort's TextureData
    lightmap_index: int  # index of this MaterialSort's LightmapHeader (can be -1)
    unknown: List[int]  # ({0?}, {??..??})
    vertex_offset: int  # offset into appropriate VERTEX_RESERVED_X lump
    __slots__ = ["texture_data", "lightmap_index", "unknown", "vertex_offset"]
    _format = "4hI"  # 12 bytes
    _arrays = {"unknown": 2}


class Mesh(base.Struct):  # LUMP 80 (0050)
    first_mesh_index: int  # index into this Mesh's VertexReservedX
    num_triangles: int  # number of triangles in VertexReservedX after first_mesh_index
    # start_vertices: int  # index to this Mesh's first VertexReservedX
    # num_vertices: int
    unknown: List[int]
    # for mp_box.VERTEX_LIT_BUMP: (2, -256, -1,  ?,  ?,  ?)
    # for mp_box.VERTEX_UNLIT:    (0,   -1, -1, -1, -1, -1)
    material_sort: int  # index of this Mesh's MaterialSort
    flags: int  # Flags(mesh.flags & Flags.MASK_VERTEX).name == "VERTEX_RESERVED_X"
    __slots__ = ["start_index", "num_triangles", "unknown", "material_sort", "flags"]
    # vertex type stored in flags
    _format = "IH3I2HI"  # 28 bytes
    _arrays = {"unknown": 4}


class Model(base.Struct):  # LUMP 14 (000E)
    mins: List[float]  # AABB mins
    maxs: List[float]  # AABB maxs
    first_mesh: int
    num_meshes: int
    unknown: List[int]  # \_(;/)_/
    __slots__ = ["mins", "maxs", "first_mesh", "num_meshes", "unknown"]
    _format = "6f2I8i"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"], "unknown": 8}


class ShadowMesh(base.Struct):  # LUMP 7F (0127)
    start_index: int  # assumed
    num_triangles: int  # assumed
    unknown: List[int]  # usually (1, -1)
    __slots__ = ["start_index", "num_triangles", "unknown"]
    _format = "2I2h"  # assuming 12 bytes
    _arrays = {"unknown": 2}


class TextureData(base.Struct):  # LUMP 2 (0002)
    # very unsure
    name_index: int  # index of this TextureData's surface name
    width: int  # powers of 2?
    height: int  # powers of 2?
    flags: int  # OR'd powers of 2?
    __slots__ = ["name_index", "width", "height", "flags"]
    _format = "4i"


class VertexBlinnPhong(base.Struct):  # LUMP 75 (004B)
    __slots__ = ["position_index", "normal_index", "uv", "uv2"]
    _format = "2I4f"  # 24 bytes
    _arrays = {"uv": [*"uv"], "uv2": [*"uv"]}


class VertexLitBump(base.Struct):  # LUMP 73 (0049)
    __slots__ = ["position_index", "normal_index", "uv", "negative_one", "unknown"]
    _format = "2I2fi3f"  # 32 bytes
    _arrays = {"uv": [*"uv"], "unknown": 3}


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


# NOTE: all Apex lumps are version 0
# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = titanfall2.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = titanfall2.LUMP_CLASSES.copy()
LUMP_CLASSES.update({"LIGHTMAP_HEADERS":   {0: titanfall.LightmapHeader},
                     "MATERIAL_SORT":      {0: MaterialSort},
                     "MESHES":             {0: Mesh},
                     "MODELS":             {0: Model},
                     "PLANES":             {0: titanfall.Plane},
                     "TEXTURE_DATA":       {0: TextureData},
                     "VERTEX_BLINN_PHONG":  {0: VertexBlinnPhong},
                     "VERTEX_LIT_BUMP":     {0: VertexLitBump},
                     "VERTEX_LIT_FLAT":     {0: VertexLitFlat},
                     "VERTEX_UNLIT":        {0: VertexUnlit},
                     "VERTEX_UNLIT_TS":     {0: VertexUnlitTS}})
LUMP_CLASSES.pop("CM_GRID")

SPECIAL_LUMP_CLASSES = titanfall2.SPECIAL_LUMP_CLASSES.copy()
SPECIAL_LUMP_CLASSES.pop("TEXTURE_DATA_STRING_DATA")
SPECIAL_LUMP_CLASSES.update({"SURFACE_NAMES": {0: shared.TextureDataStringData}})

# NOTE: Apex GAME_LUMP.sprp versions are the same as BSP_VERSION
GAME_LUMP_CLASSES = {"sprp": {47: lambda raw_lump: titanfall2.GameLump_SPRP(raw_lump, titanfall2.StaticPropv13),
                              48: lambda raw_lump: titanfall2.GameLump_SPRP(raw_lump, titanfall2.StaticPropv13),
                              49: lambda raw_lump: titanfall2.GameLump_SPRP(raw_lump, titanfall2.StaticPropv13)}}


# branch exclusive methods, in alphabetical order:
def get_mesh_texture(bsp, mesh_index: int) -> str:
    """Returns the name of the .vmt applied to bsp.MESHES[mesh_index]"""
    mesh = bsp.MESHES[mesh_index]
    material_sort = bsp.MATERIAL_SORT[mesh.material_sort]
    texture_data = bsp.TEXTURE_DATA[material_sort.texture_data]
    return bsp.SURFACE_NAMES[texture_data.name_index]


methods = [titanfall.vertices_of_mesh, titanfall.vertices_of_model,
           titanfall.search_all_entities, shared.worldspawn_volume,
           get_mesh_texture]
