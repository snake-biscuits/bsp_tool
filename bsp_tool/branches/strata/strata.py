# Strata Source Engine (closed source) v25 VBSP
# https://stratasource.github.io/Wiki/docs/Reference/bsp-v25/
# https://blog.momentum-mod.org/posts/changelog/0.9.4/
# https://github.com/momentum-mod/BSPConvert
from __future__ import annotations
import enum
import io
from typing import List

from ... import core
from ... import lumps
from ...utils import binary
from ...utils import vector
from .. import colour
from .. import shared
from ..id_software import remake_quake_old
from ..nexon import vindictus69
from ..valve import physics
from ..valve import sdk_2013
from ..valve import source


FILE_MAGIC = b"VBSP"

BSP_VERSION = 25

GAME_PATHS = {
    "Momentum Mod": "Momentum Mod/momentum",
    "Portal Revolution": "Portal Revolution/revolution"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):  # assumed
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
    FACE_IDS = 11
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
    FACE_BRUSHES = 22  # infra
    FACE_BRUSH_LIST = 23  # infra
    UNUSED_24 = 24
    UNUSED_25 = 25
    DISPLACEMENT_INFO = 26
    ORIGINAL_FACES = 27
    PHYSICS_DISPLACEMENT = 28
    PHYSICS_COLLIDE = 29
    VERTEX_NORMALS = 30
    VERTEX_NORMAL_INDICES = 31
    DISPLACEMENT_LIGHTMAP_ALPHAS = 32  # deprecated / X360 ?
    DISPLACEMENT_VERTICES = 33
    DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS = 34
    GAME_LUMP = 35
    LEAF_WATER_DATA = 36
    PRIMITIVES = 37
    PRIMITIVE_VERTICES = 38  # deprecated / X360 ?
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
    PROP_BLOB = 49  # left4dead
    WATER_OVERLAYS = 50  # deprecated / X360 ?
    LEAF_AMBIENT_INDEX_HDR = 51
    LEAF_AMBIENT_INDEX = 52
    LIGHTING_HDR = 53
    WORLD_LIGHTS_HDR = 54
    LEAF_AMBIENT_LIGHTING_HDR = 55
    LEAF_AMBIENT_LIGHTING = 56
    XZIP_PAKFILE = 57  # deprecated / X360 ?
    FACES_HDR = 58
    MAP_FLAGS = 59
    OVERLAY_FADES = 60
    OVERLAY_SYSTEM_LEVELS = 61  # left4dead
    PHYSICS_LEVEL = 62  # left4dead2
    DISPLACEMENT_MULTIBLEND = 63  # alienswarm


LumpHeader = source.LumpHeader


# known lump changes from SDK 2013 -> Chaos
# TODO: figure out what changed


# TODO: a rough map of the relationships between lumps


# engine limits:
# NOTE: max map coords are -131072 to 131072 (4^3x Source, 2^3x Apex Legends)
class MAX(enum.Enum):
    """https://blog.momentum-mod.org/posts/changelog/0.9.2/"""
    MODELS = 65536
    BRUSHES = 131072
    BRUSH_SIDES = 655360
    PLANES = 1048576
    VERTICES = 1048576
    NODES = 1048576
    # unlimited TEXTURE_INFO
    TEXTURE_DATA = 16384
    FACES = 1048576
    FACES_HDR = 1048576
    ORIGINAL_FACES = 1048576
    LEAVES = 1048576
    LEAF_FACES = 1048576
    LEAF_BRUSHES = 1048576
    AREAS = 65536
    SURFEDGES = 8192000
    EDGES = 4096000
    # unlimited WORLDLIGHTS
    # unlimited WORLDLIGHTS_HDR
    LEAF_WATER_DATA = 32768  # unchanged
    PRIMITIVES = 1048576
    PRIMITIVE_VERTICES = 1048576
    PRIMITIVE_INDICES = 1048576
    CUBEMAP_SAMPLES = 16384
    OVERLAYS = 16384
    DISPLACEMENTS = 262144
    # edicts limit quadrupled to 8192 (engine entity implementation)


