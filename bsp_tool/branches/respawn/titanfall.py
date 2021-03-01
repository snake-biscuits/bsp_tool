import enum
from typing import List

from .. import base
from .. import shared


BSP_VERSION = 29


class LUMP(enum.Enum):
    ENTITIES = 0x0000
    PLANES = 0x0001  # version 1
    TEXDATA = 0x0002  # version 1
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
    PHYS_COLLIDE = 0x001D
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
    UNKNOWN_41 = 0x0029
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
    WORLDLIGHTS_PARENT_INFO = 0x0037
    UNUSED_56 = 0x0038
    UNUSED_57 = 0x0039
    UNUSED_58 = 0x003A
    UNUSED_59 = 0x003B
    UNUSED_60 = 0x003C
    UNUSED_61 = 0x003D
    PHYS_LEVEL = 0x003E  # length 0, version 6?
    UNUSED_63 = 0x003F
    UNUSED_64 = 0x0040
    UNUSED_65 = 0x0041
    TRICOLL_TRIS = 0x0042
    UNUSED_67 = 0x0043
    TRICOLL_NODES = 0x0044
    TRICOLL_HEADERS = 0x0045
    PHYSTRIS = 0x0046
    VERTS_UNLIT = 0x0047  # VERTS_RESERVED_0 - 7
    VERTS_LIT_FLAT = 0x0048
    VERTS_LIT_BUMP = 0x0049  # version 2
    VERTS_UNLIT_TS = 0x004A
    VERTS_BLINN_PHONG = 0x004B  # version 1
    VERTS_RESERVED_5 = 0x004C  # version 1
    VERTS_RESERVED_6 = 0x004D
    VERTS_RESERVED_7 = 0x004E
    MESH_INDICES = 0x004F  # version 1
    MESHES = 0x0050  # version 1
    MESH_BOUNDS = 0x0051
    MATERIAL_SORT = 0x0052
    LIGHTMAP_HEADERS = 0x0053
    LIGHTMAP_DATA_DXT5 = 0x0054  # unused?
    CM_GRID = 0x0055
    CM_GRIDCELLS = 0x0056
    CM_GEO_SETS = 0x0057
    CM_GEO_SET_BOUNDS = 0x0058
    CM_PRIMS = 0x0059
    CM_PRIM_BOUNDS = 0x005A  # version 1
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
    LIGHTMAP_DATA_REAL_TIME_LIGHT_PAGE = 0x007A
    LEVEL_INFO = 0x007B
    SHADOW_MESH_OPAQUE_VERTS = 0x007C
    SHADOW_MESH_ALPHA_VERTS = 0x007D
    SHADOW_MESH_INDICES = 0x007E
    SHADOW_MESH_MESHES = 0x007F


lump_header_address = {LUMP_ID: (16 + i * 16) for i, LUMP_ID in enumerate(LUMP)}


# classes for lumps (alphabetical order) [12 / 128] + 2 special lumps
class Brush(base.Struct):  # LUMP 92 (005C)
    origin: List[float]
    unknown: int  # id? some index?
    # was expecting first_plane & num_planes but OK
    __slots__ = ["origin", "unknown"]
    _format = "3fI"  # seems short
    _arrays = {"origin": [*"xyz"]}


