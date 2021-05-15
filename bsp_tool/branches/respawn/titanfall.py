import enum
import io
import struct
from typing import List, Union

from .. import base
from .. import shared


BSP_VERSION = 29


class LUMP(enum.Enum):
    ENTITIES = 0x0000
    PLANES = 0x0001
    TEXDATA = 0x0002
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
    PHYSICSCOLLIDE = 0x001D
    VERTEX_NORMALS = 0x001E
    UNUSED_31 = 0x001F
    UNUSED_32 = 0x0020
    UNUSED_33 = 0x0021
    UNUSED_34 = 0x0022
    GAME_LUMP = 0x0023
    LEAF_WATERDATA = 0x0024
    UNUSED_37 = 0x0025
    UNUSED_38 = 0x0026
    UNUSED_39 = 0x0027
    PAKFILE = 0x0028  # zip file, contains cubemaps
    UNUSED_41 = 0x0029
    CUBEMAPS = 0x002A
    TEXDATA_STRING_DATA = 0x002B
    TEXDATA_STRING_TABLE = 0x002C
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
    WORLDLIGHTS_PARENT_INFO = 0x0037  # unused
    UNUSED_56 = 0x0038
    UNUSED_57 = 0x0039
    UNUSED_58 = 0x003A
    UNUSED_59 = 0x003B
    UNUSED_60 = 0x003C
    UNUSED_61 = 0x003D
    PHYSICSLEVEL = 0x003E  # length 0, version 6?
    UNUSED_63 = 0x003F
    UNUSED_64 = 0x0040
    UNUSED_65 = 0x0041
    TRICOLL_TRIS = 0x0042
    UNUSED_67 = 0x0043
    TRICOLL_NODES = 0x0044
    TRICOLL_HEADERS = 0x0045
    PHYSTRIS = 0x0046
    VERTS_UNLIT = 0x0047     # VERTS_RESERVED_0
    VERTS_LIT_FLAT = 0x0048  # VERTS_RESERVED_1  # what flags?
    VERTS_LIT_BUMP = 0x0049  # VERTS_RESERVED_2
    VERTS_UNLIT_TS = 0x004A  # VERTS_RESERVED_3
    VERTS_RESERVED_4 = 0x004B  # unused
    VERTS_RESERVED_5 = 0x004C  # unused
    VERTS_RESERVED_6 = 0x004D  # unused
    VERTS_RESERVED_7 = 0x004E  # unused
    MESH_INDICES = 0x004F
    MESHES = 0x0050
    MESH_BOUNDS = 0x0051
    MATERIAL_SORT = 0x0052
    LIGHTMAP_HEADERS = 0x0053
    LIGHTMAP_DATA_DXT5 = 0x0054  # unused
    CM_GRID = 0x0055
    CM_GRIDCELLS = 0x0056
    CM_GEO_SETS = 0x0057
    CM_GEO_SET_BOUNDS = 0x0058
    CM_PRIMS = 0x0059
    CM_PRIM_BOUNDS = 0x005A
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
    PORTAL_EDGE_ISECT_EDGE = 0x0072
    PORTAL_EDGE_ISECT_AT_VERT = 0x0073
    PORTAL_EDGE_ISECT_HEADER = 0x0074
    OCCLUSION_MESH_VERTS = 0x0075
    OCCLUSION_MESH_INDICES = 0x0076
    CELL_AABB_NODES = 0x0077
    OBJ_REFS = 0x0078
    OBJ_REF_BOUNDS = 0x0079
    LIGHTMAP_DATA_REAL_TIME_LIGHT_PAGE = 0x007A  # unused
    LEVEL_INFO = 0x007B
    SHADOW_MESH_OPAQUE_VERTS = 0x007C
    SHADOW_MESH_ALPHA_VERTS = 0x007D
    SHADOW_MESH_INDICES = 0x007E
    SHADOW_MESH_MESHES = 0x007F


lump_header_address = {LUMP_ID: (16 + i * 16) for i, LUMP_ID in enumerate(LUMP)}


# classes for lumps (alphabetical order) [13 / 128] + 3 special lumps (57 unused)
class Brush(base.Struct):  # LUMP 92 (005C)
    origin: List[float]
    contents: int  # looks like a bit flags
    __slots__ = ["origin", "contents"]
    _format = "3fI"  # seems short
    _arrays = {"origin": [*"xyz"]}


class Cubemap(base.Struct):  # LUMP 42 (002A)
    origin: List[int]
    unknown: int  # index? flags?
    __slots__ = ["origin", "unknown"]
    _format = "3iI"
    _arrays = {"origin": [*"xyz"]}


