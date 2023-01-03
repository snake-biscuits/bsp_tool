import enum
from typing import List

from .. import base
from .. import shared
from .. import vector
from ..valve import source
from . import titanfall
from . import titanfall2


FILE_MAGIC = b"rBSP"

BSP_VERSION = 47

launch = "depot/r5launch/game/r2/maps"
staging = "depot/r5staging/game/r2/maps"
r5_100 = "depot/r5-100/game/r2/maps"
r5_101 = "depot/r5-101/game/r2/maps"
r5_110 = "depot/r5-110/game/r2/maps"
r5_111 = "depot/r5-111/game/r2/maps"
r5_131 = "depot/r5-131/game/r2/maps"

GAME_PATHS = {"Apex Legends": "ApexLegends/maps",
              "Apex Legends: Season 2 - Battle Charge": "ApexLegends/season2/maps",
              "Apex Legends: Season 3 - Meltdown": "ApexLegends/season3/maps",
              "Apex Legends: Season 3 - Meltdown (launch)": f"ApexLegends/season3/{launch}",
              "Apex Legends: Season 3 - Meltdown (staging)": f"ApexLegends/season3/{staging}",
              "Apex Legends: Season 3 - Meltdown [30 Oct Patch]": "ApexLegends/season3_30oct19/maps",
              "Apex Legends: Season 3 - Meltdown [30 Oct Patch] (launch)": f"ApexLegends/season3/30oct19/{launch}",
              "Apex Legends: Season 3 - Meltdown [30 Oct Patch] (staging)": f"ApexLegends/season3/30oct19/{staging}",
              "Apex Legends: Season 3 - Meltdown [3 Dec Patch]": "ApexLegends/season3/3dec19/maps",
              "Apex Legends: Season 3 - Meltdown [3 Dec Patch] (launch)": f"ApexLegends/season3/3dec19/{launch}",
              "Apex Legends: Season 3 - Meltdown [3 Dec Patch] (staging)": f"ApexLegends/season3/3dec19/{staging}",
              "Apex Legends: Season 5 - Fortune's Favor": "ApexLegends/season5/maps",
              "Apex Legends: Season 8 - Mayhem": "ApexLegends/season8/maps",
              "Apex Legends: Season 9 - Legacy": "ApexLegends/season9/maps",
              "Apex Legends: Season 10 - Emergence [3 Aug Patch]": "ApexLegends/season10/3aug21/maps/",
              "Apex Legends: Season 10 - Emergence [10 Aug Patch]": "ApexLegends/season10/10aug21/maps/",
              "Apex Legends: Season 10 - Emergence [10 Aug Patch] (100)": f"ApexLegends/season10/10aug21/{r5_100}",
              "Apex Legends: Season 10 - Emergence [14 Sep Patch]": "ApexLegends/season10/14sep21/maps/",
              "Apex Legends: Season 10 - Emergence [14 Sep Patch] (100)": f"ApexLegends/season10/14sep21/{r5_100}",
              "Apex Legends: Season 10 - Emergence [14 Sep Patch] (101)": f"ApexLegends/season10/14sep21/{r5_101}",
              "Apex Legends: Season 10 - Emergence [24 Sep Patch]": "ApexLegends/season10/24sep21/maps/",
              "Apex Legends: Season 10 - Emergence [24 Sep Patch] (100)": f"ApexLegends/season10/24sep21/{r5_100}",
              "Apex Legends: Season 10 - Emergence [24 Sep Patch] (101)": f"ApexLegends/season10/24sep21/{r5_101}",
              "Apex Legends: Season 11 - Escape": "ApexLegends/season11/maps",
              "Apex Legends: Season 11 - Escape (110)": f"ApexLegends/season11/{r5_110}",
              "Apex Legends: Season 11 - Escape [6 Nov Patch]": "ApexLegends/season11/6nov21/maps",
              "Apex Legends: Season 11 - Escape [6 Nov Patch] (110)": f"ApexLegends/season11/6nov21/{r5_110}",
              "Apex Legends: Season 11 - Escape [19 Nov Patch]": "ApexLegends/season11/19nov21/maps",
              "Apex Legends: Season 11 - Escape [19 Nov Patch] (110)": f"ApexLegends/season11/19nov21/{r5_110}",
              "Apex Legends: Season 11 - Escape [19 Nov Patch] (111)": f"ApexLegends/season11/19nov21/{r5_111}",
              "Apex Legends: Season 13 - Saviors": "ApexLegends/season13/10mar22/maps",
              "Apex Legends: Season 13 - Saviors [Awaken] (131)": f"ApexLegends/season13/21jun22/{r5_131}"}

