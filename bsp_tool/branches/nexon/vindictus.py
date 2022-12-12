# https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Vindictus
"""Vindictus. A MMO-RPG build in the Source Engine. Also known as Mabinogi Heroes"""
from __future__ import annotations
import enum
import io
import itertools
import struct
from typing import List

from .. import base
from .. import shared
from .. import vector
from ..id_software import remake_quake_old
from ..valve import orange_box
from ..valve import source


FILE_MAGIC = b"VBSP"

BSP_VERSION = 20
# NOTE: Vindictus may have 2 format eras with identical version identifiers
# -- we currently do not know how to load / find a map in-game to test for outdated maps
# TODO: look into GitHub Issue #40; a 1.69 client exists, unsure if old maps are included
# -- should make nailing down era differences easier

GAME_PATHS = {"Vindictus": "Vindictus"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


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


LumpHeader = source.LumpHeader


# class for each lump in alphabetical order:
class Area(base.Struct):  # LUMP 20
    num_area_portals: int  # number or AreaPortals after first_area_portal in this Area
    first_area_portal: int  # index into AreaPortal lump
    __slots__ = ["num_area_portals", "first_area_portal"]
    _format = "2i"


class AreaPortal(base.Struct):  # LUMP 21
    portal_key: int  # unique ID?
    other_area: int  # index of Area this on the other side? Area -> AreaPortal -> Area?
    first_clip_portal_vertex: int  # index into the ClipPortalVertex lump
    num_clip_portal_vertices: int  # number of ClipPortalVertices after first_clip_portal_vertex in this AreaPortal
    plane: int  # Plane this AreaPortal lies on
    __slots__ = ["portal_key", "other_area", "first_clip_portal_vertex",
                 "num_clip_portal_vertices", "plane"]
    _format = "4Ii"


class BrushSide(base.Struct):  # LUMP 19
    plane: int  # Plane this BrushSide lies on
    texture_info: int  # TextureInfo this BrushSide uses
    displacement_info: int  # DisplacementInfo applied to the Face derived from this BrushSide; -1 for None
    bevel: int  # is_bevel: bool? could indicate side is only used for collision detection
    __slots__ = ["plane", "texture_info", "displacement_info", "bevel"]
    _format = "I3i"


class DisplacementInfo(source.DisplacementInfo):  # LUMP 26
    start_position: vector.vec3  # approx coords of first corner of face
    # nessecary to ensure order of displacement vertices
    first_displacement_vertex: int  # index into DisplacementVertices
    first_displacement_triangle: int  # index into DisplacementTriangles
    power: int  # number of subdivisions; {2..4}
    # used to calculate num_displacement_vertices/triangles
    # TODO: formula for both num_displacement_vertices * triangles
    smoothing_angle: float  # for shading?
    unknown: int  # don't know what this does in Vindictus' format
    # flags: source.DisplacementFlags?
    # min_tesselation: int?
    contents: source.Contents
    face: int  # Face this DisplacementInfo affects
    lightmap_alpha_start: int  # TODO: figure out displacement lightmaps
    lightmap_sample_position_start: int
    edge_neighbours: List[bytes]  # TODO: DisplacementNeighbour class
    corner_neighbours: List[bytes]  # TODO: DisplacementCornerNeighbour class
    allowed_vertices: List[int]
    __slots__ = ["start_position", "first_displacement_vertex", "first_displacement_triangle",
                 "power", "smoothing_angle", "unknown", "contents", "face",
                 "lightmap_alpha_start", "lightmap_sample_position_start",
                 "edge_neighbours", "corner_neighbours", "allowed_vertices"]
    _format = "3f3if2iI2i144c10I"  # Neighbours are also different
    # TODO: replace 44c w/ f"{DisplacementNeighbour._format}" * 4
    _arrays = {"start_position": [*"xyz"], "edge_neighbours": 72,
               "corner_neighbours": 72, "allowed_vertices": 10}
    # TODO: DisplacementNeighbour._mapping.copy()
    _classes = {"start_position": vector.vec3, "contents": source.Contents}
    # TODO: neighbour classes


class Face(base.Struct):  # LUMP 7
    plane: int  # Plane this Face lies on
    side: int  # "faces opposite to the node's plane direction"; bool / enum?
    on_node: bool  # if False, Face is in a Leaf
    unknown: int
    first_edge: int  # index into SurfEdges
    num_edges: int  # number of SurfEdges after first_edge in this Face
    texture_info: int  # TextureInfo used on this Face
    displacement_info: int  # index into DisplacementInfos; -1 for None
    surface_fog_volume_id: int  # t-junctions? QuakeIII vertex-lit fog? index?
    styles: List[int]  # 4 different lighting states? "switchable lighting info"
    light_offset: int  # index of first pixel in LIGHTING / LIGHTING_HDR
    area: float  # surface area of this face
    lightmap: List[List[float]]
    # lightmap.mins: vector.vec2  # dimensions of lightmap segment
    # lightmap.size: vector.vec2  # scalars for lightmap segment
    original_face: int  # index into OriginalFaces; -1 if an OriginalFace
    num_primitives: int  # non-zero if t-juncts are present? number of Primitives
    first_primitive: int  # index of first Primitive
    smoothing_groups: int  # lightmap smoothing group; select multiple by using bits?
    __slots__ = ["plane", "side", "on_node", "unknown", "first_edge",
                 "num_edges", "texture_info", "displacement_info",
                 "surface_fog_volume_id", "styles", "light_offset", "area",
                 "lightmap", "original_face", "num_primitives",
                 "first_primitive", "smoothing_groups"]
    _format = "I2bh5i4bif4i4I"
    _arrays = {"styles": 4, "lightmap": {"mins": [*"xy"], "size": ["width", "height"]}}
    _classes = {"lightmap.mins": vector.vec2, "lightmap.size": vector.renamed_vec2("width", "height")}


class Facev2(base.Struct):  # LUMP 7 (v2)
    plane: int  # Plane this Face lies on
    side: int  # "faces opposite to the node's plane direction"; bool / enum?
    on_node: bool  # if False, Face is in a Leaf
    unknown_1: int
    first_edge: int  # index into SurfEdges
    num_edges: int  # number of SurfEdges after first_edge in this Face
    texture_info: int  # index into TextureInfos
    displacement_info: int   # index into the DisplacementInfos; -1 for None
    surface_fog_volume_id: int  # t-junctions? QuakeIII vertex-lit fog?
    unknown_2: int
    styles: List[int]  # 4 different lighting states? "switchable lighting info"
    light_offset: int  # index of first pixel in LIGHTING / LIGHTING_HDR
    area: float  # surface area of this face
    lightmap: List[List[float]]
    # lightmap.mins: vector.vec2  # dimensions of lightmap segment
    # lightmap.size: vector.vec2  # scalars for lightmap segment
    original_face: int  # index into OriginalFaces; -1 if an OriginalFace
    num_primitives: int  # non-zero if t-juncts are present? number of Primitives
    first_primitive: int  # index of first Primitive
    smoothing_groups: int  # lightmap smoothing group; select multiple by using bits?
    __slots__ = ["plane", "side", "on_node", "unknown_1", "first_edge",
                 "num_edges", "texture_info", "displacement_info",
                 "surface_fog_volume_id", "unknown_2", "styles",
                 "light_offset", "area", "lightmap", "original_face",
                 "num_primitives", "first_primitive", "smoothing_groups"]
    _format = "I2bh6i4bif4i4I"
    _arrays = {"styles": 4, "lightmap": {"mins": [*"xy"], "size": ["width", "height"]}}
    _classes = {"lightmap.mins": vector.vec2, "lightmap.size": vector.renamed_vec2("width", "height")}


class Leaf(base.Struct):  # LUMP 10
    contents: source.Contents
    cluster: int  # index of this Leaf's cluster (leaf group in VISIBILITY lump)
    flags: int  # not area & flags bitfield?
    bounds: List[vector.vec3]  # uint16_t, very blocky
    # bounds.mins: vector.vec3
    # bounds.maxs: vector.vec3
    first_leaf_face: int  # index of first LeafFace
    num_leaf_faces: int  # number of LeafFaces in this Leaf
    first_leaf_brush: int  # index of first LeafBrush
    num_leaf_brushes: int  # number of LeafBrushes in this Leaf
    leaf_water_data: int  # index into LeafWaterData; -1 if not submerged
    __slots__ = ["contents", "cluster", "flags", "mins", "maxs",
                 "first_leaf_face", "num_leaf_faces", "first_leaf_brush",
                 "num_leaf_brushes", "leaf_water_data"]
    _format = "9i4Ii"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}
    _classes = {"contents": source.Contents, "mins": vector.vec3, "maxs": vector.vec3}
    # TODO: ivec3


