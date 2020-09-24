import enum

from . import common
from . import vector  # for faces & displacements --> vertices & indices


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
    UNUSED_22 = 22
    UNUSED_23 = 23
    UNUSED_24 = 24
    UNUSED_25 = 25
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
    UNUSED_61 = 61
    UNUSED_62 = 62
    UNUSED_63 = 63


lump_header_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}


# classes for each lump, in alphabetical order:
class Area(common.Base):  # LUMP 20
    __slots__ = ["num_area_portals", "first_area_portal"]
    _format = "2i"


class AreaPortal(common.Base):  # LUMP 21
    __slots__ = ["portal_key", "other_area", "first_clip_portal_vert",
                 "clip_portal_verts", "plane_num"]
    _format = "4Hi"


class Brush(common.Base):  # LUMP 18
    __slots__ = ["first_side", "num_sides", "contents"]
    _format = "3i"


class BrushSide(common.Base):  # LUMP 19
    __slots__ = ["plane_num", "tex_info", "disp_info", "bevel"]
    _format = "H3h"


class Cubemap(common.Base):  # LUMP 42
    __slots__ = ["origin", "size"]
    _format = "4i"
    _arrays = {"origin": [*"xyz"]}


class DisplacementInfo(common.Base):  # LUMP 26
    __slots__ = ["start_position", "disp_vert_start", "disp_tri_start", "power",
                 "min_tesselation", "smoothing_angle", "contents", "map_face",
                 "lightmap_alpha_start", "lightmap_sample_position_start",
                 "edge_neighbours", "corner_neighbours", "allowed_verts"]
    _format = "3f4ifiH2i88c10I"
    _arrays = {"start_position": [*"xyz"], "edge_neighbours": 44,
               "corner_neighbours": 44, "allowed_verts": 10}
    # extend __init__ to unpack edge & corner neighbours with another class
    # the "flat" method may need some changes to accommodate this

    # def __init__(self, _tuple):
    #     super(self, common.Base).__init__(_tuple)
    #     self.edge_neighbours = ...
    #     self.corner_neighbours = ...


class DisplacementTriangle(int):  # LUMP 48
    _format = "H"


class DisplacementVertex(common.Base):  # LUMP 33
    __slots__ = ["vector", "distance", "alpha"]
    _format = "5f"
    _arrays = {"vector": [*"xyz"]}


class Edge(list):  # LUMP 12
    _format = "2h"
    # just a list() + the _format attribute


class Face(common.Base):  # LUMP 7
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


class Leaf(common.Base):  # LUMP 10
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


class LeafFace(int):  # LUMP 16
    _format = "H"


class Model(common.Base):
    __slots__ = ["mins", "maxs", "origin", "head_node", "first_face", "num_faces"]
    _format = "9f3i"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"], "origin": [*"xyz"]}


class Node(common.Base):  # LUMP 5
    __slots__ = ["plane_num", "children", "mins", "maxs", "first_face", "num_faces",
                 "area", "padding"]
    # area is appears to always be 0
    # however leaves correctly connect to all areas
    _format = "3i6h2H2h"
    _arrays = {"children": 2, "mins": [*"xyz"], "maxs": [*"xyz"]}

# class pakfile: # LUMP 40
#     ... # it's a raw binary zip file
#     # keep the raw data and provide an extraction / editing API?


class Plane(common.Base):  # LUMP 1
    __slots__ = ["normal", "distance", "type"]
    _format = "4fi"
    _arrays = {"normal": [*"xyz"]}


class SurfEdge:  # LUMP 13
    _format = "i"


class TextureData(common.Base):  # LUMP 2
    __slots__ = ["reflectivity", "tex_data_string_index", "width", "height",
                 "view_width", "view_height"]
    _format = "3f5i"
    _arrays = {"reflectivity": [*"rgb"]}


class TextureInfo(common.Base):  # LUMP 6
    __slots__ = ["texture", "lightmap", "mip_flags", "tex_data"]
    _format = "16f2i"
    _arrays = {"texture": {"s": [*"xyz", "offset"], "t": [*"xyz", "offset"]},
               "lightmap": {"s": [*"xyz", "offset"], "t": [*"xyz", "offset"]}}


class Vertex(common.MappedArray):  # LUMP 3
    _mapping = [*"xyz"]
    _format = "3f"

    def flat(self):
        return [self.x, self.y, self.z]


class WorldLight(common.Base):  # LUMP 15
    __slots__ = ["origin", "intensity", "normal", "cluster", "type", "style",
                 "stop_dot", "stop_dot2", "exponent", "radius",
                 "constant", "linear", "quadratic",  # attenuation
                 "flags", "tex_info", "owner"]
    _format = "9f3i7f3i"
    _arrays = {"origin": [*"xyz"], "intensity": [*"xyz"], "normal": [*"xyz"]}


