import enum
import io
import struct
from typing import Dict, List, Union

from .. import base
from .. import shared


BSP_VERSION = 29


class LUMP(enum.Enum):
    ENTITIES = 0x0000
    PLANES = 0x0001
    TEXTURE_DATA = 0x0002
    VERTICES = 0x0003
    UNUSED_4 = 0x0004
    UNUSED_5 = 0x0005
    UNUSED_6 = 0x0006
    UNUSED_7 = 0x0007
    UNUSED_8 = 0x0008
    UNUSED_9 = 0x0009
    UNUSED_10 = 0x000A
    UNUSED_11 = 0x000B
    UNUSED_12 = 0x000C
    UNUSED_13 = 0x000D
    MODELS = 0x000E
    UNUSED_15 = 0x000F
    UNUSED_16 = 0x0010
    UNUSED_17 = 0x0011
    UNUSED_18 = 0x0012
    UNUSED_19 = 0x0013
    UNUSED_20 = 0x0014
    UNUSED_21 = 0x0015
    UNUSED_22 = 0x0016
    UNUSED_23 = 0x0017
    ENTITY_PARTITIONS = 0x0018
    UNUSED_25 = 0x0019
    UNUSED_26 = 0x001A
    UNUSED_27 = 0x001B
    UNUSED_28 = 0x001C
    PHYSICS_COLLIDE = 0x001D
    VERTEX_NORMALS = 0x001E
    UNUSED_31 = 0x001F
    UNUSED_32 = 0x0020
    UNUSED_33 = 0x0021
    UNUSED_34 = 0x0022
    GAME_LUMP = 0x0023
    LEAF_WATER_DATA = 0x0024
    UNUSED_37 = 0x0025
    UNUSED_38 = 0x0026
    UNUSED_39 = 0x0027
    PAKFILE = 0x0028  # zip file, contains cubemaps
    UNUSED_41 = 0x0029
    CUBEMAPS = 0x002A
    TEXTURE_DATA_STRING_DATA = 0x002B
    TEXTURE_DATA_STRING_TABLE = 0x002C
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
    UNUSED_55 = 0x0037
    UNUSED_56 = 0x0038
    UNUSED_57 = 0x0039
    UNUSED_58 = 0x003A
    UNUSED_59 = 0x003B
    UNUSED_60 = 0x003C
    UNUSED_61 = 0x003D
    PHYSICS_LEVEL = 0x003E
    UNUSED_63 = 0x003F
    UNUSED_64 = 0x0040
    UNUSED_65 = 0x0041
    TRICOLL_TRIS = 0x0042
    UNUSED_67 = 0x0043
    TRICOLL_NODES = 0x0044
    TRICOLL_HEADERS = 0x0045
    PHYSICS_TRIANGLES = 0x0046
    VERTS_UNLIT = 0x0047        # VERTS_RESERVED_0
    VERTS_LIT_FLAT = 0x0048     # VERTS_RESERVED_1
    VERTS_LIT_BUMP = 0x0049     # VERTS_RESERVED_2
    VERTS_UNLIT_TS = 0x004A     # VERTS_RESERVED_3
    VERTS_BLINN_PHONG = 0x004B  # VERTS_RESERVED_4
    VERTS_RESERVED_5 = 0x004C
    VERTS_RESERVED_6 = 0x004D
    VERTS_RESERVED_7 = 0x004E
    MESH_INDICES = 0x004F
    MESHES = 0x0050
    MESH_BOUNDS = 0x0051
    MATERIAL_SORT = 0x0052
    LIGHTMAP_HEADERS = 0x0053
    UNUSED_84 = 0x0054
    CM_GRID = 0x0055
    CM_GRID_CELLS = 0x0056
    CM_GEO_SETS = 0x0057
    CM_GEO_SET_BOUNDS = 0x0058
    CM_PRIMITIVES = 0x0059
    CM_PRIMITIVE_BOUNDS = 0x005A
    CM_UNIQUE_CONTENTS = 0x005B
    CM_BRUSHES = 0x005C
    CM_BRUSH_SIDE_PLANE_OFFSETS = 0x005D
    CM_BRUSH_SIDE_PROPS = 0x005E
    CM_BRUSH_TEX_VECS = 0x005F
    TRICOLL_BEVEL_STARTS = 0x0060
    TRICOLL_BEVEL_INDICES = 0x0061
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
    PORTAL_EDGE_ISECT_AT_EDGE = 0x0072
    PORTAL_EDGE_ISECT_AT_VERT = 0x0073
    PORTAL_EDGE_ISECT_HEADER = 0x0074
    OCCLUSION_MESH_VERTS = 0x0075
    OCCLUSION_MESH_INDICES = 0x0076
    CELL_AABB_NODES = 0x0077
    OBJ_REFS = 0x0078
    OBJ_REF_BOUNDS = 0x0079
    UNUSED_122 = 0x007A
    LEVEL_INFO = 0x007B
    SHADOW_MESH_OPAQUE_VERTS = 0x007C
    SHADOW_MESH_ALPHA_VERTS = 0x007D
    SHADOW_MESH_INDICES = 0x007E
    SHADOW_MESH_MESHES = 0x007F

