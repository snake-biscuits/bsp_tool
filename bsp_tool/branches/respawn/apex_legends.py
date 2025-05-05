import enum
from typing import List, Union

from ... import core
from ...utils import geometry
from ...utils import vector
from .. import colour
from .. import shared
from ..id_software import quake3
from ..valve import source
from . import titanfall
from . import titanfall2


FILE_MAGIC = b"rBSP"

BSP_VERSION = 47

GAME_PATHS = {"Apex Legends": "ApexLegends/maps"}

GAME_VERSIONS = {
    "Apex Legends": 47,
    "Apex Legends: Season 7 - Ascension": 48,  # Olympus
    "Apex Legends: Season 8 - Mayhem": 49,  # King's Canyon map update 3
    "Apex Legends: Season 11 - Escape [19 Nov Patch] (110)": 49,  # depots/
    "Apex Legends: Season 11 - Escape [19 Nov Patch] (111)": (49, 1)}


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
    HEIGHTFIELDS = 0x0015
    HEIGHTFIELD_SAMPLES = 0x0016
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
    CUBEMAPS_AMBIENT_RCP = 0x002B  # page for txtx .rpak asset
    WATER_BODIES = 0x002C
    WATER_BODY_CENTERS = 0x002D
    WATER_BODY_VERTICES = 0x002E
    WATER_BODY_INDICES = 0x002F
    WAVE_DATA = 0x0030  # 1024x1024 RGBA texture (green & blue channels only)
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
    MATERIAL_SORTS = 0x0052
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
    LIGHTMAP_DATA_UNKNOWN = 0x0061
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
    LIGHTMAP_DATA_RTL_PAGES = 0x007A
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
#   TRICOLL_BEVEL_INDICES -> LIGHTMAP_DATA_UNKNOWN
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

# BVHNode -> BVHNode
#        \-> BVHLeafData

# Type 0 & 1 are for BVHNode / None
# BVHLeafData2 -?>
# BVHLeafData3 -?>
# BVHLeafData4 -> Vertices
# BVHLeafData5 -> PackedVertices
# BVHLeafData6 -> Vertices
# BVHLeafData7 -> PackedVertices
# BVHLeafData8-15?

# PACKED_VERTICES is parallel with VERTICES?

# WaterBody -> WaterBodyIndex -> WaterBodyVertex -> WaveData
#          \-> WaveBodyCenter

# UNKNOWN_39 is paralell w/ CellAABBNodes; defaults to -1s


# flag enums
class BVHNodeType(enum.Enum):  # used by BVHNode
    """BVH4 (GDC 2018 - Extreme SIMD: Optimized Collision Detection in Titanfall)
https://www.youtube.com/watch?v=6BIfqfC1i7U
https://gdcvault.com/play/1025126/Extreme-SIMD-Optimized-Collision-Detection"""
    BVH_NODE = 0x00
    NO_CHILD = 0x01
    UNUSED_2 = 0x02
    # primitive types:
    UNKNOWN_3 = 0x03  # points to other leaves
    TRI_REGULAR = 0x04
    TRI_PACKED = 0x05
    QUAD_REGULAR = 0x06
    QUAD_PACKED = 0x07
    STAR_COLL = 0x08  # same as in ents, according to rexx
    STATIC_PROP = 0x09
    # UNUSED_10-15
    # NOTE: packed types are most accurate for "on-grid" coords close to world origin


# classes for lumps, in alphabetical order:
class BVHLeaf5Header(core.BitField):  # LUMP 19 (0013) [type 5]
    """TricollHeader with less diverse children"""
    unknown: int
    num_triangles: int  # number of BVHLeaf5Triangle after this header
    first_vertex: int  # starting index into PackedVertices
    _format = "I"
    _fields = {"unknown": 12, "num_triangles": 4, "first_vertex": 16}