class LightmapHeader(base.Struct):  # LUMP 83 (0053)
    count: int  # assuming this counts the number of lightmaps this size
    width: int
    height: int
    __slots__ = ["count", "width", "height"]
    _format = "I2H"
    # there's actually 2 identically sized lightmaps for each header (for titanfall2)


class MaterialSort(base.Struct):  # LUMP 82 (0052)
    # MaterialSort -> TexData, VertexReservedX
    # TexData -> TexDataStringTable -> TexDataStringTable
    # VertexReservedX -> Vertex, Vertex(normal), VertexReservedX.uv
    texdata: int  # index of this MaterialSort's Texdata
    lightmap_header: int  # index of this MaterialSort's LightmapHeader
    cubemap: int  # index of this MaterialSort's Cubemap
    vertex_offset: int
    __slots__ = ["texdata", "lightmap_header", "cubemap", "vertex_offset"]
    _format = "2h2I"  # 12 bytes


class Mesh(base.Struct):  # LUMP 80 (0050)
    # Mesh -> MaterialSort -> TexData, VertexReservedX
    # TexData -> TexDataStringTable -> TexDataStringTable
    # VertexReservedX -> Vertex, Vertex(normal), VertexReservedX.uv
    start_index: int  # index into this Mesh's VertexReservedX
    num_triangles: int  # number of Triangle in VertexReservedX after start_index
    unknown: List[int]
    material_sort: int  # index of this Mesh's MaterialSort
    flags: int  # specifies VertexReservedX to draw vertices from
    __slots__ = ["start_index", "num_triangles", "unknown",
                 "material_sort", "flags"]
    _format = "IHh3ihHI"  # 28 Bytes
    _arrays = {"unknown": [*"abcde"]}


class MeshIndex(int):  # LUMP 79 (004F)
    """Used in assembling meshes (see vertices_of_mesh)"""
    # Mesh -> MeshIndex -> Vertices
    _format = "H"


class Model(base.Struct):  # LUMP 14 (000E)
    """bsp.MODELS[0] is always worldspawn"""
    # Model -> Mesh -> MaterialSort -> TexData, VertexReservedX
    # TexData -> TexDataStringTable -> TexDataStringTable
    # VertexReservedX -> Vertex, Vertex(normal), VertexReservedX.uv
    mins: List[float]  # bounding box mins
    maxs: List[float]  # bounding box maxs
    first_mesh: int  # index of first Mesh
    num_meshes: int  # number of Meshes after first_mesh in this model
    __slots__ = ["mins", "maxs", "first_mesh", "num_meshes"]
    _format = "6f2I"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}


class Plane(base.Struct):  # LUMP 1 (0001)
    normal: List[float]  # normal unit vector
    distance: float
    # ??? -> Brush -> Plane ?  (unsure)
    __slots__ = ["normal", "distance"]
    _format = "4f"
    _arrays = {"normal": [*"xyz"]}


class ShadowMesh(base.Struct):  # LUMP 127 (007F)
    # ??? -> ShadowMesh -> ShadowMeshIndices -> ??? (triangles?)
    # presumably start_index & num_triangles point at SHADOW_MESH_INDICES
    # however SHADOW_MESH_INDICES is huge & not a multiple of 4 bytes
    start_index: int  # unsure what lump is indexed
    num_triangles: int
    # unknown.one: int  # usually one
    # unknown.negative_one: int  # usually negative one
    __slots__ = ["start_index", "num_triangles", "unknown"]
    _format = "2I2h"  # assuming 12 bytes
    _arrays = {"unknown": ["one", "negative_one"]}


class StaticPropv12(base.Struct):  # sprp GAME_LUMP (0023)
    # structure definition worked out with BobTheBob
    # Vector          origin;
    # QAngle          angles;
    # unsigned short  mdl_name;
    # unsigned short  first_leaf;
    # unsigned short  leaf_count;
    # unsigned char   solid;
    # unsigned char   flags;
    # int             skin;
    # unsigned int    cubemap;                 // new! an index?
    # float           fade_distance.min;
    # float           fade_distance.max;
    # Vector          lighting_origin;
    # float           forced_fade_scale;
    # char            cpu_level.min;           // -1 for doesn't matter
    # char            cpu_level.max;
    # char            gpu_level.min;
    # char            gpu_level.max;
    # color32         diffuse_modulation;
    # bool            disable_x360;            // 4 byte bool
    # float           scale                    // should be 1.0?
    # unsigned short  collision_flags.add;     // new!
    # unsigned short  collision_flags.remove;  // new!
    __slots__ = ["origin", "angles", "mdl_name", "first_leaf", "num_leafs",
                 "solid_mode", "flags", "skin", "cubemap", "fade_distance",
                 "lighting_origin", "forced_fade_scale", "cpu_level", "gpu_level",
                 "diffuse_modulation", "disable_x360", "scale", "collision_flags"]
    _format = "6f3H2BiI6f4b4B?f2H"
    _arrays = {"origin": [*"xyz"], "angles": [*"yzx"],
               "fade_distance": ["min", "max"], "lighting_origin": [*"xyz"],
               "cpu_level": ["min", "max"], "gpu_level": ["min", "max"],
               "diffuse_modulation": [*"rgba"], "collision_flags": ["add", "remove"]}


