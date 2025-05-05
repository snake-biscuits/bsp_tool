# https://www.mralligator.com/q3/
# https://github.com/zturtleman/spearmint/blob/master/code/qcommon/bsp_q3.c
# https://github.com/id-Software/Quake-III-Arena/blob/master/code/qcommon/qfiles.h
# NOTE: id-Software/Quake-III-Arena/q3radiant/BSPFILE.H uses BSPVERSION 34  (early Quake 2?)
# NOTE: id-Software/Quake-III-Arena/q3radiant/QFILES.H uses BSPVERSION 36
# NOTE: id-Software/Quake-III-Arena/common/qfiles.h uses BSPVERSION 46
from __future__ import annotations
import enum
import io
from typing import List, Tuple
import struct

from ... import core
from ...utils import binary
from ...utils import geometry
from ...utils import vector
from .. import colour
from .. import shared
from . import quake


FILE_MAGIC = b"IBSP"

BSP_VERSION = 46

GAME_PATHS = {
    "Quake III Arena": "Quake 3 Arena",
    # ^ includes "Quake III: Team Arena"
    "Quake Live": "Quake Live",
    "Return to Castle Wolfenstein": "realRTCW",
    # ^ Steam release (community made afaik)
    "Wolfenstein: Enemy Territory": "Wolfenstein - Enemy Territory",
    "WRATH: Aeon of Ruin": "WRATH",
    # https://mangledeyestudios.itch.io/dark-salvation
    "Dark Salvation": "Dark Salvation"}
# TODO: see where Xonotic & Nexuiz Classic fit in

GAME_VERSIONS = {
    "Quake III Arena": 46,
    "Quake Live": 46,
    "WRATH: Aeon of Ruin": 46,
    "Return to Castle Wolfenstein": 47,
    "Wolfenstein Enemy Territory": 47,
    "Dark Salvation": 666}


class LUMP(enum.Enum):
    ENTITIES = 0
    TEXTURES = 1  # SHADERS
    PLANES = 2
    NODES = 3
    LEAVES = 4
    LEAF_FACES = 5  # LEAFSURFACES
    LEAF_BRUSHES = 6
    MODELS = 7
    BRUSHES = 8
    BRUSH_SIDES = 9
    VERTICES = 10  # DRAWVERTS
    INDICES = 11  # DRAWINDICES
    EFFECTS = 12  # FOGS
    FACES = 13  # SURFACES
    LIGHTMAPS = 14  # 3x 128x128px RGB888 images
    LIGHT_GRID = 15  # LIGHTGRID
    VISIBILITY = 16


LumpHeader = quake.LumpHeader


# known lump changes from Quake 2 -> Quake 3:
#   EDGES & SURFEDGES -> INDICES?
# new:
#   EFFECTS
#   LIGHT_GRID
# deprecated:
#   AREAS
#   AREA_PORTALS
#   POP
#   TEXTURE_INFO


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


# engine limits
class MAX(enum.Enum):
    # lumps
    BRUSHES = 32768
    BRUSH_SIDES = 131072
    EFFECTS = 256
    ENTITIES = 2048
    ENTITIES_SIZE = 0x40000  # bytesize
    FACES = 131072
    INDICES = 524288
    LEAF_BRUSHES = 262144
    LEAF_FACES = 131072
    LEAVES = 131072
    LIGHTMAPS_SIZE = 0x200000  # bytesize
    LIGHT_GRID_SIZE = 0x80000  # bytesize
    MODELS = 1024
    NODES = 131072
    PLANES = 131072
    TEXTURES = 1024
    VERTICES = 524288
    VISIBILITY_SIZE = 0x200000  # bytesize
    # present conceptually, but not lumps yet
    AREAS = 256  # indexed by Leaves; used serverside
    PORTALS = 131072  # used by nodes; VIS related
    # string buffer sizes
    ENTITY_KEY = 32
    ENTITY_VALUE = 1024


# flag enums
class Contents(enum.IntFlag):
    """https://github.com/xonotic/darkplaces/blob/master/bspfile.h"""
    SOLID = 0x00000001  # opaque & transparent
    LAVA = 0x00000008
    SLIME = 0x00000010
    WATER = 0x00000020
    FOG = 0x00000040  # possibly unused
    AREA_PORTAL = 0x00008000
    PLAYER_CLIP = 0x00010000
    MONSTER_CLIP = 0x00020000
    # bot hints
    TELEPORTER = 0x00040000
    JUMP_PAD = 0x00080000
    CLUSTER_PORTAL = 0x00100000
    DO_NOT_ENTER = 0x00200000
    BOTCLIP = 0x00400000
    # end bot hints
    ORIGIN = 0x01000000  # removed during compile
    BODY = 0x02000000  # bound box collision only; never bsp
    CORPSE = 0x04000000
    DETAIL = 0x08000000
    STRUCTURAL = 0x10000000  # vis splitting brushes
    TRANSLUCENT = 0x20000000
    TRIGGER = 0x40000000
    NO_DROP = 0x80000000  # deletes drops