class BVHLeaf5Triangle(core.BitField):  # LUMP 19 (0013) [type 5]
    """TricollTriangle w/ more indices & less flags"""
    A: int  # index into PackedVertices
    B: int  # index into PackedVertices
    C: int  # index into PackedVertices
    # TODO: work out indexing math, could match TricollTriangle
    edge_mask: int  # mask for each edge; one bit per edge?
    _format = "I"
    _fields = {"A": 11, "B": 9, "C": 9, "edge_mask": 3}


class BVHNode(core.Struct):  # LUMP 18 (0012)
    """BVH4 (GDC 2018 - Extreme SIMD: Optimized Collision Detection in Titanfall)
https://www.youtube.com/watch?v=6BIfqfC1i7U
https://gdcvault.com/play/1025126/Extreme-SIMD-Optimized-Collision-Detection"""
    # Identified by Fifty & Rexx, matched to GDC talk spec
    # Corrected w/ help from Rexx & Rika
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
    # index.child0.contents_mask: int  # index into ContentsMasks
    __slots__ = [*"xyz", "index"]
    _format = "24h4I"
    _arrays = {axis: {f"child{i}": ["min", "max"] for i in range(4)} for axis in [*"xyz"]}
    _arrays.update({"index": [f"child{i}" for i in range(4)]})
    _bitfields = {"index.child0": {"index": 24, "contents_mask": 8},
                  "index.child1": {"index": 24, "padding": 8},
                  "index.child2": {"index": 24, "child0_type": 4, "child1_type": 4},
                  "index.child3": {"index": 24, "child2_type": 4, "child3_type": 4}}
    _classes = {"index.child2.child0_type": BVHNodeType, "index.child2.child1_type": BVHNodeType,
                "index.child3.child2_type": BVHNodeType, "index.child3.child3_type": BVHNodeType}

    @property
    def children(self) -> List[object]:

        class BVHChildNode:
            # TODO: inherit from some AABB class for math utils
            mins: vector.vec3
            maxs: vector.vec3
            type: BVHNodeType
            index: int

            def __init__(self, parent, i):
                name = f"child{i}"
                mmx = getattr(parent.x, name)
                mmy = getattr(parent.y, name)
                mmz = getattr(parent.z, name)
                # TODO: enforce Vec3<uint16_t>
                self.mins = vector.vec3(mmx[0], mmy[0], mmz[0])
                self.maxs = vector.vec3(mmx[1], mmy[1], mmz[1])
                self.type = getattr(getattr(parent.index, f"child{2 + i // 2}"), f"child{i}_type")
                self.index = getattr(parent.index, name).index

            def __repr__(self):

                def mm(a):
                    mins = f"mins.{a} = {str(int(getattr(self.mins, a))):>6}"
                    maxs = f"maxs.{a} = {str(int(getattr(self.maxs, a))):>6}"
                    return " ".join(["|", mins, "|", maxs, "|"])

                out = [mm(a) for a in [*"xyz"]]
                out.extend([f"| type = {str(self.type):<26} |", f"| index = {self.index:<25} |"])
                return "\n".join(out)

        return [BVHChildNode(self, i) for i in range(4)]

    @property
    def contents_mask(self) -> int:
        return self.index.child0.contents_mask

    @property
    def padding(self) -> int:
        return self.index.child1.padding

    def __repr__(self) -> str:
        out = list()
        c = self.children
        out.append("| ---------- children[0] ---------- | ---------- children[1] ---------- |")
        out.extend([f"{a}{b[1:]}" for a, b in zip(repr(c[0]).split("\n"), repr(c[1]).split("\n"))])
        out.append("| ---------- children[2] ---------- | ---------- children[3] ---------- |")
        out.extend([f"{a}{b[1:]}" for a, b in zip(repr(c[2]).split("\n"), repr(c[3]).split("\n"))])
        out.append(f"| contents_mask = {str(self.contents_mask):<53} |")
        # NOTE: padding is not displayed as it should always be 0
        return "\n".join(out)


