# https://github.com/Qfusion/qfusion/blob/master/source/qcommon/qfiles.h
from __future__ import annotations
import enum
from typing import List

from ... import core
from ...utils import vector
from .. import colour
from .. import shared
from . import quake
from . import quake3


FILE_MAGIC = b"FBSP"

BSP_VERSION = 1

GAME_PATHS = {"Warsow": "Warsow"}
# TODO: Cocaine Diesel & Nosferatu

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    ENTITIES = 0
    TEXTURES = 1
    PLANES = 2
    NODES = 3
    LEAVES = 4
    LEAF_FACES = 5
    LEAF_BRUSHES = 6
    MODELS = 7
    BRUSHES = 8
    BRUSH_SIDES = 9
    VERTICES = 10
    INDICES = 11
    EFFECTS = 12  # FOGS
    FACES = 13
    LIGHTMAPS = 14
    LIGHT_GRID = 15
    VISIBILITY = 16
    LIGHT_ARRAY = 17


LumpHeader = quake.LumpHeader


# a rough map of the relationships between lumps:

# Entity -> Model -> Node -> Leaf -> LeafFace -> Face
#                                \-> LeafBrush -> Brush

# Visibility -> Node -> Leaf -> LeafFace -> Face
#                   \-> Plane

#               /-> Texture  /-> Texture
# Model -> Brush -> BrushSide -> Plane
#      \-> Face              \-> Face
# NOTE: Brush's indexed Texture is just used for Contents flags

#     /-> Texture
# Face -> Index -> Vertex
#    \--> Vertex
#     \-> Effect


# engine limits:
class MAX(enum.Enum):
    AREAS = 256
    BRUSHES = 32768
    BRUSHSIDES = 196608
    EFFECTS = 256
    ENTITIES = 2048
    ENTITIES_SIZE = 0x40000  # bytesize
    FACES = 131072
    INDICES = 524288
    LEAVES = 131072
    LEAF_BRUSHES = 262144
    LEAF_FACES = 131072
    LIGHTMAPS = 4  # one for each lighting style?
    LIGHTMAPS_SIZE = 0x800000  # bytesize
    MODELS = 1024
    NODES = 131072
    PLANES = 131072
    PORTALS = 131072  # no lump?
    TEXTURES = 1024
    VERTEXES = 524288
    VISIBILITY_SIZE = 0x200000  # bytesize


# classes for lumps, in alphabetical order:
class BrushSide(core.MappedArray):  # LUMP 9
    plane: int  # index of Plane this BrushSide lies on
    texture: int  # index of this BrushSide's Texture
    face: int  # index of the Face created from this BrushSide
    _mapping = ["plane", "texture", "face"]
    _format = "3i"


class Face(core.Struct):  # LUMP 13
    texture: int  # index of this Face's Texture
    effect: int  # index of this Face's Effect; -1 for None?
    type: int  # see quake3.FaceType
    first_vertex: int  # first Vertex in this Face
    num_vertices: int  # number of Vertices after first_vertex in this Face
    first_index: int  # first Index in this Face
    num_indices: int  # number of Indices after first_index in this Face
    style: List[List[int]]
    # style.lightmap: List[int]
    # style.vertex: List[int]
    lightmap: List[List[int | List[int]]]
    # lightmap.texture: List[int]
    # lightmap.offset: List[vector.vec2]
    # lightmap.size: vector.vec2
    origin: vector.vec3  # FLARE only
    mins: vector.vec3  # FLARE / PATCH only
    maxs: vector.vec3  # FLARE / PATCH only
    normal: vector.vec3  # PLANAR only
    patch: vector.vec2  # control point dimensions; TODO: ivec2
    __slots__ = [
        "texture", "effect", "type", "first_vertex", "num_vertices",
        "first_index", "num_indices", "style", "lightmap", "origin",
        "mins", "maxs", "normal", "patch"]
    _format = "5iIi8B14i12f2i"
    _arrays = {
        "style": {"lightmap": 4, "vertex": 4},
        "lightmap": {
            "texture": 4,
            "offset": {s: [*"xy"] for s in "ABCD"},
            "size": [*"xy"]},
        "origin": [*"xyz"], "mins": [*"xyz"], "maxs": [*"xyz"],
        "normal": [*"xyz"], "patch": [*"xy"]}
    _classes = {
        "type": quake3.FaceType, "lightmap.top_left": vector.vec2,
        "lightmap.size": vector.vec2, "lightmap.origin": vector.vec3,
        "lightmap.vector.s": vector.vec3, "lightmap.vector.t": vector.vec3,
        "normal": vector.vec3, "patch": vector.vec2}


class GridLight(core.Struct):  # LUMP 15
    ambient: List[List[colour.RGB24]]
    diffuse: List[List[colour.RGB24]]  # scaled by dot(mesh.Normal, gridlight.direction)
    # NOTE: 4x each colour, 1 for each style
    styles: List[int]  # which style to use?
    direction: List[int]  # 2x 0-255 angles defining a 3D vector / angle (no roll)
    __slots__ = ["ambient", "diffuse", "styles", "direction"]
    _format = "30B"
    # TODO: int keys in _arrays
    _arrays = {
        "ambient": {s: [*"rgb"] for s in "ABCD"},
        "diffuse": {s: [*"rgb"] for s in "ABCD"},
        "styles": 4,
        "direction": ["phi", "theta"]}
    _classes = {
        f"{type_}.{style}": colour.RGB24
        for type_ in ("ambient", "diffuse")
        for style in "ABCD"}


class Lightmap(list):  # LUMP 14
    """Raw pixel bytes, 512x512 RGB_888 image"""
    _pixels: List[bytes] = [b"\0" * 3] * 512 * 512
    _format = "3s" * 512 * 512  # 512x512 RGB_888

    def __getitem__(self, row) -> List[bytes]:
        # Lightmap[row][column] returns self.__getitem__(row)[column]
        # to get a specific pixel: self._pixels[index]
        row_start = row * 512
        return self._pixels[row_start:row_start + 512]  # TEST: do negative indices work?

    def flat(self) -> bytes:
        return b"".join(self._pixels)

    @classmethod
    def from_tuple(cls, _tuple):
        out = cls()
        out._pixels = _tuple  # RGB_888
        return out


class Vertex(core.Struct):  # LUMP 10
    position: List[float]
    uv0: List[float]
    lightmap_uv: List[List[float]]  # 4 uvs for 4 styles
    normal: List[float]
    color: List[List[int]]  # 4 colours for 4 styles
    __slots__ = ["position", "uv0", "lightmap_uv", "normal", "colour"]
    _format = "16f16B"
    _arrays = {
        "position": [*"xyz"],
        "uv0": [*"uv"],
        "lightmap_uv": {s: [*"uv"] for s in "ABCD"},
        "normal": [*"xyz"],
        "colour": {s: 4 for s in "ABCD"}}


# {"LUMP_NAME": LumpClass}
BASIC_LUMP_CLASSES = quake3.BASIC_LUMP_CLASSES.copy()
BASIC_LUMP_CLASSES.update({
    "INDICES": shared.UnsignedShorts})

LUMP_CLASSES = quake3.LUMP_CLASSES.copy()
LUMP_CLASSES.update({
    "BRUSH_SIDES": BrushSide,
    "FACES":       Face,
    "LIGHT_GRID":  GridLight,
    "LIGHTMAPS":   Lightmap,
    "VERTICES":    Vertex})

SPECIAL_LUMP_CLASSES = quake3.SPECIAL_LUMP_CLASSES.copy()

methods = quake3.methods.copy()
