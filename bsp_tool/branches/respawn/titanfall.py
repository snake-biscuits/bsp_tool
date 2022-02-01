# https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Titanfall
import enum
import io
import struct
from typing import Dict, List, Union

from .. import base
from .. import shared
from ..id_software import quake
from ..valve import source


FILE_MAGIC = b"rBSP"

BSP_VERSION = 29

GAME_PATHS = {"Titanfall": "Titanfall",
              "Titanfall: Online": "TitanfallOnline"}

GAME_VERSIONS = {"Titanfall": 29,
                 "Titanfall: Online": 29}  # NOTE: no .bsp_lump; only .bsp


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
    WORLD_LIGHTS = 0x0036
    UNUSED_55 = 0x0037
    UNUSED_56 = 0x0038
    UNUSED_57 = 0x0039
    UNUSED_58 = 0x003A
    UNUSED_59 = 0x003B
    UNUSED_60 = 0x003C
    UNUSED_61 = 0x003D
    PHYSICS_LEVEL = 0x003E  # from L4D2 / 2013 Source SDK? (2011: Portal 2)
    UNUSED_63 = 0x003F
    UNUSED_64 = 0x0040
    UNUSED_65 = 0x0041
    TRICOLL_TRIS = 0x0042
    UNUSED_67 = 0x0043
    TRICOLL_NODES = 0x0044
    TRICOLL_HEADERS = 0x0045
    PHYSICS_TRIANGLES = 0x0046
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
    UNUSED_122 = 0x007A
    LEVEL_INFO = 0x007B  # PVS related? tied to portals & cells
    SHADOW_MESH_OPAQUE_VERTICES = 0x007C
    SHADOW_MESH_ALPHA_VERTICES = 0x007D
    SHADOW_MESH_INDICES = 0x007E
    SHADOW_MESH_MESHES = 0x007F


LumpHeader = source.LumpHeader

# Rough map of the relationships between lumps:
#              /-> MaterialSort -> TextureData -> TextureDataStringTable -> TextureDataStringData
# Model -> Mesh -> MeshIndex -\-> VertexReservedX -> Vertex
#             \--> .flags (VertexReservedX)     \--> VertexNormal
#              \-> VertexReservedX               \-> .uv

# MeshBounds & Mesh are indexed in paralell?

# LeafWaterData -> TextureData -> water material
# NOTE: LeafWaterData is also used in calculating VPhysics / PHYSICS_COLLIDE

# ??? ShadowMesh -?> ShadowMeshIndices -?> ShadowMeshAlphaVertex
#                                     \-?> ShadowMeshOpaqueVertex

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

# CM_GRID probably defines the bounds of CM_GRID_CELLS, with CM_GRID_CELLS indexing other objects?
# GM_GRID is always 1x 28 byte entry???

# Grid -?> Brush -?> BrushSidePlaneOffset -?> Plane
# (? * ? + ?) * 4 -> GridCell


# engine limits:
class MAX(enum.Enum):
    MODELS = 1024
    TEXTURE_DATA = 2048
    WORLD_LIGHTS = 4064
    STATIC_PROPS = 40960

# NOTE: max map coords are -32768 -> 32768 along each axis (Apex is 64Kx64K, double this limit!)


# flag enums
class Flags(enum.IntFlag):
    # source.Surface (source.TextureInfo rolled into titanfall.TextureData ?)
    SKY_2D = 0x0002  # TODO: test overriding sky with this in-game
    SKY = 0x0004
    WARP = 0x0008  # Quake water surface?
    TRANSLUCENT = 0x0010  # decals & atmo?
    # titanfall.Mesh.flags
    VERTEX_LIT_FLAT = 0x000     # VERTEX_RESERVED_1
    VERTEX_LIT_BUMP = 0x200     # VERTEX_RESERVED_2
    VERTEX_UNLIT = 0x400        # VERTEX_RESERVED_0
    VERTEX_UNLIT_TS = 0x600     # VERTEX_RESERVED_3
    # VERTEX_BLINN_PHONG = 0x???  # VERTEX_RESERVED_4
    SKIP = 0x20000  # 0x200 in valve.source.Surface (<< 8?)
    TRIGGER = 0x40000  # guessing
    # masks
    MASK_VERTEX = 0x600


# classes for lumps, in alphabetical order:
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
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}


