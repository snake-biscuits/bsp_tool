# https://github.com/Qfusion/qfusion/blob/master/source/qcommon/qfiles.h
from __future__ import annotations
import enum
from typing import List

from .. import base
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
    SHADER_REFERENCES = 1
    PLANES = 2
    NODES = 3
    LEAVES = 4
    LEAF_FACES = 5
    LEAF_BRUSHES = 6
    MODELS = 7
    BRUSHES = 8
    BRUSH_SIDES = 9
    VERTICES = 10
    ELEMENTS = 11
    FOGS = 12
    FACES = 13
    LIGHTMAPS = 14
    LIGHT_GRID = 15
    VISIBILITY = 16
    LIGHT_ARRAY = 17


LumpHeader = quake.LumpHeader

# a rough map of the relationships between lumps:

#               /-> Texture
# Model -> Brush -> BrushSide
#      \-> Face -> MeshVertex
#             \--> Texture
#              \-> Vertex


# TODO: MAXS & SURFACE_TYPE IntEnums

# classes for lumps, in alphabetical order:
class BrushSide(base.MappedArray):  # LUMP 9
    plane: int
    shader: int
    surface: int
    _mapping = ["plane", "shader", "surface"]
    _format = "3i"


class Face(base.Struct):  # LUMP 13
    shader: int  # index of this Face's shader
    fog: int  # index of this Face's fog
    surface_type: int  # flags
    first_vertex: int  # first Vertex in this Face
    num_vertices: int  # number of Vertices after first_vertex in this Face
    first_element: int  # first Element in this Face
    num_elements: int  # number of Elements after first_element in this Face
    style: List[List[int]]
    # style.lightmap: List[int]
    # style.vertes: List[int]
    lightmap: List[List[int | List[int]]]
    # lightmap.texture: List[int]
    # lightmap.offset
    origin: List[float]  # FLARE only
    mins: List[float]  # FLARE / PATCH only
    maxs: List[float]  # FLARE / PATCH only
    normal: List[float]  # PLANAR only
    patch_control_point_dimensions: List[int]
    __slots__ = ["shader", "fog", "surface_type", "first_vertex", "num_vertices",
                 "first_element", "num_elements", "style", "lightmap", "origin",
                 "mins", "maxs", "normal", "patch_control_point_dimensions"]
    _format = "5iIi8B14i12f2i"
    _arrays = {"style": {"lightmap": 4, "vertex": 4},
               "lightmap": {"texture": 4, "offset": {s: [*"xy"] for s in "ABCD"},
                            "size": [*"xy"]},
               "origin": [*"xyz"], "mins": [*"xyz"], "maxs": [*"xyz"],
               "normal": [*"xyz"], "patch_control_point_dimensions": ["width", "height"]}


class GridLight(base.Struct):
    ambient: List[List[int]]
    diffuse: List[List[int]]
    styles: List[int]
    direction: List[int]
    __slots__ = ["ambient", "diffuse", "styles", "direction"]
    _format = "30B"
    _arrays = {"ambient": {s: [*"rgb"] for s in "ABCD"},
               "diffuse": {s: [*"rgb"] for s in "ABCD"},
               "styles": 4,
               "direction": 2}


class Lightmap(list):  # LUMP 14
    """Raw pixel bytes, 512x512 RGB_888 image"""
    _pixels: List[bytes] = [b"\0" * 3] * 512 * 512
    _format = "3s" * 512 * 512  # 512x512 RGB_888

    def __getitem__(self, row) -> List[bytes]:
        # Lightmap[row][column] returns self.__getitem__(row)[column]
        # to get a specific pixel: self._pixels[index]
        row_start = row * 512
        return self._pixels[row_start:row_start + 512]  # TEST: does it work with negative indices?

    def flat(self) -> bytes:
        return b"".join(self._pixels)

    @classmethod
    def from_tuple(cls, _tuple):
        out = cls()
        out._pixels = _tuple  # RGB_888
        return out


class Vertex(base.MappedArray):  # LUMP 10
    position: List[float]
    uv0: List[float]
    lightmap_uv: List[List[float]]
    normal: List[float]
    color: List[List[int]]
    __slots__ = ["position", "uv0", "lightmap_uv", "normal"]
    _format = "16f16B"
    _arrays = {"position": [*"xyz"], "uv0": [*"uv"],
               "lightmap_uv": {s: [*"uv"] for s in "ABCD"},
               "normal": [*"xyz"], "color": {s: 4 for s in "ABCD"}}


# {"LUMP_NAME": LumpClass}
BASIC_LUMP_CLASSES = quake3.BASIC_LUMP_CLASSES.copy()
BASIC_LUMP_CLASSES.update({"ELEMENTS": shared.UnsignedShorts})

LUMP_CLASSES = quake3.LUMP_CLASSES.copy()
LUMP_CLASSES.update({"BRUSH_SIDES": BrushSide,
                     "FACES":       Face,
                     "LIGHT_GRID":  GridLight,
                     "LIGHTMAPS":   Lightmap,
                     "VERTICES":    Vertex})

SPECIAL_LUMP_CLASSES = quake3.SPECIAL_LUMP_CLASSES.copy()

methods = [*quake3.methods]