class CellAABBNode(core.Struct):  # LUMP 119 (0077)
    """Identified by Fifty#8113"""
    # NOTE: the struct length & positions of mins & maxs take advantage of SIMD 128-bit registers
    mins: vector.vec3
    children: core.BitField  # if children.count == 0, children.flags == 64
    maxs: vector.vec3
    unknown: int  # likely flags / metadata; might index ObjReferences?
    __slots__ = ["mins", "children", "maxs", "unknown"]
    _format = "3fI3fI"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}
    _bitfields = {"children": {"count": 8, "first": 16, "flags": 8}}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}
    # TODO: "children.flags": NodeFlags


class CSMAABBNode(core.Struct):  # LUMP 99 (0063)
    mins: vector.vec3
    children: core.BitField  # indices into CSMAABBNodes
    maxs: vector.vec3
    unknown: core.BitField  # indices into Unknown38?
    __slots__ = ["mins", "children", "maxs", "unknown"]
    _format = "3fI3fI"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}
    _bitfields = {
        "children": {"flags": 8, "first": 16, "count": 8},
        "unknown": {"first": 24, "count": 8}}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}
    # TODO: "children.flags": NodeFlags


class HeightField(core.Struct):  # LUMP 21 (0015)
    __slots__ = ["unknown"]
    _format = "10I"
    _arrays = {"unknown": 10}


# NOTE: only one 36 byte entry per file
class LevelInfo(core.Struct):  # LUMP 123 (007B)
    unknown: List[int]  # possibly linked to mesh flags in worldspawn?
    num_static_props: int  # should match len(bsp.GAME_LUMP.sprp.props) [UNTESTED]
    sun_normal: vector.vec3  # vector matching angles of last indexed light_environment entity
    num_entity_models: int  # matches num_models in .ent file headers ("ENTITY02 num_models=X")
    __slots__ = ["unknown", "num_static_props", "sun_normal", "num_entity_models"]
    _format = "5I3fI"
    _arrays = {"unknown": 4, "sun_normal": [*"xyz"]}
    _classes = {"sun_normal": vector.vec3}


class MaterialSort(core.Struct):  # LUMP 82 (0052)
    texture_data: int  # index into TextureData
    lightmap_index: int  # index into LightmapHeaders; -1 if None
    unknown: List[int]  # ({0?}, {??..??})
    vertex_offset: int  # offset into appropriate VERTEX_RESERVED_X lump
    __slots__ = ["texture_data", "lightmap_index", "unknown", "vertex_offset"]
    _format = "4hI"  # 12 bytes
    _arrays = {"unknown": 2}


class Mesh(core.Struct):  # LUMP 80 (0050)
    first_mesh_index: int  # index into MeshIndices
    num_triangles: int
    # first_vertex: int  # index into VertexReservedX
    # num_vertices: int
    unknown: List[int]
    material_sort: int  # index of this Mesh's MaterialSort
    flags: int  # MeshFlags(mesh.flags & MeshFlags.MASK_VERTEX).name == "VERTEX_RESERVED_X"
    __slots__ = ["first_mesh_index", "num_triangles", "unknown", "material_sort", "flags"]
    _format = "IH8hHI"  # 28 bytes
    _arrays = {"unknown": 8}
    _classes = {"flags": titanfall.MeshFlags}


class Model(core.Struct):  # LUMP 14 (000E)
    mins: vector.vec3  # AABB mins
    maxs: vector.vec3  # AABB maxs
    first_mesh: int
    num_meshes: int
    bvh_node: int
    bvh_leaf: int
    first_vertex: int
    vertex_flags: int  # use PACKED_VERTICES or other?
    packed_vertex_offset: vector.vec3  # center point to orient packed verts around
    node_scale: float  # this * 0xFFFF = scale applied to BVH_NODES
    __slots__ = [
        "mins", "maxs", "first_mesh", "num_meshes", "bvh_node", "bvh_leaf",
        "first_vertex", "vertex_flags", "packed_vertex_offset", "node_scale"]
    _format = "6f2I4i4f"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"], "packed_vertex_offset": [*"xyz"]}
    _classes = {v: vector.vec3 for v in ("mins", "maxs", "packed_vertex_offset")}