class Cell(base.Struct):  # LUMP 107 (006B)
    """BVH4? (GDC 2018 - Extreme SIMD: Optimized Collision Detection in Titanfall)
https://www.youtube.com/watch?v=6BIfqfC1i7U
https://gdcvault.com/play/1025126/Extreme-SIMD-Optimized-Collision-Detection"""
    a: int
    b: int
    c: int
    d: int  # always -1?
    __slots__ = [*"abcd"]
    _format = "4h"


class Cubemap(base.Struct):  # LUMP 42 (002A)
    origin: List[int]
    unknown: int  # index? flags?
    __slots__ = ["origin", "unknown"]
    _format = "3iI"
    _arrays = {"origin": [*"xyz"]}


# NOTE: only one 28 byte entry per file
class Grid(base.Struct):  # LUMP 85 (0055)
    scale: float  # scaled against some global vector in engine, I think
    min_x: int  # *close* to (world_mins * scale) + scale
    min_y: int  # *close* to (world_mins * scale) + scale
    unknown: List[int]
    __slots__ = ["scale", "min_x", "min_y", "unknown"]
    _format = "f6i"
    _arrays = {"unknown": 4}


class LeafWaterData(base.Struct):
    surface_z: float  # global Z height of the water's surface
    min_z: float  # bottom of the water volume?
    texture_data: int  # index to this LeafWaterData's TextureData
    _mapping = ["surface_z", "min_z", "texture_data"]
    _format = "2fI"


class LightmapHeader(base.Struct):  # LUMP 83 (0053)
    count: int  # assuming this counts the number of lightmaps this size
    # NOTE: there's actually 2 identically sized lightmaps for each header (for titanfall2)
    width: int
    height: int
    __slots__ = ["count", "width", "height"]
    _format = "I2H"


class LightProbeRef(base.Struct):  # LUMP 104 (0068)
    origin: List[float]  # coords of LightProbe
    lightprobe: int  # index of this LightProbeRef's LightProbe
    __slots__ = ["origin", "lightprobe"]
    _format = "3fI"
    _arrays = {"origin": [*"xyz"]}


class MaterialSort(base.MappedArray):  # LUMP 82 (0052)
    texture_data: int  # index of this MaterialSort's TextureData
    lightmap_header: int  # index of this MaterialSort's LightmapHeader
    cubemap: int  # index of this MaterialSort's Cubemap
    unknown: int
    vertex_offset: int  # offset into appropriate VERTEX_RESERVED_X lump
    _mapping = ["texture_data", "lightmap_header", "cubemap", "unknown", "vertex_offset"]
    _format = "4hi"  # 12 bytes


class Mesh(base.Struct):  # LUMP 80 (0050)
    first_mesh_index: int  # index into MeshIndices
    num_triangles: int  # number of triangles in MeshIndices after first_mesh_index
    first_vertex: int  # index to this Mesh's first VertexReservedX
    num_vertices: int
    unknown: List[int]
    # for mp_box.VERTEX_LIT_BUMP: (2, -256, -1,  ?,  ?,  ?)
    # for mp_box.VERTEX_UNLIT:    (0,   -1, -1, -1, -1, -1)
    material_sort: int  # index of this Mesh's MaterialSort
    flags: int  # Flags(mesh.flags & Flags.MASK_VERTEX).name == "VERTEX_RESERVED_X"
    __slots__ = ["first_mesh_index", "num_triangles", "first_vertex",
                 "num_vertices", "unknown", "material_sort", "flags"]
    _format = "I3H6hHI"  # 28 Bytes
    _arrays = {"unknown": 6}


class MeshBounds(base.Struct):  # LUMP 81 (0051)
    # NOTE: these are all guesses based on GDC 2018 - Extreme SIMD
    mins: List[float]  # TODO: verify
    flags_1: int  # unsure
    maxs: List[float]
    flags_2: int
    __slots__ = ["mins", "flags_1", "maxs", "flags_2"]
    _format = "3fI3fI"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}


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
    """SHADOW_MESH_INDICES offset is end of previous ShadowMesh"""
    vertex_offset: int  # add each index in SHADOW_MESH_INDICES[prev_end:prev_end + num_triangles * 3]
    num_triangles: int  # number of triangles in SHADOW_MESH_INDICES
    unknown: List[int]  # [1, -1] or [0, small_int]
    __slots__ = ["vertex_offset", "num_triangles", "unknown"]
    _format = "2I2h"
    _arrays = {"unknown": 2}


