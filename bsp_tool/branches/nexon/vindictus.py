"""Vindictus. A MMO-RPG build in the Source Engine. Also known as Mabinogi Heroes"""
import collections
import enum
import struct
from typing import List

from .. import base
from .. import shared
from ..valve import orange_box, source


FILE_MAGIC = b"VBSP"

BSP_VERSION = 20

GAME_PATHS = ["Vindictus"]

GAME_VERSIONS = {GAME: BSP_VERSION for GAME in GAME_PATHS}


class LUMP(enum.Enum):
    ENTITIES = 0
    PLANES = 1
    TEXTURE_DATA = 2
    VERTICES = 3
    VISIBILITY = 4
    NODES = 5
    TEXTURE_INFO = 6
    FACES = 7
    LIGHTING = 8
    OCCLUSION = 9
    LEAVES = 10
    FACEIDS = 11
    EDGES = 12
    SURFEDGES = 13
    MODELS = 14
    WORLD_LIGHTS = 15
    LEAF_FACES = 16
    LEAF_BRUSHES = 17
    BRUSHES = 18
    BRUSH_SIDES = 19
    AREAS = 20
    AREA_PORTALS = 21
    UNUSED_22 = 22
    UNUSED_23 = 23
    UNUSED_24 = 24
    UNUSED_25 = 25
    DISPLACEMENT_INFO = 26
    ORIGINAL_FACES = 27
    PHYSICS_DISPLACEMENT = 28
    PHYSICS_COLLIDE = 29
    VERTEX_NORMALS = 30
    VERTEX_NORMAL_INDICES = 31
    DISPLACEMENT_LIGHTMAP_ALPHAS = 32
    DISPLACEMENT_VERTICES = 33
    DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS = 34
    GAME_LUMP = 35
    LEAF_WATER_DATA = 36
    PRIMITIVES = 37
    PRIMITIVE_VERTICES = 38
    PRIMITIVE_INDICES = 39
    PAKFILE = 40
    CLIP_PORTAL_VERTICES = 41
    CUBEMAPS = 42
    TEXTURE_DATA_STRING_DATA = 43
    TEXTURE_DATA_STRING_TABLE = 44
    OVERLAYS = 45
    LEAF_MIN_DIST_TO_WATER = 46
    FACE_MARCO_TEXTURE_INFO = 47
    DISPLACEMENT_TRIS = 48
    PHYSICS_COLLIDE_SURFACE = 49
    WATER_OVERLAYS = 50
    LEAF_AMBIENT_INDEX_HDR = 51
    LEAF_AMBIENT_INDEX = 52
    LIGHTING_HDR = 53
    WORLD_LIGHTS_HDR = 54
    LEAF_AMBIENT_LIGHTING_HDR = 55
    LEAF_AMBIENT_LIGHTING = 56
    XZIP_PAKFILE = 57
    FACES_HDR = 58
    MAP_FLAGS = 59
    OVERLAY_FADES = 60
    UNUSED_61 = 61
    UNUSED_62 = 62
    UNUSED_63 = 63


# struct VindictusBspHeader { char file_magic[4]; int version; VindictusLumpHeader headers[64]; int revision; };
lump_header_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}

VindictusLumpHeader = collections.namedtuple("VindictusLumpHeader", ["id", "flags", "version", "offset", "length"])


def read_lump_header(file, LUMP_ID: enum.Enum) -> VindictusLumpHeader:
    file.seek(lump_header_address[LUMP_ID])
    id, flags, version, offset, length = struct.unpack("5i", file.read(20))
    header = VindictusLumpHeader(id, flags, version, offset, length)
    return header


# class for each lump in alphabetical order: [10 / 64] + orange_box.LUMP_CLASSES
class Area(base.Struct):  # LUMP 20
    num_area_portals: int  # number or AreaPortals after first_area_portal in this Area
    first_area_portal: int  # index into AreaPortal lump
    __slots__ = ["num_area_portals", "first_area_portal"]
    _format = "2i"


class AreaPortal(base.Struct):  # LUMP 21
    portal_key: int  # unique ID?
    other_area: int  # ???
    first_clip_portal_vertex: int  # index into the ClipPortalVertex lump
    num_clip_portal_vertices: int  # number of ClipPortalVertices after first_clip_portal_vertex in this AreaPortal
    __slots__ = ["portal_key", "other_area", "first_clip_portal_vertex",
                 "num_clip_portal_vertices", "plane_num"]
    _format = "4Ii"


class BrushSide(base.Struct):  # LUMP 19
    plane: int      # index into Plane lump
    texture_info: int   # index into TextureInfo lump
    displacement_info: int  # index into DisplacementInfo lump
    bevel: int      # smoothing group?
    __slots__ = ["plane_num", "texture_info", "displacement_info", "bevel"]
    _format = "I3i"