# Rough map of the relationships between lumps:
# Model -> Mesh -> MaterialSort -> TextureData
#                              |-> VertexReservedX
#                              |-> MeshIndex
#
# MeshBounds & Mesh (must have equal number of each)
#
# TextureData -> TextureDataStringTable -> TextureDataStringTable
# VertexReservedX -> Vertex
#                |-> VertexNormal
#
# LeafWaterData -> TextureData -> water material
# NOTE: LeafWaterData is also used in calculating VPhysics / PHYSICS_COLLIDE
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


# classes for lumps (alphabetical order)
class Bounds(base.Struct):  # LUMP 88 & 90 (0058 & 005A)
    unknown: List[int]  # shorts seem to work best? doesn't look like AABB bounds?
    __slots__ = ["unknown"]
    _format = "8h"
    _arrays = {"unknown": 8}


class Brush(base.Struct):  # LUMP 92 (005C)
    mins: List[float]
    flags: int
    maxs: List[float]
    unknown: int  # almost always 0
    __slots__ = ["mins", "flags", "maxs", "unknown"]
    _format = "3fi3fi"
    _arrays = {"mins": [*"xyz"], "maxs:": [*"xyz"]}


class Cell(base.Struct):  # LUMP 107 (006B)
    a: int
    b: int
    c: int
    d: int  # always -1?
    _format = "4h"
    __slots__ = [*"abcd"]


class Cubemap(base.Struct):  # LUMP 42 (002A)
    origin: List[int]
    unknown: int  # index? flags?
    __slots__ = ["origin", "unknown"]
    _format = "3iI"
    _arrays = {"origin": [*"xyz"]}


# NOTE: only one 28 byte entry per file
class Grid(base.Struct):  # LUMP 85 (0055)
    scale: float  # scaled against some global vector in engine, I think
    unknown: List[int]
    __slots__ = ["scale", "unknown"]
    _format = "f6i"
    _arrays = {"unknown": 6}


class LeafWaterData(base.Struct):
    surface_z: float  # global Z height of the water's surface
    min_z: float  # bottom of the water volume?
    texture_data: int  # index to this LeafWaterData's TextureData
    _format = "2fI"
    _mapping = ["surface_z", "min_z", "texture_data"]


class LightmapHeader(base.Struct):  # LUMP 83 (0053)
    count: int  # assuming this counts the number of lightmaps this size
    # NOTE: there's actually 2 identically sized lightmaps for each header (for titanfall2)
    width: int
    height: int
    __slots__ = ["count", "width", "height"]
    _format = "I2H"


