import enum
from typing import List

from .. import base
from .. import shared
from ..valve import source
from . import titanfall
from . import titanfall2


FILE_MAGIC = b"rBSP"

BSP_VERSION = 47

launch = "depot/r5launch/game/r2/maps"
staging = "depot/r5staging/game/r2/maps"
r5100 = "depot/r5-100/game/r2/maps"
r5101 = "depot/r5-101/game/r2/maps"
r5110 = "depot/r5-110/game/r2/maps"
r5111 = "depot/r5-111/game/r2/maps"

GAME_PATHS = {"Apex Legends": "ApexLegends/maps",
              "Apex Legends: Season 2 - Battle Charge": "ApexLegends/season2/maps",
              "Apex Legends: Season 3 - Meltdown": "ApexLegends/season3/maps",
              "Apex Legends: Season 3 - Meltdown (launch)": f"ApexLegends/season3/{launch}",
              "Apex Legends: Season 3 - Meltdown (staging)": f"ApexLegends/season3/{staging}",
              "Apex Legends: Season 3 - Meltdown [30 Oct Patch]": "ApexLegends/season3_30oct19/maps",
              "Apex Legends: Season 3 - Meltdown [30 Oct Patch] (launch)": f"ApexLegends/season3_30oct19/{launch}",
              "Apex Legends: Season 3 - Meltdown [30 Oct Patch] (staging)": f"ApexLegends/season3_30oct19/{staging}",
              "Apex Legends: Season 3 - Meltdown [3 Dec Patch]": "ApexLegends/season3_3dec19/maps",
              "Apex Legends: Season 3 - Meltdown [3 Dec Patch] (launch)": f"ApexLegends/season3_3dec19/{launch}",
              "Apex Legends: Season 3 - Meltdown [3 Dec Patch] (staging)": f"ApexLegends/season3_3dec19/{staging}",
              "Apex Legends: Season 5 - Fortune's Favor": "ApexLegends/season5/maps",
              "Apex Legends: Season 8 - Mayhem": "ApexLegends/season8/maps",
              "Apex Legends: Season 9 - Legacy": "ApexLegends/season9/maps",
              "Apex Legends: Season 10 - Emergence [3 Aug Patch]": "ApexLegends/season10_3aug21/maps/",
              "Apex Legends: Season 10 - Emergence [10 Aug Patch]": "ApexLegends/season10_10aug21/maps/",
              "Apex Legends: Season 10 - Emergence [10 Aug Patch] (100)": f"ApexLegends/season10_10aug21/{r5100}",
              "Apex Legends: Season 10 - Emergence [14 Sep Patch]": "ApexLegends/season10_14sep21/maps/",
              "Apex Legends: Season 10 - Emergence [14 Sep Patch] (100)": f"ApexLegends/season10_14sep21/{r5100}",
              "Apex Legends: Season 10 - Emergence [14 Sep Patch] (101)": f"ApexLegends/season10_14sep21/{r5101}",
              "Apex Legends: Season 10 - Emergence [24 Sep Patch]": "ApexLegends/season10_24sep21/maps/",
              "Apex Legends: Season 10 - Emergence [24 Sep Patch] (100)": f"ApexLegends/season10_24sep21/{r5100}",
              "Apex Legends: Season 10 - Emergence [24 Sep Patch] (101)": f"ApexLegends/season10_24sep21/{r5101}",
              "Apex Legends: Season 11 - Escape": "ApexLegends/season11/maps",
              "Apex Legends: Season 11 - Escape (110)": f"ApexLegends/season11/{r5110}",
              "Apex Legends: Season 11 - Escape [6 Nov Patch]": "ApexLegends/season11_6nov21/maps",
              "Apex Legends: Season 11 - Escape [6 Nov Patch] (110)": f"ApexLegends/season11_6nov21/{r5110}",
              "Apex Legends: Season 11 - Escape [19 Nov Patch]": "ApexLegends/season11_19nov21/maps",
              "Apex Legends: Season 11 - Escape [19 Nov Patch] (110)": f"ApexLegends/season11_19nov21/{r5110}",
              "Apex Legends: Season 11 - Escape [19 Nov Patch] (111)": f"ApexLegends/season11_19nov21/{r5111}"}