class ShadowMeshAlphaVertex(base.Struct):  # LUMP 125 (007D)
    x: float
    y: float
    z: float
    unknown: List[float]  # both are always from 0.0 -> 1.0 (uvs?)
    _format = "5f"
    __slots__ = [*"xyz", "unknown"]
    _arrays = {"unknown": 2}


class StaticPropv12(base.Struct):  # sprp GAME_LUMP (0023)
    origin: List[float]  # x, y, z
    angles: List[float]  # pitch, yaw, roll
    model_name: int  # index into GAME_LUMP.sprp.model_names
    first_leaf: int
    num_leaves: int  # NOTE: Titanfall doesn't have visleaves?
    solid_mode: int  # bitflags
    flags: int
    skin: int
    # NOTE: BobTheBob's definition varies here:
    # int skin; float fade_min, fade_max; Vector lighting_origin;
    cubemap: int  # index of this StaticProp's Cubemap
    unknown: int
    fade_distance: float
    cpu_level: List[int]  # min, max (-1 = any)
    gpu_level: List[int]  # min, max (-1 = any)
    diffuse_modulation: List[int]  # RGBA 32-bit colour
    scale: float
    disable_x360: int
    collision_flags: List[int]  # add, remove
    __slots__ = ["origin", "angles", "model_name", "first_leaf", "num_leaves",
                 "solid_mode", "flags", "skin", "cubemap", "unknown",
                 "forced_fade_scale", "cpu_level", "gpu_level",
                 "diffuse_modulation", "scale", "disable_x360", "collision_flags"]
    _format = "6f3H2Bi2h4i2f8bfi2H"
    _arrays = {"origin": [*"xyz"], "angles": [*"yzx"], "unknown": 6, "fade_distance": ["min", "max"],
               "cpu_level": ["min", "max"], "gpu_level": ["min", "max"],
               "diffuse_modulation": [*"rgba"], "collision_flags": ["add", "remove"]}


class TextureData(base.Struct):  # LUMP 2 (0002)
    """Hybrid of Source TextureData & TextureInfo"""
    reflectivity: List[float]  # matches .vtf reflectivity.rgb (always? black in r2)
    name_index: int  # index of material name in TEXTURE_DATA_STRING_DATA / TABLE
    size: List[int]  # dimensions of full texture
    view: List[int]  # dimensions of visible section of texture
    flags: int  # matches Mesh's .flags; probably from source.TextureInfo
    __slots__ = ["reflectivity", "name_index", "size", "view", "flags"]
    _format = "3f6i"
    _arrays = {"reflectivity": [*"rgb"],
               "size": ["width", "height"], "view": ["width", "height"]}


class TextureVector(base.Struct):  # LUMP 95 (005F)
    s: List[float]  # S vector
    t: List[float]  # T vector
    __slots__ = ["s", "t"]
    _format = "8f"
    _arrays = {"s": [*"xyzw"], "t": [*"xyzw"]}


class TricollHeader(base.Struct):  # LUMP 69 (0045)
    __slots__ = ["unknown"]
    _format = "11i"
    _arrays = {"unknown": 11}


class WorldLight(base.Struct):  # LUMP 54 (0036)
    __slots__ = ["unknown"]
    _format = "25I"  # 100 bytes
    _arrays = {"unknown": 25}


# special vertices
class VertexBlinnPhong(base.Struct):  # LUMP 75 (004B)
    """Not used?"""
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    __slots__ = ["position_index", "normal_index", "unknown"]
    _format = "4I"  # 16 bytes
    _arrays = {"unknown": 2}


class VertexLitBump(base.Struct):  # LUMP 73 (0049)
    """Common Worldspawn Geometry"""
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    uv0: List[float]  # albedo / normal / gloss / specular uv
    negative_one: int  # -1
    uv1: List[float]  # small 0-1 floats, lightmap uv?
    unknown: List[int]  # (0, 0, ?, ?)
    # {v[-2:] for v in mp_box.VERTEX_LIT_BUMP}}
    # {x[0] for x in _}.union({x[1] for x in _})  # all numbers
    # for "mp_box": {*range(27)} - {0, 1, 6, 17, 19, 22, 25}
    __slots__ = ["position_index", "normal_index", "uv0", "unknown"]
    _format = "2I2fi2f4i"  # 44 bytes
    _arrays = {"uv0": [*"uv"], "unknown": 7}