# classes for each lump, in alphabetical order:
class BrushSide(core.MappedArray):  # LUMP 19
    plane: int  # Plane this BrushSide lies on
    texture_info: int  # index into TextureInfo lump
    displacement_info: int  # index into DisplacementInfo lump
    bevel: int  # bool? indicates if side is a bevel plane (BSPVERSION 7)
    thin: int  # bool? new, might be from CSGO (bullet / PAS penetration)?
    padding: int
    _mapping = ["plane", "texture_info", "displacement_info", "bevel", "thin", "padding"]
    _format = "I2i2bh"


# class DisplacementCornerNeighbour(core.Struct):  # LUMP 26
#     neighbours: List[int]  # 4x indices into DisplacementInfo?
#     num_neighbours: int  # {0..4}?
#     __slots__ = ["neighbours", "num_neighbours"]
#     _format = "4IB"  # padding hell
#     _arrays = {"neighbours": 4}


# class DisplacementSubNeighbour(core.MappedArray):  # LUMP 26
#     # TODO: Source SDK displacement neighbour ascii diagram & comment block
#     neighbour: int  # DisplacementInfo index?
#     orientation: int  # neighbourOrient; enum?
#     span: int  # ?
#     neighbour_span: int  # ??
#     _mapping = ["neighbour", "orientation", "span", "neighbour_span"]
#     _format = "I3B"  # struct alignment hell


# class DisplacementNeighbour(list):  # LUMP 26
#     """x2 DisplacementSubNeighbour"""
#     _format = DisplacementSubNeighbour._format * 2


class DisplacementInfo(core.Struct):  # LUMP 26
    """Holds the information defining a displacement"""
    start_position: vector.vec3  # approx coords of first corner of face
    # nessecary to ensure order of displacement vertices
    first_displacement_vertex: int  # index of first DisplacementVertex
    # num_displacement_vertices: int = ((1 << power) + 1) ** 2
    first_displacement_triangle: int  # index of first DisplacementTriangle
    # num_diplacement_triangles: int = 2 * (1 << power) ** 2
    power: int  # level of subdivision
    min_tesselation: int  # for tesselation shaders / triangle assembley?
    smoothing_angle: float  # ?
    contents: source.Contents
    face: int  # Face this DisplacementInfo affects
    first_lightmap_alpha: int  # index into DisplacementLightmapAlphas?
    first_lightmap_sample_position: int  # ...
    # TODO: lightmap lengths
    # substruct packing hell:
    edge_neighbours: List[bytes]  # TODO: DisplacementNeighbour class
    corner_neighbours: List[bytes]  # TODO: DisplacementCornerNeighbour class
    allowed_vertices: List[int]
    __slots__ = [
        "start_position", "first_displacement_vertex", "first_displacement_triangle",
        "power", "min_tesselation", "smoothing_angle", "contents", "face",
        "first_lightmap_alpha", "first_lightmap_sample_position",
        "edge_neighbours", "corner_neighbours", "allowed_vertices"]
    _format = "3f4ifiI2i144B10I"
    _arrays = {
        "start_position": [*"xyz"], "edge_neighbours": 72, "corner_neighbours": 72,
        "allowed_vertices": 10}
    # 4x DisplacementNeighbour: edge_neighbours
    # 4x DisplacementCornerNeighbours: corner_neighbours
    _classes = {"start_position": vector.vec3, "contents": source.Contents}
    # TODO: neighbour classes