class MaterialSort(base.Struct):  # LUMP 82 (0052)
    texture_data: int  # index of this MaterialSort's TextureData
    lightmap_header: int  # index of this MaterialSort's LightmapHeader
    cubemap: int  # index of this MaterialSort's Cubemap
    vertex_offset: int  # offset into appropriate VERTS_RESERVED_X lump
    __slots__ = ["texture_data", "lightmap_header", "cubemap", "vertex_offset"]
    _format = "2h2I"  # 12 bytes


class Mesh(base.Struct):  # LUMP 80 (0050)
    start_index: int  # index into this Mesh's VertexReservedX
    num_triangles: int  # number of triangles in VertexReservedX after start_index
    unknown: List[int]
    material_sort: int  # index of this Mesh's MaterialSort
    flags: int  # specifies VertexReservedX to draw vertices from
    # 0x4, 0x8, 0x10, 0x20  (0x10 MESHES?)
    # 0x200, 0x400  (MESHES?)
    # 0x800, 0x1000, 0x2000, 0x40000, 0x100000, 0x200000
    __slots__ = ["start_index", "num_triangles", "unknown",
                 "material_sort", "flags"]
    _format = "IHh3ihHI"  # 28 Bytes
    _arrays = {"unknown": 5}


class MeshBounds(base.Struct):  # LUMP 81 (0051)
    # NOTE: these are all guesses
    mins: List[float]
    flags_1: int  # is this finally the extreme SIMD AABB?
    maxs: List[float]
    flags_2: int
    __slots__ = ["mins", "flags_1", "maxs", "flags_2"]
    _format = "3fI3fI"
    _arrays = {"unknown": 8}


class Model(base.Struct):  # LUMP 14 (000E)
    """bsp.MODELS[0] is always worldspawn"""
    mins: List[float]  # bounding box mins
    maxs: List[float]  # bounding box maxs
    first_mesh: int  # index of first Mesh
    num_meshes: int  # number of Meshes after first_mesh in this model
    __slots__ = ["mins", "maxs", "first_mesh", "num_meshes"]
    _format = "6f2I"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}


class Node(base.Struct):  # LUMP 99, 106 & 119 (0063, 006A & 0077)
    mins: List[float]
    unknown_1: int
    maxs: List[float]
    unknown_2: int
    __slots__ = ["mins", "unknown_1", "maxs", "unknown_2"]
    _format = "3fi3fi"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}


class ObjRefBounds(base.Struct):  # LUMP 121 (0079)
    # NOTE: w is always 0, could be a copy of the Node class
    # - CM_BRUSHES Brush may also use this class
    # NOTE: introduced in v29, not present in v25
    mins: List[float]
    maxs: List[float]
    _format = "8f"
    __slots__ = ["mins", "maxs"]
    _arrays = {"mins": [*"xyzw"], "maxs": [*"xyzw"]}


class Plane(base.Struct):  # LUMP 1 (0001)
    normal: List[float]  # normal unit vector
    distance: float
    __slots__ = ["normal", "distance"]
    _format = "4f"
    _arrays = {"normal": [*"xyz"]}


class Portal(base.Struct):  # LUMP 108 (006C)
    unknown: List[int]
    index: int  # looks like an index
    __slots__ = ["unknown", "index"]
    _format = "3I"
    _arrays = {"unknown": 2}


class PortalEdge(list):  # LUMP 110 (006E)
    _format = "2h"


class PortalEdgeIntersect(base.Struct):  # LUMP 114 & 115 (0072 & 0073)
    unknown: List[int]  # oftens ends with a few -1, allows for variable length?
    __slots__ = ["unknown"]
    _format = "4i"
    _arrays = {"unknown": 4}


class PortalEdgeIntersectHeader(base.MappedArray):  # LUMP 116 (0074)
    start: int  # 0 - 3170
    count: int  # 1 - 6
    _mapping = ["start", "count"]  # assumed
    _format = "2i"


class ShadowMesh(base.Struct):  # LUMP 127 (007F)
    start_index: int  # unsure what lump is indexed
    num_triangles: int
    # unknown.one: int  # usually one
    # unknown.negative_one: int  # usually negative one
    __slots__ = ["start_index", "num_triangles", "unknown"]
    _format = "2I2h"  # assuming 12 bytes
    _arrays = {"unknown": ["one", "negative_one"]}