class TextureData(base.Struct):  # LUMP 2 (0002)
    # MaterialSort -> TexData, VertexReservedX
    # TexData -> TexDataStringTable -> TexDataStringData
    # VertexReservedX -> Vertex, Vertex(normal), VertexReservedX.uv
    unknown: List[int]
    string_table_index: int  # index of material name in TEXDATA_STRING_DATA / TABLE
    # ^ nameStringTableID
    width: int
    height: int
    view_width: int
    view_height: int
    flags: int
    __slots__ = ["unknown", "string_table_index", "width", "height",
                 "view_width", "view_height", "flags"]
    _format = "9i"
    _arrays = {"unknown": [*"abc"]}


class TextureDataStringTable(int):  # LUMP 44 (002C)
    """Points to the starting index of string of same index in TEXDATA_STRING_DATA"""
    _format = "I"


class Vertex(base.MappedArray):  # LUMP 3 (0003)
    """3D position / normal vector"""
    x: float
    y: float
    z: float
    _mapping = [*"xyz"]
    _format = "3f"


# special vertices
class VertexLitBump(base.Struct):  # LUMP 73 (0049)
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VERTEX_NORMALS lump
    uv: List[float]  # albedo / normal / gloss / specular uv
    uv2: List[float]  # secondary uv? any target?
    uv3: List[float]  # lightmap uv
    unknown: List[int]  # unknown
    __slots__ = ["position_index", "normal_index", "uv", "uv2", "uv3", "unknown"]
    _format = "2I6f3I"  # 44 bytes
    _arrays = {"uv": [*"uv"], "uv2": [*"uv"], "uv3": [*"uv"],
               "unknown": [*"abc"]}


class VertexLitFlat(base.Struct):  # LUMP 72 (0048)
    __slots__ = ["position_index", "normal_index", "uv", "unknown"]
    _format = "9I"
    _arrays = {"uv": [*"uv"], "unknown": [*"abcde"]}


class VertexUnlit(base.Struct):  # LUMP 71 (0047)
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VERTEX_NORMALS lump
    uv: List[float]  # uv coords
    unknown: int
    __slots__ = ["position_index", "normal_index", "uv", "unknown"]
    _format = "2I2fi"  # 20 bytes
    _arrays = {"uv": [*"uv"]}


class VertexUnlitTS(base.Struct):  # LUMP 74 (004A)
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VERTEX_NORMALS lump
    uv: List[float]  # uv coords
    unknown: List[int]
    __slots__ = ["position_index", "normal_index", "uv", "unknown"]
    _format = "2I2f3i"  # 28 bytes
    _arrays = {"uv": [*"uv"], "unknown": [*"abc"]}


# classes for special lumps (alphabetical order)
class TitanfallGameLump_SPRP:
    def __init__(self, raw_sprp_lump: bytes, StaticPropClass: object):
        self._static_prop_format = StaticPropClass._format
        sprp_lump = io.BytesIO(raw_sprp_lump)
        mdl_name_count = int.from_bytes(sprp_lump.read(4), "little")
        mdl_names = struct.iter_unpack("128s", sprp_lump.read(128 * mdl_name_count))
        setattr(self, "mdl_names", [t[0].replace(b"\0", b"").decode() for t in mdl_names])
        leaf_count = int.from_bytes(sprp_lump.read(4), "little")  # usually 0
        leafs = list(struct.iter_unpack("H", sprp_lump.read(2 * leaf_count)))
        setattr(self, "leafs", leafs)
        prop_count, unknown1, unknown2 = struct.unpack("3i", sprp_lump.read(12))
        self.unknown1, self.unknown2 = unknown1, unknown2
        prop_size = struct.calcsize(StaticPropClass._format)
        props = struct.iter_unpack(StaticPropClass._format, sprp_lump.read(prop_count * prop_size))
        setattr(self, "props", list(map(StaticPropClass, props)))

    def as_bytes(self) -> bytes:
        return b"".join([int.to_bytes(len(self.prop_names), 4, "little"),
                         *[struct.pack("128s", n) for n in self.prop_names],
                         int.to_bytes(len(self.leafs), 4, "little"),
                         *[struct.pack("H", L) for L in self.leafs],
                         *struct.pack("3I", len(self.props), self.unknown1, self.unknown2),
                         *[struct.pack(self._static_prop_format, *p.flat()) for p in self.props]])