class Surface(enum.IntFlag):
    """https://github.com/id-Software/Quake-III-Arena/blob/master/common/surfaceflags.h"""
    NO_DAMAGE = 0x01  # no fall damage
    SLICK = 0x02  # slippery physics
    SKY = 0x04  # "lighting from environment map"
    LADDER = 0x8
    NO_IMPACT = 0x10  # don't make missile explosions
    NO_MARKS = 0x20  # don't leave missile marks
    FLESH = 0x40  # make flesh sounds and effects
    NO_DRAW = 0x80  # don't generate a face, nothing to render here
    HINT = 0x100  # make a primary bsp splitter
    SKIP = 0x200  # completely ignore, allowing non-closed brushes
    NO_LIGHTMAP = 0x400  # surface doesn't need a lightmap
    POINT_LIGHT = 0x800  # generate lighting info at vertexes
    METAL_STEPS = 0x1000  # clanking footsteps
    NO_STEPS = 0x2000  # no footstep sounds
    NON_SOLID = 0x4000  # don't collide against curves with this set
    LIGHT_FILTER = 0x8000  # act as a light filter during q3map -light
    ALPHA_SHADOW = 0x10000  # do per-pixel light shadow casting in q3map
    NO_DYNAMIC_LIGHT = 0x20000  # never add dynamic lights


class FaceType(enum.Enum):
    BAD = 0
    PLANAR = 1
    PATCH = 2  # displacement-like
    TRIANGLE_SOUP = 3  # mesh (dynamic LoD?)
    FLARE = 4  # billboard sprite?
    FOLIAGE = 5


# classes for lumps, in alphabetical order:
class Brush(core.Struct):  # LUMP 8
    first_side: int  # index into BrushSide lump
    num_sides: int  # number of BrushSides after first_side in this Brush
    texture: int  # index into Texture lump (use the Contents flags of the selected Texture)
    __slots__ = ["first_side", "num_sides", "texture"]
    _format = "3i"


class BrushSide(core.Struct):  # LUMP 9
    plane: int  # index into Plane lump
    texture: int  # index into Texture lump
    __slots__ = ["plane", "texture"]
    _format = "2i"


class Effect(core.Struct):  # LUMP 12
    shader_name: str
    brush: int  # index into Brush lump
    visible_side: int  # side of brush to clip ray tests against (-1 = None)
    __slots__ = ["shader_name", "brush", "visible_side"]
    _format = "64s2i"


class Face(core.Struct):  # LUMP 13
    texture: int  # index into Texture lump
    effect: int  # index into Effect lump; -1 for no effect
    type: FaceType
    first_vertex: int  # index into Vertex lump
    num_vertices: int  # number of Vertices after first_vertex in this face
    first_mesh_vertex: int  # index into MeshVertex lump
    num_mesh_vertices: int  # number of MeshVertices after first_mesh_vertex in this face
    # lightmap.index: int  # which of the 3 lightmap textures to use
    # lightmap.top_left: vector.vec2  # approximate top-left corner of visible lightmap segment
    # lightmap.size: vector.vec2  # size of visible lightmap segment
    # lightmap.origin: vector.vec3  # world space lightmap origin
    # lightmap.vector: List[vector.vec3]  # lightmap texture projection vectors
    normal: vector.vec3
    patch: vector.vec2  # for patches; control point dimensions?; TODO: ivec2
    __slots__ = ["texture", "effect", "type", "first_vertex", "num_vertices",
                 "first_mesh_vertex", "num_mesh_vertices", "lightmap", "normal", "patch"]
    _format = "12i12f2i"
    _arrays = {
        "lightmap": {
            "index": None, "top_left": [*"xy"], "size": [*"xy"],
            "origin": [*"xyz"], "vector": {"s": [*"xyz"], "t": [*"xyz"]}},
        "normal": [*"xyz"], "patch": [*"xy"]}
    _classes = {
        "type": FaceType, "lightmap.top_left": vector.vec2,
        "lightmap.size": vector.vec2, "lightmap.origin": vector.vec3,
        "lightmap.vector.s": vector.vec3, "lightmap.vector.t": vector.vec3,
        "normal": vector.vec3, "patch": vector.vec2}