class DisplacementInfo(source.DisplacementInfo):  # LUMP 26
    start_position: List[float]  # approximate XYZ of first point in face this DisplacementInfo is rotated around
    displacement_vertex_start: int  # index into DisplacementVertex lump
    displacement_triangle_start: int  # index into DisplacementTriangle lump
    power: int  # 2, 3 or 4; indicates subdivision level
    smoothing_angle: float
    unknown: int  # don't know what this does in Vindictus' format
    contents: int  # contents flags
    face: int  # index into Face lump
    __slots__ = ["start_position", "displacement_vertex_start", "displacement_triangle_start",
                 "power", "smoothing_angle", "unknown", "contents", "face",
                 "lightmap_alpha_start", "lightmap_sample_position_start",
                 "edge_neighbours", "corner_neighbours", "allowed_verts"]
    _format = "3f3if2iI2i144c10I"  # Neighbours are also different
    _arrays = {"start_position": [*"xyz"], "edge_neighbours": 72,
               "corner_neighbours": 72, "allowed_verts": 10}


class Edge(list):  # LUMP 12
    _format = "2I"

    def flat(self):
        return self  # HACK


class Face(base.Struct):  # LUMP 7
    plane: int  # index into Plane lump
    __slots__ = ["plane", "side", "on_node", "unknown", "first_edge",
                 "num_edges", "texture_info", "displacement_info", "surface_fog_volume_id",
                 "styles", "light_offset", "area",
                 "lightmap_texture_mins_in_luxels",
                 "lightmap_texture_size_in_luxels",
                 "original_face", "num_primitives", "first_primitive_id",
                 "smoothing_groups"]
    _format = "I2bh5i4bif4i4I"
    _arrays = {"styles": 4, "lightmap_texture_mins_in_luxels": [*"st"],
               "lightmap_texture_size_in_luxels": [*"st"]}


class Leaf(base.Struct):  # LUMP 10
    __slots__ = ["contents", "cluster", "flags", "mins", "maxs",
                 "firstleafface", "numleaffaces", "firstleafbrush",
                 "numleafbrushes", "leafWaterDataID"]
    _format = "9i4Ii"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}


class Node(base.Struct):  # LUMP 5
    __slots__ = ["planenum", "children", "mins", "maxs", "firstface",
                 "numfaces", "padding"]
    _format = "12i"
    _arrays = {"children": 2, "mins": [*"xyz"], "maxs": [*"xyz"]}


class Overlay(base.Struct):  # LUMP 45
    __slots__ = ["id", "texture_info", "face_count_and_render_order",
                 "faces", "u", "v", "uv_points", "origin", "normal"]
    _format = "2iIi4f18f"
    _arrays = {"faces": 64,  # OVERLAY_BSP_FACE_COUNT (bspfile.h:998)
               "u": 2, "v": 2,
               "uv_points": {P: [*"xyz"] for P in "ABCD"}}


# classes for special lumps, in alphabetical order:
# TODO: StaticPropv5, StaticPropv6
# TODO: GameLump (alternate header format)
# old: struct GameLumpHeader { char id[4]; unsigned short flags, version; int offset, length; };
# new: struct GameLumpHeader { char id[4]; int flags, version, offset, length; };
# also the sprp lump includes a "scales" sub-lump after leaves
# struct StaticPropScale { int static_prop; Vector scales; };  // Different scalar for each axis
# struct StaticPropScalesLump { int count; StaticPropScales scales[count]; };


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = orange_box.BASIC_LUMP_CLASSES.copy()
BASIC_LUMP_CLASSES["LEAF_FACES"] = {0: shared.UnsignedInts}

LUMP_CLASSES = orange_box.LUMP_CLASSES.copy()
LUMP_CLASSES.update({"AREAS":             {0: Area},
                     "AREA_PORTALS":      {0: AreaPortal},
                     "BRUSH_SIDES":       {0: BrushSide},
                     "DISPLACEMENT_INFO": {0: DisplacementInfo},
                     "EDGES":             {0: Edge},
                     "FACES":             {0: Face},
                     # NOTE: LeafBrush also differs from orange_box (not implemented)
                     "LEAVES":            {0: Leaf},
                     "NODES":             {0: Node},
                     "ORIGINAL_FACES":    {0: Face},
                     "OVERLAYS":          {0: Overlay}})

SPECIAL_LUMP_CLASSES = orange_box.SPECIAL_LUMP_CLASSES.copy()

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = orange_box.GAME_LUMP_CLASSES.copy()
# GAME_LUMP_CLASSES = {"sprp": {5: lambda raw_lump: GameLump_SPRP(raw_lump, StaticPropv5),
#                               6: lambda raw_lump: GameLump_SPRP(raw_lump, StaticPropv6)}}


methods = [*orange_box.methods]
