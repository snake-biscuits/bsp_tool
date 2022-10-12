# https://wiki.zeroy.com/index.php?title=Call_of_Duty_1:_d3dbsp
import enum
from typing import List

from .. import base
from .. import shared
from ..id_software import quake
# from ..id_software import quake3  # RTCW based


FILE_MAGIC = b"IBSP"

BSP_VERSION = 59

GAME_PATHS = {"Call of Duty": "Call of Duty",
              "Call of Duty: United Offensive": "Call of Duty"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    SHADERS = 0
    LIGHTMAPS = 1
    PLANES = 2
    BRUSH_SIDES = 3
    BRUSHES = 4
    TRIANGLE_SOUPS = 6
    DRAW_VERTICES = 7
    DRAW_INDICES = 8
    CULL_GROUPS = 9
    CULL_GROUP_INDICES = 10
    PORTAL_VERTICES = 11
    OCCLUDERS = 12
    OCCLUDER_PLANES = 13
    OCCLUDER_EDGES = 14
    OCCLUDER_INDICES = 15
    AABB_TREES = 16
    CELLS = 17
    PORTALS = 18
    LIGHT_INDICES = 19
    NODES = 20
    LEAVES = 21
    LEAF_BRUSHES = 22
    LEAF_SURFACES = 23
    PATCH_COLLISION = 24
    COLLISION_VERTICES = 25
    COLLISION_INDICES = 26
    MODELS = 27
    VISIBILITY = 28
    ENTITIES = 29
    LIGHTS = 30
    UNKNOWN_31 = 31  # FOGS ?
    # big "32nd lump" at end of file, not in header?


class LumpHeader(base.MappedArray):
    _mapping = ["length", "offset"]
    _format = "2I"


# flag enums
class LightType(enum.Enum):  # Light.type
    # NOTE: sun is baked into light volumes (6 sp maps have no lights)
    DIRECTIONAL_1 = 0x01
    UNKNOWN_2 = 0x02
    DIRECTIONLESS_4 = 0x04
    UNKNOWN_5 = 0x05
    DIRECTIONAL_7 = 0x07


# classes for lumps, in alphabetical order:
# NOTE: haven't properly identified the formats for a lot of these yet
class AxisAlignedBoundingBox(base.Struct):  # LUMP 16
    """AABB tree"""
    # not floats. some kind of node indices?
    unknown: List[int]
    __slots__ = ["unknown"]
    _format = "3I"
    _arrays = {"unknown": 3}


class Brush(base.MappedArray):  # LUMP 6
    # NOTE: first side is calculated via: sum([b.num_sides for b in bsp.BRUSHES[-i]]) - 1
    num_sides: int
    material_id: int  # Brush's overall contents flag?
    _mapping = ["num_sides", "material_id"]
    _format = "2H"


class BrushSide(base.Struct):  # LUMP 3
    plane: int   # index into Plane lump
    # NOTE: in some cases the plane index is a distance instead (float)
    # "first 6 entries indicated by an entry in lump 6 [brushes] are distances (float), rest is plane ID's"
    shader: int  # index into Texture lump
    __slots__ = ["plane", "shader"]
    _format = "2I"


class Cell(base.Struct):  # LUMP 17
    """No idea what this is / does"""
    unknown: List[int]
    __slots__ = ["unknown"]
    _format = "13i"


class CullGroup(base.Struct):  # LUMP 9
    # indices & aabb tree stuff?
    unknown: List[int]
    __slots__ = ["unknown"]
    _format = "8i"


class DrawVertex(base.Struct):  # LUMP 7
    # position, uv0 (albedo), uv1 (lightmap), colour etc.
    unknown: List[int]
    __slots__ = ["unknown"]
    _format = "11i"
    _arryas = {"unknown": 11}


class Leaf(base.Struct):  # LUMP 21
    unknown_1: List[int]
    first_leaf_brush: int
    num_leaf_brushes: int
    unknown_2: List[int]
    __slots__ = ["unknown_1", "first_leaf_brush", "num_leaf_brush", "unknown_2"]
    _format = "9i"
    _arrays = {"unknown_1": 4, "unknown_2": 3}


class Light(base.Struct):  # LUMP 30
    type: int  # see LightType
    unknown_1: List[float]  # big floats
    origin: List[float]  # seems legit
    vector: List[float]  # magnitude of ~1.0 if a directional type
    unknown_2: List[float]
    unknown_3: List[int]  # indices into other lumps?
    __slots__ = ["type", "unknown_1", "origin", "vector", "unknown_2", "unknown_3"]
    _format = "i12f5i"
    _arrays = {"unknown_1": 3, "origin": [*"xyz"], "vector": [*"xyz"], "unknown_2": 3, "unknown_3": 5}


class Lightmap(list):  # LUMP 1
    """Raw pixel bytes, 512x512 RGB_888 image"""
    _pixels: List[bytes] = [b"\0" * 3] * 512 * 512
    _format = "3s" * 512 * 512  # 512x512 RGB_888

    def __getitem__(self, row) -> bytes:
        r"""returns 3 bytes: b'\xRR\xGG\xBB'"""
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


class Model(base.Struct):  # LUMP 27
    mins: List[float]  # Bounding box
    maxs: List[float]
    first_face: int  # index into Face lump
    num_faces: int  # number of Faces after first_face included in this Model
    first_brush: int  # index into Brush lump
    num_brushes: int  # number of Brushes after first_brush included in this Model
    unknown: List[int]
    __slots__ = ["mins", "maxs", "first_face", "num_faces", "first_brush", "num_brushes", "unknown"]
    _format = "6f6i"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"], "unknown": 2}


class Node(base.Struct):  # LUMP 20
    plane: int  # index of Plane that splits this Node
    children: List[int]  # likely -ve for Leaves
    # bounds
    mins: List[int]
    maxs: List[int]
    __slots__ = ["plane", "children", "mins", "maxs"]
    _format = "9i"
    _arrays = {"children": 2, "mins": [*"xyz"], "maxs": [*"xyz"]}


class Occluder(base.Struct):  # LUMP 12
    first_occluder_plane: int  # index into the OccluderPlane lump
    num_occluder_planes: int   # number of OccluderPlanes after first_occluder_plane in this Occluder
    first_occluder_edges: int  # index into the OccluderEdge lump
    num_occluder_edges: int    # number of OccluderEdges after first_occluder_edge in this Occluder
    # first, num? isn't it usually the opposite? interesting
    __slots__ = ["first_occluder_plane", "num_occluder_planes", "first_occluder_edge", "num_occluder_edges"]
    _format = "4i"


class PatchCollision(base.Struct):  # LUMP 24
    """'Patches' are the CoD version of Source's Displacements (think of a fabric patch on torn clothes)"""
    unknown: List[int]
    __slots__ = ["unknown"]
    _format = "16b"
    _arrays = {"unknown": 16}


class Plane(base.Struct):  # LUMP 2
    normal: List[float]
    distance: float
    __slots__ = ["normal", "distance"]
    _format = "4f"
    _arrays = {"normal": [*"xyz"]}


class Portal(base.Struct):  # LUMP 18
    unknown: List[int]
    __slots__ = ["unknown"]
    _format = "4i"
    _arrays = {"unknown": 4}


class Shader(base.Struct):  # LUMP 0
    """possibly based on Quake3 Texture LumpClass"""
    texture: str
    flags: List[int]
    __slots__ = ["texture", "flags"]
    _format = "64s2i"
    _arrays = {"flags": ["surface", "contents"]}


class TriangleSoup(base.MappedArray):  # LUMP 5
    material: int
    draw_order: int  # ?
    first_vertex: int
    num_vertices: int
    first_triangle: int
    num_triangles: int
    _mapping = ["material", "draw_order", "first_vertex", "num_vertices",
                "first_triangle", "num_triangles"]
    _format = "2HI2HI"


# {"LUMP_NAME": LumpClass}
BASIC_LUMP_CLASSES = {"COLLISION_INDICES":  shared.UnsignedShorts,
                      "CULL_GROUP_INDICES": shared.UnsignedInts,
                      "DRAW_INDICES":       shared.UnsignedShorts,
                      "LEAF_BRUSHES":       shared.UnsignedInts,
                      "LEAF_SURFACES":      shared.UnsignedInts,
                      "LIGHT_INDICES":      shared.UnsignedShorts,
                      "OCCLUDER_INDICES":   shared.UnsignedShorts,
                      "OCCLUDER_PLANES":    shared.UnsignedInts}

LUMP_CLASSES = {
                # "AABB_TREES":         AxisAlignedBoundingBox,
                # "BRUSHES":            Brush,
                "BRUSH_SIDES":        BrushSide,
                # "CELLS":              Cell,
                # "COLLISION_VERTICES": quake.Vertex,
                # "CULL_GROUPS":        CullGroup,
                # "DRAW_VERTICES":      DrawVertex,
                "LEAVES":             Leaf,
                "LIGHTS":             Light,
                "LIGHTMAPS":          Lightmap,
                # "MODELS":             Model,
                "NODES":              Node,
                # "OCCLUDERS":          Occluder,
                "OCCLUDER_EDGES":     quake.Edge,
                # "PATCH_COLLISION":    PatchCollision,
                "PLANES":             Plane,
                "PORTALS":            Portal,
                "SHADERS":            Shader,
                "TRIANGLE_SOUPS":     TriangleSoup}

SPECIAL_LUMP_CLASSES = {"ENTITIES": shared.Entities}


methods = [shared.worldspawn_volume]
