# https://github.com/RealityFactory/Genesis3D/blob/master/World/Gbspfile.h
import enum
from typing import Any, Dict, List, Union

from ... import core
from ...utils import vector
from .. import shared
from .. import time
from ..id_software import quake
from ..id_software import quake2
from ..id_software import remake_quake
from ..id_software import remake_quake_old


FILE_MAGIC = b"GBSP"

BSP_VERSION = 15

GAME_PATHS = {"Amsterdoom": "Amsterdoom"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


# NOTE: id-based "CHUNKS"; file header is a chunk
class LUMP(enum.Enum):
    HEADER = 0
    MODELS = 1
    NODES = 2
    CLIP_NODES = 3  # BNODES
    LEAVES = 4
    CLUSTERS = 5
    AREAS = 6
    AREA_PORTALS = 7
    LEAF_SIDES = 8
    PORTALS = 9
    PLANES = 10
    FACES = 11
    LEAF_FACES = 12
    INDICES = 13
    VERTICES = 14
    RGB_VERTICES = 15
    ENTITIES = 16
    TEXTURE_INFO = 17
    TEXTURES = 18
    TEXELS = 19  # TEXTURE_DATA
    LIGHTING = 20
    VISIBILITY = 21
    SKY = 22
    PALETTES = 23
    MOTIONS = 24
    END = 0xFFFF


class LumpHeader(core.MappedArray):
    id: int
    size: int  # sizeof(LumpClass)
    count: int  # num_elements
    # derived by Genesis3DBsp._preload
    offset: int  # "chunk" headers & data appear inline
    length: int  # size * count
    _mapping = ["id", "size", "count"]
    _format = "3I"


# TODO: a rough map of the relationships between lumps:


# flag enums:
class Contents(enum.IntFlag):
    # NOTE: BSP_CONTENTS, separate from GE_CONTENTS
    SOLID = -1
    EMPTY = -2

    def __repr__(self):
        if self < 0:
            return super().__repr__()
        else:
            return str(int(self))


# classes for lumps, in alphabetical order:
class AreaPortal(core.Struct):  # LUMP 7
    model: int
    area: int
    __slots__ = ["model", "area"]
    _format = "2i"


class ClipNode(remake_quake_old.ClipNode):  # LUMP 3
    __slots__ = ["children", "plane"]


class Face(core.Struct):  # LUMP 11
    first_vertex: int
    num_vertices: int
    plane: int
    side: quake.PlaneSide
    texture_info: int
    lighting: List[int]
    # lighting.offset: int  # -1 for unlit
    # lighting.size: vector.vec2(width, height)
    # lighting.type: List[int]  # styles?
    __slots__ = ["first_vertex", "num_vertices", "plane", "side", "texture_info", "lighting"]
    _format = "8i4B"
    _arrays = {"lighting": {"offset": None, "size": ["width", "height"], "types": 4}}
    _classes = {"side": quake.PlaneSide}


class Header(core.Struct):  # LUMP 0
    magic: bytes
    padding: bytes  # 4 NULL bytes
    version: int
    time: time.SystemTime
    __slots__ = ["magic", "padding", "version", "time"]
    _format = "4s4si8H"
    _arrays = {
        "time": [
            "year", "month", "day_of_week", "day",
            "hour", "minute", "second", "millisecond"]}
    _classes = {"time": time.SystemTime}

    @classmethod
    def _defaults(cls) -> Dict[str, Any]:
        return {
            "magic": b"",
            "padding": b"",
            "version": 0,
            "time": time.SystemTime()}


class Leaf(core.Struct):  # LUMP 4
    contents: int
    bounds: List[vector.vec3]
    # bounds.mins: vector.vec3
    # bounds.maxs: vector.vec3
    first_leaf_face: int
    num_leaf_faces: int
    first_portal: int
    num_portals: int
    cluster: int  # index into Cluster lump
    area: int  # -1: Area, 0: Solid, *: Area Index
    first_leaf_side: int
    num_leaf_sides: int
    __slots__ = [
        "contents", "bounds", "first_leaf_face", "num_leaf_faces",
        "first_portal", "num_portals", "cluster", "area",
        "first_leaf_side", "num_leaf_sides"]
    _format = "i6f8i"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}
    _classes = {
        "contents": Contents,
        "bounds.mins": vector.vec3, "bounds.maxs": vector.vec3}


