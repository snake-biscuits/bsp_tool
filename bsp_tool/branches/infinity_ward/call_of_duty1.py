# https://wiki.zeroy.com/index.php?title=Call_of_Duty_1:_d3dbsp
import enum
from typing import List

from .. import base
from .. import shared  # special lumps


BSP_VERSION = 0x00  # !!! UNKNOWN !!!


class LUMP(enum.Enum):
    SHADERS = 0
    LIGHTMAPS = 1
    PLANES = 2
    BRUSH_SIDES = 3
    BRUSHES = 4
    TRIANGLE_SOUPS = 6  # mmm tasty
    DRAW_VERTICES = 7
    DRAW_INDICES = 8
    CULL_GROUPS = 9  # visibility
    CULL_GROUP_INDICES = 10
    PORTAL_VERTS = 11  # areaportals; doors & windows
    OCCLUDERS = 12
    OCCLUDER_PLANES = 13
    OCCLUDER_EDGES = 14
    OCCLUDER_INDICES = 15
    AABB_TREES = 16  # Physics? or Vis Nodes?
    CELLS = 17
    PORTALS = 18
    LIGHT_INDICES = 19
    NODES = 20
    LEAVES = 21
    LEAF_BRUSHES = 22
    LEAF_SURFACES = 23
    PATCH_COLISION = 24  # decal clipping? reference for painting bullet holes?
    COLLISION_VERTICES = 25
    COLLISION_INDICES = 26
    MODELS = 27
    VISIBILITY = 28  # SPECIAL: Binary Partition tree (read bit by bit, with masks?)
    ENTITIES = 29  # SPECIAL: string (typically ENTITIES would be #0)
    LIGHTS = 30
    UNKNOWN_31 = 31  # FOGS ?
    # big 32nd lump at ed of file, not in header?
    # likely a zip / pakfile
    # checking for file-magic would confirm this


lump_header_address = {LUMP_ID: (8 + i * 8) for i, LUMP_ID in enumerate(LUMP)}


# classes for lumps (alphabetical order): [31 / 32] + shared.Entities
# all are incomplete guesses; only lump sizes are known
class AxisAlignedBoundingBox(base.Struct):  # LUMP 16
    """AABB tree"""
    # too small to be mins & maxs of an AABB; probably indices (hence: AABB_TREE)
    data: bytes
    __slots__ = ["data"]
    _format = "12c"  # equivalent "3i"


class Brush(base.Struct):  # LUMP 4
    first_side: int  # index into the BrushSide lump
    num_sides: int   # number of sides after first_side in this Brush
    __slots__ = ["first_side", "num_sides"]
    _format = "2i"


class BrushSide(base.Struct):  # LUMP 3
    plane: int   # index into Plane lump
    shader: int  # index into Texture lump
    __slots__ = ["plane", "shader"]
    _format = "2i"


class Cell(base.Struct):  # LUMP 17
    """No idea what this is / does"""
    data: bytes
    __slots__ = ["data"]
    _format = "52c"  # equivalent "13i"


class CollisionIndex(int):  # LUMP 26
    _format = "H"  # index into ??? lump


class CollisionVertex(base.MappedArray):  # LUMP 25
    x: float
    y: float
    z: float
    _mapping = [*"xyz"]
    _format = "3f"


class CullGroup(base.Struct):  # LUMP 9
    data: bytes
    __slots__ = ["data"]
    _format = "32c"  # equivalent "8i"


class CullGroupIndex(int):  # LUMP 10
    _format = "I"


class DrawIndex(int):  # LUMP 8
    _format = "H"


class DrawVertex(base.Struct):  # LUMP 7
    data: bytes
    __slots__ = ["data"]
    _format = "44c"  # equivalent "11f"


class Leaf(base.Struct):  # LUMP 21
    # first_leaf_brush
    # num_leaf_brushes
    data: bytes
    __slots__ = ["data"]
    _format = "36c"  # equivalent "9i"


class LeafBrush(int):  # LUMP 22
    _format = "I"  # index into Brush lump


class LeafSurface(int):  # LUMP 4
    _format = "I"  # index into Face lump ?


class Light(base.Struct):  # LUMP 30
    # attenuations, colours, strengths
    data: bytes
    __slots__ = ["data"]
    _format = "72c"  # equivalent "18i"


class LightIndex(int):  # LUMP 19
    _format = "H"  # index into Light lump


