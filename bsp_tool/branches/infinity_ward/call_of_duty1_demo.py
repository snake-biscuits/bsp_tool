# https://wiki.zeroy.com/index.php?title=Call_of_Duty_1:_d3dbsp
import enum
import struct
from typing import List

from ... import core
from ...utils import editor
from ...utils import geometry
from ...utils import physics
from ...utils import vector
from .. import colour
from .. import shared
from ..id_software import quake
from ..id_software import quake3  # CoD1 was built on RTCW


FILE_MAGIC = b"IBSP"

BSP_VERSION = 58

GAME_PATHS = {
    "Call of Duty (Demo) Burnville": "Call of Duty Single Player Demo",
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


# TODO: known lump changes from Quake 3 -> CoD 1 Demo:


# TODO: a rough map of the relationships between lumps:
#                    /-> Texture
# Brush -> BrushSides -> Plane
#      \-> Texture

# Cell -> Portals
#     \-> CullGroupIndices

#       /-> Plane
# Portal -> Cell
#       \-> PortalVertices

#      /-> TriangleSoups
# Model -> LeafFaces -> PatchCollision
#      \-> Brushes -> BrushSides

# Leaf -> LeafFaces -> PatchCollision
#     \-> LeafBrushes -> Brushes -> BrushSides

# PatchCollision -> CollisionVertices
#               \-> CollisionIndices


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
class AxisAlignedBoundingBox(core.Struct):  # LUMP 16
    """AABB tree"""
    # not floats. some kind of node indices?
    unknown: List[int]
    __slots__ = ["unknown"]
    _format = "3I"
    _arrays = {"unknown": 3}


class Brush(core.MappedArray):  # LUMP 6
    # NOTE: first_side is calculated via: sum([b.num_sides for b in bsp.BRUSHES[-i]]) - 1
    num_sides: int  # number of BrushSides after first_side in this Brush
    texture: int  # index of Texture that sets this Brush's Contents flag
    _mapping = ["num_sides", "texture"]
    _format = "2H"


class BrushSide(core.Struct):  # LUMP 3
    plane: int  # axial: Plane distance (float), non-axial: Plane index (uint32_t)
    texture: int  # index into Textures
    __slots__ = ["plane", "texture"]
    _format = "2I"


class Cell(core.Struct):  # LUMP 17
    mins: vector.vec3
    maxs: vector.vec3
    unknown_1: int  # increments w/ each cell
    first_portal: int  # index into Portals
    num_portals: int
    first_cull_group_index: int  # index into CullGroupIndices
    num_cull_group_indices: int
    unknown_2: bytes
    __slots__ = [
        "mins", "maxs", "unknown_1", "first_portal", "num_portals",
        "first_cull_group_index", "num_cull_group_indices", "unknown_2"]
    _format = "6f5I8s"  # 52 bytes
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}


class CullGroup(core.Struct):  # LUMP 9
    mins: vector.vec3
    maxs: vector.vec3
    first_unknown: int  # index into ??? (renderables?)
    num_unknowns: int
    __slots__ = ["mins", "maxs", "first_unknown", "num_unknowns"]
    _format = "6f2i"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}


class Leaf(core.Struct):  # LUMP 21
    unknown_1: List[int]
    first_leaf_face: int  # index into Leaf Brushes
    num_leaf_faces: int
    first_leaf_brush: int  # index into Leaf Brushes
    num_leaf_brushes: int
    unknown_2: List[int]
    __slots__ = [
        "unknown_1", "first_leaf_face", "num_leaf_faces",
        "first_leaf_brush", "num_leaf_brushes", "unknown_2"]
    _format = "9i"
    _arrays = {"unknown_1": 2, "unknown_2": 3}


class Light(core.Struct):  # LUMP 30
    type: LightType
    unknown_1: List[float]  # big floats
    origin: vector.vec3
    vector: vector.vec3  # magnitude of ~1.0 if a directional type
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