class VertexLitFlat(base.Struct):  # LUMP 72 (0048)
    """Uncommon Worldspawn Geometry"""
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    uv0: List[float]  # uv coords
    unknown: List[int]
    __slots__ = ["position_index", "normal_index", "uv0", "unknown"]
    _format = "2I2f5I"
    _arrays = {"uv0": [*"uv"], "unknown": 5}


class VertexUnlit(base.Struct):  # LUMP 71 (0047)
    """Tool Brushes"""
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    uv0: List[float]  # uv coords
    unknown: int  # usually -1
    __slots__ = ["position_index", "normal_index", "uv0", "unknown"]
    _format = "2I2fi"  # 20 bytes
    _arrays = {"uv0": [*"uv"]}


class VertexUnlitTS(base.Struct):  # LUMP 74 (004A)
    """Glass"""
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    uv0: List[float]  # uv coords
    unknown: List[int]
    __slots__ = ["position_index", "normal_index", "uv0", "unknown"]
    _format = "2I2f3I"  # 28 bytes
    _arrays = {"uv0": [*"uv"], "unknown": 3}


VertexReservedX = Union[VertexBlinnPhong, VertexLitBump, VertexLitFlat, VertexUnlit, VertexUnlitTS]  # type hint


# classes for special lumps, in alphabetical order:
class EntityPartitions(list):
    """name of each used .ent file"""  # [0] = "01*"; .0000.bsp_lump?
    def __init__(self, raw_lump: bytes):
        super().__init__(raw_lump.decode("ascii")[:-1].split(" "))

    def as_bytes(self) -> bytes:
        return " ".join(self).encode("ascii") + b"\0"


class GameLump_SPRP:
    """unique to TitanFall"""
    _static_prop_format: str  # StaticPropClass._format
    model_names: List[str]
    leaves: List[int]
    unknown_1: int
    unknown_2: int
    props: List[object]  # List[StaticPropClass]

    def __init__(self, raw_sprp_lump: bytes, StaticPropClass: object):
        self._static_prop_format = StaticPropClass._format
        sprp_lump = io.BytesIO(raw_sprp_lump)
        model_name_count = int.from_bytes(sprp_lump.read(4), "little")
        model_names = struct.iter_unpack("128s", sprp_lump.read(128 * model_name_count))
        setattr(self, "model_names", [t[0].replace(b"\0", b"").decode() for t in model_names])
        leaf_count = int.from_bytes(sprp_lump.read(4), "little")  # usually 0
        leaves = list(struct.iter_unpack("H", sprp_lump.read(2 * leaf_count)))
        setattr(self, "leaves", leaves)
        prop_count, unknown_1, unknown_2 = struct.unpack("3i", sprp_lump.read(12))
        self.unknown_1, self.unknown_2 = unknown_1, unknown_2
        # TODO: if StaticPropClass is None: split into appropriate groups of bytes
        read_size = struct.calcsize(StaticPropClass._format) * prop_count
        props = struct.iter_unpack(StaticPropClass._format, sprp_lump.read(read_size))
        setattr(self, "props", list(map(StaticPropClass.from_tuple, props)))

    def as_bytes(self) -> bytes:
        return b"".join([len(self.model_names).to_bytes(4, "little"),
                         *[struct.pack("128s", n.encode("ascii")) for n in self.model_names],
                         len(self.leaves).to_bytes(4, "little"),
                         *[struct.pack("H", L) for L in self.leaves],
                         struct.pack("3I", len(self.props), self.unknown_1, self.unknown_2),
                         *[struct.pack(self._static_prop_format, *p.flat()) for p in self.props]])


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = {"CM_BRUSH_SIDE_PLANE_OFFSETS": {0: shared.UnsignedShorts},
                      "CM_BRUSH_SIDE_PROPS":         {0: shared.UnsignedShorts},
                      "CM_GRID_CELLS":               {0: shared.UnsignedInts},
                      "CM_PRIMITIVES":               {0: shared.UnsignedInts},
                      "CM_UNIQUE_CONTENTS":          {0: shared.UnsignedInts},  # flags?
                      "CSM_OBJ_REFERENCES":          {0: shared.UnsignedShorts},
                      "MESH_INDICES":                {0: shared.UnsignedShorts},
                      "OBJ_REFERENCES":              {0: shared.UnsignedShorts},
                      "OCCLUSION_MESH_INDICES":      {0: shared.Shorts},
                      "PORTAL_EDGE_REFERENCES":      {0: shared.UnsignedShorts},
                      "PORTAL_VERTEX_REFERENCES":    {0: shared.UnsignedShorts},
                      "SHADOW_MESH_INDICES":         {0: shared.UnsignedShorts},
                      "TEXTURE_DATA_STRING_TABLE":   {0: shared.UnsignedShorts},
                      "TRICOLL_BEVEL_STARTS":        {0: shared.UnsignedShorts},
                      "TRICOLL_BEVEL_INDICES":       {0: shared.UnsignedInts}}

