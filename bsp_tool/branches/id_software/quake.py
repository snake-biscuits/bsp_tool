# https://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_4.htm
import enum
from typing import Dict, List
import struct

from .. import base
from .. import shared  # special lumps


BSP_VERSION = 23


class LUMP(enum.Enum):
    ENTITIES = 0  # one long string
    PLANES = 1
    MIP_TEXTURES = 2
    VERTICES = 3
    VISIBILITY = 4  # appears to be same as in Source Engine
    NODES = 5
    TEXTURE_INFO = 6
    FACES = 7
    LIGHTMAPS = 8  # 8bpp 0x00-0xFF black-white
    CLIP_NODES = 9
    LEAVES = 10  # indexed by NODES, index ranges of LEAF_FACES
    LEAF_FACES = 11  # indices into FACES, sorted for (start, len) lookups
    EDGES = 12
    SURFEDGES = 13  # indices into EDGES (-ve indices reverse edge direction)
    MODELS = 14

# a rough map of the relationships between lumps:
# ENTITIES -> MODELS -> NODES -> LEAVES -> LEAF_FACES -> FACES
#                   |-> CLIP_NODES -> PLANES

# FACES -> SURFEDGES -> EDGES -> VERTICES
#      |-> TEXTURE_INFO -> MIP_TEXTURES
#      |-> LIGHTMAPS
#      |-> PLANES


lump_header_address = {LUMP_ID: (8 + i * 8) for i, LUMP_ID in enumerate(LUMP)}


# classes for lumps (alphabetical order) [X / 15] + shared.Entities
class ClipNode(base.Struct):  # LUMP 9
    # https://en.wikipedia.org/wiki/Half-space_(geometry)
    # NOTE: bounded by associated model
    # basic convex solid stuff
    plane: int
    children: List[int]  # +ve ClipNode, -1 outside model, -2 inside model

    __slots__ = ["plane", "children"]
    _format = "I2h"
    _arrays = {"children": ["front", "back"]}


class Edge(list):  # LUMP 12
    _format = "2H"  # List[int]


class Face(base.Struct):  # LUMP 7
    plane: int
    side: int  # 0 or 1 for side of plane
    first_edge: int
    num_edges: int
    texture_info_index: int  # index of this face's TextureInfo
    lighting_type: int  # 0x00=lightmap, 0xFF=no-lightmap, 0x01=fast-pulse, 0x02=slow-pulse, 0x03-0x10 other
    base_light: int  # 0x00 bright - 0xFF dark (lowest possible light level)
    light: int
    lightmap: int  # index into lightmap lump, or -1
    __slots__ = ["plane", "side", "first_edge", "num_edges", "texture_info_index",
                 "lighting_type", "base_light", "light", "lightmap"]
    _format = "2HI2H4Bi"
    _arrays = {"light": 2}


class Leaf(base.Struct):  # LUMP 10
    type: int
    cluster: int  # index into the VISIBILITY lump
    bounds: List[int]
    first_leaf_face: int
    num_leaf_faces: int
    sound: List[int]  # ambient master of all 4 elements (0x00 - 0xFF)

    __slots__ = ["type", "cluster", "bounds", "first_leaf_face",
                 "num_leaf_faces", "sound"]
    _format = "2i6h2H4B"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]},
               "sound": ["water", "sky", "slime", "lava"]}


class LeafType(enum.Enum):
    # NOTE: other types exist, but are unknown
    NORMAL = -1
    SOLID = -2
    WATER = -3
    SLIME = -4
    LAVA = -5
    SKY = -6
    # NOTE: types below 6 may not be implemented, but act like water


class Model(base.Struct):  # LUMP 14
    bounds: List[float]  # mins & maxs
    origin: List[float]
    first_node: int  # first node in NODES lumps
    clip_nodes: int  # 1st & second CLIP_NODES indices
    node_id3: int  # usually 0, unsure of lump
    num_leaves: int
    first_leaf_face: int
    num_leaf_faces: int
    __slots__ = ["bounds", "origin", "first_node", "clip_nodes", "node_id3",
                 "num_leaves", "first_face", "num_faces"]
    _format = "9f7i"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}, "origin": [*"xyz"],
               "clip_nodes": 2}