class Model(core.Struct):  # LUMP 27
    mins: vector.vec3
    maxs: vector.vec3
    first_triangle_soup: int  # index into TriangleSoups
    num_triangle_soups: int
    first_leaf_face: int  # index into LeafFaces
    num_leaf_faces: int
    first_brush: int  # index into Brushes
    num_brushes: int
    __slots__ = [
        "mins", "maxs", "first_triangle_soup", "num_triangle_soups",
        "first_leaf_face", "num_leaf_faces", "first_brush", "num_brushes"]
    _format = "6f6i"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}


class Occluder(core.Struct):  # LUMP 12
    first_occluder_plane: int  # index into OccluderPlanes
    num_occluder_planes: int
    first_occluder_edges: int  # index into OccluderEdges
    num_occluder_edges: int
    __slots__ = ["first_occluder_plane", "num_occluder_planes", "first_occluder_edge", "num_occluder_edges"]
    _format = "4i"


class PatchCollision(core.Struct):  # LUMP 24
    """for Terrain, like Source Displacements"""
    unknown_1: int  # flags?
    num_vertices: int
    num_indices: int
    first_vertex: int  # index into CollisionVertices
    first_index: int  # index into CollisionIndices
    # NOTE: indices go out of bounds sometimes, and don't account for the whole lump
    # -- so could be incorrect, but PatchCollision early in the lump seem to work OK
    __slots__ = ["unknown_1", "num_vertices", "num_indices", "first_vertex", "first_index"]
    _format = "I2h2I"


class Portal(core.Struct):  # LUMP 18
    plane: int  # index of Plane this portal lies on
    cell: int  # index into Cells
    first_portal_vertex: int  # index into PortalVertices
    num_portal_vertices: int
    __slots__ = ["plane", "cell", "first_portal_vertex", "num_portal_vertices"]
    _format = "4i"


class TriangleSoup(core.Struct):  # LUMP 5
    texture: int  # index into Textures
    draw_order: int  # priority?
    first_vertex: int  # index into Vertices
    num_vertices: int
    num_indices: int  # should always be a multiple of 3
    first_index: int  # index into Indices
    __slots__ = ["texture", "draw_order", "first_vertex", "num_vertices", "num_indices", "first_index"]
    _format = "2HI2HI"


class Vertex(core.Struct):  # LUMP 7
    position: vector.vec3
    albedo_uv: vector.vec2
    lightmap_uv: vector.vec2
    position: vector.vec3
    colour: colour.RGBA32
    __slots__ = ["position", "albedo_uv", "lightmap_uv", "normal", "colour"]
    _format = "10f4b"
    _arrays = {
        "position": [*"xyz"],
        "albedo_uv": [*"xy"], "lightmap_uv": [*"xy"],
        "normal": [*"xyz"], "colour": [*"rgba"]}
    _classes = {
        "position": vector.vec3,
        "albedo_uv": vector.vec2, "lightmap_uv": vector.vec2,
        "normal": vector.vec3, "colour": colour.RGBA32}


# {"LUMP_NAME": LumpClass}
BASIC_LUMP_CLASSES = {
    "COLLISION_INDICES":  shared.UnsignedShorts,
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
    "COLLISION_VERTICES": quake.Vertex,
    "CULL_GROUPS":        CullGroup,
    "VERTICES":           Vertex,
    "LEAVES":             Leaf,
    "LIGHTS":             Light,
    "LIGHTMAPS":          Lightmap,
    "MODELS":             Model,
    "NODES":              quake3.Node,
    # "OCCLUDERS":          Occluder,
    "OCCLUDER_EDGES":     quake.Edge,
    "PATCH_COLLISION":    PatchCollision,
    "PLANES":             quake3.Plane,
    "PORTALS":            Portal,
    "TEXTURES":           quake3.Texture,
    "TRIANGLE_SOUPS":     TriangleSoup}

SPECIAL_LUMP_CLASSES = {
    "ENTITIES": shared.Entities}