class ShadowMeshAlphaVertex(base.Struct):  # LUMP 125 (007D)
    origin: List[float]
    unknown: List[int]  # unknown[1] might be a float
    _format = "3f2i"
    __slots__ = ["origin", "unknown"]
    _arrays = {"origin": [*"xyz"], "unknown": 2}


class StaticPropv12(base.Struct):  # sprp GAME_LUMP (0023)
    origin: List[float]  # x, y, z
    angles: List[float]  # pitch, yaw, roll
    mdl_name: int  # index into GAME_LUMP.sprp.mdl_names
    first_leaf: int
    num_leaves: int  # NOTE: Titanfall doesn't have visleaves?
    solid_mode: int  # bitflags
    flags: int
    skin: int
    cubemap: int  # index of this StaticProp's Cubemap
    fade_distance: float
    lighting_origin: List[float]  # x, y, z
    forced_fade_scale: float  # two fade distances?
    cpu_level: List[int]  # min, max (-1 = any)
    gpu_level: List[int]  # min, max (-1 = any)
    diffuse_modulation: List[int]  # RGBA 32-bit colour
    collision_flags: List[int]  # add, remove
    __slots__ = ["origin", "angles", "mdl_name", "first_leaf", "num_leaves",
                 "solid_mode", "flags", "skin", "cubemap", "fade_distance",
                 "lighting_origin", "forced_fade_scale", "cpu_level", "gpu_level",
                 "diffuse_modulation", "disable_x360", "scale", "collision_flags"]
    _format = "6f3H2BiI6f4b4B?f2H"
    _arrays = {"origin": [*"xyz"], "angles": [*"yzx"],
               "fade_distance": ["min", "max"], "lighting_origin": [*"xyz"],
               "cpu_level": ["min", "max"], "gpu_level": ["min", "max"],
               "diffuse_modulation": [*"rgba"], "collision_flags": ["add", "remove"]}


class TextureData(base.Struct):  # LUMP 2 (0002)
    reflectivity: List[int]  # copy of .vtf reflectivity value, for bounce lighting
    name_index: int  # index of material name in TEXTURE_DATA_STRING_DATA / TABLE
    width: int
    height: int
    view_width: int
    view_height: int
    flags: int
    __slots__ = ["reflectivity", "name_index", "width", "height",
                 "view_width", "view_height", "flags"]
    _format = "9i"
    _arrays = {"reflectivity": [*"rgb"]}


class TextureVector(base.Struct):  # LUMP 95 (005F)
    __slots__ = ["s", "t"]
    __format = "8f"
    _arrays = {"s": [*"xyzw"], "t": [*"xyzw"]}


class Vertex(base.MappedArray):  # LUMP 3 (0003)
    """3D position / normal vector"""
    x: float
    y: float
    z: float
    _mapping = [*"xyz"]
    _format = "3f"


# special vertices
class VertexBlinnPhong(base.Struct):  # LUMP 75 (004B)
    __slots__ = ["position_index", "normal_index", "unknown"]
    _format = "4I"  # 16 bytes
    _arrays = {"unknown": 2}


class VertexLitBump(base.Struct):  # LUMP 73 (0049)
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    uv: List[float]  # albedo / normal / gloss / specular uv
    uv2: List[float]  # secondary uv? any target?
    uv3: List[float]  # lightmap uv
    unknown: List[int]  # unknown
    __slots__ = ["position_index", "normal_index", "uv", "uv2", "uv3", "unknown"]
    _format = "2I6f3I"  # 44 bytes
    _arrays = {"uv": [*"uv"], "uv2": [*"uv"], "uv3": [*"uv"], "unknown": 3}


class VertexLitFlat(base.Struct):  # LUMP 72 (0048)
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    uv: List[float]  # uv coords
    unknown: List[int]
    __slots__ = ["position_index", "normal_index", "uv", "unknown"]
    _format = "2I2f5I"
    _arrays = {"uv": [*"uv"], "unknown": 5}