class PackedVertex(core.MappedArray):  # LUMP 20  (0014)
    """a point in 3D space"""
    # TODO: subclass vector.ivec3
    x: int
    y: int
    z: int
    _mapping = [*"xyz"]
    _format = "3h"


class ShadowMesh(core.Struct):  # LUMP 127 (007F)
    vertex_offset: int  # index into ShadowMeshAlpha / OpaqueVertices
    # first_index = sum(sm.num_triangles * 3 for sm in bsp.SHADOW_MESH_INDICES[:index])
    num_triangles: int  # number of triangles in ShadowMeshIndices
    is_opaque: bool  # indexes ShadowMeshAlphaVertex if 0, ShadowMeshVertex if 1
    material_sort: int  # index into MaterialSort; -1 for None
    __slots__ = ["vertex_offset", "num_triangles", "is_opaque", "material_sort"]
    _format = "2I2h"  # assuming 12 bytes
    _classes = {"is_opaque": bool}


class SurfaceProperty(core.MappedArray):  # LUMP 17 (0011)
    unknown_1: int
    unknown_2: int
    contents_mask: int  # index into ContentsMasks
    surface_name: int  # index into SurfaceNames
    _mapping = ["unknown_1", "unknown_2", "content_mask", "surface_name"]
    _format = "h2bi"


class TextureData(core.Struct):  # LUMP 2 (0002)
    """Name indices get out of range errors?"""
    name_index: int  # index of this TextureData's SurfaceName
    # NOTE: indexes the starting char of the SurfaceName, skipping TextureDataStringTable
    size: List[int]
    flags: int  # TODO: TextureDataFlags
    __slots__ = ["name_index", "size", "flags"]
    _format = "4i"  # 16 bytes?
    _arrays = {"size": ["width", "height"]}


# special vertices
class VertexBlinnPhong(core.Struct):  # LUMP 75 (004B)
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    albedo_uv: vector.vec2
    lightmap_uv: vector.vec2
    __slots__ = ["position_index", "normal_index", "albedo_uv", "lightmap_uv"]
    _format = "2I4f"  # 24 bytes
    _arrays = {"albedo_uv": [*"uv"], "lightmap_uv": [*"uv"]}


class VertexLitBump(core.Struct):  # LUMP 73 (0049)
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    albedo_uv: vector.vec2
    negative_one: int  # always -1
    lightmap_uv: vector.vec2
    colour: colour.RGBA32
    __slots__ = ["position_index", "normal_index", "albedo_uv", "negative_one", "lightmap_uv", "colour"]
    _format = "2I2fi2f4B"  # 32 bytes
    _arrays = {"albedo_uv": [*"uv"], "lightmap_uv": [*"uv"], "colour": [*"rgba"]}
    _classes = {"albedo_uv": vector.vec2, "lightmap_uv": vector.vec2, "colour": colour.RGBA32}


class VertexLitFlat(core.Struct):  # LUMP 72 (0048)
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    albedo_uv: vector.vec2
    unknown: int
    __slots__ = ["position_index", "normal_index", "albedo_uv", "unknown"]
    _format = "2I2fi"  # 20 bytes
    _arrays = {"albedo_uv": [*"uv"]}
    _classes = {"albedo_uv": vector.vec2}


class VertexUnlit(core.Struct):  # LUMP 71 (0047)
    # NOTE: identical to VertexLitFlat?
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    albedo_uv: vector.vec2
    unknown: int
    __slots__ = ["position_index", "normal_index", "albedo_uv", "unknown"]
    _format = "2i2fi"  # 20 bytes
    _arrays = {"albedo_uv": [*"uv"]}
    _classes = {"albedo_uv": vector.vec2}


class VertexUnlitTS(core.Struct):  # LUMP 74 (004A)
    position_index: int  # index into VERTICES
    normal_index: int  # index into VERTEX_NORMALS
    albedo_uv: vector.vec2
    unknown: List[int]  # 8 bytes
    __slots__ = ["position_index", "normal_index", "albedo_uv", "unknown"]
    _format = "2I2f2i"  # 24 bytes
    _arrays = {"albedo_uv": [*"uv"], "unknown": 2}
    _classes = {"albedo_uv": vector.vec2}