# methods for interfacing with lumps from this branch:
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

    out = list()
    # axial sides (-X +X -Y +Y -Z +Z order)
    axis_signs = [
        (axis, sign)
        for axis in "xyz"
        for sign in (-1, +1)]
    for (axis, sign), side in zip(axis_signs, sides[:6]):
        plane = physics.Plane(
            vector.vec3(**{axis: sign}),
            int_as_float(side.plane) * sign)
        out.append(editor.BrushSide(plane, texture_name(side)))
    # non-axial sides
    out.extend([
        editor.BrushSide(bsp.PLANES[side.plane], texture_name(side))
        for side in sides[6:]])
    return editor.Brush(out)


def model(bsp, model_index: int) -> geometry.Model:
    # entity
    entities = bsp.ENTITIES.search(model=f"*{model_index}")
    model_entity = entities[0] if len(entities) != 0 else dict()
    origin = model_entity.get("origin", "0 0 0")
    origin = vector.vec3(*origin.split())
    # NOTE: haven't found any model ents w/ angles
    # geometry
    model = bsp.MODELS[model_index]
    start, length = model.first_triangle_soup, model.num_triangle_soups
    out = geometry.Model([
        bsp.triangle_soup_mesh(i)
        for i in range(start, start + length)], origin)
    out.entity = model_entity
    return out


def patch_collision_mesh(bsp, patch_collision_index: int) -> geometry.Mesh:
    # BUG: indices go out of bounds at a certain point (LeafFaces?)
    patch = bsp.PATCH_COLLISION[patch_collision_index]
    # material
    material = geometry.Material("patch_collision")
    # geometry
    start, length = patch.first_vertex, patch.num_vertices
    positions = bsp.COLLISION_VERTICES[start:start + length]
    no_normal = vector.vec3(0, 0, 0)
    vertices = [
        geometry.Vertex(position, no_normal)
        for position in positions]
    start, length = patch.first_index, patch.num_indices
    indices = bsp.COLLISION_INDICES[start:start + length]
    return geometry.Mesh(
        material,
        geometry.triangle_soup([
            vertices[i]
            for i in indices]))


def portal_file(bsp) -> str:
    out = ["PRT1", str(len(bsp.CELLS)), str(len(bsp.PORTALS))]
    for ci, cell in enumerate(bsp.CELLS):
        start, length = cell.first_portal, cell.num_portals
        for pi, portal in enumerate(bsp.PORTALS[start:start + length]):
            start = portal.first_portal_vertex
            length = portal.num_portal_vertices
            winding = bsp.PORTAL_VERTICES[start:start + length]
            out.append(" ".join([
                f"{len(winding)} {ci} {portal.cell}",
                *[
                    f"({vertex.x} {vertex.y} {vertex.z})"
                    for vertex in winding]]))
    return "\n".join(out)


def triangle_soup_mesh(bsp, triangle_soup_index: int) -> geometry.Mesh:
    triangle_soup = bsp.TRIANGLE_SOUPS[triangle_soup_index]
    # material
    texture = bsp.TEXTURES[triangle_soup.texture]
    material = geometry.Material(texture.name.split(b"\0")[0].decode())
    # geometry
    start, length = triangle_soup.first_vertex, triangle_soup.num_vertices
    vertices = bsp.VERTICES[start:start + length]
    vertices = [
        geometry.Vertex(
            vertex.position,
            vertex.normal,
            vertex.albedo_uv,
            vertex.lightmap_uv,
            colour=vertex.colour.as_floats())
        for vertex in vertices]
    start, length = triangle_soup.first_index, triangle_soup.num_indices
    indices = bsp.INDICES[start:start + length]
    return geometry.Mesh(
        material,
        geometry.triangle_soup([
            vertices[i]
            for i in indices]))


methods = [
    quake.leaves_of_node, shared.worldspawn_volume, brush,
    model, patch_collision_mesh, portal_file, triangle_soup_mesh]
methods = {method.__name__: method for method in methods}