class GridLight(core.Struct):  # LUMP 15
    # GridLights make up a 3D grid whose dimensions are:
    # x = floor(MODELS[0].maxs.x / 64) - ceil(MODELS[0].mins.x / 64) + 1
    # y = floor(MODELS[0].maxs.y / 64) - ceil(MODELS[0].mins.y / 64) + 1
    # z = floor(MODELS[0].maxs.z / 128) - ceil(MODELS[0].mins.z / 128) + 1
    ambient: colour.RGB24
    diffuse: colour.RGB24  # scaled by dot(mesh.Normal, gridlight.direction)
    direction: List[int]  # 2x 0-255 angles defining a 3D vector / angle (no roll)
    _format = "8B"
    __slots__ = ["ambient", "directional", "direction"]
    _arrays = {"ambient": [*"rgb"], "directional": [*"rgb"], "direction": ["phi", "theta"]}
    _classes = {"ambient": colour.RGB24, "directional": colour.RGB24}


class Leaf(core.Struct):  # LUMP 4
    cluster: int  # index into Visibility
    area: int  # Areaportal Area index; used for server entity segregation?
    bounds: List[vector.vec3]  # mins & maxs (int32_t)
    # bounds.mins: vector.vec3
    # bounds.maxs: vector.vec3
    first_leaf_face: int  # index into LeafFace lump
    num_leaf_faces: int  # number of LeafFaces in this Leaf
    first_leaf_brush: int  # index into LeafBrush lump
    num_leaf_brushes: int  # number of LeafBrushes in this Leaf
    __slots__ = ["cluster", "area", "bounds", "first_leaf_face",
                 "num_leaf_faces", "first_leaf_brush", "num_leaf_brushes"]
    _format = "12i"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}
    _classes = {"bounds.mins": vector.vec3, "bounds.maxs": vector.vec3}  # TODO: ivec3


class Lightmap(list):  # LUMP 14
    """Raw pixel bytes, 128x128 RGB_888 image"""
    _pixels: List[bytes] = [b"\0" * 3] * 128 * 128
    _format = "3s" * 128 * 128  # 128x128 RGB_888

    def __getitem__(self, row) -> List[bytes]:
        # Lightmap[row][column] returns self.__getitem__(row)[column]
        # to get a specific pixel: self._pixels[index]
        row_start = row * 128
        return self._pixels[row_start:row_start + 128]  # TEST: does it work with negative indices?

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} 128x128px RGB_888>"

    def as_bytes(self) -> bytes:
        return b"".join(self._pixels)

    @classmethod
    def from_tuple(cls, _tuple):
        out = cls()
        out._pixels = _tuple  # RGB_888
        return out


class Model(core.Struct):  # LUMP 7
    bounds: List[vector.vec3]
    # bounds.mins: vector.vec3
    # bounds.maxs: vector.vec3
    first_face: int  # index into Face lump
    num_faces: int  # number of Faces after first_face included in this Model
    first_brush: int  # index into Brush lump
    num_brushes: int  # number of Brushes after first_brush included in this Model
    __slots__ = ["bounds", "first_face", "num_faces", "first_brush", "num_brushes"]
    _format = "6f4i"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}
    _classes = {"bounds.mins": vector.vec3, "bounds.maxs": vector.vec3}