class WaterBody(core.Struct):  # LUMP 44 (002C)
    origin: vector.vec3
    height: float  # sea level
    bounds: List[vector.vec3]
    first_center: int  # index into WaterBodyCenters
    num_centers: int  # also num_nodes
    first_vertex: int  # index into WaterBodyVertices
    first_index: int  # index into WaterBodyIndices
    num_vertices: int
    num_indices: int
    targetname_hash: int  # indexes targetname of linked entity
    uv_scale: float  # dimension of WaveData uv tiles (in uv 0..1 space)
    node_size: float
    __slots__ = [
        "origin", "height", "bounds",
        "first_center", "num_centers", "first_vertex", "first_index", "num_vertices", "num_indices",
        "targetname_hash", "uv_scale", "node_size"]
    _format = "10f6IQ2f"
    _arrays = {"origin": [*"xyz"], "bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}
    _classes = {"origin": vector.vec3, "bounds.mins": vector.vec3, "bounds.maxs": vector.vec3}


class WaterBodyVertex(core.Struct):  # LUMP 46 (002E)
    position: vector.vec3
    uv: vector.vec2
    colour: colour.RGBA32  # white or blue
    __slots__ = ["position", "uv", "colour"]
    _format = "5f4B"
    _arrays = {"position": [*"xyz"], "uv": [*"uv"], "colour": [*"rgba"]}
    _classes = {"position": vector.vec3, "uv": vector.vec2, "colour": colour.RGBA32}


# special lump classes, in alphabetical order:
# TODO: BVHLeafData
# TODO: UNKNOWN_37

class Unknown3(core.Struct):  # sprp GAME_LUMP (LUMP 35 / 0023)
    """all assumptions"""
    # NOTE: doesn't appear in smaller maps
    # -- could be to help with floating point precision
    unknown_1: List[float]  # SIMD aligned?
    flags: int  # TODO: IntFlags
    prop: int  # index into sprp.props?
    unknown_2: List[int]
    __slots__ = ["unknown_1", "flags", "prop", "unknown_2"]
    _format = "12f4i"  # 64 bytes
    _arrays = {"unknown_1": 12, "unknown_2": 2}


class GameLump_SPRP(titanfall2.GameLump_SPRPv13):  # sprp GameLump (LUMP 35)
    Unknown3Class = Unknown3


# NOTE: all Apex lumps are version 0, except GAME_LUMP
# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = titanfall2.BASIC_LUMP_CLASSES.copy()

pops = ("CM_BRUSH_SIDE_PLANE_OFFSETS", "CM_BRUSH_SIDE_PROPERTIES", "CM_PRIMITIVES", "CM_UNIQUE_CONTENTS",
        "TEXTURE_DATA_STRING_TABLE", "TRICOLL_BEVEL_STARTS", "TRICOLL_BEVEL_INDICES", "TRICOLL_TRIANGLES")
for LUMP_NAME in pops:
    BASIC_LUMP_CLASSES.pop(LUMP_NAME)
del LUMP_NAME, pops

BASIC_LUMP_CLASSES.update({
    "CONTENTS_MASKS":       {0: shared.UnsignedInts},
    "CSM_OBJ_REFERENCES":   {0: shared.UnsignedInts},
    "CUBEMAPS_AMBIENT_RCP": {0: shared.Floats},
    "HEIGHTFIELD_SAMPLES":  {0: shared.UnsignedShorts},
    "UNKNOWN_38":           {0: shared.UnsignedInts},
    "UNKNOWN_39":           {0: shared.Shorts},
    "WATER_BODY_INDICES":   {0: shared.UnsignedShorts}})


LUMP_CLASSES = titanfall2.LUMP_CLASSES.copy()

pops = ("CM_BRUSHES", "CM_BRUSH_SIDE_TEXTURE_VECTORS", "CM_GEO_SETS", "CM_GEO_SET_BOUNDS",
        "CM_GRID_CELLS", "CM_PRIMITIVE_BOUNDS", "LEAF_WATER_DATA",
        "LIGHTMAP_DATA_RTL_PAGES", "TRICOLL_HEADERS", "TRICOLL_NODES")
for LUMP_NAME in pops:
    LUMP_CLASSES.pop(LUMP_NAME)
del LUMP_NAME, pops

LUMP_CLASSES.update({
    "BVH_NODES":           {0: BVHNode},
    "CELL_AABB_NODES":     {0: CellAABBNode},
    "CSM_AABB_NODES":      {0: CSMAABBNode},
    "HEIGHTFIELDS":        {0: HeightField},
    "LIGHTMAP_HEADERS":    {0: titanfall.LightmapHeader},
    "MATERIAL_SORTS":      {0: MaterialSort},
    "MESHES":              {0: Mesh},
    "MODELS":              {0: Model},
    "PACKED_VERTICES":     {0: PackedVertex},
    "PLANES":              {0: quake3.Plane},
    "SHADOW_MESHES":       {0: ShadowMesh},
    "SURFACE_PROPERTIES":  {0: SurfaceProperty},
    "TEXTURE_DATA":        {0: TextureData},
    "VERTEX_BLINN_PHONG":  {0: VertexBlinnPhong},
    "VERTEX_LIT_BUMP":     {0: VertexLitBump},
    "VERTEX_LIT_FLAT":     {0: VertexLitFlat},
    "VERTEX_UNLIT":        {0: VertexUnlit},
    "VERTEX_UNLIT_TS":     {0: VertexUnlitTS},
    "WATER_BODIES":        {0: WaterBody},
    "WATER_BODY_CENTERS":  {0: WaterBodyVertex},
    "WATER_BODY_VERTICES": {0: WaterBodyVertex},
    "WORLD_LIGHTS":        {0: titanfall2.WorldLightv3}})


SPECIAL_LUMP_CLASSES = titanfall2.SPECIAL_LUMP_CLASSES.copy()

SPECIAL_LUMP_CLASSES.pop("CM_GRID")
# SPECIAL_LUMP_CLASSES.pop("PHYSICS_COLLIDE")  # currently disabled in titanfall.py
SPECIAL_LUMP_CLASSES.pop("TEXTURE_DATA_STRING_DATA")

SPECIAL_LUMP_CLASSES.update({
    "LEVEL_INFO":    {0: LevelInfo},
    "SURFACE_NAMES": {0: source.TextureDataStringData}})


GAME_LUMP_HEADER = source.GameLumpHeader

GAME_LUMP_CLASSES = {"sprp": {bsp_version: GameLump_SPRP for bsp_version in (47, 48, 49)}}


# branch exclusive methods, in alphabetical order:
def lit_vertex(bsp, vertex: Union[VertexLitBump, VertexLitFlat]) -> geometry.Vertex:
    position = bsp.VERTICES[vertex.position_index]
    normal = bsp.VERTEX_NORMALS[vertex.normal_index]
    uv1 = vertex.lightmap_uv if isinstance(vertex, VertexLitBump) else vector.vec2(0, 0)
    colour = vertex.colour if hasattr(vertex, "colour") else (0xFF, 0x00, 0xFF, 0xFF)
    return geometry.Vertex(position, normal, vertex.albedo_uv, uv1, colour=colour)


def mesh(bsp, mesh_index: int) -> geometry.Mesh:
    mesh = bsp.MESHES[mesh_index]
    # material
    material_sort = bsp.MATERIAL_SORTS[mesh.material_sort]
    material = geometry.Material(bsp.texture_data_surface_name(material_sort.texture_data))
    # indices
    start, length = mesh.first_mesh_index, mesh.num_triangles * 3
    indices = [material_sort.vertex_offset + i for i in bsp.MESH_INDICES[start:start + length]]
    # vertices
    vertex_lump = (mesh.flags & titanfall.MeshFlags.MASK_VERTEX).name
    converter = bsp.lit_vertex if vertex_lump.split("_")[1] == "LIT" else bsp.unlit_vertex
    VERTEX_LUMP = getattr(bsp, vertex_lump)
    vertices = [converter(VERTEX_LUMP[i]) for i in indices]
    return geometry.Mesh(material, geometry.triangle_soup(vertices))


def shadow_mesh(bsp, shadow_mesh_index: int) -> geometry.Mesh:
    no_normal = vector.vec3(0, 0, 0)
    shadow_mesh = bsp.SHADOW_MESHES[shadow_mesh_index]
    # material
    if shadow_mesh.material_sort == -1:
        material = geometry.Material("shadow")  # placeholder, might have a special material in-engine
    else:
        material_sort = bsp.MATERIAL_SORTS[shadow_mesh.material_sort]
        material = geometry.Material(bsp.texture_data_surface_name(material_sort.texture_data))
    # indices
    start = sum(sm.num_triangles * 3 for sm in bsp.SHADOW_MESHES[:shadow_mesh_index])
    length = shadow_mesh.num_triangles * 3
    indices = [shadow_mesh.vertex_offset + i for i in bsp.SHADOW_MESH_INDICES[start:start + length]]
    # vertices
    # TODO: convert each vertex once, then index
    if shadow_mesh.is_opaque:
        vertices = [geometry.Vertex(bsp.SHADOW_MESH_OPAQUE_VERTICES[i], no_normal) for i in indices]
    else:
        vertices = [bsp.SHADOW_MESH_ALPHA_VERTICES[i] for i in indices]
        vertices = [geometry.Vertex(v.position, no_normal, v.uv) for v in vertices]
    return geometry.Mesh(material, geometry.triangle_soup(vertices))


def texture_data_surface_name(bsp, texture_data_index: int) -> str:
    texture_data = bsp.TEXTURE_DATA[texture_data_index]
    return bsp.SURFACE_NAMES.as_bytes()[texture_data.name_index:].lstrip(b"\0").partition(b"\0")[0].decode()


def unlit_vertex(bsp, vertex: Union[VertexLitBump, VertexLitFlat]) -> geometry.Vertex:
    position = bsp.VERTICES[vertex.position_index]
    normal = bsp.VERTEX_NORMALS[vertex.normal_index]
    colour = vertex.colour if hasattr(vertex, "colour") else (0xFF, 0x00, 0xFF, 0xFF)
    return geometry.Vertex(position, normal, vertex.albedo_uv, colour=colour)


def water_body_model(bsp, water_body_index: int) -> geometry.Model:
    water_body = bsp.WATER_BODIES[water_body_index]
    origin = water_body.origin
    # material
    material_names = {e["material"] for e in bsp.ENTITIES.search(classname="water_body")}
    assert len(material_names) == 1, "need to use targetname_hash to get material"
    material = geometry.Material(list(material_names)[0])
    # geometry
    normal = vector.vec3(0, 0, 1)
    triangles = list()
    for i in range(0, water_body.num_indices, 3):
        offset = water_body.first_index + i
        triangles.append([
            bsp.WATER_BODY_VERTICES[j + water_body.first_vertex]
            for j in bsp.WATER_BODY_INDICES[offset:offset + 3]])
    triangles = [[geometry.Vertex(v.position - origin, normal, v.uv, colour=v.colour) for v in tri] for tri in triangles]
    return geometry.Model([geometry.Mesh(material, [*map(geometry.Polygon, triangles)])], origin)


# TODO: wave_model(bsp, water_body_index: int) -> geometry.Mesh:  # WaterBodyVertices & WaterBodyCenters


methods = [lit_vertex, mesh, titanfall.model, unlit_vertex,  # geo
           titanfall.search_all_entities, shared.worldspawn_volume,  # entities
           titanfall.occlusion_mesh, shadow_mesh, water_body_model,  # other geo
           texture_data_surface_name]  # materials
methods = {m.__name__: m for m in methods}
