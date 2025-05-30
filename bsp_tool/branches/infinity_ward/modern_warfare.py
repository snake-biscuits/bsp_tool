# https://wiki.zeroy.com/index.php?title=Call_of_Duty_4:_d3dbsp
import enum
from typing import List

from ... import core
from ...utils import geometry
from ...utils import vector
from .. import shared
from ..id_software import quake
from ..id_software import quake3
from . import call_of_duty1_demo
from . import call_of_duty2


FILE_MAGIC = b"IBSP"

BSP_VERSION = 22

GAME_PATHS = {"Call of Duty 4: Modern Warfare": "Call of Duty 4"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


# NOTE: lumps are given ids and headers reference these ids in order
class LUMP(enum.Enum):
    TEXTURES = 0x00
    LIGHTMAPS = 0x01
    LIGHT_GRID_POINTS = 0x02
    LIGHT_GRID_COLOURS = 0x03
    PLANES = 0x04
    BRUSH_SIDES = 0x05
    UNKNOWN_6 = 0x06
    UNKNOWN_7 = 0x07
    BRUSHES = 0x08
    LAYERED_TRIANGLE_SOUPS = 0x09
    LAYERED_VERTICES = 0x0A
    LAYERED_INDICES = 0x0B
    PORTAL_VERTICES = 0x13
    LAYERED_AABB_TREE = 0x18
    CELLS = 0x19
    PORTALS = 0x1A
    NODES = 0x1B
    LEAVES = 0x1C
    LEAF_BRUSHES = 0x1D
    LEAF_FACES = 0x1E
    COLLISION_VERTICES = 0x1F
    COLLISION_TRIANGLES = 0x20
    COLLISION_EDGE_WALK = 0x21
    COLLISION_BORDERS = 0x22
    COLLISION_PARTS = 0x23
    COLLISION_AABBS = 0x24
    MODELS = 0x25
    ENTITIES = 0x27
    PATHS = 0x28
    REFLECTION_PROBES = 0x29  # textures? pretty huge
    LAYERED_DATA = 0x2A
    PRIMARY_LIGHTS = 0x2B
    LIGHT_GRID_HEADER = 0x2C
    LIGHT_GRID_ROWS = 0x2D
    SIMPLE_TRIANGLE_SOUPS = 0x2F
    SIMPLE_VERTICES = 0x30
    SIMPLE_INDICES = 0x31
    SIMPLE_AABB_TREE = 0x33
    LIGHT_REGIONS = 0x34
    LIGHT_REGION_HULLS = 0x35
    LIGHT_REGION_AXES = 0x36


class LumpHeader(core.MappedArray):
    id: int  # see LUMP
    length: int
    # generated by D3DBsp._preload
    offset: int  # calculated from the sum of preceding lump's lengths (+ padding)
    name: str  # LUMP(id).name
    _mapping = ["id", "length"]
    _format = "2I"
    _classes = {"id": LUMP}


# Known lump changes from Call of Duty 2 -> Call of Duty 4:
# New:
#   LIGHT_GRID_HASHES -> LIGHT_GRID_POINTS
#   LIGHT_GRID_VALUES -> LIGHT_GRID_COLOURS
#   UNKNOWN_6
#   UNKNOWN_7
#   TRIANGLE_SOUPS -> LAYERED_TRIANGLE_SOUPS & SIMPLE_TRIANGLE_SOUPS
#   VERTICES -> LAYERED_VERTICES & SIMPLE_VERTICES
#   TRIANGLES -> LAYERED_INDICES & SIMPLE_INDICES ?
#   AABB_TREE -> LAYERED_AABB_TREE & SIMPLE_AABB_TREE
#   COLLISION_EDGES -> COLLISION_EDGE_WALK ?
#   REFLECTION_PROBES
#   LAYERED_DATA
#   PRIMARY_LIGHTS
#   LIGHT_GRID_HEADER
#   LIGHT_GRID_ROWS
#   LIGHT_REGIONS
#   LIGHT_REGION_HULLS
#   LIGHT_REGION_AXES
# Deprecated:
#   CULL_GROUPS
#   CULL_GROUP_INDICES
# NOTE: func_cull_group is still present in CoD4Radiant


# a rough map of the relationships between lumps:
# AABBTree -> TriangleSoups -> Indices -> Vertices

# LeafBrushes -> Brushes

#       /-> LayeredTriangleSoups
# Models -> Brushes
#       \-> SimpleTriangleSoups

# CollisionParts -> CollisionTriangles -> CollisionVertices
#               \-> CollisionBorders


# classes for lumps, in alphabetical order:
class AABBTree(core.Struct):  # LUMP 0x18 & 0x24
    unknown_1: int
    num_triangle_soups: int
    unknown_2: int
    __slots__ = ["unknown_1", "num_triangle_soups", "unknown_2"]
    _format = "3I"


class Cell(core.Struct):  # LUMP 0x19
    mins: vector.vec3
    maxs: vector.vec3
    unknown: bytes
    __slots__ = ["mins", "maxs", "unknown"]
    _format = "6f88s"  # 112 bytes
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}