LUMP_CLASSES = {"CELLS":                             {0: Cell},
                "CELL_AABB_NODES":                   {0: Node},
                # "CELL_BSP_NODES":                    {0: Node},
                "CM_BRUSHES":                        {0: Brush},
                "CM_BRUSH_TEX_VECS":                 {0: TextureVector},
                "CM_GEO_SET_BOUNDS":                 {0: Bounds},
                "CM_PRIMITIVE_BOUNDS":               {0: Bounds},
                "CSM_AABB_NODES":                    {0: Node},
                "CUBEMAPS":                          {0: Cubemap},
                "LEAF_WATER_DATA":                   {0: LeafWaterData},
                "LIGHTMAP_HEADERS":                  {1: LightmapHeader},
                "LIGHTPROBE_REFERENCES":             {0: LightProbeRef},
                "MATERIAL_SORT":                     {0: MaterialSort},
                "MESHES":                            {0: Mesh},
                "MESH_BOUNDS":                       {0: MeshBounds},
                "MODELS":                            {0: Model},
                "OBJ_REFERENCE_BOUNDS":              {0: ObjRefBounds},
                "OCCLUSION_MESH_VERTICES":           {0: quake.Vertex},
                "PLANES":                            {1: Plane},
                "PORTALS":                           {0: Portal},
                "PORTAL_EDGES":                      {0: quake.Edge},
                "PORTAL_EDGE_INTERSECT_AT_VERTEX":   {0: PortalEdgeIntersect},
                "PORTAL_EDGE_INTERSECT_AT_EDGE":     {0: PortalEdgeIntersect},
                "PORTAL_EDGE_INTERSECT_HEADER":      {0: PortalEdgeIntersectHeader},
                "PORTAL_VERTICES":                   {0: quake.Vertex},
                "PORTAL_VERTEX_EDGES":               {0: PortalEdgeIntersect},
                "SHADOW_MESH_MESHES":                {0: ShadowMesh},
                "SHADOW_MESH_ALPHA_VERTICES":        {0: ShadowMeshAlphaVertex},
                "SHADOW_MESH_OPAQUE_VERTICES":       {0: quake.Vertex},
                "TEXTURE_DATA":                      {1: TextureData},
                "TRICOLL_HEADERS":                   {0: TricollHeader},
                "VERTEX_NORMALS":                    {0: quake.Vertex},
                "VERTICES":                          {0: quake.Vertex},
                "VERTEX_BLINN_PHONG":                {0: VertexBlinnPhong},
                "VERTEX_LIT_BUMP":                   {1: VertexLitBump},
                "VERTEX_LIT_FLAT":                   {1: VertexLitFlat},
                "VERTEX_UNLIT":                      {0: VertexUnlit},
                "VERTEX_UNLIT_TS":                   {0: VertexUnlitTS},
                "WORLD_LIGHTS":                      {1: WorldLight}}

SPECIAL_LUMP_CLASSES = {"CM_GRID":                   {0: Grid.from_bytes},
                        "ENTITY_PARTITIONS":         {0: EntityPartitions},
                        "ENTITIES":                  {0: shared.Entities},
                        # NOTE: .ent files are handled directly by the RespawnBsp class
                        "PAKFILE":                   {0: shared.PakFile},
                        "PHYSICS_COLLIDE":           {0: shared.physics.CollideLump},
                        "TEXTURE_DATA_STRING_DATA":  {0: shared.TextureDataStringData}}

GAME_LUMP_HEADER = source.GameLumpHeader

GAME_LUMP_CLASSES = {"sprp": {12: lambda raw_lump: GameLump_SPRP(raw_lump, StaticPropv12)}}