lump_classes = {"AREAS": Area,
                "AREA_PORTALS": AreaPortal,
                "BRUSHES": Brush,
                "BRUSH_SIDES": BrushSide,
                "CUBEMAPS": Cubemap,
                "DISP_INFO": DisplacementInfo,
                "DISP_TRIS": DisplacementTriangle,
                "DISP_VERTS": DisplacementVertex,
                "EDGES": Edge,
                "FACES": Face,
                "LEAVES": Leaf,
                "LEAF_FACES": LeafFace,
                "MODELS": Model,
                "NODES": Node,
                "ORIGINAL_FACES": Face,
                "PLANES": Plane,
                "TEXDATA": TextureData,
                "TEXINFO": TextureInfo,
                "VERTICES": Vertex,
                "WORLD_LIGHTS": WorldLight,
                "WORLD_LIGHTS_HDR": WorldLight}


# METHODS EXCLUSIVE TO THIS MOD:
def vertices_of_face(bsp, face_index):
    """Format: [Position, Normal, TexCoord, LightCoord, Colour]"""
    face = bsp.FACES[face_index]
    uvs, uv2s = [], []
    first_edge = face.first_edge
    edges = []
    positions = []
    for surfedge in bsp.SURFEDGES[first_edge:(first_edge + face.num_edges)]:
        if surfedge >= 0:  # index is positive
            edge = bsp.EDGES[surfedge]
            positions.append(bsp.VERTICES[bsp.EDGES[surfedge][0]])
            # ^ utils/vrad/trace.cpp:637
        else:  # index is negatice
            edge = bsp.EDGES[-surfedge][::-1]  # reverse
            positions.append(bsp.VERTICES[bsp.EDGES[-surfedge][1]])
            # ^ utils/vrad/trace.cpp:635
        edges.append(edge)
    positions = t_junction_fixer(bsp, face, positions, edges)
    tex_info = bsp.TEXINFO[face.tex_info]
    tex_data = bsp.TEXDATA[tex_info.tex_data]
    texture = tex_info.texture
    lightmap = tex_info.lightmap

    def vector_of(P):
        """returns the normal of plane (P)"""
        return (P.x, P.y, P.z)

    # texture vector -> uv calculation discovered in:
    # github.com/VSES/SourceEngine2007/blob/master/src_main/engine/matsys_interface.cpp
    # SurfComputeTextureCoordinate & SurfComputeLightmapCoordinate
    for P in positions:
        # texture UV
        uv = [vector.dot(P, vector_of(texture.s)) + texture.s.offset,
              vector.dot(P, vector_of(texture.t)) + texture.t.offset]
        uv[0] /= tex_data.view_width if tex_data.view_width != 0 else 1
        uv[1] /= tex_data.view_height if tex_data.view_height != 0 else 1
        uvs.append(vector.vec2(*uv))
        # lightmap UV
        uv2 = [vector.dot(P, vector_of(lightmap.s)) + lightmap.s.offset,
               vector.dot(P, vector_of(lightmap.t)) + lightmap.t.offset]
        if any([(face.lightmap_texture_size_in_luxels.s == 0), (face.lightmap_texture_size_in_luxels.t == 0)]):
            uv2 = [0, 0]
        else:
            uv2[0] -= face.lightmap_texture_mins_in_luxels.s
            uv2[1] -= face.lightmap_texture_mins_in_luxels.t
            uv2[0] /= face.lightmap_texture_size_in_luxels.s
            uv2[1] /= face.lightmap_texture_size_in_luxels.t
        uv2s.append(uv2)
    normal = [bsp.PLANES[face.plane_num].normal] * len(positions)  # X Y Z
    colour = [tex_data.reflectivity] * len(positions)  # R G B
    return list(zip(positions, normal, uvs, uv2s, colour))