class CollisionAABB(core.Struct):  # LUMP 0x24
    mins: vector.vec3
    maxs: vector.vec3
    unknown_1: List[int]  # (4, mostly 0)
    unknown_2: int  # CollisionPart indices?
    # TODO: test for CollisionPart triangles inside bounds
    __slots__ = ["mins", "maxs", "unknown_1", "unknown_2"]
    _format = "6f2HI"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"], "unknown_1": 2}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}


class CollisionBorder(core.Struct):  # LUMP 0x22
    unknown: bytes  # compressed bits? BevelIndices?
    __slots__ = ["unknown"]
    _format = "28s"


class CollisionPart(core.Struct):  # LUMP 0x23
    unknown: int  # always 0 so far
    num_triangles: int
    num_borders: int
    first_triangle: int  # index into CollisionTriangles
    first_border: int  # index into CollisionBorders
    __slots__ = ["unknown", "num_triangles", "num_borders", "first_triangle", "first_border"]
    _format = "H2B2I"


class Leaf(core.Struct):  # LUMP 0x1C
    unknown: List[int]
    __slots__ = ["unknown"]
    _format = "6i"
    _arrays = {"unknown": 6}


class Model(core.Struct):  # LUMP 0x25
    mins: vector.vec3
    maxs: vector.vec3
    first_triangle_soup: List[int]
    # first_triangle_soup.layered: int
    # first_triangle_soup.simple: int
    num_triangle_soups: List[int]
    # num_triangle_soups.layered: int
    # num_triangle_soups.simple: int
    # NOTE: can't determine order because lengths are the same
    unknown: List[int]  # 0 in all test maps, need more .d3dbsp
    first_brush: int
    num_brushes: int
    __slots__ = [
        "mins", "maxs",
        "first_triangle_soup", "num_triangle_soups",
        "unknown", "first_brush", "num_brushes"]
    _format = "6f4H4I"  # 48 bytes
    _arrays = {
        "mins": [*"xyz"], "maxs": [*"xyz"],
        "first_triangle_soup": ["layered", "simple"],
        "num_triangle_soups": ["layered", "simple"],
        "unknown": 2}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}


class Node(core.Struct):  # LUMP 0x1B
    unknown: List[int]
    __slots__ = ["unknown"]
    _format = "9i"
    _arrays = {"unknown": 9}


class TriangleSoup(core.Struct):  # LUMP 0x09 & 0x2F
    # TODO: texture indices
    unknown: bytes
    first_vertex: int  # index into Layered / Simple Vertices
    num_vertices: int
    num_indices: int
    first_index: int  # index into Layered / Simple Indices
    __slots__ = [
        "unknown",
        "first_vertex", "num_vertices", "num_indices", "first_index"]
    _format = "12sI2HI"


# {"LUMP_NAME": LumpClass}
BASIC_LUMP_CLASSES = {
    "LAYERED_INDICES":   shared.UnsignedShorts,
    "LEAF_BRUSHES":      shared.UnsignedInts,
    "LIGHT_GRID_HEADER": shared.UnsignedShorts,
    "LIGHT_GRID_POINTS": shared.UnsignedInts,
    "LIGHT_REGIONS":     shared.UnsignedBytes,
    "SIMPLE_INDICES":    shared.UnsignedShorts}