# branch exclusive methods, in alphabetical order:
def vertices_of_mesh(bsp, mesh_index: int) -> List[VertexReservedX]:
    """gets the VertexReservedX linked to bsp.MESHES[mesh_index]"""
    # https://raw.githubusercontent.com/Wanty5883/Titanfall2/master/tools/TitanfallMapExporter.py (McSimp)
    mesh = bsp.MESHES[mesh_index]
    material_sort = bsp.MATERIAL_SORT[mesh.material_sort]
    start = mesh.first_mesh_index
    finish = start + mesh.num_triangles * 3
    indices = [material_sort.vertex_offset + i for i in bsp.MESH_INDICES[start:finish]]
    VERTEX_LUMP = getattr(bsp, (Flags(mesh.flags) & Flags.MASK_VERTEX).name)
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
        results = entity_lump.search(**search)
        if len(results) != 0:
            out[LUMP_name] = results
    return out


def shadow_meshes_as_obj(bsp) -> str:
    """almost working"""
    # TODO: figure out how SHADOW_MESH_ALPHA_VERTICES are indexed
    # TODO: what does ShadowMesh.unknown relate to? alpha indexing?
    out = [f"# generated with bsp_tool from {bsp.filename}",
           "# SHADOW_MESH_OPAQUE_VERTICES"]
    for v in bsp.SHADOW_MESH_OPAQUE_VERTICES:
        out.append(f"v {v.x} {v.y} {v.z}")
    if hasattr(bsp, "SHADOW_MESH_ALPHA_VERTICES"):
        out.append("# SHADOW_MESH_ALPHA_VERTICES")
        for v in bsp.SHADOW_MESH_ALPHA_VERTICES:
            out.append(f"v {v.x} {v.y} {v.z}\nvt {v.unknown[0]} {v.unknown[1]}")
    # TODO: group by ShadowEnvironment if titanfall2
    end = 0
    for i, mesh in enumerate(bsp.SHADOW_MESH_MESHES):
        out.append(f"o mesh_{i}")
        for j in range(mesh.num_triangles):
            start = end + j * 3
            tri = bsp.SHADOW_MESH_INDICES[start:start + 3]
            assert max(tri) < len(bsp.SHADOW_MESH_OPAQUE_VERTICES)
            v_tri = [x + 1 + mesh.vertex_offset for x in tri]
            out.append(f"f {v_tri[0]} {v_tri[1]} {v_tri[2]}")
        end = start + 3
    return "\n".join(out)


# "debug" methods for investigating the compile process
def debug_TextureData(bsp):
    print("# TD_index  TD.name  TextureData.flags")
    for i, td in enumerate(bsp.TEXTURE_DATA):
        print(f"{i:02d} {bsp.TEXTURE_DATA_STRING_DATA[td.name_index]:<48s} {source.Surface(td.flags)!r}")


def debug_unused_TextureData(bsp):
    used_texture_datas = {bsp.MATERIAL_SORT[m.material_sort].texture_data for m in bsp.MESHES}
    return used_texture_datas.difference({*range(len(bsp.TEXTURE_DATA))})


def debug_Mesh_stats(bsp):
    print("# index  vertex_lump  texture_data_index  texture  mesh_indices_range")
    for i, model in enumerate(bsp.MODELS):
        print(f"# MODELS[{i}]")
        for j in range(model.first_mesh, model.first_mesh + model.num_meshes):
            mesh = bsp.MESHES[j]
            material_sort = bsp.MATERIAL_SORT[mesh.material_sort]
            texture_data = bsp.TEXTURE_DATA[material_sort.texture_data]
            texture_name = bsp.TEXTURE_DATA_STRING_DATA[texture_data.name_index]
            vertex_lump = (Flags(mesh.flags) & Flags.MASK_VERTEX).name
            indices = set(bsp.MESH_INDICES[mesh.first_mesh_index:mesh.first_mesh_index + mesh.num_triangles * 3])
            _min, _max = min(indices), max(indices)
            _range = f"({_min}->{_max})" if indices == {*range(_min, _max + 1)} else indices
            print(f"{j:02d} {vertex_lump:<15s} {material_sort.texture_data:02d} {texture_name:<48s} {_range}")


methods = [vertices_of_mesh, vertices_of_model,
           replace_texture, find_mesh_by_texture, get_mesh_texture,
           search_all_entities, shared.worldspawn_volume, shadow_meshes_as_obj,
           debug_TextureData, debug_unused_TextureData, debug_Mesh_stats]