GAME_VERSIONS = {"Apex Legends": 47,
                 "Apex Legends: Season 7 - Ascension": 48,  # Olympus
                 "Apex Legends: Season 8 - Mayhem": 49,  # King's Canyon map update 3
                 "Apex Legends: Season 10 - Emergence": 50,  # Arenas: Encore / SkyGarden
                 "Apex Legends: Season 11 - Escape [19 Nov Patch] (110)": 49,
                 "Apex Legends: Season 11 - Escape [19 Nov Patch] (111)": (49, 1),
                 "Apex Legends: Season 11 - Escape [19 Nov Patch]": (50, 1),
                 "Apex Legends: Season 13 - Saviors": (51, 1)}


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
    MATERIAL_SORT = 0x0052
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
    PORTAL_EDGE_INTERSECT_AT_EDGE = 0x0072
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
    SHADOW_MESHES = 0x007F


LumpHeader = source.LumpHeader


# Known lump changes from Titanfall 2 -> Apex Legends:
# New:
#   CM_GRID -> TWEAK_LIGHTS
#   TEXTURE_DATA_STRING_DATA -> UNKNOWN_43
#   TRICOLL_BEVEL_INDICES -> UNKNOWN_97
#   UNUSED_15 -> SURFACE_NAMES
#   UNUSED_16 -> CONTENTS_MASKS
#   UNUSED_17 -> SURFACE_PROPERTIES
#   UNUSED_18 -> BVH_NODES
#   UNUSED_19 -> BVH_LEAF_DATA
#   UNUSED_20 -> PACKED_VERTICES
#   UNUSED_37 -> UNKNOWN_37
#   UNUSED_38 -> UNKNOWN_38
#   UNUSED_39 -> UNKNOWN_39
# Deprecated:
#   CM_BRUSHES
#   CM_BRUSH_SIDE_PLANE_OFFSETS
#   CM_BRUSH_SIDE_PROPERTIES
#   CM_BRUSH_SIDE_TEXTURE_VECTORS
#   CM_GEO_SETS
#   CM_GEO_SET_BOUNDS
#   CM_GRID_CELLS
#   CM_PRIMITIVES
#   CM_PRIMITIVE_BOUNDS
#   CM_UNIQUE_CONTENTS
#   LEAF_WATER_DATA
#   LIGHTPROBE_BSP_NODES
#   LIGHTPROBE_BSP_REF_IDS
#   PHYSICS_COLLIDE
#   PHYSICS_LEVEL
#   TEXTURE_DATA_STRING_TABLE
#   TRICOLL_BEVEL_STARTS
#   TRICOLL_HEADERS
#   TRICOLL_NODES
#   TRICOLL_TRIANGLES

# a rough map of the relationships between lumps:

#                /-> BVHNode
# Entity -> Model -> Mesh -> MaterialSort -> TextureData -> SurfaceName
#                \-> BVHLeaf            \--> VertexReservedX
#                                        \-> MeshIndex?
# MeshBounds & Mesh are parallel
# NOTE: parallel means each entry is paired with an entry of the same index in the parallel lump
# -- this means you can collect only the data you need, but increases the chance of storing redundant data

# VertexReservedX -> Vertex
#                \-> VertexNormal

# ShadowEnvironment -> ShadowMesh -> ShadowMeshIndices -> ShadowMeshOpaqueVertex
#                                                    \-?> ShadowMeshAlphaVertex
# ShadowEnvironments are indexed by entities (light_environment(_volume) w/ lightEnvironmentIndex key)

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