class Node(base.Struct):  # LUMP 5
    plane: int  # index into Plane lump
    children: List[int]  # 2 indices; Node if positive, Leaf if negative
    bounds: List[vector.vec3]  # uint16_t, very blocky
    # bounds.mins: vector.vec3
    # bounds.maxs: vector.vec3
    first_face: int  # index into Face lump
    num_faces: int  # number of Faces after first_face in this Node
    padding: int  # should be 0
    __slots__ = ["plane", "children", "bounds", "first_face", "num_faces", "padding"]
    _format = "12i"
    _arrays = {"children": 2, "bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}


class Overlay(base.Struct):  # LUMP 45
    id: int
    texture_info: int  # index to this Overlay's TextureInfo
    face_count_and_render_order: int  # render order uses the top 2 bits
    bitfield: int  # num_faces + render_order
    # bitfield.num_faces  # number of faces this Overlay touches?
    # bitfield.render_order
    faces: List[int]  # face indices this overlay is tied to (need bitfield.num_faces to read accurately)
    u: List[float]  # mins & maxs?
    v: List[float]  # mins & maxs?
    uv_points: List[List[float]]  # Vector[4]; 3D corners of the overlay?
    origin: List[float]
    normal: List[float]
    __slots__ = ["id", "texture_info", "face_count_and_render_order",
                 "faces", "u", "v", "uv_points", "origin", "normal"]
    _format = "2iI64i22f"
    _arrays = {"faces": 64,  # OVERLAY_BSP_FACE_COUNT (src/public/bspfile.h:998)
               "u": 2, "v": 2,
               "uv_points": {P: [*"xyz"] for P in "ABCD"},
               "origin": [*"xyz"], "normal": [*"xyz"]}
    _bitfields = {"bitfield": {"num_faces": 30, "render_order": 2}}
    _classes = {"origin": vector.vec3, "normal": vector.vec3}


# classes for special lumps, in alphabetical order:
class GameLumpHeader(base.MappedArray):
    id: str
    flags: int
    version: int
    offset: int
    length: int
    _mapping = ["id", "flags", "version", "offset", "length"]
    _format = "4s4i"


class GameLump_SPRP(source.GameLump_SPRP):  # sprp GameLump (LUMP 35)
    """use `lambda raw_lump: GameLump_SPRP(raw_lump, StaticPropvXX)` to implement"""
    StaticPropClass: object
    model_names: List[str]
    leaves: List[int]
    scales: List[StaticPropScale]
    props: List[object]  # List[StaticPropClass]

    def __init__(self, raw_sprp_lump: bytes, StaticPropClass: object):
        sprp_lump = io.BytesIO(raw_sprp_lump)
        model_name_count = int.from_bytes(sprp_lump.read(4), "little")
        model_names = struct.iter_unpack("128s", sprp_lump.read(128 * model_name_count))
        setattr(self, "model_names", [t[0].replace(b"\0", b"").decode() for t in model_names])
        leaf_count = int.from_bytes(sprp_lump.read(4), "little")
        leaves = itertools.chain(*struct.iter_unpack("H", sprp_lump.read(2 * leaf_count)))
        setattr(self, "leaves", list(leaves))
        scale_count = int.from_bytes(sprp_lump.read(4), "little")
        read_size = struct.calcsize(StaticPropScale._format) * scale_count
        scales = struct.iter_unpack(StaticPropScale._format, sprp_lump.read(read_size))
        setattr(self, "scales", list(scales))
        prop_count = int.from_bytes(sprp_lump.read(4), "little")
        if StaticPropClass is not None:
            read_size = struct.calcsize(StaticPropClass._format) * prop_count
            props = struct.iter_unpack(StaticPropClass._format, sprp_lump.read(read_size))
            setattr(self, "props", list(map(StaticPropClass.from_tuple, props)))
        else:
            prop_bytes = sprp_lump.read()
            prop_size = len(prop_bytes) // prop_count
            # NOTE: will break if prop_size does not divide evenly by prop_count
            setattr(self, "props", list(struct.iter_unpack(f"{prop_size}s", prop_bytes)))
        here = sprp_lump.tell()
        end = sprp_lump.seek(0, 2)
        assert here == end, "Had some leftover bytes, bad format"

    def as_bytes(self) -> bytes:
        if len(self.props) > 0:
            prop_bytes = [struct.pack(self.StaticPropClass._format, *p.flat()) for p in self.props]
        else:
            prop_bytes = []
        return b"".join([int.to_bytes(len(self.model_names), 4, "little"),
                         *[struct.pack("128s", n) for n in self.model_names],
                         int.to_bytes(len(self.leaves), 4, "little"),
                         *[struct.pack("H", L) for L in self.leaves],
                         int.to_bytes(len(self.scales), 4, "little"),
                         *[struct.pack(StaticPropScale._format, s) for s in self.scales],
                         int.to_bytes(len(self.props), 4, "little"),
                         *prop_bytes])


class StaticPropScale(base.Struct):
    prop: int  # index of prop to scale? (SPRP.props[sps.prop] * sps.scale)
    scale: vector.vec3
    __slots__ = ["index", "scale"]
    _format = "i3f"
    _arrays = {"scale": [*"xyz"]}
    _classes = {"scale": vector.vec3}


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = orange_box.BASIC_LUMP_CLASSES.copy()
BASIC_LUMP_CLASSES.update({"LEAF_BRUSHES":              {0: shared.UnsignedInts},
                           "LEAF_FACES":                {0: shared.UnsignedInts}})

LUMP_CLASSES = orange_box.LUMP_CLASSES.copy()
LUMP_CLASSES.update({"AREAS":             {0: Area},
                     "AREA_PORTALS":      {0: AreaPortal},
                     "BRUSH_SIDES":       {0: BrushSide},
                     "DISPLACEMENT_INFO": {0: DisplacementInfo},
                     "EDGES":             {0: remake_quake_old.Edge},
                     "FACES":             {1: Face,
                                           2: Facev2},
                     "LEAVES":            {1: Leaf},
                     "NODES":             {0: Node},
                     "ORIGINAL_FACES":    {1: Face,
                                           2: Facev2},
                     "OVERLAYS":          {0: Overlay}})

SPECIAL_LUMP_CLASSES = orange_box.SPECIAL_LUMP_CLASSES.copy()

GAME_LUMP_HEADER = GameLumpHeader

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = {"sprp": orange_box.GAME_LUMP_CLASSES["sprp"].copy()}
GAME_LUMP_CLASSES.update({"sprp": {6: lambda raw_lump: GameLump_SPRP(raw_lump, None)}})


methods = [*orange_box.methods]