class Node(core.Struct):  # LUMP 3
    plane: int  # Plane that splits this Node (hence front-child, back-child)
    children: List[int]  # +ve Node, -ve Leaf
    # NOTE: -1 (leaf 1) terminates tree searches
    bounds: List[vector.vec3]  # mins & maxs (uint16_t)
    # bounds.mins: vector.vec3
    # bounds.maxs: vector.vec3
    # NOTE: bounds are generous, rounding up to the nearest 16 units
    __slots__ = ["plane", "children", "bounds"]
    _format = "9i"
    _arrays = {"children": ["front", "back"],
               "bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}
    _classes = {"bounds.mins": vector.vec3, "bounds.maxs": vector.vec3}  # TODO: ivec3


class Plane(core.Struct):  # LUMP 2
    normal: vector.vec3
    distance: float
    __slots__ = ["normal", "distance"]
    _format = "4f"
    _arrays = {"normal": [*"xyz"]}
    _classes = {"normal": vector.vec3}


class Texture(core.Struct):  # LUMP 1
    name: str  # 64 char texture name; stored in WAD (Where's All the Data)?
    flags: Tuple[Surface, Contents]
    __slots__ = ["name", "flags"]
    _format = "64s2i"
    _arrays = {"flags": ["surface", "contents"]}
    _classes = {"flags.surface": Surface, "flags.contents": Contents}


class Vertex(core.Struct):  # LUMP 10
    position: vector.vec3
    uv: List[List[float]]  # texture & lightmap uv coords
    # uv.texture: List[float]
    # uv.lightmap: List[float]
    normal: vector.vec3
    colour: List[int]  # 1 RGBA32 pixel / texel
    __slots__ = ["position", "uv", "normal", "colour"]
    _format = "10f4B"
    _arrays = {"position": [*"xyz"], "uv": {"texture": [*"uv"], "lightmap": [*"uv"]},
               "normal": [*"xyz"], "colour": [*"rgba"]}
    _classes = {"position": vector.vec3, "normal": vector.vec3, "colour": colour.RGBA32}
    # TODO: "uv.texture.uv": vec2.uv, "uv.lightmap.uv": vec2.uv


# special lump classes, in alphabetical order:
class Visibility(list):
    """Cluster A is visible from Cluster B if bit B of Visibility[A] is set
    bit (1 << Y % 8) of vecs[X * vector_size + Y // 8] is set
    NOTE: Clusters are associated with Leaves"""
    vectors: List[bytes]
    # TODO: detect fast vis / leaked
    # NOTE: tests/mp_lobby.bsp  {*Visibility} == {(2 ** len(Visibility) - 1).to_bytes(len(Visibility), "little")}

    def __init__(self, vectors: List[bytes] = tuple()):
        super().__init__(vectors)

    def as_bytes(self, compress=False) -> bytes:
        # lazy method (compress=False)
        # NOTE: should match .from_bytes() input exactly
        num_vectors = len(self)
        vector_size = len(self[0])  # assumption! verified later
        best_vector_size = num_vectors // 8 + (1 if num_vectors % 8 else 0)
        if vector_size >= best_vector_size and compress is False:
            vector_sizes = {len(vector_) for vector_ in self}
            assert len(vector_sizes) == 1, "inconsistently sized vectors"
            return b"".join([
                struct.pack("2i", num_vectors, vector_size),
                *self])
        # robust method (compress=True)
        # TODO: verify "compression" does not break maps
        vectors = list()
        for vector_ in self:
            if len(vector_) > best_vector_size:  # trim (scary)
                vector_ = vector_[:best_vector_size]
            elif len(vector) < best_vector_size:  # pad
                vector_ += b"\0" * (best_vector_size - len(vector_))
            vectors.append(vector_)
        return b"".join([
            struct.pack("2i", num_vectors, best_vector_size),
            *vectors])

    @classmethod
    def from_bytes(cls, raw_lump: bytes) -> Visibility:
        return cls.from_stream(io.BytesIO(raw_lump), len(raw_lump))

    @classmethod
    def from_stream(cls, stream: io.BytesIO, lump_length: int) -> Visibility:
        num_vectors, vector_size = binary.read_struct(stream, "2i")
        assert num_vectors * vector_size == lump_length - 8
        return cls([stream.read(vector_size) for i in range(num_vectors)])


# {"LUMP": LumpClass}
BASIC_LUMP_CLASSES = {
    "LEAF_BRUSHES": shared.Ints,
    "LEAF_FACES":   shared.Ints,
    "INDICES":      shared.Ints}

LUMP_CLASSES = {
    "BRUSHES":     Brush,
    "BRUSH_SIDES": BrushSide,
    "EFFECTS":     Effect,
    "FACES":       Face,
    "LEAVES":      Leaf,
    "LIGHTMAPS":   Lightmap,
    "LIGHT_GRID":  GridLight,
    "MODELS":      Model,
    "NODES":       Node,
    "PLANES":      Plane,
    "TEXTURES":    Texture,
    "VERTICES":    Vertex}

SPECIAL_LUMP_CLASSES = {
    "ENTITIES":   shared.Entities,
    "VISIBILITY": Visibility}


# branch exclusive methods, in alphabetical order:
def face_mesh(bsp, face_index: int) -> geometry.Mesh:
    raise NotImplementedError()


def model(bsp, model_index: int) -> geometry.Model:
    raise NotImplementedError()


methods = [quake.leaves_of_node, shared.worldspawn_volume]
methods = {method.__name__: method for method in methods}