# flag enums
class BVHNodeType(enum.Enum):  # used by BVHNode
    """BVH4 (GDC 2018 - Extreme SIMD: Optimized Collision Detection in Titanfall)
https://www.youtube.com/watch?v=6BIfqfC1i7U
https://gdcvault.com/play/1025126/Extreme-SIMD-Optimized-Collision-Detection"""
    BVH_NODE = 0x00
    NO_CHILD = 0x01
    # primitive types:
    UNKNOWN_2 = 0x02  # edge?
    UNKNOWN_3 = 0x03
    UNKNOWN_4 = 0x04
    UNKNOWN_5 = 0x05
    UNKNOWN_6 = 0x06
    UNKNOWN_7 = 0x07
    UNKNOWN_8 = 0x08
    UNKNOWN_9 = 0x09
    UNKNOWN_10 = 0x0A
    UNKNOWN_11 = 0x0B
    UNKNOWN_12 = 0x0C
    UNKNOWN_13 = 0x0D
    UNKNOWN_14 = 0x0E
    UNKNOWN_15 = 0x0F


# classes for lumps, in alphabetical order:
class BVHNode(base.Struct):  # LUMP 18 (0012)
    """BVH4 (GDC 2018 - Extreme SIMD: Optimized Collision Detection in Titanfall)
https://www.youtube.com/watch?v=6BIfqfC1i7U
https://gdcvault.com/play/1025126/Extreme-SIMD-Optimized-Collision-Detection"""
    # Identified by Fifty & Rexx, matched to GDC talk spec
    # |     child0    |     child1    |     child2    |     child3    |
    # | min x | max x | min x | max x | min x | max x | min x | max x |
    # | min y | max y | min y | max y | min y | max y | min y | max y |
    # | min z | max z | min z | max z | min z | max z | min z | max z |
    # |   INDEX  | 01 |   INDEX  | 23 |   INDEX  | CM |   INDEX  |    |
    # arranged for easy SIMD operations
    x: List[List[int]]  # x.child0.min .. x.child3.max
    y: List[List[int]]  # y.child0.min .. y.child3.max
    z: List[List[int]]  # z.child0.min .. z.child3.max
    index: List[List[int]]  # child indices and metadata
    # NOTE: bitfields are definitely all wrong, not all padding is 0
    # NOTE: index.child2.collision_mask should be an index (SurfaceProperties?)
    __slots__ = [*"xyz", "index"]
    _format = "24h4I"
    _arrays = {axis: {f"child{i}": ["min", "max"] for i in range(4)} for axis in [*"xyz"]}
    _arrays.update({"index": [f"child{i}" for i in range(4)]})
    _bitfields = {"index.child0": {"child0_type": 4, "child1_type": 4, "index": 24},
                  "index.child1": {"child2_type": 4, "child3_type": 4, "index": 24},
                  "index.child2": {"collision_mask": 8, "index": 24},
                  "index.child3": {"padding": 8, "index": 24}}
    _classes = {"index.child0.child0_type": BVHNodeType, "index.child0.child1_type": BVHNodeType,
                "index.child1.child2_type": BVHNodeType, "index.child1.child3_type": BVHNodeType}

    # TODO: remap w/ properties and use a bounding box class
    # node.children[0].mins.x
    # node.children[1].index  # TODO: might need to allow signed bitfield members
    # node.collision_mask

    def __repr__(self) -> str:
        out = list()

        def minmax(node: BVHNode, axis: str, child: str) -> str:
            a = getattr(getattr(node, axis), child)
            return f"min.{axis} = {str(a.min):<6} | max.{axis} = {str(a.max):<6}"

        out.append("| ------------ child0 ----------- | ------------ child1 ----------- |")
        out.append(f"| {minmax(self, 'x', 'child0')} | {minmax(self, 'x', 'child1')} |")
        out.append(f"| {minmax(self, 'y', 'child0')} | {minmax(self, 'y', 'child1')} |")
        out.append(f"| {minmax(self, 'z', 'child0')} | {minmax(self, 'z', 'child1')} |")
        out.append(f"| index = {str(self.index.child0.index):<23} | index = {str(self.index.child1.index):<23} |")
        out.append(f"| type = {str(self.index.child0.child0_type):<24} | type = {str(self.index.child0.child1_type):<24} |")
        out.append("| ------------ child2 ----------- | ------------ child3 ----------- |")
        out.append(f"| {minmax(self, 'x', 'child2')} | {minmax(self, 'x', 'child3')} |")
        out.append(f"| {minmax(self, 'y', 'child2')} | {minmax(self, 'y', 'child3')} |")
        out.append(f"| {minmax(self, 'z', 'child2')} | {minmax(self, 'z', 'child3')} |")
        out.append(f"| index = {str(self.index.child2.index):<23} | index = {str(self.index.child3.index):<23} |")
        out.append(f"| type = {str(self.index.child1.child2_type):<24} | type = {str(self.index.child1.child3_type):<24} |")
        out.append(f"| collision_mask = {str(self.index.child2.collision_mask):<48} |")
        out.append(f"| padding = {str(self.index.child2.collision_mask):<55} |")
        # NOTE: padding is not displayed with this method
        return "\n".join(out)


