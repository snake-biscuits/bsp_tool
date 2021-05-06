import collections
import enum
import struct
from typing import List

from .. import base
from .. import shared  # special lumps
from .. import vector  # for methods


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
    UNUSED_22 = 22
    UNUSED_23 = 23
    UNUSED_24 = 24
    UNUSED_25 = 25
    DISPLACEMENT_INFO = 26
    ORIGINAL_FACES = 27
    PHYSICS_DISPLACEMENT = 28
    PHYSICS_COLLIDE = 29
    VERT_NORMALS = 30
    VERT_NORMAL_INDICES = 31
    DISPLACEMENT_LIGHTMAP_ALPHAS = 32
    DISPLACEMENT_VERTS = 33
    DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS = 34
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
    FACE_MACRO_TEXTURE_INFO = 47
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


class Contents(enum.Enum):
    EMPTY = 0x00
    SOLID = 0x01
    WINDOW = 0x02
    AUX = 0x04
    GRATE = 0x08  # allows bullets & vis
    SLIME = 0x10
    WATER = 0x20
    MIST = 0x40
    OPAQUE = 0x80  # blocks NPC line of sight
    TEST_FOG_VOLUME = 0x100  # cannot be seen through, but may be non-solid
    UNUSED_1 = 0x200
    UNUSED_2 = 0x400
    TEAM1 = 0x0800
    TEAM2 = 0x1000
    IGNORE_NODRAW_OPAQUE = 0x2000
    MOVEABLE = 0x4000
    AREAPORTAL = 0x8000
    PLAYER_CLIP = 0x10000
    MONSTER_CLIP = 0x20000
    # orientations?
    CURRENT_0 = 0x40000
    CURRENT_90 = 0x80000
    CURRENT_180 = 0x100000
    CURRENT_270 = 0x200000
    CURRENT_UP = 0x400000
    CURRENT_DOWN = 0x800000
    ORIGIN = 0x1000000  # "removed before bsping an entity"
    MONSTER = 0x2000000  # in-game only, shouldn't be in a .bsp
    DEBRIS = 0x4000000
    DETAIL = 0x8000000  # func_detail; for VVIS (visleaf assembly from Brushes)
    TRANSLUCENT = 0x10000000
    LADDER = 0x20000000
    HITBOX = 0x40000000  # requests hit tracing use hitboxes


lump_header_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}
LumpHeader = collections.namedtuple("LumpHeader", ["offset", "length", "version", "fourCC"])


def read_lump_header(file, LUMP: enum.Enum):
    file.seek(lump_header_address[LUMP])
    offset, length, version, fourCC = struct.unpack("4I", file.read(16))
    header = LumpHeader(offset, length, version, fourCC)
    return header


# classes for each lump, in alphabetical order: [22 / 64]
class Area(base.Struct):  # LUMP 20
    num_area_portals: int   # number of AreaPortals after first_area_portal in this Area
    first_area_portal: int  # index of first AreaPortal
    __slots__ = ["num_area_portals", "first_area_portal"]
    _format = "2i"


class AreaPortal(base.Struct):  # LUMP 21
    portal_key: int                # from brush id?
    first_clip_portal_vert: int    # index into the ClipPortalVertex lump
    num_clip_portal_vertices: int  # number of ClipPortalVertices after first_clip_portal_vertex in this AreaPortal
    plane: int                     # index of into the Plane lump
    __slots__ = ["portal_key", "other_area", "first_clip_portal_vertex",
                 "num_clip_portal_vertices", "plane"]
    _format = "4Hi"


class Brush(base.Struct):  # LUMP 18
    """Assumed to carry over from .vmf"""
    first_side: int  # index into BrushSide lump
    num_sides: int   # number of BrushSides after first_side in this Brush
    contents: int    # contents bitflags
    __slots__ = ["first_side", "num_sides", "contents"]
    _format = "3i"


class BrushSide(base.Struct):  # LUMP 19
    plane: int      # index into Plane lump
    tex_info: int   # index into TextureInfo lump
    displacement_info: int  # index into DisplacementInfo lump
    bevel: int      # smoothing group?
    __slots__ = ["plane", "tex_info", "displacement_info", "bevel"]
    _format = "H3h"


class Cubemap(base.Struct):  # LUMP 42
    """Location (origin) & resolution (size)"""
    origin: List[float]  # origin.xyz
    size: int  # texture dimension (each face of a cubemap is square)
    __slots__ = ["origin", "size"]
    _format = "4i"
    _arrays = {"origin": [*"xyz"]}


