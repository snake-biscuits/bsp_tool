# https://wiki.zeroy.com/index.php?title=Call_of_Duty_1:_d3dbsp
import enum
import struct
from typing import List

from ...utils import editor
from ...utils import physics
from ...utils import vector
from .. import base
from .. import shared
from ..id_software import quake
from ..id_software import quake3  # CoD1 was built on RTCW


FILE_MAGIC = b"IBSP"

BSP_VERSION = 58

GAME_PATHS = {"Call of Duty (Demo) Burnville": "Call of Duty Single Player Demo",
              "Call of Duty (Demo) Dawnville": "Call of Duty Dawnville Demo"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    TEXTURES = 0
    LIGHTMAPS = 1
    PLANES = 2
    BRUSH_SIDES = 3
    BRUSHES = 4
    TRIANGLE_SOUPS = 6
    VERTICES = 7
    INDICES = 8
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
    LEAF_FACES = 23
    PATCH_COLLISION = 24
    COLLISION_VERTICES = 25
    COLLISION_INDICES = 26
    MODELS = 27
    VISIBILITY = 28
    ENTITIES = 29
    LIGHTS = 30
    UNKNOWN_31 = 31  # EFFECTS / FOGS ?
    # big "32nd lump" at end of file, not in header?


LumpHeader = quake.LumpHeader


# TODO: known lump changes from Quake 3 -> CoD 1:


# TODO: a rough map of the relationships between lumps:


# flag enums:
class LightType(enum.Enum):  # Light.type
    # NOTE: sun is baked into LightGrid (6 sp maps have no lights)
    INVALID = 0x00  # required for Light.__init__ with 0 arguments
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
    # NOTE: first_side is calculated via: sum([b.num_sides for b in bsp.BRUSHES[-i]]) - 1
    num_sides: int  # number of BrushSides after first_side in this Brush
    texture: int  # index of Texture that sets this Brush's Contents flag
    _mapping = ["num_sides", "texture"]
    _format = "2H"


class BrushSide(base.Struct):  # LUMP 3
    plane: int  # axial: Plane distance (float), non-axial: Plane index (uint32_t)
    texture: int  # index into Textures
    __slots__ = ["plane", "texture"]
    _format = "2I"


class Cell(base.Struct):  # LUMP 17
    mins: vector.vec3
    maxs: vector.vec3
    unknown_1: int  # increments w/ each cell
    first_portal: int
    num_portals: int
    unknown_2: bytes
    __slots__ = ["mins", "maxs", "unknown_1", "first_portal", "num_portals", "unknown_2"]
    _format = "6f3I16s"  # 52 bytes
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}


class CullGroup(base.Struct):  # LUMP 9
    # indices & aabb tree stuff?
    unknown: List[int]
    __slots__ = ["unknown"]
    _format = "8i"
    _arrays = {"unknown": 8}


class Leaf(base.Struct):  # LUMP 21
    unknown_1: List[int]
    first_leaf_brush: int  # index of first LeafBrush in this Leaf
    num_leaf_brushes: int  # number of LeafBrushes after first_leaf_brush in this Leaf
    unknown_2: List[int]
    # LeafFace indices are probably in here somewhere...
    __slots__ = ["unknown_1", "first_leaf_brush", "num_leaf_brush", "unknown_2"]
    _format = "9i"
    _arrays = {"unknown_1": 4, "unknown_2": 3}


class Light(base.Struct):  # LUMP 30
    type: LightType
    unknown_1: List[float]  # big floats
    origin: List[float]  # seems legit
    vector: List[float]  # magnitude of ~1.0 if a directional type
    unknown_2: List[float]
    unknown_3: List[int]  # indices into other lumps?
    __slots__ = ["type", "unknown_1", "origin", "vector", "unknown_2", "unknown_3"]
    _format = "i12f5i"
    _arrays = {"unknown_1": 3, "origin": [*"xyz"], "vector": [*"xyz"], "unknown_2": 3, "unknown_3": 5}
    _classes = {"type": LightType, "origin": vector.vec3, "vector": vector.vec3}


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
    mins: vector.vec3
    maxs: vector.vec3
    first_face: int  # index into Face lump
    num_faces: int  # number of Faces after first_face included in this Model
    first_brush: int  # index into Brush lump
    num_brushes: int  # number of Brushes after first_brush included in this Model
    unknown: List[int]
    __slots__ = ["mins", "maxs", "first_face", "num_faces", "first_brush", "num_brushes", "unknown"]
    _format = "6f6i"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"], "unknown": 2}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}


class Occluder(base.Struct):  # LUMP 12
    first_occluder_plane: int  # index into the OccluderPlane lump
    num_occluder_planes: int   # number of OccluderPlanes after first_occluder_plane in this Occluder
    first_occluder_edges: int  # index into the OccluderEdge lump
    num_occluder_edges: int    # number of OccluderEdges after first_occluder_edge in this Occluder
    __slots__ = ["first_occluder_plane", "num_occluder_planes", "first_occluder_edge", "num_occluder_edges"]
    _format = "4i"