BASIC_LUMP_CLASSES = {"MESH_INDICES": MeshIndex,
                      "TEXDATA_STRING_TABLE": TextureDataStringTable}

LUMP_CLASSES = {"CM_BRUSHES": Brush,
                "CUBEMAPS": Cubemap,
                "LIGHTMAP_HEADERS": LightmapHeader,
                "MATERIAL_SORT": MaterialSort,
                "MESHES": Mesh,
                "MODELS": Model,
                "PLANES": Plane,
                "SHADOW_MESH_MESHES": ShadowMesh,
                "TEXDATA": TextureData,
                "VERTEX_NORMALS": Vertex,
                "VERTICES": Vertex,
                "VERTS_LIT_BUMP": VertexLitBump,
                "VERTS_LIT_FLAT": VertexLitFlat,
                "VERTS_UNLIT": VertexUnlit,
                "VERTS_UNLIT_TS": VertexUnlitTS}

SPECIAL_LUMP_CLASSES = {"ENTITIES": shared.Entities,  # RespawnBsp uses shared.Entites to unpack the .ent files
                        "PAKFILE": shared.PakFile,
                        "TEXDATA_STRING_DATA": shared.TexDataStringData}

GAME_LUMP_CLASSES = {"sprp": lambda raw_lump: TitanfallGameLump_SPRP(raw_lump, StaticPropv12)}
# NOTE: expecting Python 3.6+ for consistent dict order


# branch exclusive methods, in alphabetical order:
mesh_types = {0x600: "VERTS_UNLIT_TS",  # VERTS_RESERVED_3
              0x400: "VERTS_UNLIT",     # VERTS_RESERVED_0
              0x200: "VERTS_LIT_BUMP",  # VERTS_RESERVED_2
              0x000: "VERTS_LIT_FLAT"}  # VERTS_RESERVED_1


# https://raw.githubusercontent.com/Wanty5883/Titanfall2/master/tools/TitanfallMapExporter.py
# simplified from McSimp's exporter ^
def vertices_of_mesh(bsp, mesh_index: int) -> List[Union[VertexLitBump, VertexUnlit, VertexUnlitTS]]:
    """Spits out VertexLitBump / VertexUnlit / VertexUnlitTS"""
    mesh = bsp.MESHES[mesh_index]
    material_sort = bsp.MATERIAL_SORT[mesh.material_sort]
    start = mesh.start_index
    finish = start + mesh.num_triangles * 3
    indices = [material_sort.vertex_offset + i for i in bsp.MESH_INDICES[start:finish]]
    # mesh.flags -> vertex lump
    # TODO: is there a better way to determine the vertex lump from mesh.flags?
    mesh_type = list(filter(lambda k: mesh.flags & k == k, mesh_types))[0]
    verts = getattr(bsp, mesh_types[mesh_type])
    return [verts[i] for i in indices]


def vertices_of_model(bsp, model_index: int):
    # NOTE: model 0 is worldspawn, other models are referenced by entities
    out = list()
    model = bsp.MODELS[model_index]
    for i in range(model.first_mesh, model.num_meshes):
        out.extend(bsp.vertices_of_mesh(i))
    return out


def replace_texture(bsp, texture: str, replacement: str):
    texture_index = bsp.TEXDATA_STRING_DATA.index(texture)  # fails if texture is not in bsp
    bsp.TEXDATA_STRING_DATA.insert(texture_index, replacement)
    bsp.TEXDATA_STRING_DATA.pop(texture_index + 1)
    bsp.TEXDATA_STRING_TABLE = list()
    offset = 0  # starting index of texture name in raw TEXDATA_STRING_DATA
    for texture_name in bsp.TEXDATA_STRING_DATA:
        bsp.TEXDATA_STRING_TABLE.append(offset)
        offset += len(texture_name) + 1  # +1 for null byte


methods = [vertices_of_mesh, vertices_of_model, replace_texture]