class CellAABBNode(base.Struct):  # LUMP 119 (0077)
    """Identified by Fifty#8113"""
    # NOTE: the struct length & positions of mins & maxs take advantage of SIMD 128-bit registers
    mins: List[float]
    children: int  # bitfield
    # if children.count == 0, children.flags == 64
    maxs: List[float]
    unknown: int  # likely flags / metadata; might index ObjReferences?
    __slots__ = ["mins", "child_data",
                 "maxs", "unknown"]
    _format = "3fI3fI"
    # 3FI3fI is a common pattern for Respawn AABB based objects
    # since you can pipe XYZ into SIMD registers quickly
    # .w ints contain metadata & flags (see Extreme SIMD GDC Talk / Notes)
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}
    _bitfields = {"children": {"flags": 8, "first": 16, "count": 8}}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}  # TODO: "children.flags": CellAABBNodeFlags


# NOTE: only one 36 byte entry per file
class LevelInfo(base.Struct):  # LUMP 123 (007B)
    unknown: List[int]  # possibly linked to mesh flags in worldspawn?
    num_static_props: int  # should match len(bsp.GAME_LUMP.sprp.props) [UNTESTED]
    sun_angle: List[float]  # sun angle vector matching last ShadowEnvironment's light_environment if r2
    num_entity_models: int  # matches num_models in .ent file headers ("ENTITY02 num_models=X")
    __slots__ = ["unknown", "num_static_props", "sun_angle", "num_entity_models"]
    _format = "5I3fI"
    _arrays = {"unknown": 4, "sun_angle": [*"xyz"]}


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
    flags: int  # MeshFlags(mesh.flags & MeshFlags.MASK_VERTEX).name == "VERTEX_RESERVED_X"
    __slots__ = ["first_mesh_index", "num_triangles", "unknown", "material_sort", "flags"]
    _format = "IH8hHI"  # 28 bytes
    _arrays = {"unknown": 8}
    _classes = {"flags": titanfall.MeshFlags}


class Model(base.Struct):  # LUMP 14 (000E)
    mins: List[float]  # AABB mins
    maxs: List[float]  # AABB maxs
    first_mesh: int
    num_meshes: int
    bvh_node: int
    bvh_leaf: int
    first_vertex: int
    vertex_flags: int  # use PACKED_VERTICES or other?
    unknown_1: List[float]
    unknown_2: int
    __slots__ = ["mins", "maxs", "first_mesh", "num_meshes", "bvh_node", "bvh_leaf",
                 "first_vertex", "vertex_flags", "unknown_1", "unknown_2"]
    _format = "6f2I4i3fi"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"], "unknown_1": 3}


class PackedVertex(base.MappedArray):  # LUMP 20  (0014)
    """a point in 3D space"""
    x: int
    y: int
    z: int
    _mapping = [*"xyz"]
    _format = "3h"


class ShadowMesh(base.Struct):  # LUMP 127 (007F)
    start_index: int  # assumed
    num_triangles: int  # assumed
    unknown: List[int]  # usually (1, -1)
    __slots__ = ["start_index", "num_triangles", "unknown"]
    _format = "2I2h"  # assuming 12 bytes
    _arrays = {"unknown": 2}