class VertexUnlit(base.Struct):  # LUMP 71 (0047)
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    uv: List[float]  # uv coords
    unknown: int
    __slots__ = ["position_index", "normal_index", "uv", "unknown"]
    _format = "2I2fI"  # 20 bytes
    _arrays = {"uv": [*"uv"]}


class VertexUnlitTS(base.Struct):  # LUMP 74 (004A)
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    uv: List[float]  # uv coords
    unknown: List[int]
    __slots__ = ["position_index", "normal_index", "uv", "unknown"]
    _format = "2I2f3I"  # 28 bytes
    _arrays = {"uv": [*"uv"], "unknown": 3}


# classes for special lumps (alphabetical order)
class EntityPartition(list):
    def __init__(self, raw_lump: bytes):
        super().__init__(raw_lump.decode("ascii")[:-1].split(" "))

    def as_bytes(self) -> bytes:
        return b" ".join([*self, b"\x00"])


class GameLump_SPRP:  # unique to Titanfall
    def __init__(self, raw_sprp_lump: bytes, StaticPropClass: object):
        self._static_prop_format = StaticPropClass._format
        sprp_lump = io.BytesIO(raw_sprp_lump)
        mdl_name_count = int.from_bytes(sprp_lump.read(4), "little")
        mdl_names = struct.iter_unpack("128s", sprp_lump.read(128 * mdl_name_count))
        setattr(self, "mdl_names", [t[0].replace(b"\0", b"").decode() for t in mdl_names])
        leaf_count = int.from_bytes(sprp_lump.read(4), "little")  # usually 0
        leafs = list(struct.iter_unpack("H", sprp_lump.read(2 * leaf_count)))
        setattr(self, "leafs", leafs)
        prop_count, unknown_1, unknown_2 = struct.unpack("3i", sprp_lump.read(12))
        self.unknown_1, self.unknown_2 = unknown_1, unknown_2
        prop_size = struct.calcsize(StaticPropClass._format)
        props = struct.iter_unpack(StaticPropClass._format, sprp_lump.read(prop_count * prop_size))
        setattr(self, "props", list(map(StaticPropClass, props)))

    def as_bytes(self) -> bytes:
        return b"".join([int.to_bytes(len(self.prop_names), 4, "little"),
                         *[struct.pack("128s", n) for n in self.prop_names],
                         int.to_bytes(len(self.leafs), 4, "little"),
                         *[struct.pack("H", L) for L in self.leafs],
                         *struct.pack("3I", len(self.props), self.unknown_1, self.unknown_2),
                         *[struct.pack(self._static_prop_format, *p.flat()) for p in self.props]])


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = {"CM_BRUSH_SIDE_PLANE_OFFSETS": {0: shared.UnsignedShorts},
                      "CM_BRUSH_SIDE_PROPS":         {0: shared.UnsignedShorts},
                      "CM_GRID_CELLS":               {0: shared.UnsignedInts},
                      "CM_PRIMITIVES":               {0: shared.UnsignedInts},
                      "CM_UNIQUE_CONTENTS":          {0: shared.UnsignedInts},  # flags?
                      "CSM_OBJ_REFS":                {0: shared.UnsignedShorts},
                      "MESH_INDICES":                {0: shared.UnsignedShorts},
                      "OBJ_REFS":                    {0: shared.UnsignedShorts},
                      "OCCLUSION_MESH_INDICES":      {0: shared.Shorts},
                      "PORTAL_EDGE_REFS":            {0: shared.UnsignedShorts},
                      "PORTAL_VERT_REFS":            {0: shared.UnsignedShorts},
                      "SHADOW_MESH_INDICES":         {0: shared.UnsignedShorts},
                      "TEXTURE_DATA_STRING_TABLE":   {0: shared.UnsignedShorts},
                      "TRICOLL_BEVEL_STARTS":        {0: shared.UnsignedShorts},
                      "TRICOLL_BEVEL_INDICES":       {0: shared.UnsignedInts}}