class DisplacementInfo(base.Struct):  # LUMP 26
    """Holds the information defining a displacement"""
    start_position: List[float]  # rough XYZ of the vertex to orient around
    displacement_vert_start: int  # index of first DisplacementVertex
    displacement_tri_start: int   # index of first DisplacementTriangle
    # ^ length of sequence for each varies depending on power
    power: int  # level of subdivision
    min_tesselation: int  # for tesselation shaders / triangle assembley?
    smoothing_angle: float  # ?
    contents: int  # contents bitflags
    map_face: int  # index of Face?
    __slots__ = ["start_position", "displacement_vert_start", "displacement_tri_start", "power",
                 "min_tesselation", "smoothing_angle", "contents", "map_face",
                 "lightmap_alpha_start", "lightmap_sample_position_start",
                 "edge_neighbours", "corner_neighbours", "allowed_verts"]
    _format = "3f4ifiH2i88c10I"
    _arrays = {"start_position": [*"xyz"], "edge_neighbours": 44,
               "corner_neighbours": 44, "allowed_verts": 10}
    # TODO: map neighbours with base.Struct subclasses, rather than MappedArrays
    # both the __init__ & flat methods may need some changes to accommodate this

    # def __init__(self, _tuple):
    #     super(base.Struct, self).__init__(_tuple)
    #     self.edge_neighbours = ...
    #     self.corner_neighbours = ...


class DisplacementTriangle(int):  # LUMP 48
    """Bitflags"""
    # 0x01  SURFACE
    # 0x02  WALKABLE
    # 0x04  BUILDABLE
    # 0x08  SURFPROP1
    # 0x10  SURFPROP2
    _format = "H"


class DisplacementVertex(base.Struct):  # LUMP 33
    """The positional deformation & blend value of a point in a displacement"""
    vector: List[float]  # direction of vertex offset from barymetric base
    distance: float      # length to scale deformation vector by
    alpha: float         # [0-1] material blend factor
    __slots__ = ["vector", "distance", "alpha"]
    _format = "5f"
    _arrays = {"vector": [*"xyz"]}


class Edge(list):  # LUMP 12
    """Edge of a Face, flipped if indexed negatively by a SurfEdge"""
    _format = "2h"  # List[int]


class Face(base.Struct):  # LUMP 7
    """makes up Models (including worldspawn), also referenced by LeafFaces"""
    plane: int       # index into Plane lump
    side: int        # "faces opposite to the node's plane direction"
    on_node: bool    # if False, face is in a leaf
    first_edge: int  # index into the SurfEdge lump
    num_edges: int   # number of SurfEdges after first_edge in this Face
    tex_info: int    # index into the TextureInfo lump
    displacement_info: int   # index into the DisplacementInfo lump (None if -1)
    surface_fog_volume_id: int  # t-junctions? QuakeIII vertex-lit fog?
    styles: int      # 4 different lighting states? "switchable lighting info"
    light_offset: int  # index of first pixel in LIGHTING / LIGHTING_HDR
    area: float  # surface area of this face
    lightmap_texture_mins_in_luxels: List[int]  # dimensions of lightmap segment
    lightmap_texture_size_in_luxels: List[int]  # scalars for lightmap segment
    original_face: int  # ORIGINAL_FACES index, -1 if this is an original face
    num_primitives: int  # non-zero if t-juncts are present? number of Primitives
    first_primitive_id: int  # index of Primitive
    smoothing_groups: int    # lightmap smoothing group
    __slots__ = ["plane", "side", "on_node", "first_edge", "num_edges",
                 "tex_info", "displacement_info", "surface_fog_volume_id", "styles",
                 "light_offset", "area", "lightmap", "original_face",
                 "num_primitives", "first_primitive_id", "smoothing_groups"]
    _format = "Hb?i4h4bif5i2HI"
    _arrays = {"styles": 4, "lightmap": {"mins": [*"xy"], "size": ["width", "height"]}}

# class game_lump: # LUMP 35
#     pass # unique sub-headers & offsets...