class SurfaceProperty(base.MappedArray):  # LUMP 17 (0011)
    unknown_1: int
    unknown_2: int
    contents_mask: int  # index of ContentsMask for this SurfaceProperty
    surface_name: int  # index of SurfaceName for this SurfaceProperty
    _mapping = ["unknown_1", "unknown_2", "content_mask", "surface_name"]
    _format = "h2bi"


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
    negative_one: int  # always -1
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
pops = ("CM_BRUSH_SIDE_PLANE_OFFSETS", "CM_BRUSH_SIDE_PROPERTIES", "CM_PRIMITIVES", "CM_UNIQUE_CONTENTS",
        "TEXTURE_DATA_STRING_TABLE", "TRICOLL_BEVEL_STARTS", "TRICOLL_BEVEL_INDICES", "TRICOLL_TRIANGLES")
for LUMP_NAME in pops:
    BASIC_LUMP_CLASSES.pop(LUMP_NAME)
del LUMP_NAME, pops
BASIC_LUMP_CLASSES.update({"CONTENTS_MASKS": {0: shared.UnsignedInts}})

LUMP_CLASSES = titanfall2.LUMP_CLASSES.copy()
pops = ("CM_BRUSHES", "CM_BRUSH_SIDE_TEXTURE_VECTORS", "CM_GEO_SETS", "CM_GEO_SET_BOUNDS",
        "CM_GRID_CELLS", "CM_PRIMITIVE_BOUNDS", "LEAF_WATER_DATA",
        "LIGHTMAP_DATA_REAL_TIME_LIGHTS_PAGE", "TRICOLL_HEADERS", "TRICOLL_NODES")
for LUMP_NAME in pops:
    LUMP_CLASSES.pop(LUMP_NAME)
del LUMP_NAME, pops
LUMP_CLASSES.update({"BVH_NODES":          {0: BVHNode},
                     "CELL_AABB_NODES":    {0: CellAABBNode},
                     "LIGHTMAP_HEADERS":   {0: titanfall.LightmapHeader},
                     "MATERIAL_SORT":      {0: MaterialSort},
                     "MESHES":             {0: Mesh},
                     "MODELS":             {0: Model},
                     "PACKED_VERTICES":    {0: PackedVertex},
                     "PLANES":             {0: titanfall.Plane},
                     "SHADOW_MESHES":      {0: ShadowMesh},
                     "SURFACE_PROPERTIES": {0: SurfaceProperty},
                     "TEXTURE_DATA":       {0: TextureData},
                     "VERTEX_BLINN_PHONG": {0: VertexBlinnPhong},
                     "VERTEX_LIT_BUMP":    {0: VertexLitBump},
                     "VERTEX_LIT_FLAT":    {0: VertexLitFlat},
                     "VERTEX_UNLIT":       {0: VertexUnlit},
                     "VERTEX_UNLIT_TS":    {0: VertexUnlitTS}})

SPECIAL_LUMP_CLASSES = titanfall2.SPECIAL_LUMP_CLASSES.copy()
SPECIAL_LUMP_CLASSES.pop("CM_GRID")
SPECIAL_LUMP_CLASSES.pop("PHYSICS_COLLIDE")
SPECIAL_LUMP_CLASSES.pop("TEXTURE_DATA_STRING_DATA")
SPECIAL_LUMP_CLASSES.update({"LEVEL_INFO":    {0: LevelInfo.from_bytes},
                             "SURFACE_NAMES": {0: shared.TextureDataStringData}})


GAME_LUMP_HEADER = source.GameLumpHeader

GAME_LUMP_CLASSES = {"sprp": {bsp_version: ApexSPRP for bsp_version in (47, 48, 49, 50, 51)}}


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
            vertex_lump = (titanfall.MeshFlags(mesh.flags) & titanfall.MeshFlags.MASK_VERTEX).name
            indices = set(bsp.MESH_INDICES[mesh.first_mesh_index:mesh.first_mesh_index + mesh.num_triangles * 3])
            _min, _max = min(indices), max(indices)
            _range = f"({_min}->{_max})" if indices == {*range(_min, _max + 1)} else indices
            print(f"{j:02d} {vertex_lump:<15s} {material_sort.texture_data:02d} {texture_name:<48s} {_range}")


methods = [titanfall.vertices_of_mesh, titanfall.vertices_of_model,
           titanfall.search_all_entities, shared.worldspawn_volume,
           titanfall.shadow_meshes_as_obj,
           get_TextureData_SurfaceName, get_Mesh_SurfaceName,
           debug_TextureData, debug_unused_SurfaceNames, debug_Mesh_stats]