class Face(core.Struct):  # LUMPS 7, 27 * 58
    """makes up Models (including worldspawn), also referenced by LeafFaces"""
    plane: int  # index into Plane lump
    side: int  # "faces opposite to the Node's Plane direction"
    on_node: bool  # if False: Face is in a Leaf
    first_edge: int  # index into the SurfEdge lump
    num_edges: int  # number of SurfEdges after first_edge in this Face
    texture_info: int  # index into the TextureInfo lump
    displacement_info: int  # index into the DisplacementInfo lump (None if -1)
    surface_fog_volume_id: int  # related to QuakeIII vertex-lit fog?
    styles: List[int]  # 4 different lighting states? "switchable lighting info"
    light_offset: int  # index of first pixel in LIGHTING / LIGHTING_HDR
    area: float  # surface area of this face
    lightmap: List[vector.vec2]
    # lightmap.mins: vector.vec2  # dimensions of lightmap segment
    # lightmap.size: vector.vec2  # scalars for lightmap segment
    original_face: int  # OriginalFace this Face came from; -1 if this is an OriginalFace
    primitives: int
    # primitives.allow_dynamic_shadows: bool
    # primitives.count: int  # limit of 2^15 - 1
    first_primitive: int  # index of Primitive (if primitives.count != 0)
    smoothing_groups: int  # lightmap smoothing group
    __slots__ = [
        "plane", "side", "on_node", "first_edge", "num_edges", "texture_info",
        "displacement_info", "surface_fog_volume_id", "styles", "light_offset",
        "area", "lightmap", "original_face", "primitives", "first_primitive", "smoothing_groups"]
    _format = "I2b5I4bif5i3I"
    _arrays = {"styles": 4, "lightmap": {"mins": [*"xy"], "size": [*"xy"]}}
    _bitfields = {"primitives": {"allow_dynamic_shadows": 1, "count": 31}}
    # TODO: ivec2 for lightmap vectors
    _classes = {
        "lightmap.mins": vector.vec2, "lightmap.size": vector.vec2,
        "primitives.allow_dynamic_shadows": bool}


class FaceBrushList(core.MappedArray):  # LUMP 23
    num_face_brushes: int
    first_face_brush: int  # index into FaceBrushes
    _mapping = ["num_face_brushes", "first_face_brush"]
    _format = "2I"


class Leaf(source.Face):  # LUMP 10
    """Endpoint of a vis tree branch, a pocket of Faces"""
    contents: source.Contents
    cluster: int  # index of viscluster in Visibility; -1 for None
    bitfield: core.BitField
    # bitfield.area: int  # index?
    # bitfield.flags: int  # LeafFlags enum?
    bounds: List[vector.vec3]
    # bounds.mins: vector.vec3
    # bounds.maxs: vector.vec3
    first_leaf_face: int  # index into LeafFaces
    num_leaf_faces: int
    first_leaf_brush: int  # index into LeafBrushes
    num_leaf_brushes: int
    leaf_water_data: int  # index into LeafWaterData
    __slots__ = [
        "contents", "cluster", "bitfield", "bounds", "first_leaf_face",
        "num_leaf_faces", "first_leaf_brush", "num_leaf_brushes", "leaf_water_id"]
    _format = "IiI6f4Ii"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}
    _bitfields = {"bitfield": {"area": 17, "flags": 15}}
    _classes = {"contents": source.Contents, "bounds.mins": vector.vec3, "bounds.maxs": vector.vec3}
    # TODO: bounds AABB class


class LeafAmbientIndex(source.LeafAmbientIndex):  # LUMP 52
    num_samples: int
    first_sample: int  # index into LeafAmbientSamples
    _format = "2I"
    _mapping = ["num_samples", "first_sample"]