LUMP_CLASSES = {"CELLS":                     {0: Cell},
                "CELL_AABB_NODES":           {0: Node},
                # "CELL_BSP_NODES":            {0: Node},
                "CM_BRUSHES":                {0: Brush},
                # "CM_BRUSH_TEX_VECS":         {0: TextureVector},
                "CM_GEO_SET_BOUNDS":         {0: Bounds},
                "CM_GRID":                   {0: Grid},
                "CM_PRIMITIVE_BOUNDS":       {0: Bounds},
                "CSM_AABB_NODES":            {0: Node},
                "CUBEMAPS":                  {0: Cubemap},
                "LEAF_WATER_DATA":           {0: LeafWaterData},
                "LIGHTMAP_HEADERS":          {1: LightmapHeader},
                "MATERIAL_SORT":             {0: MaterialSort},
                "MESHES":                    {0: Mesh},
                "MESH_BOUNDS":               {0: MeshBounds},
                "MODELS":                    {0: Model},
                "OBJ_REF_BOUNDS":            {0: ObjRefBounds},
                "OCCLUSION_MESH_VERTS":      {0: Vertex},
                "PLANES":                    {1: Plane},
                "PORTALS":                   {0: Portal},
                "PORTAL_EDGES":              {0: PortalEdge},
                "PORTAL_EDGE_ISECT_AT_VERT": {0: PortalEdgeIntersect},
                "PORTAL_EDGE_ISECT_AT_EDGE": {0: PortalEdgeIntersect},
                "PORTAL_EDGE_ISECT_HEADER":  {0: PortalEdgeIntersectHeader},
                "PORTAL_VERTS":              {0: Vertex},
                "PORTAL_VERT_EDGES":         {0: PortalEdgeIntersect},
                "SHADOW_MESH_MESHES":        {0: ShadowMesh},
                "SHADOW_MESH_ALPHA_VERTS":   {0: ShadowMeshAlphaVertex},
                "SHADOW_MESH_OPAQUE_VERTS":  {0: Vertex},
                "TEXTURE_DATA":              {1: TextureData},
                "VERTEX_NORMALS":            {0: Vertex},
                "VERTICES":                  {0: Vertex},
                "VERTS_BLINN_PHONG":         {0: VertexBlinnPhong},
                "VERTS_LIT_BUMP":            {1: VertexLitBump},
                "VERTS_LIT_FLAT":            {1: VertexLitFlat},
                "VERTS_UNLIT":               {0: VertexUnlit},
                "VERTS_UNLIT_TS":            {0: VertexUnlitTS}}

SPECIAL_LUMP_CLASSES = {"ENTITY_PARTITIONS":        {0: EntityPartition},
                        "ENTITIES":                 {0: shared.Entities},
                        "PAKFILE":                  {0: shared.PakFile},
                        "PHYSICS_COLLIDE":          {0: shared.PhysicsCollide},
                        "TEXTURE_DATA_STRING_DATA": {0: shared.TextureDataStringData}}
# NOTE: .ent files are handled by the RespawnBsp class directly

GAME_LUMP_CLASSES = {"sprp": {12: lambda raw_lump: GameLump_SPRP(raw_lump, StaticPropv12)}}


# branch exclusive methods, in alphabetical order:
# mesh.flags -> VERTS_RESERVED_X
mesh_types = {0x600: "VERTS_UNLIT_TS",     # VERTS_RESERVED_3
              # 0x?: "VERTS_BLINN_PHONG",  # VERTS_RESERVED_4
              0x400: "VERTS_UNLIT",        # VERTS_RESERVED_0
              0x200: "VERTS_LIT_BUMP",     # VERTS_RESERVED_2
              0x000: "VERTS_LIT_FLAT"}     # VERTS_RESERVED_1

VertexReservedX = Union[VertexBlinnPhong, VertexLitBump, VertexLitFlat, VertexUnlit, VertexUnlitTS]