GAME_VERSIONS = {"Apex Legends": 47,
                 "Apex Legends: Season 7 - Ascension": 48,  # Olympus
                 "Apex Legends: Season 8 - Mayhem": 49,  # King's Canyon map update 3
                 "Apex Legends: Season 10 - Emergence": 50,  # Arenas: Encore / SkyGarden
                 "Apex Legends: Season 11 - Escape [19 Nov Patch] (110)": 49,
                 "Apex Legends: Season 11 - Escape [19 Nov Patch] (111)": (49, 1),
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
    UNKNOWN_38 = 0x0026  # connected to CSM lumps
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
    CM_GRID = 0x0055  # Tweaklights?
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
    PORTAL_EDGE_INTERSECT_EDGE = 0x0072
    PORTAL_EDGE_INTERSECT_AT_VERTEX = 0x0073
    PORTAL_EDGE_INTERSECT_HEADER = 0x0074
    OCCLUSION_MESH_VERTICES = 0x0075
    OCCLUSION_MESH_INDICES = 0x0076
    CELL_AABB_NODES = 0x0077
    OBJ_REFERENCES = 0x0078
    OBJ_REFERENCE_BOUNDS = 0x0079
    LIGHTMAP_DATA_RTL_PAGE = 0x007A
    LEVEL_INFO = 0x007B
    SHADOW_MESH_OPAQUE_VERTICES = 0x007C
    SHADOW_MESH_ALPHA_VERTICES = 0x007D
    SHADOW_MESH_INDICES = 0x007E
    SHADOW_MESH_MESHES = 0x007F


# struct RespawnBspHeader { char file_magic[4]; int version, revision, lump_count; SourceLumpHeader headers[128]; };
lump_header_address = {LUMP_ID: (16 + i * 16) for i, LUMP_ID in enumerate(LUMP)}

# Known lump changes from Titanfall 2 -> Apex Legends:
# New:
#   UNUSED_15 -> SURFACE_NAMES
#   UNUSED_16 -> CONTENTS_MASKS
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

# a rough map of the relationships between lumps:
# Model -> Mesh -> MaterialSort -> TextureData -> SurfaceName
#                             \--> VertexReservedX
#                              \-> MeshIndex?

# MeshBounds & Mesh (must have equal number of each)
# CM_GRID is linked to mesh bounds?

# VertexReservedX -> Vertex
#                \-> VertexNormal

# ??? -> ShadowMeshIndices -?> ShadowMesh -> ???
# ??? -> Brush -?> Plane

# LightmapHeader -> LIGHTMAP_DATA_SKY
#               \-> LIGHTMAP_DATA_REAL_TIME_LIGHTS

# Portal -?> PortalEdge -> PortalVertex
# PortalEdgeRef -> PortalEdge
# PortalVertRef -> PortalVertex
# PortalEdgeIntersect -> PortalEdge?
#                    \-> PortalVertex

# PortalEdgeIntersectHeader -> ???
# NOTE: there are always as many intersect headers as edges
# NOTE: there are also always as many vert refs as edge refs

# collision: ???
#   CONTENTS_MASKS  # Extreme SIMD?
#   SURFACE_PROPERTIES  # $surfaceprop etc.
#   BVH_NODES = 0x0012  # BVH4 collision tree
#   BVH_LEAF_DATA = 0x0013  # parallel w/ content masks & nodes?

# PACKED_VERTICES is parallel with VERTICES?


# classes for lumps, in alphabetical order:
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
    material_sort: int  # index of this Mesh's MaterialSort
    flags: int  # Flags(mesh.flags & Flags.MASK_VERTEX).name == "VERTEX_RESERVED_X"
    __slots__ = ["first_mesh_index", "num_triangles", "unknown", "material_sort", "flags"]
    _format = "IHh3ihHI"  # 28 bytes
    _arrays = {"unknown": 5}


class Model(base.Struct):  # LUMP 14 (000E)
    mins: List[float]  # AABB mins
    maxs: List[float]  # AABB maxs
    first_mesh: int
    num_meshes: int
    unknown: List[int]  # \_(;/)_/
    __slots__ = ["mins", "maxs", "first_mesh", "num_meshes", "unknown"]
    _format = "6f2I8i"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"], "unknown": 8}


class PackedVertex(base.MappedArray):  # LUMP 20  (0014)
    """a point in 3D space"""
    x: int
    y: int
    z: int
    _mapping = [*"xyz"]
    _format = "3h"


class ShadowMesh(base.Struct):  # LUMP 7F (0127)
    start_index: int  # assumed
    num_triangles: int  # assumed
    unknown: List[int]  # usually (1, -1)
    __slots__ = ["start_index", "num_triangles", "unknown"]
    _format = "2I2h"  # assuming 12 bytes
    _arrays = {"unknown": 2}


class TextureData(base.Struct):  # LUMP 2 (0002)
    """Name indices get out of range errors?"""
    name_index: int  # index of this TextureData's SurfaceName
    # NOTE: indexes the starting char of the SurfaceName, skipping TextureDataStringTable
    size: List[int]  # texture dimensions
    flags: int
    __slots__ = ["name_index", "size", "flags"]
    _format = "4i"  # 16 bytes?
    _arrays = {"size": ["width", "height"]}


# special vertices
class VertexBlinnPhong(base.Struct):  # LUMP 75 (004B)
    __slots__ = ["position_index", "normal_index", "uv0", "uv1"]
    _format = "2I4f"  # 24 bytes
    _arrays = {"uv0": [*"uv"], "uv1": [*"uv"]}


class VertexLitBump(base.Struct):  # LUMP 73 (0049)
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    uv0: List[float]  # texture coordindates
    negative_one: int  # -1
    uv1: List[float]  # lightmap coords
    colour: List[int]
    __slots__ = ["position_index", "normal_index", "uv0", "negative_one", "uv1", "colour"]
    _format = "2I2fi2f4B"  # 32 bytes
    _arrays = {"uv0": [*"uv"], "uv1": [*"uv"], "colour": [*"rgba"]}


class VertexLitFlat(base.Struct):  # LUMP 72 (0048)
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    uv0: List[float]  # texture coordindates
    __slots__ = ["position_index", "normal_index", "uv0", "unknown"]
    _format = "2I2fi"  # 20 bytes
    _arrays = {"uv0": [*"uv"]}


class VertexUnlit(base.Struct):  # LUMP 71 (0047)
    # NOTE: identical to VertexLitFlat?
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    uv0: List[float]  # texture coordindates
    __slots__ = ["position_index", "normal_index", "uv0", "unknown"]
    _format = "2i2fi"  # 20 bytes
    _arrays = {"uv0": [*"uv"]}


class VertexUnlitTS(base.Struct):  # LUMP 74 (004A)
    position_index: int  # index into VERTICES
    normal_index: int  # index into VERTEX_NORMALS
    uv0: List[float]  # texture coordinates
    unknown: List[int]  # 8 bytes
    __slots__ = ["position_index", "normal_index", "uv0", "unknown"]
    _format = "2I2f2i"  # 24 bytes
    _arrays = {"uv0": [*"uv"], "unknown": 2}


# special lump classes, in alphabetical order:
def ApexSPRP(raw_lump):
    return titanfall2.GameLump_SPRP(raw_lump, titanfall2.StaticPropv13)


# NOTE: all Apex lumps are version 0, except GAME_LUMP
# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = titanfall2.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = titanfall2.LUMP_CLASSES.copy()
LUMP_CLASSES.update({"LIGHTMAP_HEADERS":    {0: titanfall.LightmapHeader},
                     "MATERIAL_SORT":       {0: MaterialSort},
                     "MESHES":              {0: Mesh},
                     "MODELS":              {0: Model},
                     "PACKED_VERTICES":     {0: PackedVertex},
                     "PLANES":              {0: titanfall.Plane},
                     "SHADOW_MESHES":       {0: ShadowMesh},
                     "TEXTURE_DATA":        {0: TextureData},
                     "VERTEX_BLINN_PHONG":  {0: VertexBlinnPhong},
                     "VERTEX_LIT_BUMP":     {0: VertexLitBump},
                     "VERTEX_LIT_FLAT":     {0: VertexLitFlat},
                     "VERTEX_UNLIT":        {0: VertexUnlit},
                     "VERTEX_UNLIT_TS":     {0: VertexUnlitTS}})

SPECIAL_LUMP_CLASSES = titanfall2.SPECIAL_LUMP_CLASSES.copy()
SPECIAL_LUMP_CLASSES.pop("CM_GRID")
SPECIAL_LUMP_CLASSES.pop("TEXTURE_DATA_STRING_DATA")
SPECIAL_LUMP_CLASSES.update({"SURFACE_NAMES": {0: shared.TextureDataStringData}})


GAME_LUMP_HEADER = source.GameLumpHeader

GAME_LUMP_CLASSES = {"sprp": {bsp_version: ApexSPRP for bsp_version in (47, 48, 49, 50)}}


# branch exclusive methods, in alphabetical order:
def get_TextureData_SurfaceName(bsp, texture_data_index: int) -> str:
    texture_data = bsp.TEXTURE_DATA[texture_data_index]
    return bsp.SURFACE_NAMES.as_bytes()[texture_data.name_index:].lstrip(b"\0").partition(b"\0")[0].decode()


def get_Mesh_SurfaceName(bsp, mesh_index: int) -> str:
    """Returns the name of the .vmt applied to bsp.MESHES[mesh_index]"""
    mesh = bsp.MESHES[mesh_index]
    material_sort = bsp.MATERIAL_SORT[mesh.material_sort]
    return bsp.get_TextureData_SurfaceName(material_sort.texture_data)


# "debug" methods for investigating the compile process
def debug_TextureData(bsp):
    print("# TextureData_index  TextureData.name_index  SURFACE_NAMES[name_index]  TextureData.flags")
    for i, td in enumerate(bsp.TEXTURE_DATA):
        texture_name = bsp.get_TextureData_SurfaceName(i)
        print(f"{i:02d} {td.name_index:03d} {texture_name:<48s} {source.Surface(td.flags)!r}")


def debug_unused_SurfaceNames(bsp):
    return set(bsp.SURFACE_NAMES).difference({bsp.get_TextureData_SurfaceName(i) for i in range(len(bsp.TEXTURE_DATA))})


def debug_Mesh_stats(bsp):
    print("# index  VERTEX_LUMP  texture_data_index  texture  mesh_indices_range")
    for i, model in enumerate(bsp.MODELS):
        print(f"# MODELS[{i}]")
        for j in range(model.first_mesh, model.first_mesh + model.num_meshes):
            mesh = bsp.MESHES[j]
            material_sort = bsp.MATERIAL_SORT[mesh.material_sort]
            texture_name = bsp.get_TextureData_SurfaceName(material_sort.texture_data)
            vertex_lump = (titanfall.Flags(mesh.flags) & titanfall.Flags.MASK_VERTEX).name
            indices = set(bsp.MESH_INDICES[mesh.first_mesh_index:mesh.first_mesh_index + mesh.num_triangles * 3])
            _min, _max = min(indices), max(indices)
            _range = f"({_min}->{_max})" if indices == {*range(_min, _max + 1)} else indices
            print(f"{j:02d} {vertex_lump:<15s} {material_sort.texture_data:02d} {texture_name:<48s} {_range}")


methods = [titanfall.vertices_of_mesh, titanfall.vertices_of_model,
           titanfall.search_all_entities, shared.worldspawn_volume,
           titanfall.shadow_meshes_as_obj,
           get_TextureData_SurfaceName, get_Mesh_SurfaceName,
           debug_TextureData, debug_unused_SurfaceNames, debug_Mesh_stats]