class PatchCollision(base.Struct):  # LUMP 24
    """'Patches' are the CoD version of Source's Displacements (think of a fabric patch on torn clothes)"""
    unknown: List[int]
    __slots__ = ["unknown"]
    _format = "16b"
    _arrays = {"unknown": 16}


class Portal(base.Struct):  # LUMP 18
    plane: int  # index of Plane this portal lies on
    cell: int  # index into Cells
    first_portal_vertex: int  # index into PortalVertices
    num_portal_vertices: int
    __slots__ = ["plane", "cell", "first_portal_vertex", "num_portal_vertices"]
    _format = "4i"


class TriangleSoup(base.MappedArray):  # LUMP 5
    texture: int  # index into Textures?
    draw_order: int  # ?
    first_vertex: int
    num_vertices: int
    first_triangle: int  # index into Indices?
    num_triangles: int
    _mapping = ["texture", "draw_order", "first_vertex", "num_vertices",
                "first_triangle", "num_triangles"]
    _format = "2HI2HI"


class Vertex(base.Struct):  # LUMP 7
    # position, uv0 (albedo), uv1 (lightmap), colour etc.
    unknown: List[int]
    __slots__ = ["unknown"]
    _format = "11i"
    _arrays = {"unknown": 11}


# {"LUMP_NAME": LumpClass}
BASIC_LUMP_CLASSES = {"COLLISION_INDICES":  shared.UnsignedShorts,
                      "CULL_GROUP_INDICES": shared.UnsignedInts,
                      "INDICES":            shared.UnsignedShorts,
                      "LEAF_BRUSHES":       shared.UnsignedInts,
                      "LEAF_FACES":         shared.UnsignedInts,
                      "LIGHT_INDICES":      shared.UnsignedShorts,
                      "OCCLUDER_INDICES":   shared.UnsignedShorts,
                      "OCCLUDER_PLANES":    shared.UnsignedInts}

LUMP_CLASSES = {
                # "AABB_TREES":         AxisAlignedBoundingBox,
                "BRUSHES":            Brush,
                "BRUSH_SIDES":        BrushSide,
                "CELLS":              Cell,
                # "COLLISION_VERTICES": quake.Vertex,
                # "CULL_GROUPS":        CullGroup,
                # "VERTICES":           Vertex,
                "LEAVES":             Leaf,
                "LIGHTS":             Light,
                "LIGHTMAPS":          Lightmap,
                # "MODELS":             Model,
                "NODES":              quake3.Node,
                # "OCCLUDERS":          Occluder,
                "OCCLUDER_EDGES":     quake.Edge,
                # "PATCH_COLLISION":    PatchCollision,
                "PLANES":             quake3.Plane,
                "PORTALS":            Portal,
                "TEXTURES":           quake3.Texture,
                "TRIANGLE_SOUPS":     TriangleSoup}

SPECIAL_LUMP_CLASSES = {"ENTITIES": shared.Entities}


def brush(bsp, brush_index) -> editor.Brush:
    # NOTE: generates a generic TextureVector
    first_side = sum(b.num_sides for b in bsp.BRUSHES[:brush_index])
    brush = bsp.BRUSHES[brush_index]
    assert brush.num_sides >= 6
    sides = bsp.BRUSH_SIDES[first_side:first_side + brush.num_sides]

    def int_as_float(x: int) -> float:
        return struct.unpack("f", x.to_bytes(4, "little"))[0]

    def texture_name(side: BrushSide) -> str:
        return bsp.TEXTURES[side.texture].name.decode().split("\x00")[0]

    out = list()  # axial: -X +X -Y +Y -Z +Z; non-axial: w/e
    for (axis, sign), side in zip([(a, s) for a in "xyz" for s in (-1, 1)], sides[:6]):
        plane = physics.Plane(vector.vec3(**{axis: sign}), int_as_float(side.plane) * sign)
        out.append(editor.BrushSide(plane, texture_name(side)))
    out.extend([editor.BrushSide(bsp.PLANES[side.plane], texture_name(side)) for side in sides[6:]])
    return editor.Brush(out)


def portal_file(bsp) -> str:
    out = ["PRT1", str(len(bsp.CELLS)), str(len(bsp.PORTALS))]
    for ci, cell in enumerate(bsp.CELLS):
        start, length = cell.first_portal, cell.num_portals
        for pi in enumerate(start, start + length):
            portal = bsp.PORTALS[pi]
            start, length = portal.first_portal_vertex, portal.num_portal_vertices
            winding = bsp.PORTAL_VERTICES[start:start + length]
            out.append(" ".join([f"{len(winding)} {ci} {portal.cell}", *[f"({v.x} {v.y} {v.z})" for v in winding]]))
    return "\n".join(out)


methods = [quake.leaves_of_node, shared.worldspawn_volume, brush, portal_file]
methods = {m.__name__: m for m in methods}
