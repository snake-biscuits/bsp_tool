import collections
import enum
import os
import struct
from typing import List

from .. import base
from ..valve import orange_box


with open(os.path.join(os.path.dirname(__file__), "vindictus_notes.txt")) as notes:
    __doc__ = notes.read()  # help(vindictus) will contain vindictus_notes.txt

BSP_VERSION = 20


class LUMP(enum.Enum):
    ENTITIES = 0
    PLANES = 1
    TEXDATA = 2
    VERTICES = 3
    VISIBILITY = 4
    NODES = 5
    TEXINFO = 6
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
    UNUSED0 = 22
    UNUSED1 = 23
    UNUSED2 = 24
    UNUSED3 = 25
    DISP_INFO = 26
    ORIGINAL_FACES = 27
    PHYS_DISP = 28
    PHYS_COLLIDE = 29
    VERT_NORMALS = 30
    VERT_NORMAL_INDICES = 31
    DISP_LIGHTMAP_ALPHAS = 32
    DISP_VERTS = 33
    DISP_LIGHTMAP_SAMPLE_POSITIONS = 34
    GAME_LUMP = 35
    LEAF_WATER_DATA = 36
    PRIMITIVES = 37
    PRIM_VERTS = 38
    PRIM_INDICES = 39
    PAKFILE = 40
    CLIP_PORTAL_VERTICES = 41
    CUBEMAPS = 42
    TEXDATA_STRING_DATA = 43
    TEXDATA_STRING_TABLE = 44
    OVERLAYS = 45
    LEAF_MIN_DIST_TO_WATER = 46
    FACE_MARCO_TEXTURE_INFO = 47
    DISP_TRIS = 48
    PHYS_COLLIDE_SURFACE = 49
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
    UNUSED4 = 61
    UNUSED5 = 62
    UNUSED6 = 63


lump_header_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}
LumpHeader = collections.namedtuple("LumpHeader", ["id", "flags", "version", "offset", "length"])
# since vindictus has a unique header format, valve .bsp have a header reading function in here


def read_lump_header(file, LUMP_ID: enum.Enum):
    file.seek(lump_header_address[LUMP_ID])
    id, flags, version, offset, length = struct.unpack("5i", file.read(20))
    header = LumpHeader(id, flags, version, offset, length)
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
    tex_info: int   # index into TextureInfo lump
    disp_info: int  # index into DisplacementInfo lump
    bevel: int      # smoothing group?
    __slots__ = ["plane_num", "tex_info", "disp_info", "bevel"]
    _format = "I3i"


class DisplacementInfo(orange_box.DisplacementInfo):  # LUMP 26
    start_position: List[float]  # approximate XYZ of first point in face this DisplacementInfo is rotated around
    displacement_vertex_start: int  # index into DisplacementVertex lump
    displacement_triangle_start: int  # index into DisplacementTriangle lump
    power: int  # 2, 3 or 4; indicates subdivision level
    smoothing_angle: float
    unknown1: int  # don't know what this does in Vindictus' format
    contents: int  # contents flags
    face: int  # index into Face lump
    __slots__ = ["start_position", "displacement_vertex_start", "displacement_triangle_start",
                 "power", "smoothing_angle", "unknown1", "contents", "face",
                 "lightmap_alpha_start", "lightmap_sample_position_start",
                 "edge_neighbours", "corner_neighbours", "allowed_verts"]
    _format = "3f3if2iI2i144c10I"  # Neighbours are also different
    _arrays = {"start_position": [*"xyz"], "edge_neighbours": 44,
               "corner_neighbours": 44, "allowed_verts": 10}


class Edge(list):  # LUMP 12
    _format = "2I"


class Face(base.Struct):  # LUMP 7
    plane: int  # index into Plane lump
    __slots__ = ["plane", "side", "on_node", "unknown1", "first_edge",
                 "num_edges", "tex_info", "disp_info", "surface_fog_volume_id",
                 "styles", "light_offset", "area",
                 "lightmap_texture_mins_in_luxels",
                 "lightmap_texture_size_in_luxels",
                 "original_face", "num_primitives", "first_primitive_id",
                 "smoothing_groups"]
    _format = "I2bh5i4bif4i4I"
    _arrays = {"styles": 4, "lightmap_texture_mins_in_luxels": [*"st"],
               "lightmap_texture_size_in_luxels": [*"st"]}


# class game_lump(base.Struct):  # LUMP 35
#    __slots__ = ["id", "flags", "version", "offset", "length"]
#    _format = "5i"


class Leaf(base.Struct):  # LUMP 10
    __slots__ = ["contents", "cluster", "flags", "mins", "maxs",
                 "firstleafface", "numleaffaces", "firstleafbrush",
                 "numleafbrushes", "leafWaterDataID"]
    _format = "9i4Ii"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}


class LeafFace(base.Struct):  # LUMP 16
    __slots__ = ["value"]
    _format = "I"


class Node(base.Struct):  # LUMP 5
    __slots__ = ["planenum", "children", "mins", "maxs", "firstface",
                 "numfaces", "area", "padding"]
    _format = "12i"
    _arrays = {"children": 2, "mins": [*"xyz"], "maxs": [*"xyz"]}


class Overlay(base.Struct):  # LUMP 45
    __slots__ = ["id", "tex_info", "face_count_and_render_order",
                 "faces", "u", "v", "uv_points", "origin", "normal"]
    _format = "2iIi4f18f"
    _arrays = {"faces": 64,  # OVERLAY_BSP_FACE_COUNT (bspfile.h:998)
               "u": 2, "v": 2,
               "uv_points": {P: [*"xyz"] for P in "ABCD"}}


# every other class is the same as orange_box
LUMP_CLASSES = orange_box.LUMP_CLASSES.copy()
LUMP_CLASSES.update({"AREAS": Area,
                     "AREA_PORTALS": AreaPortal,
                     "BRUSH_SIDES": BrushSide,
                     "DISP_INFO": DisplacementInfo,
                     "EDGES": Edge,
                     "FACES": Face,
                     "LEAVES": Leaf,
                     "LEAF_FACES": LeafFace,
                     "NODES": Node,
                     "ORIGINAL_FACES": Face})

SPECIAL_LUMP_CLASSES = orange_box.SPECIAL_LUMP_CLASSES.copy()

methods = [*orange_box.methods]