class Leaf(base.Struct):  # LUMP 10
    """Endpoint of a vis tree branch, a pocket of Faces"""
    contents: int  # contents bitflags
    cluster: int   # index of this Leaf's cluster (parent node?)
    area_flags: int  # area + flags (short area:9; short flags:7;)
    # area and flags are held in the same float
    # area = leaf[2] & 0xFF80 >> 7 # 9 bits
    # flags = leaf[2] & 0x007F # 7 bits
    # TODO: automatically split area & flags, merging back for flat()
    # why was this done when the struct is padded by one short anyway?
    mins: List[float]  # bounding box minimums along XYZ axes
    maxs: List[float]  # bounding box maximums along XYZ axes
    first_leaf_face: int   # index of first LeafFace
    num_leaf_faces: int    # number of LeafFaces
    first_leaf_brush: int  # index of first LeafBrush
    num_leaf_brushes: int  # number of LeafBrushes
    leaf_water_data_id: int  # -1 if this leaf isn't submerged
    padding: int  # should be empty
    __slots__ = ["contents", "cluster", "area_flags", "mins", "maxs",
                 "first_leaf_face", "num_leaf_faces", "first_leaf_brush",
                 "num_leaf_brushes", "leaf_water_data_id", "padding"]
    _format = "i8h4H2h"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}


class LeafFace(int):  # LUMP 16
    """Index of Face, this lump is a pre-organised sequence for the vis system"""
    _format = "H"


class Model(base.Struct):  # LUMP 14
    """Brush based entities; Index 0 is worldspawn"""
    mins: List[float]  # bounding box minimums along XYZ axes
    maxs: List[float]  # bounding box maximums along XYZ axes
    origin: List[float]  # center of model, worldspawn is always at 0 0 0
    head_node: int   # index into Node lump
    first_face: int  # index into Face lump
    num_faces: int   # number of Faces after first_face in this Model
    __slots__ = ["mins", "maxs", "origin", "head_node", "first_face", "num_faces"]
    _format = "9f3i"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"], "origin": [*"xyz"]}


class Node(base.Struct):  # LUMP 5
    plane: int            # index into Plane lump
    children: List[int]   # 2 indices; Node if positive, Leaf if negative
    mins: List[float]     # bounding box minimums along XYZ axes
    maxs: List[float]     # bounding box maximums along XYZ axes
    first_face: int       # index into Face lump
    num_faces: int        # number of Faces after first_face in this Node
    area: int             # index into Area lump, if all children are in the same area, else -1
    padding: int          # should be empty
    __slots__ = ["plane", "children", "mins", "maxs", "first_face", "num_faces",
                 "area", "padding"]
    # area is appears to always be 0
    # however leaves correctly connect to all areas
    _format = "3i6h2H2h"
    _arrays = {"children": 2, "mins": [*"xyz"], "maxs": [*"xyz"]}


class Plane(base.Struct):  # LUMP 1
    """3D Plane defining shape, used for physics & BSP/CSG calculations?"""
    normal: List[float]
    distance: float
    type: int  # flags for axis alignment, appears to be unused
    __slots__ = ["normal", "distance", "type"]
    _format = "4fi"
    _arrays = {"normal": [*"xyz"]}


class SurfEdge(int):  # LUMP 13
    """Index into EDGES, edge direction is reversed if negative"""
    _format = "i"


class TextureData(base.Struct):  # LUMP 2
    """Data on this view of a texture (.vmt), indexed by TextureInfo"""
    reflectivity: List[float]
    tex_data_string_index: int  # index of texture name (TEXDATA_STRING_TABLE)
    width: int  # width of full texture
    height: int  # height of full texture
    view_width: int  # width of visible section of texture
    view_height: int  # height of visible section of texture
    __slots__ = ["reflectivity", "tex_data_string_index", "width", "height",
                 "view_width", "view_height"]
    _format = "3f5i"
    _arrays = {"reflectivity": [*"rgb"]}


class TextureInfo(base.Struct):  # LUMP 6
    """Texture projection info & index into TEXDATA"""
    texture: List[List[float]]  # 2 texture projection vectors
    lightmap: List[List[float]]  # 2 lightmap projection vectors
    mip_flags: int  # flags for mipmapping?
    tex_data: int  # index of TextureData
    __slots__ = ["texture", "lightmap", "mip_flags", "tex_data"]
    _format = "16f2i"
    _arrays = {"texture": {"s": [*"xyz", "offset"], "t": [*"xyz", "offset"]},
               "lightmap": {"s": [*"xyz", "offset"], "t": [*"xyz", "offset"]}}
    # ^ nested MappedArrays; texture.s.x, texture.t.x


class Vertex(base.MappedArray):  # LUMP 3
    """a point in 3D space"""
    x: float
    y: float
    z: float
    _mapping = [*"xyz"]
    _format = "3f"

    def flat(self):
        return [self.x, self.y, self.z]


