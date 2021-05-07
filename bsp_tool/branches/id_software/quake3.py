# https://www.mralligator.com/q3/
import enum
from typing import List
import struct

from .. import base
from .. import shared  # special lumps


BSP_VERSION = 46


class LUMP(enum.Enum):
    ENTITIES = 0  # one long string
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
    MESH_VERTICES = 11
    EFFECTS = 12
    FACES = 13
    LIGHTMAPS = 14  # 3 128x128 RGB888 images
    LIGHT_VOLUMES = 15
    VIS_DATA = 16


lump_header_address = {LUMP_ID: (8 + i * 8) for i, LUMP_ID in enumerate(LUMP)}


# classes for lumps (alphabetical order) [16 / 17] + shared.Entities
class Brush(base.Struct):  # LUMP 8
    first_side: int  # index into BrushSide lump
    num_sides: int  # number of BrushSides after first_side in this Brush
    texture: int  # index into Texture lump
    __slots__ = ["first_side", "num_sides", "texture"]
    _format = "3i"


class BrushSide(base.Struct):  # LUMP 9
    plane: int  # index into Plane lump
    texture: int  # index into Texture lump
    __slots__ = ["plane", "texture"]
    _format = "2i"


class Effect(base.Struct):  # LUMP 12
    name: str
    brush: int  # index into Brush lump
    unknown: int  # Always 5, except in q3dm8, which has one effect with -1
    __slots__ = ["name", "brush", "unknown"]
    _format = "64s2i"


class Face(base.Struct):  # LUMP 13
    texture: int  # index into Texture lump
    effect: int  # index into Effect lump; -1 for no effect
    type: int  # polygon, patch, mesh, billboard (env_sprite)
    first_vertex: int  # index into Vertex lump
    num_vertices: int  # number of Vertices after first_vertex in this face
    first_mesh_vertex: int  # index into MeshVertex lump
    num_mesh_vertices: int  # number of MeshVertices after first_mesh_vertex in this face
    # lightmap.index: int  # which of the 3 lightmap textures to use
    # lightmap.top_left: List[int]  # approximate top-left corner of visible lightmap segment
    # lightmap.size: List[int]  # size of visible lightmap segment
    # lightmap.origin: List[float]  # world space lightmap origin
    # lightmap.vector: List[List[float]]  # lightmap texture projection vectors
    normal: List[float]
    size: List[float]  # texture patch dimensions
    __slots__ = ["texture", "effect", "type", "first_vertex", "num_vertices",
                 "first_mesh_vertex", "num_mesh_vertices", "lightmap", "normal", "size"]
    _format = "12i12f2i"
    _arrays = {"lightmap": {"index": None, "top_left": [*"xy"], "size": ["width", "height"],
                            "origin": [*"xyz"], "vector": {"s": [*"xyz"], "t": [*"xyz"]}},
               "normal": [*"xyz"], "size": ["width", "height"]}


class Leaf(base.Struct):  # LUMP 4
    cluster: int  # index into VisData
    area: int
    mins: List[float]  # Bounding box
    maxs: List[float]
    first_leaf_face: int  # index into LeafFace lump
    num_leaf_faces: int  # number of LeafFaces in this Leaf
    __slots__ = ["cluster", "area", "mins", "maxs", "first_leaf_face", "num_leaf_faces"]
    _format = "12i"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}


class LeafBrush(int):  # LUMP 6
    """index into Brushes"""
    _format = "i"


class LeafFace(int):  # LUMP 5
    """index into Faces"""
    _format = "i"


class Lightmap(list):  # LUMP 14
    """Raw pixel bytes, 128x128 RGB_888 image"""
    _format = "3s" * 128 * 128  # 128x128 RGB_888

    def __init__(self, _tuple):
        self._pixels: List[bytes] = _tuple  # RGB_888

    def __getitem__(self, row) -> List[bytes]:  # returns 3 bytes: b"\xRR\xGG\xBB"
        # Lightmap[row][column] returns self.__getitem__(row)[column]
        # to get a specific pixel: self._pixels[index]
        row_start = row * 512
        return self._pixels[row_start:row_start + 512]  # TEST: does it work with negative indices?

    def flat(self) -> bytes:
        return b"".join(self._pixels)