def t_junction_fixer(bsp, face, positions, edges):  # WIP
    # report to bsp.log rather than printing
    # bsp may need a method wrapper to give a warning to check the logs
    # face_index = bsp.FACES.index(face)
    # first_edge = face.first_edge
    if {positions.count(P) for P in positions} != {1}:
        # print(f"Face #{face_index} has interesting edges (t-junction?):")
        # print("\tAREA:", f"{face.area:.3f}")
        # center = sum(map(vector.vec3, positions), start=vector.vec3()) / len(positions)
        # print("\tCENTER:", f"({center:.3f})")
        # print("\tSURFEDGES:", bsp.SURFEDGES[first_edge:first_edge + face.num_edges])
        # print("\tEDGES:", edges)
        # loops = [(e[0] == edges[i-1][1]) for i, e in enumerate(edges)]
        # if not all(loops):
        #     print("\tWARINNG! EDGES do not loop!")
        #     print("\tLOOPS:", loops)
        # print("\tPOSITIONS:", [bsp.VERTICES.index(P) for P in positions])

        # PATCH
        # -- if you see 1 index between 2 indentical indicies:
        # -- compress the 3 indices down to just the first
        repeats = [i for i, P in enumerate(positions) if positions.count(P) != 1]
        # if len(repeats) > 0:
        #     print("\tREPEATS:", repeats)
        #     print([bsp.VERTICES.index(P) for P in positions], "-->")
        if len(repeats) == 2:
            index_a, index_b = repeats
            if index_b - index_a == 2:
                # edge goes out to one point and doubles back; delete it
                positions.pop(index_a + 1)
                positions.pop(index_a + 1)
            # what about Ts around the ends?
            print([bsp.VERTICES.index(P) for P in positions])
        else:
            if repeats[1] == repeats[0] + 1 and repeats[1] == repeats[2] - 1:
                positions.pop(repeats[1])
                positions.pop(repeats[1])
            print([bsp.VERTICES.index(P) for P in positions])
    return positions


def vertices_of_displacement(bsp, face_index):
    """Format: [Position, Normal, TexCoord, LightCoord, Colour]"""
    face = bsp.FACES[face_index]
    if face.disp_info == -1:
        raise RuntimeError(f"Face #{face_index} is not a displacement!")
    base_vertices = bsp.vertices_of_face(face_index)
    if len(base_vertices) != 4:
        raise RuntimeError(f"Face #{face_index} does not have 4 corners (probably t-junctions)")
    disp_info = bsp.DISP_INFO[face.disp_info]
    start = vector.vec3(disp_info.start_position)
    base_quad = [vector.vec3(*P) for P, N, uv, uv2, rgb in base_vertices]
    # rotate so the point closest to start on the quad is index 0
    if start not in base_quad:
        start = sorted(base_quad, key=lambda P: (start - P).magnitude())[0]
    starting_index = base_quad.index(start)

    def rotated(q):
        return q[starting_index:] + q[:starting_index]

    A, B, C, D = rotated(base_quad)
    AD = D - A
    BC = C - B
    quad = rotated(base_vertices)
    uvA, uvB, uvC, uvD = [vector.vec2(*uv) for P, N, uv, uv2, rgb in quad]
    uvAD = uvD - uvA
    uvBC = uvC - uvB
    uv2A, uv2B, uv2C, uv2D = [vector.vec2(*uv2) for P, N, uv, uv2, rgb in quad]
    uv2AD = uv2D - uv2A
    uv2BC = uv2C - uv2B
    power2 = 2 ** disp_info.power
    disp_verts = bsp.DISP_VERTS[disp_info.disp_vert_start:]
    disp_verts = disp_verts[:(power2 + 1) ** 2]
    vertices = []
    for index, disp_vert in enumerate(disp_verts):
        t1 = index % (power2 + 1) / power2
        t2 = index // (power2 + 1) / power2
        bary_vert = vector.lerp(A + (AD * t1), B + (BC * t1), t2)
        # ^ interpolates across the base_quad to find the barymetric point
        disp_vert = [x * disp_vert.distance for x in disp_vert.vector]
        true_vertex = [a + b for a, b in zip(bary_vert, disp_vert)]
        texture_uv = vector.lerp(uvA + (uvAD * t1), uvB + (uvBC * t1), t2)
        lightmap_uv = vector.lerp(uv2A + (uv2AD * t1), uv2B + (uv2BC * t1), t2)
        normal = base_vertices[0][1]
        colour = base_vertices[0][4]
        vertices.append((true_vertex, normal, texture_uv, lightmap_uv, colour))
    return vertices


methods = [vertices_of_face, vertices_of_displacement]


def displacement_indices(power):  # static method / tool
    """returns an array of indices ((2 ** power) + 1) ** 2 long"""
    power2 = 2 ** power
    power2A = power2 + 1
    power2B = power2 + 2
    power2C = power2 + 3
    tris = []
    for line in range(power2):
        line_offset = power2A * line
        for block in range(2 ** (power - 1)):
            offset = line_offset + 2 * block
            if line % 2 == 0:  # |\|/|
                tris.extend([offset + 0, offset + power2A, offset + 1])
                tris.extend([offset + power2A, offset + power2B, offset + 1])
                tris.extend([offset + power2B, offset + power2C, offset + 1])
                tris.extend([offset + power2C, offset + 2, offset + 1])
            else:  # |/|\|
                tris.extend([offset + 0, offset + power2A, offset + power2B])
                tris.extend([offset + 1, offset + 0, offset + power2B])
                tris.extend([offset + 2, offset + 1, offset + power2B])
                tris.extend([offset + power2C, offset + 2, offset + power2B])
    return tris