class LeafSide(core.Struct):  # LUMP 8
    """bevelled sides for BBox collisions"""
    plane: int  # index into Planes
    side: int  # 0/1 front/back?
    __slots__ = ["plane", "side"]
    _format = "2i"


class Model(core.Struct):  # LUMP 1
    node: int  # top level Node
    clip_node: int  # top level ClipNode
    bounds: List[vector.vec3]
    origin: vector.vec3
    first_face: int
    num_faces: int
    first_leaf: int
    num_leaves: int
    first_cluster: int
    num_clusters: int
    areas: List[int]
    motion: int
    __slots__ = [
        "node", "clip_node", "bounds", "origin", "first_face", "num_faces",
        "first_leaf", "num_leaves", "first_cluster", "num_clusters",
        "areas", "motion"]
    _format = "2i9f9i"
    _arrays = {
        "bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]},
        "origin": [*"xyz"], "areas": 2}
    _classes = {
        "bounds.mins": vector.vec3, "bounds.maxs": vector.vec3,
        "origin": vector.vec3}


class Node(remake_quake.Node):  # LUMP 2
    __slots__ = ["children", "num_faces", "first_face", "plane", "bounds"]
    _format = "5I6f"


# TODO: Palette (256x colour.Colour24)


class Portal(core.Struct):  # LUMP 9
    origin: vector.vec3
    leaf: int  # Leaf this Portal "looks into"
    __slots__ = ["origin", "leaf"]
    _format = "3fi"
    _arrays = {"origin": [*"xyz"]}
    _classes = {"origin": vector.vec3}


class Sky(core.Struct):  # LUMP 22
    axis: vector.vec3  # axis of rotation
    degrees_per_minute: float
    textures: List[int]  # indices into Textures
    draw_scale: float
    __slots__ = ["axis", "degrees_per_minute", "textures", "draw_scale"]
    _format = "4f6If"
    _arrays = {"axis": [*"xyz"], "textures": 6}
    _classes = {"axis": vector.vec3}


class Texture(core.Struct):  # LUMP 18
    name: str
    flags: int
    size: List[int]
    first_texel: int
    # num_texels = size.width * size.height
    palette: int
    _format = "32sI4i"
    __slots__ = ["name", "flags", "size", "first_texel", "palette"]
    _arrays = {"size": ["width", "height"]}
    # TODO: _classes = {"flags": TextureFlags, "size": ivec2}


class TextureInfo(core.Struct):  # LUMP 17
    # NOTE: TextureVector(ProjectionAxis(projection.axes.s, projection.offsets.s, projection.sizes.s), ...)
    projection: List[List[Union[vector.vec3, float]]]
    # projections.axes: List[vector.vec3]
    # projections.offsets: List[float]
    # projections.sizes: List[float]
    flags: int
    face_light: float  # for radiosity calculations; temp compile variable?
    reflectiveness: float  # "scale"
    alpha: float
    mip_map_bias: float  # ???
    texture: int
    __slots__ = [
        "projection", "flags", "face_light", "reflectiveness",
        "alpha", "mip_map_bias", "texture"]
    _format = "10fi4fi"
    _arrays = {
        "projection": {
            "axes": {"s": [*"xyz"], "t": [*"xyz"]},
            "offsets": [*"st"], "sizes": [*"st"]}}
    _classes = {f"projection.axes.{a}": vector.vec3 for a in "st"}
    # TODO: _classes = {"flags": TextureInfoFlags}


# {"LUMP_NAME": LumpClass}
BASIC_LUMP_CLASSES = {
    "CLUSTERS":   shared.Ints,
    "INDICES":    shared.Ints,
    "LEAF_FACES": shared.Ints,
    "TEXELS":     shared.Bytes}

LUMP_CLASSES = {
    "AREAS":        quake2.Area,
    "AREA_PORTALS": AreaPortal,
    "CLIP_NODES":   ClipNode,
    "FACES":        Face,
    "LEAVES":       Leaf,
    "LEAF_SIDES":   LeafSide,
    "MODELS":       Model,
    "NODES":        Node,
    "PLANES":       quake.Plane,
    "PORTALS":      Portal,
    "RGB_VERTICES": quake.Vertex,  # colour values parallel w/ indices?
    "TEXTURES":     Texture,
    "TEXTURE_INFO": TextureInfo,
    "VERTICES":     quake.Vertex}

SPECIAL_LUMP_CLASSES = {
    "HEADER": Header,
    "SKY":    Sky}


methods = dict()