class WorldLight(base.Struct):  # LUMP 15
    """A static light"""
    origin: List[float]  # origin point of this light source
    intensity: float     # light strength scalar
    normal: List[float]  # light direction
    cluster: int  # ?
    type: int  # some enum?
    style: int  # related to face styles?
    # see base.fgd:
    stop_dot: float  # ?
    stop_dot2: float  # ?
    exponent: float  # falloff?
    radius: float
    # attenuations:
    constant: float
    linear: float
    quadratic: float
    # ^ these factor into some equation...
    flags: int  # bitflags?
    tex_info: int  # index of TextureInfo
    owner: int  # parent entity ID?
    __slots__ = ["origin", "intensity", "normal", "cluster", "type", "style",
                 "stop_dot", "stop_dot2", "exponent", "radius",
                 "constant", "linear", "quadratic",  # attenuation
                 "flags", "tex_info", "owner"]
    _format = "9f3i7f3i"
    _arrays = {"origin": [*"xyz"], "intensity": [*"xyz"], "normal": [*"xyz"]}


BASIC_LUMP_CLASSES = {"DISPLACEMENT_TRIS": DisplacementTriangle,
                      "LEAF_FACES": LeafFace,
                      "SURFEDGES": SurfEdge}

LUMP_CLASSES = {"AREAS": Area,
                "AREA_PORTALS": AreaPortal,
                "BRUSHES": Brush,
                "BRUSH_SIDES": BrushSide,
                "CUBEMAPS": Cubemap,
                "DISPLACEMENT_INFO": DisplacementInfo,
                "DISPLACEMENT_VERTS": DisplacementVertex,
                "EDGES": Edge,
                "FACES": Face,
                "LEAVES": Leaf,
                "MODELS": Model,
                "NODES": Node,
                "ORIGINAL_FACES": Face,
                "PLANES": Plane,
                "TEXDATA": TextureData,
                "TEXINFO": TextureInfo,
                "VERTICES": Vertex,
                "WORLD_LIGHTS": WorldLight,
                "WORLD_LIGHTS_HDR": WorldLight}

SPECIAL_LUMP_CLASSES = {"ENTITIES": shared.Entities,
                        "TEXDATA_STRING_DATA": shared.TexDataStringData,
                        "PAKFILE": shared.PakFile}


# branch exclusive methods, in alphabetical order:
def vertices_of_face(bsp, face_index: int) -> List[float]:
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
    normal = [bsp.PLANES[face.plane].normal] * len(positions)  # X Y Z
    colour = [tex_data.reflectivity] * len(positions)  # R G B
    return list(zip(positions, normal, uvs, uv2s, colour))


def t_junction_fixer(bsp, face: int, positions: List[List[float]], edges: List[List[float]]) -> List[List[float]]:
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


def vertices_of_displacement(bsp, face_index: int) -> List[List[float]]:
    """Format: [Position, Normal, TexCoord, LightCoord, Colour]"""
    face = bsp.FACES[face_index]
    if face.displacement_info == -1:
        raise RuntimeError(f"Face #{face_index} is not a displacement!")
    base_vertices = bsp.vertices_of_face(face_index)
    if len(base_vertices) != 4:
        raise RuntimeError(f"Face #{face_index} does not have 4 corners (probably t-junctions)")
    disp_info = bsp.DISPLACEMENT_INFO[face.displacement_info]
    start = vector.vec3(*disp_info.start_position)
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
    disp_verts = bsp.DISPLACEMENT_VERTS[disp_info.displacement_vert_start:]
    disp_verts = disp_verts[:(power2 + 1) ** 2]
    vertices = []
    for index, disp_vertex in enumerate(disp_verts):
        t1 = index % (power2 + 1) / power2
        t2 = index // (power2 + 1) / power2
        bary_vert = vector.lerp(A + (AD * t1), B + (BC * t1), t2)
        # ^ interpolates across the base_quad to find the barymetric point
        displacement_vert = [x * disp_vertex.distance for x in disp_vertex.vector]
        true_vertex = [a + b for a, b in zip(bary_vert, displacement_vert)]
        texture_uv = vector.lerp(uvA + (uvAD * t1), uvB + (uvBC * t1), t2)
        lightmap_uv = vector.lerp(uv2A + (uv2AD * t1), uv2B + (uv2BC * t1), t2)
        normal = base_vertices[0][1]
        colour = base_vertices[0][4]
        vertices.append((true_vertex, normal, texture_uv, lightmap_uv, colour))
    return vertices


# TODO: vertices_of_model method which walks the node tree
# TODO: vertices_of_node method


methods = [vertices_of_face, vertices_of_displacement]


def displacement_indices(power: int) -> List[List[int]]:  # static method?
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
