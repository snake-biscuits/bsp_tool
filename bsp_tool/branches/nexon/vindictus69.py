# https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Vindictus
"""Archived v1.69 pre-steam release build of Vindictus"""
from __future__ import annotations
import enum
import io
import struct
from typing import List

from ... import core
from ... import lumps
from ...utils import binary
from ...utils import vector
from .. import shared
from ..id_software import remake_quake_old
from ..valve import orange_box
from ..valve import source


FILE_MAGIC = b"VBSP"

BSP_VERSION = 20

GAME_PATHS = {"Vindictus": "Vindictus EU/en-EU"}
# NOTE: maps are stored in .hfs archives

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
    FACE_MACRO_TEXTURE_INFO = 47
    DISPLACEMENT_TRIANGLES = 48
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
class Area(core.Struct):  # LUMP 20
    num_area_portals: int  # number or AreaPortals after first_area_portal in this Area
    first_area_portal: int  # index into AreaPortal lump
    __slots__ = ["num_area_portals", "first_area_portal"]
    _format = "2i"


class AreaPortal(core.Struct):  # LUMP 21
    portal_key: int  # unique ID?
    other_area: int  # index of Area this on the other side? Area -> AreaPortal -> Area?
    first_clip_portal_vertex: int  # index into the ClipPortalVertex lump
    num_clip_portal_vertices: int  # number of ClipPortalVertices after first_clip_portal_vertex in this AreaPortal
    plane: int  # Plane this AreaPortal lies on
    __slots__ = [
        "portal_key", "other_area", "first_clip_portal_vertex",
        "num_clip_portal_vertices", "plane"]
    _format = "4Ii"


class BrushSide(core.Struct):  # LUMP 19
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
    __slots__ = [
        "start_position", "first_displacement_vertex", "first_displacement_triangle",
        "power", "smoothing_angle", "unknown", "contents", "face",
        "lightmap_alpha_start", "lightmap_sample_position_start",
        "edge_neighbours", "corner_neighbours", "allowed_vertices"]
    _format = "3f3if2iI2i144B10I"  # Neighbours are also different
    # TODO: replace 44c w/ f"{DisplacementNeighbour._format}" * 4
    _arrays = {
        "start_position": [*"xyz"], "edge_neighbours": 72,
        "corner_neighbours": 72, "allowed_vertices": 10}
    # TODO: DisplacementNeighbour._mapping.copy()
    _classes = {"start_position": vector.vec3, "contents": source.Contents}
    # TODO: neighbour classes


class Face(core.Struct):  # LUMP 7
    plane: int  # Plane this Face lies on
    side: int  # "faces opposite to the Node's Plane direction"; bool / enum?
    on_node: bool  # if False: Face is in a Leaf
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
    original_face: int  # OriginalFace this Face came from; -1 if this is an OriginalFace
    primitives: int
    # primitives.allow_dynamic_shadows: bool
    # primitives.count: int  # limit of 2^15 - 1
    first_primitive: int  # index of Primitive (if primitives.count != 0)
    smoothing_groups: int  # lightmap smoothing group; select multiple by using bits?
    __slots__ = [
        "plane", "side", "on_node", "unknown", "first_edge",
        "num_edges", "texture_info", "displacement_info",
        "surface_fog_volume_id", "styles", "light_offset", "area",
        "lightmap", "original_face", "primitives",
        "first_primitive", "smoothing_groups"]
    _format = "I2bh5i4bif4i4I"
    _arrays = {"styles": 4, "lightmap": {"mins": [*"xy"], "size": [*"xy"]}}
    _bitfields = {"primitives": {"allow_dynamic_shadows": 1, "count": 31}}
    # TODO: ivec2 for lightmap vectors
    _classes = {
        "lightmap.mins": vector.vec2, "lightmap.size": vector.vec2,
        "primitives.allow_dynamic_shadows": bool}


class Facev2(core.Struct):  # LUMP 7 (v2)
    plane: int  # Plane this Face lies on
    side: int  # "faces opposite to the Node's Plane direction"; bool / enum?
    on_node: bool  # if False: Face is in a Leaf
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
    original_face: int  # OriginalFace this Face came from; -1 if this is an OriginalFace
    primitives: int
    # primitives.allow_dynamic_shadows: bool
    # primitives.count: int  # limit of 2^15 - 1
    first_primitive: int  # index of Primitive (if primitives.count != 0)
    smoothing_groups: int  # lightmap smoothing group; select multiple by using bits?
    __slots__ = [
        "plane", "side", "on_node", "unknown_1", "first_edge",
        "num_edges", "texture_info", "displacement_info",
        "surface_fog_volume_id", "unknown_2", "styles",
        "light_offset", "area", "lightmap", "original_face",
        "primitives", "first_primitive", "smoothing_groups"]
    _format = "I2bh6i4bif4i4I"
    _arrays = {"styles": 4, "lightmap": {"mins": [*"xy"], "size": [*"xy"]}}
    _bitfields = {"primitives": {"allow_dynamic_shadows": 1, "count": 31}}
    # TODO: ivec2 for lightmap vectors
    _classes = {
        "lightmap.mins": vector.vec2, "lightmap.size": vector.vec2,
        "primitives.allow_dynamic_shadows": bool}


class Leaf(core.Struct):  # LUMP 10
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
    __slots__ = [
        "contents", "cluster", "flags", "mins", "maxs",
        "first_leaf_face", "num_leaf_faces", "first_leaf_brush",
        "num_leaf_brushes", "leaf_water_data"]
    _format = "9i4Ii"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}
    _classes = {"contents": source.Contents, "mins": vector.vec3, "maxs": vector.vec3}
    # TODO: ivec3