class Dxt5(base.Struct):  # LUMP 84 (0054)
    # unused?
    alpha: (int, int, bytes)
    # alpha.a0: int  # 8bit alpha pallet pixel
    # alpha.a1: int  # 8bit alpha pallet pixel
    # alpha.lut: bytes  # 3-bit 4x4 lookup table (6 bytes)
    colour: (int, int, bytes)
    # colour.c0: int  # 565RGB pallet pixel
    # colour.c1: int  # 565RGB pallet pixel
    # colour.lut: bytes  # 2-bit 4x4 lookup table (4 bytes)
    """4x4 encoded tiles of pixels"""
    __slots__ = ["alpha", "colour"]
    _format = "2B6s2H4s"
    _arrays = {"alpha": ["a0", "a1", "lut"],
               "colour": ["c0", "c1", "lut"]}

    def as_rgba(self) -> bytes:
        # https://en.wikipedia.org/wiki/S3_Texture_Compression#DXT4_and_DXT5
        # calculate a2 - a7 (alpha palette)
        a0, a1 = self.alpha.a0, self.alpha.a1
        if a0 > a1:
            a2, a3, a4, a5, a6, a7 = [((6 - i) * a0 + (1 + i) * a1) // 7 for i in range(6)]
        else:
            a2, a3, a4, a5 = [((4 - i) * a0 + (1 + i) * a1) // 5 for i in range(4)]
            a6 = 0
            a7 = 255
        alpha_palette = [a0, a1, a2, a3, a4, a5, a6, a7]
        # calculate c2 & c3 (colour palette)
        c0, c1 = self.colour.c0, self.colour.c1
        c0, c1 = map(lambda c: [(c >> 11) << 3, ((c >> 5) % 64) << 2, (c % 32) << 3], [c0, c1])
        # ^ 565RGB to 888RGB
        if c0 > c1:
            c2 = [a * 2 // 3 + b // 3 for a, b in zip(c0, c1)]
            c3 = [a // 3 + b * 2 // 3 for a, b in zip(c0, c1)]
        else:  # c0 <= c1
            c2 = [a // 2 + b // 2 for a, b in zip(c0, c1)]
            c3 = [0, 0, 0]
        colour_palette = [c0, c1, c2, c3]
        # lookup tables --> pixels
        alpha_lut = int.from_bytes(self.alpha.lut, "big")
        colour_lut = int.from_bytes(self.colour.lut, "big")
        pixels = []
        for i in range(16):
            colour = colour_palette[colour_lut % 4]
            alpha = alpha_palette[alpha_lut % 8]
            pixels.append(bytes([*colour, alpha]))
            colour_lut = colour_lut >> 2
            alpha_lut = alpha_lut >> 3
        return b"".join(reversed(pixels))  # 4x4 tile of 8888RGBA pixels


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
    unknown: int
    vertex_offset: int
    __slots__ = ["texdata", "lightmap_header", "unknown", "vertex_offset"]
    _format = "2h2I"  # 12 bytes


class Mesh(base.Struct):  # LUMP 80 (0050)
    # Mesh -> MaterialSort -> TexData, VertexReservedX
    # TexData -> TexDataStringTable -> TexDataStringTable
    # VertexReservedX -> Vertex, Vertex(normal), VertexReservedX.uv
    start_index: int  # ...
    num_triangles: int  # ...
    # unknown.a - d
    material_sort: int  # index of this Mesh's MaterialSort
    flags: int  # specifies VertexReservedX to draw vertices from
    __slots__ = ["start_index", "num_triangles", "unknown",
                 "material_sort", "flags"]
    # vertex type stored in flags
    _format = "2I 3ih HI"  # 28 Bytes
    _arrays = {"unknown": [*"abcd"]}


class MeshIndices(int):  # LUMP 79 (004F)
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
    # Brush -> Plane?
    __slots__ = ["normal", "distance"]
    _format = "4f"
    _arrays = {"normal": [*"xyz"]}


class ShadowMesh(base.Struct):  # LUMP 7F (0127)
    # ??? -> ShadowMesh -> ???
    # presumably start_index & num_triangles point at SHADOW_MESH_INDICES
    # however SHADOW_MESH_INDICES is huge & not a multiple of 4 bytes
    __slots__ = ["start_index", "num_triangles", "unknown"]
    _format = "2I2h"  # assuming 12 bytes
    _arrays = {"unknown": ["one", "negative_one"]}


class TextureData(base.Struct):  # LUMP 2 (0002)
    # MaterialSort -> TexData, VertexReservedX
    # TexData -> TexDataStringTable -> TexDataStringTable
    # VertexReservedX -> Vertex, Vertex(normal), VertexReservedX.uv
    __slots__ = ["unknown", "string_table_index", "unknown2"]
    _format = "9i"
    _arrays = {"unknown": [*"abc"], "unknown2": [*"abcde"]}


class TextureDataStringTable(int):  # LUMP 44 (002C)
    """Points to the starting index of string of same index in TEXDATA_STRING_DATA"""
    _format = "I"


class Vertex(base.MappedArray):  # LUMP 3 (0003)
    """3D position / normal vector"""
    _mapping = [*"xyz"]
    _format = "3f"

    def flat(self):
        return [self.x, self.y, self.z]


# special vertices
class VertexBlinnPhong(base.Struct):  # LUMP 75 (004B)
    __slots__ = ["position_index", "normal_index", "unknown"]
    _format = "4I"  # 16 bytes
    _arrays = {"unknown": [*"ab"]}


class VertexLitBump(base.Struct):  # LUMP 71 (0047)
    __slots__ = ["position_index", "normal_index", "uv", "uv2", "uv3", "unknown"]
    # byte 8  - 12 = uv coords for albedo, normal, gloss & specular maps
    # byte 20 - 28 = uv coords for lightmap
    _format = "2I6f3I"  # 44 bytes
    _arrays = {"uv": [*"uv"], "uv2": [*"uv"], "uv3": [*"uv"],
               "unknown": [*"abc"]}


class VertexReserved5(base.Struct):  # LUMP 76 (004C)
    __slots__ = ["position_index", "normal_index", "unknown", "uv", "uv2"]
    _format = "7I4f"  # 44 bytes
    _arrays = {"unknown": [*"abcd"], "uv": [*"uv"], "uv2": [*"uv"]}


class VertexReserved7(base.Struct):  # LUMP 78 (004E)
    __slots__ = ["position_index", "normal_index", "uv", "negative_one"]
    _format = "2I2fi"  # 20 bytes
    _arrays = {"uv": [*"uv"]}


class VertexUnlit(base.Struct):  # LUMP 71 (0047)
    __slots__ = ["position_index", "normal_index", "uv", "unknown"]
    _format = "2I2fi"  # 20 bytes
    _arrays = {"uv": [*"uv"]}


class VertexUnlitTS(base.Struct):  # LUMP 74 (004A)
    __slots__ = ["position_index", "normal_index", "uv", "unknown"]
    _format = "2I2f3i"  # 28 bytes
    _arrays = {"uv": [*"uv"], "unknown": [*"abc"]}


LUMP_CLASSES = {"CM_BRUSHES": Brush,
                "LIGHTMAP_DATA_DXT5": Dxt5,  # unused?
                "LIGHTMAP_HEADERS": LightmapHeader,
                "MATERIAL_SORT": MaterialSort,
                "MODELS": Model,
                "PLANES": Plane,
                "TEXDATA": TextureData,
                "TEXDATA_STRING_TABLE": TextureDataStringTable,
                "SHADOW_MESH_MESHES": ShadowMesh,
                "VERTEX_NORMALS": Vertex,
                "VERTICES": Vertex,
                "VERTS_LIT_BUMP": VertexLitBump,
                "VERTS_RESERVED_7": VertexReserved7,
                "VERTS_UNLIT": VertexUnlit,
                "VERTS_UNLIT_TS": VertexUnlitTS,
                "MESHES": Mesh,
                "MESH_INDICES": MeshIndices}

SPECIAL_LUMP_CLASSES = {"ENTITIES": shared.Entities,  # RespawnBsp uses shared.Entites to unpack the .ent files
                        "PAKFILE": shared.PakFile,
                        "TEXDATA_STRING_DATA": shared.TexDataStringData}


# branch exclusive methods, in alphabetical order:
mesh_types = {0x600: "VERTS_UNLIT_TS",
              0x400: "VERTS_UNLIT",
              0x200: "VERTS_LIT_BUMP"}
# ^ a proper mapping of the flags would be nice


# https://raw.githubusercontent.com/Wanty5883/Titanfall2/master/tools/TitanfallMapExporter.py
def vertices_of_mesh(bsp, mesh_index: int):  # simplified from McSimp's exporter ^
    """Vertex Format: (position.xyz, normal.xyz, uv.xy)"""
    mesh = bsp.MESHES[mesh_index]
    material_sort = bsp.MATERIAL_SORT[mesh.material_sort]
    start = mesh.start_index
    finish = start + mesh.num_triangles * 3
    indices = [material_sort.vertex_offset + i for i in bsp.MESH_INDICES[start:finish]]
    # TODO: cleaup these last 3 lines, the mesh_types dict is a wierd approach
    mesh_type = list(filter(lambda k: mesh.flags & k == k, mesh_types))[0]
    # ^ use mesh_types & mesh.flags with a bitmask to select the vertex lump
    verts = getattr(bsp, mesh_types[mesh_type])
    return [verts[i] for i in indices]


def vertices_of_model(bsp, model_index: int):
    # NOTE: model 0 is worldspawn, other models are referenced by entities
    out = ()
    model = bsp.MODELS[model_index]
    for i in range(model.first_mesh, model.num_meshes):
        out.extend(bsp.vertices_of_mesh(i))
    return out


def replace_texture(bsp, texture: str, replacement: str):
    texture_index = bsp.TEXDATA_STRING_DATA.index(texture)
    bsp.TEXDATA_STRING_DATA.insert(texture_index, replacement)
    bsp.TEXDATA_STRING_DATA.pop(texture_index + 1)
    for texture_name in bsp.TEXDATA_STRING_DATA:
        ...


methods = [vertices_of_mesh, vertices_of_model, replace_texture]