class LightVolume(base.Struct):  # LUMP 15
    # LightVolumess make up a 3D grid whose dimensions are:
    # x = floor(MODELS[0].maxs.x / 64) - ceil(MODELS[0].mins.x / 64) + 1
    # y = floor(MODELS[0].maxs.y / 64) - ceil(MODELS[0].mins.y / 64) + 1
    # z = floor(MODELS[0].maxs.z / 128) - ceil(MODELS[0].mins.z / 128) + 1
    _format = "8B"
    __slots__ = ["ambient", "directional", "direction"]
    _arrays = {"ambient": [*"rgb"], "directional": [*"rgb"], "direction": ["phi", "theta"]}


class MeshVertex(int):  # LUMP 11
    _format = "i"


class Model(base.Struct):  # LUMP 7
    mins: List[float]  # Bounding box
    maxs: List[float]
    first_face: int  # index into Face lump
    num_faces: int  # number of Faces after first_face included in this Model
    first_brush: int  # index into Brush lump
    num_brushes: int  # number of Brushes after first_brush included in this Model
    __slots__ = ["mins", "maxs", "first_face", "num_faces", "first_brush", "num_brushes"]
    _format = "6f4i"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}


class Node(base.Struct):  # LUMP 3
    plane: int  # index into Plane lump; the plane this node was split from the bsp tree with
    child: List[int]  # two indices; into the Node lump if positive, the Leaf lump if negative
    __slots__ = ["plane", "child", "mins", "maxs"]
    _format = "9i"
    _arrays = {"child": [*"ab"], "mins": [*"xyz"], "maxs": [*"xyz"]}


class Plane(base.Struct):  # LUMP 2
    normal: List[float]
    distance: float
    __slots__ = ["normal", "distance"]
    _format = "4f"
    _arrays = {"normal": [*"xyz"]}


class Texture(base.Struct):  # LUMP 1
    name: str  # 64 char texture name; stored in WAD (Where's All the Data)?
    flags: int  # rendering bit flags?
    contents: int  # SOLID, AIR etc.
    __slots__ = ["name", "flags", "contents"]
    _format = "64s2i"


class Vertex(base.Struct):  # LUMP 10
    position: List[float]
    # uv.texture: List[float]
    # uv.lightmap: List[float]
    normal: List[float]
    colour: bytes  # 1 RGBA32 pixel / texel
    __slots__ = ["position", "uv", "normal", "colour"]
    _format = "10f4B"
    _arrays = {"position": [*"xyz"], "uv": {"texture": [*"uv"], "lightmap": [*"uv"]},
               "normal": [*"xyz"]}


# special lump classes (alphabetical order):
class Visibility:
    """Cluster X is visible from Cluster Y if:
    bit (1 << Y % 8) of vecs[X * vector_size + Y // 8] is set
    NOTE: Clusters are associated with Leaves"""
    def __init__(self, raw_visiblity: bytes):
        self.vector_count, self.vector_size = struct.unpack("2i", raw_visiblity[:8])
        self.vectors = struct.unpack(f"{self.vector_count * self.vector_size}B", raw_visiblity[8:])

    def as_bytes(self):
        vectors_bytes = f"{self.vector_count * self.vector_size}B"
        return struct.pack(f"2i{vectors_bytes}", (self.vector_count, self.vector_size, *self.vectors))


BASIC_LUMP_CLASSES = {"LEAF_BRUSHES": LeafBrush,
                      "LEAF_FACES": LeafFace,
                      "MESH_VERTICES": MeshVertex}

LUMP_CLASSES = {"BRUSHES": Brush,
                "BRUSH_SIDES": BrushSide,
                "EFFECTS": Effect,
                "FACES": Face,
                "LEAVES": Leaf,
                "LIGHTMAPS": Lightmap,
                "LIGHT_VOLUMES": LightVolume,
                "MODELS": Model,
                "NODES": Node,
                "PLANES": Plane,
                "TEXTURES": Texture,
                "VERTICES": Vertex}

SPECIAL_LUMP_CLASSES = {"ENTITIES": shared.Entities,
                        "VIS_DATA": Visibility}


# branch exclusive methods, in alphabetical order:
def vertices_of_face(bsp, face_index: int) -> List[float]:
    raise NotImplementedError()


def vertices_of_model(bsp, model_index: int) -> List[float]:
    raise NotImplementedError()


methods = []
