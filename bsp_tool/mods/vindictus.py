import enum

from . import common
from . import team_fortress2


bsp_version = 20

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
    CLIP_PORTAL_VERTS = 41
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

# class for each lump in alphabetical order
class area(common.base):
    __slots__ = ["num_area_portals", "first_area_portal"]
    _format = "2i"

class area_portal(common.base): # LUMP 21
    __slots__ = ["portal_key", "other_area", "first_clip_portal_vert",
                 "clip_portal_verts", "plane_num"]
    _format = "4Ii"

class brush_side(common.base): # LUMP 19
    __slots__ = ["plane_num", "tex_info", "disp_info", "bevel"]
    _format = "I3i"

class disp_info(common.base): # LUMP 26
    __slots__ = ["start_position", "disp_vert_start", "disp_tri_start",
                 "power", "smoothing_angle", "unknown1", "contents", "face",
                 "lightmap_alpha_start", "lightmap_sample_position_start",
                 "edge_neighbours", "corner_neighbours", "allowed_verts"]
    _format = "3f3if2iI2i144c10I" # Neighbours are also different
    _arrays = {"start_position": [*"xyz"], "edge_neighbours": 44,
               "corner_neighbours": 44, "allowed_verts": 10}

class edge(list): # LUMP 12
    _format = "2I"

class face(common.base): # LUMP 7
    __slots__ = ["plane_num", "side", "on_node", "unknown1", "first_edge",
                 "num_edges", "tex_info", "disp_info", "surface_fog_volume_id",
                 "styles", "light_offset", "area",
                 "lightmap_texture_mins_in_luxels",
                 "lightmap_texture_size_in_luxels",
                 "original_face", "num_primitives", "first_primitive_id",
                 "smoothing_groups"]
    _format = "I2bh5i4bif4i4I"
    _arrays = {"styles": 4, "lightmap_texture_mins_in_luxels": [*"st"],
               "lightmap_texture_size_in_luxels": [*"st"]}

#class game_lump(common.base): # LUMP 35
#    __slots__ = ["id", "flags", "version", "offset", "length"]
#    _format = "5i"

class leaf(common.base): # LUMP 10
    __slots__ = ["contents", "cluster", "flags", "mins", "maxs",
                 "firstleafface", "numleaffaces", "firstleafbrush",
                 "numleafbrushes", "leafWaterDataID"]
    _format = "9i4Ii"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}

class leaf_face(common.base): # LUMP 16
    __slots__ = ["value"]
    _format = "I"
    
class node(common.base): # LUMP 5
    __slots__ = ["planenum", "children", "mins", "maxs", "firstface",
                 "numfaces", "area", "padding"]
    _format = "12i"
    _arrays = {"children": 2, "mins": [*"xyz"], "maxs": [*"xyz"]}

##class overlay(common.base): # LUMP 45
##    __slots__ = ["id", "tex_info", "face_count_and_render_order",
##                 "faces", "u", "v", "uv_points", "origin", "normal"]
##    _format = "2iIi4f18f"
##    _arrays = {"faces": 64, # OVERLAY_BSP_FACE_COUNT (bspfile.h:998)
##               "u": 2, "v": 2,
##               "uv_points": {P: [*"xyz"] for P in "ABCD"}}

lump_classes = team_fortress2.lump_classes.copy() # copy tf2 for other classes
lump_classes.update({"AREAS": area, "AREA_PORTALS": area_portal,
                "BRUSH_SIDES": brush_side, "DISP_INFO": disp_info,
                "EDGES": edge, "FACES": face, "LEAVES": leaf,
                "LEAF_FACES": leaf_face, "NODES": node, "ORIGINAL_FACES": face})

methods = team_fortress2.methods # same methods as tf2