# https://raw.githubusercontent.com/Wanty5883/Titanfall2/master/tools/TitanfallMapExporter.py (McSimp)
def vertices_of_mesh(bsp, mesh_index: int) -> List[VertexReservedX]:
    """gets the VertexReservedX linked to bsp.MESHES[mesh_index]"""
    mesh = bsp.MESHES[mesh_index]
    material_sort = bsp.MATERIAL_SORT[mesh.material_sort]
    start = mesh.start_index
    finish = start + mesh.num_triangles * 3
    indices = [material_sort.vertex_offset + i for i in bsp.MESH_INDICES[start:finish]]
    VERTEX_LUMP = getattr(bsp, mesh_types[mesh.flags & 0x600])
    # NOTE: which vertex lump is used matters for shaders & buffer assembly
    return [VERTEX_LUMP[i] for i in indices]


def vertices_of_model(bsp, model_index: int) -> List[VertexReservedX]:
    """gets the VertexReservedX linked to every Mesh in bsp.MODELS[model_index]"""
    # NOTE: model 0 is worldspawn, other models are referenced by entities
    out = list()
    model = bsp.MODELS[model_index]
    for i in range(model.first_mesh, model.num_meshes):
        out.extend(bsp.vertices_of_mesh(i))
    return out


def replace_texture(bsp, texture: str, replacement: str):
    """Substitutes a texture name in the .bsp (if it is present)"""
    texture_index = bsp.TEXTURE_DATA_STRING_DATA.index(texture)  # fails if texture is not in bsp
    bsp.TEXTURE_DATA_STRING_DATA.insert(texture_index, replacement)
    bsp.TEXTURE_DATA_STRING_DATA.pop(texture_index + 1)
    bsp.TEXTURE_DATA_STRING_TABLE = list()
    offset = 0  # starting index of texture name in raw TEXTURE_DATA_STRING_DATA
    for texture_name in bsp.TEXTURE_DATA_STRING_DATA:
        bsp.TEXTURE_DATA_STRING_TABLE.append(offset)
        offset += len(texture_name) + 1  # +1 for null byte


def find_mesh_by_texture(bsp, texture: str) -> Mesh:
    """This is a generator, will yeild one Mesh at a time.  Very innefficient!"""
    texture_index = bsp.TEXTURE_DATA_STRING_DATA.index(texture)  # fails if texture is not in bsp
    for texture_data_index, texture_data in enumerate(bsp.TEXTURE_DATA):
        if texture_data.name_index != texture_index:
            continue
        for material_sort_index, material_sort in enumerate(bsp.MATERIAL_SORT):
            if material_sort.texture_data != texture_data_index:
                continue
            for mesh in bsp.MESHES:
                if mesh.material_sort == material_sort_index:
                    yield mesh


def get_mesh_texture(bsp, mesh_index: int) -> str:
    """Returns the name of the .vmt applied to bsp.MESHES[mesh_index]"""
    mesh = bsp.MESHES[mesh_index]
    material_sort = bsp.MATERIAL_SORT[mesh.material_sort]
    texture_data = bsp.TEXTURE_DATA[material_sort.texture_data]
    return bsp.TEXTURE_DATA_STRING_DATA[texture_data.name_index]


def search_all_entities(bsp, **search: Dict[str, str]) -> Dict[str, List[Dict[str, str]]]:
    """search_all_entities(key="value") -> {"LUMP": [{"key": "value", ...}]}"""
    out = dict()
    for LUMP_name in ("ENTITIES", *(f"ENTITIES_{s}" for s in ("env", "fx", "script", "snd", "spawn"))):
        entity_lump = getattr(bsp, LUMP_name, shared.Entities(b""))
        results = entity_lump.find(**search)
        if len(results) != 0:
            out[LUMP_name] = results
    return out


methods = [vertices_of_mesh, vertices_of_model,
           replace_texture, find_mesh_by_texture, get_mesh_texture,
           search_all_entities]