class Node(core.Struct):  # LUMP 5
    plane: int  # Plane that splits this Node
    children: List[int]  # 2 indices; Node if positive, Leaf if negative
    # TODO: match children to sides of Plane
    bounds: List[vector.vec3]  # uint16_t, very blocky
    # bounds.mins: vector.vec3
    # bounds.maxs: vector.vec3
    first_face: int  # index into Face lump
    num_faces: int  # number of Faces after first_face in this Node
    area: int  # index into Area lump, if all children are in the same area, else -1
    padding: int
    __slots__ = ["plane", "children", "bounds", "first_face", "num_faces", "area", "padding"]
    _format = "3i6f2I2h"
    _arrays = {"children": 2, "bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}
    _classes = {"bounds.mins": vector.vec3, "bounds.maxs": vector.vec3}
    # TODO: AABB bounds class


class Overlay(core.Struct):  # LUMP 45
    id: int
    texture_info: int  # index into TextureInfo
    face_count: int  # render order in top 2 bits
    faces: List[int]
    u: List[float]
    v: List[float]
    points: List[vector.vec3]
    origin: vector.vec3
    normal: vector.vec3
    __slots__ = [
        "id", "texture_info", "face_count", "faces",
        "u", "v", "points", "origin", "normal"]
    _format = "2iH64i22f"
    _arrays = {
        "faces": 64,
        "u": ["min", "max"], "v": ["min", "max"],
        "points": {P: [*"xyz"] for P in "ABCD"},
        "origin": [*"xyz"], "normal": [*"xyz"]}
    # TODO: index uv & points w/ {int: _mapping} _arrays
    _classes = {
        **{f"points.{P}": vector.vec3 for P in "ABCD"},
        "origin": vector.vec3, "normal": vector.vec3}


class Primitive(source.Primitive):  # LUMP 37
    type: source.PrimitiveType
    first_index: int  # index into PrimitiveIndices
    num_indices: int
    first_vertex: int  # index into PrimitiveVertices
    num_vertices: int
    _mapping = ["type", "first_index", "num_indices", "first_vertex", "num_vertices"]
    _format = "B4I"
    _classes = {"type": source.PrimitiveType}


class WaterOverlay(core.Struct):  # LUMP 50
    id: int
    texture_info: int  # index into TextureInfo
    face_count: int  # render order in top 2 bits
    faces: List[int]
    u: List[float]
    v: List[float]
    points: List[vector.vec3]
    origin: vector.vec3
    normal: vector.vec3
    __slots__ = ["id", "texture_info", "face_count", "faces",
                 "u", "v", "points", "origin", "normal"]
    _format = "2iH256i22f"
    _arrays = {"faces": 256, "u": ["min", "max"], "v": ["min", "max"],
               "points": {P: [*"xyz"] for P in "ABCD"}, "origin": [*"xyz"], "normal": [*"xyz"]}
    # TODO: index uv & points w/ {int: _mapping} _arrays
    _classes = {**{f"points.{P}": vector.vec3 for P in "ABCD"}, "origin": vector.vec3, "normal": vector.vec3}


# special lump classes, in alphabetical order:
class GameLump_SPRPv12(sdk_2013.GameLump_SPRPv11):  # sprp GAME LUMP (LUMP 35) [version 12]
    """leaves uint16_t -> uint32_t"""
    StaticPropClass = sdk_2013.StaticPropv11

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> GameLump_SPRPv12:
        out = cls()
        endian = {"little": "<", "big": ">"}[cls.endianness]
        num_model_names = binary.read_struct(stream, f"{endian}I")
        out.model_names = [
            stream.read(128).replace(b"\0", b"").decode()
            for i in range(num_model_names)]
        num_leaves = binary.read_struct(stream, f"{endian}I")
        out.leaves = binary.read_struct(stream, f"{endian}{num_leaves}I")
        num_props = binary.read_struct(stream, f"{endian}I")
        out.props = lumps.BspLump.from_count(stream, num_props, cls.StaticPropClass)
        tail = stream.read()
        if len(tail) > 0:
            props_bytes = b"".join([prop.as_bytes() for prop in out.props])
            resized = (len(props_bytes) + len(tail)) / num_props
            raise RuntimeError(f"tail of {len(tail)} bytes; StaticPropClass might be {resized} bytes long")
        return out


class StaticPropv13(core.Struct):  # sprp GAME LUMP (LUMP 35) [version 13]
    """for Portal: Revolution"""
    origin: List[float]  # origin.xyz
    angles: List[float]  # origin.yzx  QAngle; Z0 = East
    model_name: int  # index into GAME_LUMP.sprp.model_names
    first_leaf: int  # index into Leaf lump
    num_leafs: int  # number of Leafs after first_leaf this StaticProp is in
    solid_mode: int  # collision flags enum
    flags: int  # other flags
    skin: int  # index of this StaticProp's skin in the .mdl
    fade_distance: List[float]  # min & max distances to fade out
    lighting_origin: List[float]  # xyz position to sample lighting from
    forced_fade_scale: float  # relative to pixels used to render on-screen?
    cpu_level: List[int]  # min, max (-1 = any)
    gpu_level: List[int]  # min, max (-1 = any)
    diffuse_modulation: colour.RGBExponent
    disable_x360: int  # 4 byte bool
    flags_2: int  # values unknown
    scale: vector.vec3
    __slots__ = [
        "origin", "angles", "name_index", "first_leaf", "num_leafs", "solid_mode",
        "flags", "skin", "fade_distance", "lighting_origin", "forced_fade_scale",
        "cpu_level", "gpu_level", "diffuse_modulation", "disable_x360", "flags_2", "scale"]
    _format = "6f3H2Bi6f8B2I3f"
    _arrays = {
        "origin": [*"xyz"], "angles": [*"yzx"], "fade_distance": ["min", "max"],
        "lighting_origin": [*"xyz"], "cpu_level": ["min", "max"],
        "gpu_level": ["min", "max"], "diffuse_modulation": [*"rgba"], "scale": [*"xyz"]}
    _classes = {  # TODO: "angles": QAngle
        "origin": vector.vec3, "solid_mode": source.StaticPropCollision, "flags": source.StaticPropFlags,
        "lighting_origin": vector.vec3, "diffuse_modulation": colour.RGBExponent, "scale": vector.vec3}


class GameLump_SPRPv13(GameLump_SPRPv12):  # sprp GAME LUMP (LUMP 35) [version 13]
    StaticPropClass = StaticPropv13


class PhysicsDisplacement(physics.Displacement):  # LUMP 28
    _format = "I"


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = sdk_2013.BASIC_LUMP_CLASSES.copy()
BASIC_LUMP_CLASSES.update({
    "FACE_IDS":              {1: shared.UnsignedInts},
    "LEAF_BRUSHES":          {1: shared.UnsignedInts},
    "LEAF_FACES":            {1: shared.UnsignedInts},
    "VERTEX_NORMAL_INDICES": {1: shared.UnsignedInts}})

LUMP_CLASSES = sdk_2013.LUMP_CLASSES.copy()
LUMP_CLASSES.update({
    "AREA_PORTALS":           {1: vindictus69.AreaPortal},
    "BRUSH_SIDES":            {1: BrushSide},
    "DISPLACEMENT_INFO":      {1: DisplacementInfo},
    "EDGES":                  {1: remake_quake_old.Edge},
    "FACES":                  {2: Face},
    "FACES_HDR":              {2: Face},
    "LEAVES":                 {2: Leaf},
    "LEAF_AMBIENT_INDEX":     {1: LeafAmbientIndex},
    "LEAF_AMBIENT_INDEX_HDR": {1: LeafAmbientIndex},
    "LEAF_WATER_DATA":        {1: source.LeafWaterData},
    "NODES":                  {1: Node},
    "ORIGINAL_FACES":         {2: Face},
    "OVERLAYS":               {1: Overlay},
    "PRIMITIVE":              {1: Primitive},
    "WATER_OVERLAYS":         {1: WaterOverlay}})

SPECIAL_LUMP_CLASSES = sdk_2013.SPECIAL_LUMP_CLASSES.copy()
SPECIAL_LUMP_CLASSES.update({
    "PHYSICS_DISPLACEMENT": {2: PhysicsDisplacement}})

GAME_LUMP_HEADER = sdk_2013.GAME_LUMP_HEADER

GAME_LUMP_CLASSES = {
    "sprp": sdk_2013.GAME_LUMP_CLASSES["sprp"].copy()}
GAME_LUMP_CLASSES["sprp"].update({
        12: GameLump_SPRPv12,
        13: GameLump_SPRPv13})

methods = sdk_2013.methods.copy()
