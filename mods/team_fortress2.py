# structs for BSP version 20 (TF2)
import mods.common as common
import enum

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
    _format = "4Hi"
    
class brush(common.base): # LUMP 18
    __slots__ = ["first_side", "num_sides", "contents"]
    _format = "3i"

class brush_side(common.base): # LUMP 19
    __slots__ = ["plane_num", "tex_info", "disp_info", "bevel"]
    _format = "H3h"

class cubemap(common.base): # LUMP 42
    __slots__ = ["origin", "size"]
    _format = "4i"
    _arrays = {"origin": [*"xyz"]}

class disp_info(common.base): # LUMP 26
    __slots__ = ["start_position", "disp_vert_start", "disp_tri_start", "power",
                 "min_tesselation", "smoothing_angle", "contents", "map_face",
                 "lightmap_alpha_start", "lightmap_sample_position_start",
                 "edge_neighbours", "corner_neighbours", "allowed_verts"]
    _format = "3f4ifiH2i88c10I"
    _arrays = {"start_position": [*"xyz"], "edge_neighbours": 44,
                "corner_neighbours": 44, "allowed_verts": 10}

class disp_tri(common.base): # LUMP 48
    __slots__ = ["value"]
    _format = "H"

class disp_vert(common.base): # LUMP 33
    __slots__ = ["vector", "distance", "alpha"]
    _format = "5f"
    _arrays = {"vector": [*"xyz"]}

class edge(list): # LUMP 12
    _format = "2h"

class face(common.base): # LUMP 7
    __slots__ = ["plane_num", "side", "on_node", "first_edge", "num_edges",
                 "tex_info", "disp_info", "surface_fog_volume_id", "styles",
                 "light_offset", "area", "lightmap_texture_mins_in_luxels",
                 "lightmap_texture_size_in_luxels", "original_face",
                 "num_primitives", "first_primitive_id", "smoothing_groups"]
    _format = "Hb?i4h4bif5i2HI"
    _arrays = {"styles": 4, "lightmap_texture_mins_in_luxels": [*"st"],
               "lightmap_texture_size_in_luxels": [*"st"]}

# class game_lump: # LUMP 35
#     ... # another unique class

class leaf(common.base): # LUMP 10
    __slots__ = ["contents", "cluster", "area_flags", "mins", "maxs",
                 "first_leaf_face", "num_leaf_faces", "first_leaf_brush",
                 "num_leaf_brushes", "leaf_water_data_id", "padding"]
    _format = "i8h4H2h"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}
    # area and flags are bitmasked from the same value
    # area = leaf[2] & 0xFF80 >> 7 # 9 bits
    # flags = leaf[2] & 0x007F # 7 bits
    # need to reverse this for leaf.flat()
    # why did those bits need saving when the struct is padded?

class leaf_face(common.base): # LUMP 16
    __slots__ = ["value"]
    _format = "H"

class node(common.base): # LUMP 5
    __slots__ = ["plane_num", "children", "mins", "maxs", "first_face", "num_faces",
                 "area", "padding"]
    # area is appears to always be 0
    # however leaves correctly connect to all areas
    _format = "3i6h2H2h"
    _arrays = {"children": 2, "mins": [*"xyz"], "maxs": [*"xyz"]}

# class pakfile: # LUMP 40
#     ... # it's a raw binary zip file
#     # keep the raw data and provide an extraction / editing API?

class plane(common.base): # LUMP 1
    __slots__ = ["normal", "distance", "type"]
    _format = "4fi"
    _arrays = {"normal": [*"xyz"]}

class surf_edge: # LUMP 13
    _format = "i"

class tex_data(common.base): # LUMP 2
    __slots__ = ["reflectivity", "tex_data_string_index", "width", "height",
                 "view_width", "view_height"]
    _format = "3f5i"
    _arrays = {"reflectivity": [*"rgb"]}

class tex_info(common.base): # LUMP 6
    __slots__ = ["texture", "lightmap", "mip_flags", "tex_data"]
    _format = "16f2i"
    _arrays = {"texture": {"s": [*"xyz", "offset"], "t": [*"xyz", "offset"]},
               "lightmap": {"s": [*"xyz", "offset"], "t": [*"xyz", "offset"]}}

class vertex(common.mapped_array): # LUMP 3
    _mapping = ["x", "y", "z"]
    _format = "3f"
    
    def flat(self):
        return [self.x, self.y, self.z]

class world_light(common.base): # LUMP 15
    __slots__ = ["origin", "intensity", "normal", "cluster", "type", "style",
                 "stop_dot", "stop_dot2", "exponent", "radius",
                 "constant", "linear", "quadratic", # attenuation
                 "flags", "tex_info", "owner"]
    _format = "9f3i7f3i"
    _arrays = {"origin": [*"xyz"], "intensity": [*"xyz"], "normal": [*"xyz"]}

lump_classes = {"AREAS": area, "AREA_PORTALS": area_portal, "BRUSHES": brush,
                "BRUSH_SIDES": brush_side, "CUBEMAPS": cubemap,
                "DISP_INFO": disp_info, "DISP_TRIS": disp_tri,
                "DISP_VERTS": disp_vert, "EDGES": edge, "FACES": face,
                "LEAVES": leaf, "LEAF_FACES": leaf_face, "NODES": node,
                "ORIGINAL_FACES": face, "PLANES": plane,
                "TEXDATA": tex_data, "TEXINFO": tex_info,
                "VERTICES": vertex, "WORLD_LIGHTS": world_light,
                "WORLD_LIGHTS_HDR": world_light}