class Node(core.Struct):  # LUMP 5
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
    _classes = {"bounds.mins": vector.vec3, "bounds.maxs": vector.vec3}


class Overlay(core.Struct):  # LUMP 45
    id: int
    texture_info: int  # index to this Overlay's TextureInfo
    face_count_and_render_order: int  # render order uses the top 2 bits
    bitfield: int  # render_order & num_faces
    # bitfield.render_order
    # bitfield.num_faces  # number of faces this Overlay touches?
    faces: List[int]  # face indices this overlay is tied to (need bitfield.num_faces to read accurately)
    u: List[float]  # mins & maxs?
    v: List[float]  # mins & maxs?
    uv_points: List[List[float]]  # Vector[4]; 3D corners of the overlay?
    origin: List[float]
    normal: List[float]
    __slots__ = ["id", "texture_info", "bitfield", "faces", "u", "v", "uv_points", "origin", "normal"]
    _format = "2iI64i22f"
    _arrays = {
        "faces": 64,  # OVERLAY_BSP_FACE_COUNT (src/public/bspfile.h:998)
        "u": 2, "v": 2,
        "uv_points": {P: [*"xyz"] for P in "ABCD"},
        "origin": [*"xyz"], "normal": [*"xyz"]}
    _bitfields = {"bitfield": {"render_order": 2, "num_faces": 30}}
    _classes = {"origin": vector.vec3, "normal": vector.vec3}


# classes for special lumps, in alphabetical order:
class GameLumpHeader(core.MappedArray):
    id: str
    flags: int
    version: int
    offset: int
    length: int
    _mapping = ["id", "flags", "version", "offset", "length"]
    _format = "4s4i"


class StaticPropScale(core.Struct):
    prop: int  # index of prop to scale? (SPRP.props[sps.prop] * sps.scale)
    scale: vector.vec3
    __slots__ = ["index", "scale"]
    _format = "i3f"
    _arrays = {"scale": [*"xyz"]}
    _classes = {"scale": vector.vec3}


class GameLump_SPRPv6(source.GameLump_SPRPv4):  # sprp GameLump (LUMP 35) [version 6]
    StaticPropClass: object = source.StaticPropv5
    model_names: List[str]
    leaves: List[int]
    scales: List[StaticPropScale]
    props: List[source.StaticPropv5]

    def __init__(self):
        self.model_names = list()
        self.leaves = list()
        self.scales = list()
        self.props = list()

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> GameLump_SPRPv6:
        out = cls()
        endian = {"little": "<", "big": ">"}[cls.endianness]
        num_model_names = binary.read_struct(stream, f"{endian}I")
        out.model_names = [
            stream.read(128).replace(b"\0", b"").decode()
            for i in range(num_model_names)]
        num_leaves = binary.read_struct(stream, f"{endian}I")
        assert num_leaves != 1
        out.leaves = binary.read_struct(stream, f"{endian}{num_leaves}H")
        num_scales = binary.read_struct(stream, f"{endian}I")
        out.scales = lumps.BspLump.from_count(stream, num_scales, StaticPropScale)
        num_props = binary.read_struct(stream, f"{endian}I")
        out.props = lumps.BspLump.from_count(stream, num_props, cls.StaticPropClass)
        tail = stream.read()
        if len(tail) > 0:
            props_bytes = b"".join([prop.as_bytes() for prop in out.props])
            resized = (len(props_bytes) + len(tail)) / num_props
            raise RuntimeError(f"tail of {len(tail)} bytes; StaticPropClass might be {resized} bytes long")
        return out

    def as_bytes(self) -> bytes:
        assert all([
            isinstance(prop, self.StaticPropClass)
            for prop in self.props])
        endian = {"little": "<", "big": ">"}[self.endianness]
        return b"".join([
            struct.pack(f"{endian}I", len(self.model_names)),
            *[
                struct.pack("128s", model_name.encode("ascii"))
                for model_name in self.model_names],
            struct.pack(f"{endian}I", len(self.leaves)),
            struct.pack(f"{endian}{len(self.leaves)}H", *self.leaves),
            struct.pack(f"{endian}I", len(self.scales)),
            *[
                scale.as_bytes()
                for scale in self.scales],
            struct.pack(f"{endian}I", len(self.props)),
            *[
                prop.as_bytes()
                for prop in self.props]])


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = orange_box.BASIC_LUMP_CLASSES.copy()
BASIC_LUMP_CLASSES.update({
    "LEAF_BRUSHES": {0: shared.UnsignedInts},
    "LEAF_FACES":   {0: shared.UnsignedInts}})

LUMP_CLASSES = orange_box.LUMP_CLASSES.copy()
LUMP_CLASSES.update({
    "AREAS":             {0: Area},
    "AREA_PORTALS":      {0: AreaPortal},
    "BRUSH_SIDES":       {0: BrushSide},
    "DISPLACEMENT_INFO": {0: DisplacementInfo},
    "EDGES":             {0: remake_quake_old.Edge},
    "FACES": {
        1: Face,
        2: Facev2},
    "LEAVES":            {1: Leaf},
    "NODES":             {0: Node},
    "ORIGINAL_FACES": {
        1: Face,
        2: Facev2},
    "OVERLAYS":          {0: Overlay}})

SPECIAL_LUMP_CLASSES = orange_box.SPECIAL_LUMP_CLASSES.copy()

GAME_LUMP_HEADER = GameLumpHeader

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = {
    "sprp": {
        5: source.GameLump_SPRPv5,
        6: GameLump_SPRPv6}}


methods = orange_box.methods.copy()