LUMP_CLASSES = {
    "BRUSHES":                call_of_duty1_demo.Brush,
    "BRUSH_SIDES":            call_of_duty1_demo.BrushSide,
    "CELLS":                  Cell,
    "COLLISION_AABBS":        CollisionAABB,
    "COLLISION_BORDERS":      CollisionBorder,
    "COLLISION_PARTS":        CollisionPart,
    "COLLISION_TRIANGLES":    call_of_duty2.Triangle,
    "COLLISION_VERTICES":     quake.Vertex,
    "LAYERED_AABB_TREE":      AABBTree,
    "LAYERED_TRIANGLE_SOUPS": TriangleSoup,
    "LAYERED_VERTICES":       call_of_duty2.Vertex,
    "LEAVES":                 Leaf,
    "MODELS":                 Model,
    "NODES":                  Node,
    "PLANES":                 quake3.Plane,
    "TEXTURES":               quake3.Texture,
    "SIMPLE_AABB_TREE":       AABBTree,
    "SIMPLE_TRIANGLE_SOUPS":  TriangleSoup,
    "SIMPLE_VERTICES":        call_of_duty2.Vertex}

SPECIAL_LUMP_CLASSES = {
    "ENTITIES": shared.Entities}


# methods for interfacing with lumps from this branch:
def collision_part_mesh(bsp, collision_part_index: int) -> geometry.Mesh:
    collision_part = bsp.COLLISION_PARTS[collision_part_index]
    start, length = collision_part.first_triangle, collision_part.num_triangles
    no_normal = vector.vec3(0, 0, 0)
    triangles = [
        [
            geometry.Vertex(bsp.COLLISION_VERTICES[i], no_normal)
            for i in triangle]
        for triangle in bsp.COLLISION_TRIANGLES[start:start + length]]
    return geometry.Mesh(polygons=[*map(geometry.Polygon, triangles)])


def layered_triangle_soup_mesh(bsp, layered_triangle_soup_index: int) -> geometry.Mesh:
    triangle_soup = bsp.LAYERED_TRIANGLE_SOUPS[layered_triangle_soup_index]
    # material
    # texture = bsp.TEXTURES[triangle_soup.texture]  # not found yet
    # material_name = texture.name.split(b"\0")[0].decode()
    material = geometry.Material("unknown")
    # geometry
    start, length = triangle_soup.first_vertex, triangle_soup.num_vertices
    vertices = bsp.LAYERED_VERTICES[start:start + length]
    vertices = [
        geometry.Vertex(
            vertex.position,
            vertex.normal,
            vertex.albedo_uv,
            vertex.lightmap_uv,
            colour=vertex.colour.as_floats())
        for vertex in vertices]
    start, length = triangle_soup.first_index, triangle_soup.num_indices
    indices = bsp.LAYERED_INDICES[start:start + length]
    return geometry.Mesh(
        material,
        geometry.triangle_soup([
            vertices[i]
            for i in indices]))


def simple_triangle_soup_mesh(bsp, simple_triangle_soup_index: int) -> geometry.Mesh:
    triangle_soup = bsp.LAYERED_TRIANGLE_SOUPS[simple_triangle_soup_index]
    # material
    # texture = bsp.TEXTURES[triangle_soup.texture]  # not found yet
    # material_name = texture.name.split(b"\0")[0].decode()
    material = geometry.Material("unknown")
    # geometry
    start, length = triangle_soup.first_vertex, triangle_soup.num_vertices
    vertices = bsp.SIMPLE_VERTICES[start:start + length]
    vertices = [
        geometry.Vertex(
            vertex.position,
            vertex.normal,
            vertex.albedo_uv,
            vertex.lightmap_uv,
            colour=vertex.colour.as_floats())
        for vertex in vertices]
    start, length = triangle_soup.first_index, triangle_soup.num_indices
    indices = bsp.SIMPLE_INDICES[start:start + length]
    return geometry.Mesh(
        material,
        geometry.triangle_soup([
            vertices[i]
            for i in indices]))


# NOTE: no mins & maxs in worldspawn?
methods = [
    call_of_duty1_demo.brush, collision_part_mesh,
    layered_triangle_soup_mesh, simple_triangle_soup_mesh]
methods = {method.__name__: method for method in methods}