class Lightmap:  # LUMP 1
    _format = "3c" * 512 * 512  # 512x512 RGB
    # what if: base.Struct._arrays = {512: {512: [*"rgb"]}}

    def __init__(self, _tuple):
        self._pixels: List[bytes] = _tuple  # RGB_888

    def __getitem__(self, row) -> List[bytes]:  # returns 3 bytes: b"\xRR\xGG\xBB"
        # Lightmap[row][column] returns self.__getitem__(row)[column]
        row_start = row * 512
        return self._pixels[row_start:row_start + 512]  # TEST: does it work with negative indices?

    def flat(self) -> bytes:
        return b"".join(self._pixels)


class Model(base.Struct):  # LUMP 27
    mins: List[float]  # Bounding box
    maxs: List[float]
    first_face: int  # index into Face lump
    num_faces: int  # number of Faces after first_face included in this Model
    first_brush: int  # index into Brush lump
    num_brushes: int  # number of Brushes after first_brush included in this Model
    unknown: List[bytes]
    __slots__ = ["mins", "maxs", "first_face", "num_faces", "first_brush", "num_brushes", "unknown"]
    _format = "6f4i4c4c"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"], "unknown": 2}


class Node(base.Struct):  # LUMP 20
    data: bytes
    __slots__ = ["data"]
    _format = "36c"


class Occluder(base.Struct):  # LUMP 12
    first_occluder_plane: int  # index into the OccluderPlane lump
    num_occluder_planes: int   # number of OccluderPlanes after first_occluder_plane in this Occluder
    first_occluder_edges: int  # index into the OccluderEdge lump
    num_occluder_edges: int    # number of OccluderEdges after first_occluder_edge in this Occluder
    __slots__ = ["first_occluder_plane", "num_occluder_planes", "first_occluder_edge", "num_occluder_edges"]
    _format = "4i"


class OccluderEdge(int):  # LUMP 14
    _format = "I"  # index into the ??? lump


class OccluderIndex(int):  # LUMP 15
    _format = "H"  # index into the Occluder lump


class OccluderPlane(int):  # LUMP 13
    _format = "I"  # index into Plane lump


class PatchCollision(base.Struct):  # LUMP 24
    data: bytes
    __slots__ = ["data"]
    _format = "16c"  # equivalent 4i


class Plane(base.Struct):  # LUMP 2
    normal: List[float]
    distance: float
    __slots__ = ["normal", "distance"]
    _format = "4f"
    _arrays = {"normal": [*"xyz"]}


class Portal(base.Struct):  # LUMP 18
    data: bytes
    __slots__ = ["data"]
    _format = "16c"  # equivalent "4i"


class Shader(base.Struct):  # LUMP 0
    data: bytes
    __slots__ = ["data"]
    _format = "72c"  # equivelent "18i"


class TriangleSoup(base.Struct):  # LUMP 5
    data: bytes
    __slots__ = ["data"]
    _format = "16c"  # equivalent "4i"


LUMP_CLASSES = {"AABB_TREES": AxisAlignedBoundingBox,
                "BRUSHES": Brush,
                "BRUSH_SIDES": BrushSide,
                "CELLS": Cell,
                "COLLISION_INDICES": CollisionIndex,
                "COLLISION_VERTICES": CollisionVertex,
                "CULL_GROUPS": CullGroup,
                "CULL_GROUP_INDICES": CullGroupIndex,
                "DRAW_INDICES": DrawIndex,
                "DRAW_VERTICES": DrawVertex,
                "LEAVES": Leaf,
                "LEAF_BRUSHES": LeafBrush,
                "LEAF_SURFACES": LeafSurface,
                "LIGHTS": Light,
                "LIGHT_INDICES": LightIndex,
                "LIGHTMAPS": Lightmap,
                "MODELS": Model,
                "NODES": Node,
                "OCCLUDERS": Occluder,
                "OCCLUDER_EDGES": OccluderEdge,
                "OCCLUDER_INDICES": OccluderIndex,
                "OCCLUDER_PLANES": OccluderPlane,
                "PATCH_COLISION": PatchCollision,
                "PLANES": Plane,
                "PORTALS": Portal,
                "SHADERS": Shader,
                "TRIANGLE_SOUPS": TriangleSoup}  # mmm tasty

SPECIAL_LUMP_CLASSES = {"ENTITIES": shared.Entities}

methods = []