class MipTexture(base.Struct):  # LUMP 2 (used in MipTextureLump)
    name: str  # texture name
    # if name starts with "*" it scrolls
    # if name starts with "+" it ...
    size: List[int]  # width & height
    offsets: List[int]  # offset from entry start to texture
    __slots__ = ["name", "size", "offsets"]
    _format = "16s6I"
    _arrays = {"size": ["width", "height"],
               "offsets": ["full", "half", "quarter", "eighth"]}
    # TODO: transparently access texture data with offsets


class Node(base.Struct):  # LUMP 5
    plane_index: int
    children: List[int]  # +ve Node, -ve Leaf
    # NOTE: -1 (leaf 0) is a dummy leaf & terminates tree searches
    bounds: List[int]
    # NOTE: bounds are generous, rounding up to the nearest 16 units
    first_face: int
    num_faces: int

    _format = "I8h"
    _arrays = {"children": ["front", "back"],
               "bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}


class Plane(base.Struct):  # LUMP 1
    normal: List[float]
    distance: float
    type: int  # 0-5 (Axial X-Z, Non-Axial X-Z)

    __slots__ = ["normal", "distance", "type"]
    _format = "4fI"
    _arrays = {"normal": [*"xyz"]}


class TextureInfo(base.Struct):  # LUMP 6
    U: List[float]
    V: List[float]
    mip_texture_index: int
    animated: int  # 0 or 1
    __slots__ = ["U", "V", "mip_texture_index", "animated"]
    _format = "8f2I"
    _arrays = {"U": [*"xyzw"], "V": [*"xyzw"]}


class Vertex(base.MappedArray):  # LUMP 3
    """a point in 3D space"""
    x: float
    y: float
    z: float
    _mapping = [*"xyz"]
    _format = "3f"


# special lump classes (alphabetical order):
class MipTextureLump:  # LUMP 2
    """Lists MipTextures and handles lookups"""
    _bytes: bytes
    _changes: Dict[int, MipTexture]

    def __init__(self, raw_lump: bytes):
        self._bytes = raw_lump
        mip_texture_count = int.from_bytes(raw_lump[:4], "little")
        self.offsets = struct.iter_unpack(f"{mip_texture_count}I")

    def __getitem__(self, index):
        if index in self._changes:
            entry = self._changes[index]
        else:
            start = self.offsets[index]
            entry_bytes = self._bytes[start: start + struct.calcsize(MipTexture._format)]
            entry = MipTexture(struct.unpack(MipTexture._format, entry_bytes))
            # TODO: map MipTexture offsets to texture data in lump
        return entry

    def as_bytes(self):
        # NOTE: this lump seems really complex, need to test on actual .bsps
        raise NotImplementedError("Haven't tested to locate texture data yet")


BASIC_LUMP_CLASSES = {"EDGES":      Edge,
                      "LEAF_FACES": shared.Shorts,
                      "SURFEDGES":  shared.Shorts}

LUMP_CLASSES = {"CLIP_NODES":   ClipNode,
                "FACES":        Face,
                "LEAVES":       Leaf,
                "MODELS":       Model,
                "NODES":        Node,
                "PLANES":       Plane,
                "TEXTURE_INFO": TextureInfo,
                "VERTICES":     Vertex}

SPECIAL_LUMP_CLASSES = {"ENTITIES":     shared.Entities,
                        "MIP_TEXTURES": MipTextureLump}


# branch exclusive methods, in alphabetical order:
def vertices_of_face(bsp, face_index: int) -> List[float]:
    raise NotImplementedError()


def vertices_of_model(bsp, model_index: int) -> List[float]:
    raise NotImplementedError()


methods = []
