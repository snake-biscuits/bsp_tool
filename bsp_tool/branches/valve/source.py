# https://developer.valvesoftware.com/wiki/Source_BSP_File_Format
# https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/bspfile.h
# https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/bspflags.h
# https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/bsplib.cpp
from __future__ import annotations
import enum
import io
import struct
from typing import List, Tuple

from ... import archives
from ... import core
from ... import lumps
from ...utils import binary
from ...utils import geometry
from ...utils import texture
from ...utils import vector
from .. import colour
from .. import shared
from ..id_software import quake
from ..id_software import quake2
from . import physics


FILE_MAGIC = b"VBSP"

BSP_VERSION = 19

GAME_PATHS = {
    "Counter-Strike: Source": "counter-strike source/cstrike",
    "Half-Life Deathmatch: Source": "Half-Life 1 Source Deathmatch/hl1mp",
    "Half-Life: Source": "half-life 2/hl1",
    "Half-Life 2": "half-life 2/hl2",
    "Half-Life 2: Deathmatch": "half-life 2 deathmatch/hl2mp"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    ENTITIES = 0
    PLANES = 1
    TEXTURE_DATA = 2
    VERTICES = 3
    VISIBILITY = 4
    NODES = 5
    TEXTURE_INFO = 6
    FACES = 7  # version 1
    LIGHTING = 8  # version 1
    OCCLUSION = 9  # version 2
    LEAVES = 10  # version 1
    FACE_IDS = 11
    EDGES = 12
    SURFEDGES = 13
    MODELS = 14
    WORLD_LIGHTS = 15
    LEAF_FACES = 16
    LEAF_BRUSHES = 17
    BRUSHES = 18
    BRUSH_SIDES = 19
    AREAS = 20
    AREA_PORTALS = 21
    PORTALS = 22
    CLUSTERS = 23
    PORTAL_VERTICES = 24
    CLUSTER_PORTALS = 25
    DISPLACEMENT_INFO = 26
    ORIGINAL_FACES = 27
    PHYSICS_DISPLACEMENT = 28
    PHYSICS_COLLIDE = 29
    VERTEX_NORMALS = 30
    VERTEX_NORMAL_INDICES = 31
    DISPLACEMENT_LIGHTMAP_ALPHAS = 32  # deprecated / X360 ?
    DISPLACEMENT_VERTICES = 33
    DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS = 34
    GAME_LUMP = 35
    LEAF_WATER_DATA = 36
    PRIMITIVES = 37
    PRIMITIVE_VERTICES = 38  # deprecated / X360 ?
    PRIMITIVE_INDICES = 39
    PAKFILE = 40
    CLIP_PORTAL_VERTICES = 41
    CUBEMAPS = 42
    TEXTURE_DATA_STRING_DATA = 43
    TEXTURE_DATA_STRING_TABLE = 44
    OVERLAYS = 45
    LEAF_MIN_DIST_TO_WATER = 46
    FACE_MACRO_TEXTURE_INFO = 47
    DISPLACEMENT_TRIANGLES = 48
    PHYSICS_COLLIDE_SURFACE = 49  # deprecated / X360 ?
    WATER_OVERLAYS = 50  # deprecated / X360 ?
    LEAF_AMBIENT_INDEX_HDR = 51
    LEAF_AMBIENT_INDEX = 52
    LIGHTING_HDR = 53  # version 1
    WORLD_LIGHTS_HDR = 54
    LEAF_AMBIENT_LIGHTING_HDR = 55  # version 1
    LEAF_AMBIENT_LIGHTING = 56  # version 1
    XZIP_PAKFILE = 57  # deprecated / X360 ?
    FACES_HDR = 58  # version 1
    MAP_FLAGS = 59
    OVERLAY_FADES = 60
    UNUSED_61 = 61
    UNUSED_62 = 62
    UNUSED_63 = 63


class LumpHeader(core.MappedArray):
    _mapping = ["offset", "length", "version", "fourCC"]
    _format = "4I"


# known lump changes from GoldSrc -> Source:

# MipTextures -> TextureInfo & TextureData -> TextureDataStringTable/Data
# NOTE: GoldSrc MipTextures didn't store textures, just gave the texture name & flags


# a rough map of the relationships between lumps:

# Entity -> Model -> Node -> Leaf
#                \-> Face

# Leaf -> LeafBrush -> Brush -> BrushSide -> TextureInfo
#     \-> LeafFace -> Face               \-> Plane

#     /-> SurfEdge -> Edge -> Vertex
# Face -> Plane
#    \--> TextureInfo -> TextureData -> TextureDataStringTable
#     \-> DisplacementInfo -> DisplacementVertex

# FaceID is parallel with Faces & lists Hammer ids per face

# Leaf is parallel with LeafAmbientIndex
# LeafAmbientIndex -> LeafAmbientSample

# ClipPortalVertices are AreaPortal geometry [unverified]

# Overlay & OverlayFade are parallel (paired w/ other of same index)


# engine limits: (2013 SDK bspfile.h)
class MIN(enum.Enum):
    DISPLACEMENT_POWER = 2


class MAX(enum.Enum):
    # misc:
    CUBEMAP_SAMPLES = 1024
    DISPLACEMENT_CORNER_NEIGHBORS = 4
    DISPLACEMENT_POWER = 4
    ENTITY_KEY, ENTITY_VALUE = 32, 1024  # key value pair sizes
    LIGHTMAPS = 4  # max lightmap styles?
    LIGHTMAP_DIMENSION_WITHOUT_BORDER_BRUSH = 32
    LIGHTMAP_DIMENSION_WITHOUT_BORDER_DISPLACEMENT = 125
    LIGHTMAP_DIMENSION_WITH_BORDER_BRUSH = 35  # "vbsp cut limit" +1 (to account for rounding errors)
    LIGHTMAP_DIMENSION_WITH_BORDER_DISPLACEMENT = 128
    # absolute maximum, based on previous values
    LIGHTMAP_DIMENSION_WITH_BORDER = LIGHTMAP_DIMENSION_WITH_BORDER_DISPLACEMENT
    LIGHTMAP_DIMENSION_WITHOUT_BORDER = LIGHTMAP_DIMENSION_WITHOUT_BORDER_DISPLACEMENT
    LIGHTING_STYLES = 64
    PORTAL_VERTICES = 128000
    # lumps:
    ENTITIES = 8192
    PLANES = 65536
    TEXTURE_DATA = 2048
    VERTICES = 65536
    VISIBILITY_CLUSTERS = 65536
    VISIBILITY_SIZE = 0x1000000  # "increased in BSPVERSION 7"
    NODES = 65536
    TEXTURE_INFO = 12288
    FACES = 65536
    LIGHTING_SIZE = 0x1000000
    LEAVES = 65536
    EDGES = 256000
    SURFEDGES = 512000
    MODELS = 1024
    WORLD_LIGHTS = 8192
    LEAF_FACES = 65536
    LEAF_BRUSHES = 65536
    BRUSHES = 8192
    BRUSH_SIDES = 65536
    AREAS = 256
    AREA_BYTES = AREAS // 8
    AREA_PORTALS = 1024
    # UNUSED_24 [PORTALVERTS] = 128000
    DISPLACEMENT_INFO = 2048
    ORIGINAL_FACES = FACES
    VERTEX_NORMALS = 256000
    VERTEX_NORMAL_INDICES = 256000
    DISPLACEMENT_VERTICES_FOR_ONE = (2 ** DISPLACEMENT_POWER + 1) ** 2
    DISPLACEMENT_VERTICES = DISPLACEMENT_INFO * DISPLACEMENT_VERTICES_FOR_ONE
    LEAF_WATER_DATA = 32768
    PRIMITIVES = 32768
    PRIMITIVE_VERTICES = 65536
    PRIMITIVE_INDICES = 65536
    TEXTURE_DATA_STRING_DATA = 256000
    TEXTURE_DATA_STRING_TABLE = 65536
    OVERLAYS = 512
    DISPLACEMENT_TRIANGLES_FOR_ONE = 2 ** DISPLACEMENT_POWER * 3
    DISPLACEMENT_TRIANGLES = DISPLACEMENT_INFO * DISPLACEMENT_TRIANGLES_FOR_ONE
    WATER_OVERLAYS = 16384
    LIGHTING_HDR_SIZE = LIGHTING_SIZE
    WORLD_LIGHTS_HDR = WORLD_LIGHTS
    FACES_HDR = FACES


# flag enums
class Contents(enum.IntFlag):  # src/public/bspflags.h
    """Brush flags"""  # NOTE: vbsp sets these in src/utils/vbsp/textures.cpp
    # visible
    EMPTY = 0x00
    SOLID = 0x01
    WINDOW = 0x02  # bulletproof glass etc. (transparent but solid)
    AUX = 0x04  # unused?
    GRATE = 0x08  # allows bullets & vis
    SLIME = 0x10
    WATER = 0x20
    BLOCK_LOS = 0x40  # blocks AI Line Of Sight
    OPAQUE = 0x80  # blocks AI Line Of Sight, may be non-solid
    TEST_FOG_VOLUME = 0x100  # cannot be seen through, but may be non-solid
    UNUSED_1 = 0x200
    UNUSED_2 = 0x400
    TEAM1 = 0x0800
    TEAM2 = 0x1000
    IGNORE_NODRAW_OPAQUE = 0x2000  # ignore opaque if Surface.NO_DRAW
    MOVEABLE = 0x4000  # half-life 1 push crates etc.
    # not visible
    AREAPORTAL = 0x8000
    PLAYER_CLIP = 0x10000
    MONSTER_CLIP = 0x20000
    # CURRENT_ flags are for moving water
    CURRENT_0 = 0x40000
    CURRENT_90 = 0x80000
    CURRENT_180 = 0x100000
    CURRENT_270 = 0x200000
    CURRENT_UP = 0x400000
    CURRENT_DOWN = 0x800000
    ORIGIN = 0x1000000  # "removed before bsping an entity"
    MONSTER = 0x2000000  # in-game only, shouldn't be in a .bsp
    DEBRIS = 0x4000000
    DETAIL = 0x8000000  # func_detail; for VVIS (visleaf assembly from Brushes)
    TRANSLUCENT = 0x10000000
    LADDER = 0x20000000
    HITBOX = 0x40000000  # requests hit tracing use hitboxes


class ContentsMask(enum.IntEnum):
    ALL = 0xFFFFFFFF
    # PHYSICS
    SOLID = Contents.SOLID | Contents.MOVEABLE | Contents.WINDOW | Contents.MONSTER | Contents.GRATE
    PLAYER_SOLID = SOLID | Contents.PLAYER_CLIP
    NPC_SOLID = SOLID | Contents.MONSTER_CLIP
    WATER = Contents.WATER | Contents.MOVEABLE | Contents.SLIME  # water physics apply inside this volume
    # VIS
    OPAQUE = Contents.SOLID | Contents.MOVEABLE | Contents.OPAQUE  # blocks light
    OPAQUE_AND_NPCS = OPAQUE | Contents.MONSTER
    BLOCK_LOS = Contents.SOLID | Contents.MOVEABLE | Contents.BLOCK_LOS  # blocks AI Line Of Sight
    BLOCK_LOS_AND_NPCS = BLOCK_LOS | Contents.MONSTER
    VISIBLE = OPAQUE | Contents.IGNORE_NODRAW_OPAQUE  # blocks Player Line Of Sight
    VISIBLE_AND_NPCS = OPAQUE_AND_NPCS | Contents.IGNORE_NODRAW_OPAQUE
    # WEAPONS
    SHOT_HULL = SOLID | Contents.DEBRIS  # projectile weapons
    SHOT = SHOT_HULL | Contents.HITBOX  # raycast weapons
    SHOT_PORTAL = SOLID & ~Contents.GRATE  # other projectile weapons
    # ALTERNATES
    SOLID_BRUSH_ONLY = SOLID & ~Contents.MONSTER
    PLAYER_SOLID_BRUSH_ONLY = SOLID_BRUSH_ONLY | Contents.PLAYER_CLIP
    NPC_SOLID_BRUSH_ONLY = SOLID_BRUSH_ONLY | Contents.MONSTER_CLIP
    NPC_WORLD_STATIC = Contents.SOLID | Contents.WINDOW | Contents.MONSTER_CLIP | Contents.GRATE  # for route rebuilding
    # OTHER
    SPLIT_AREAPORTAL = Contents.WATER | Contents.SLIME  # can split areaportals
    CURRENT = sum([c for c in Contents if c.name.startswith("CURRENT")])
    DEAD_SOLID = Contents.SOLID | Contents.PLAYER_CLIP | Contents.WINDOW | Contents.GRATE  # unused?


class DisplacementChildNode(enum.Enum):
    """These can be used to index g_ChildNodeIndexMul"""
    UPPER_RIGHT = 0
    UPPER_LEFT = 1
    LOWER_LEFT = 2
    LOWER_RIGHT = 3


class DisplacementCorner(enum.Enum):
    """Corner indices. Used to index m_CornerNeighbors"""
    LOWER_LEFT = 0
    UPPER_LEFT = 1
    UPPER_RIGHT = 2
    LOWER_RIGHT = 3


class DisplacementEdge(enum.Enum):  # used to index DisplacementInfo.neighbours.edges
    """These edge indices must match the edge indices of the CCoreDispSurface"""
    LEFT = 0
    TOP = 1
    RIGHT = 2
    BOTTOM = 3


class DisplacementSpan(enum.Enum):
    """Where one DisplacementInfo fits on another"""
    CORNER_TO_CORNER = 0  # 1 -> x -> 2
    CORNER_TO_MIDPOINT = 1  # 1 -> x
    MIDPOINT_TO_CORNER = 2  # x -> 2
    # 1 -> x -> 2
    # ^         ^
    # |         |
    # x    x    x
    # ^         ^
    # |         |
    # 0 -> x -> 3


class DisplacementOrientation(enum.Enum):
    """Relative orientations of displacement neighbors"""
    CCW_0 = 0
    CCW_90 = 1
    CCW_180 = 2
    CCW_270 = 3


class DisplacementFlags(enum.IntFlag):
    UNUSED = 1
    NO_PHYS = 2
    NO_HULL = 4
    NO_RAY = 8


class EmitType(enum.Enum):
    SURFACE = 0x00  # 90 degree spotlight
    POINT = 0x01
    SPOTLIGHT = 0x02  # spotlight w/ penumbra
    SKY_LIGHT = 0x03  # directional light w/ no falloff (surface must trace to SKY texture)
    QUAKE_LIGHT = 0x04  # linear falloff, non-lambertian
    SKY_AMBIENT = 0x05  # spherical light w/ no falloff (surface must trace to SKY texture)


class LeafFlags(enum.IntFlag):
    SKY = 0x01
    RADIAL = 0x02
    SKY_2D = 0x04


class PrimitiveType(enum.Enum):
    """stored in Primitive.type"""
    TRIANGLE_LIST = 0
    TRIANGLE_STRIP = 1


class StaticPropFlags(enum.IntFlag):
    # derived at compile or run time
    FADES = 0x1  # use fade distances
    USE_LIGHTING_ORIGIN = 0x2
    NO_DRAW = 0x4    # computed at run time based on dx level
    # the following are set in a level editor:
    IGNORE_NORMALS = 0x8
    NO_SHADOW = 0x10
    SCREEN_SPACE_FADE = 0x20
    # next 3 are for lighting compiler
    NO_PER_VERTEX_LIGHTING = 0x40
    NO_SELF_SHADOWING = 0x80
    NO_PER_TEXEL_LIGHTING = 0x100  # when was this added
    # mask
    EDITOR_MASK = 0x1D8


class StaticPropCollision(enum.IntFlag):
    NON_SOLID = 0
    BOUNDING_BOX = 2
    VPHYSICS = 6


class Surface(enum.IntFlag):  # src/public/bspflags.h
    """TextureInfo flags"""  # NOTE: vbsp sets these in src/utils/vbsp/textures.cpp
    LIGHT = 0x0001  # "value will hold the light strength"
    SKY_2D = 0x0002  # don't draw, indicates we should skylight + draw 2d sky but not draw the 3D skybox
    SKY = 0x0004  # don't draw, but add to skybox
    WARP = 0x0008  # turbulent water warp
    TRANSLUCENT = 0x0010
    NO_PORTAL = 0x0020  # the surface can not have a portal placed on it
    TRIGGER = 0x0040  # xbox hack to work around elimination of trigger surfaces, which breaks occluders
    NO_DRAW = 0x0080
    HINT = 0x0100  # make a bsp split on this face
    SKIP = 0x0200  # don't split on this face, allows for non-closed brushes
    NO_LIGHT = 0x0400  # don't calculate light
    BUMPLIGHT = 0x0800  # calculate three lightmaps for the surface for bumpmapping (ssbump?)
    NO_SHADOWS = 0x1000
    NO_DECALS = 0x2000
    NO_CHOP = 0x4000	 # don't subdivide patches on this surface
    HITBOX = 0x8000  # surface is part of a hitbox


class WorldLightFlags(enum.IntFlag):  # DWL_FLAGS_* in src/public/bspfile.h
    IN_AMBIENT_CUBE = 0x0001


# classes for each lump, in alphabetical order:
class Area(core.MappedArray):  # LUMP 20
    num_area_portals: int   # number of AreaPortals after first_area_portal in this Area
    first_area_portal: int  # index of first AreaPortal
    _mapping = ["num_area_portals", "first_area_portal"]
    _format = "2i"


class AreaPortal(core.MappedArray):  # LUMP 21
    # public/bspfile.h dareaportal_t &  utils/vbsp/portals.cpp EmitAreaPortals
    portal_key: int  # for tying to entities
    first_clip_portal_vert: int  # index into the ClipPortalVertex lump
    num_clip_portal_vertices: int  # number of ClipPortalVertices after first_clip_portal_vertex in this AreaPortal
    plane: int  # index of into the Plane lump
    _mapping = ["portal_key", "other_area", "first_clip_portal_vertex",
                "num_clip_portal_vertices", "plane"]
    _format = "4Hi"


class Brush(core.Struct):  # LUMP 18
    """Assumed to carry over from .vmf"""
    first_side: int  # first BrushSide of this Brush
    num_sides: int  # number of BrushSides after first_side in this Brush
    contents: Contents
    __slots__ = ["first_side", "num_sides", "contents"]
    _format = "3i"
    _classes = {"contents": Contents}


class BrushSide(core.Struct):  # LUMP 19
    plane: int  # Plane this BrushSide lies on
    texture_info: int  # TextureInfo this BrushSide uses
    displacement_info: int  # DisplacementInfo applied to the Face derived from this BrushSide; -1 for None
    bevel: int  # bool? indicates if side is a bevel plane (BSPVERSION 7)
    __slots__ = ["plane", "texture_info", "displacement_info", "bevel"]
    _format = "H3h"


class Cubemap(core.Struct):  # LUMP 42
    """Location (origin) & resolution (size)"""
    origin: vector.vec3
    size: int  # texture dimension (each face of a cubemap is square)
    __slots__ = ["origin", "size"]
    _format = "4i"
    _arrays = {"origin": [*"xyz"]}
    _classes = {"origin": vector.vec3}


class CornerNeighbour(core.MappedArray):  # LUMP 26
    neighbours: List[int]  # indices of neighbouring DisplacementInfos
    num_neighbours: int  # number of DisplacementInfos indexed; {0..4}
    padding: int
    _mapping = {"neighbours": 4, "num_neighbours": None, "padding": None}
    _format = "4H2B"


class SubNeighbour(core.MappedArray):  # LUMP 26
    neighbour: int  # index of neighbouring DisplacementInfo; 0xFFFF for None
    neighbour_orientation: DisplacementOrientation  # orientation of neighbour relative to self
    span: DisplacementSpan  # where neighbour fits onto this side
    neighbour_span: DisplacementSpan  # how this side connects to neighbour
    padding: int
    _mapping = ["neighbour", "neighbour_orientation", "span", "neighbour_span", "padding"]
    _format = "H4B"
    _classes = {"neighbour_orientation": DisplacementOrientation,
                "span": DisplacementSpan, "neighbour_span": DisplacementSpan}


class DisplacementInfo(core.Struct):  # LUMP 26
    """Holds the information defining a displacement"""
    start_position: vector.vec3  # approx coords of first corner of face
    # nessecary to ensure order of displacement vertices
    first_displacement_vertex: int  # index of first DisplacementVertex
    # num_displacement_vertices: int = ((1 << power) + 1) ** 2
    first_displacement_triangle: int  # index of first DisplacementTriangle
    # num_diplacement_triangles: int = 2 * (1 << power) ** 2
    power: int  # level of subdivision
    flags: DisplacementFlags
    min_tesselation: int  # for tesselation shaders / triangle assembley?
    smoothing_angle: float  # for smooth lighting
    contents: Contents
    face: int  # Face this DisplacementInfo affects / came from
    lightmap_alpha_start: int  # TODO: figure out displacement lightmaps
    lightmap_sample_position_start: int
    neighbours: List[List[SubNeighbour] | List[CornerNeighbour]]
    # neighbours.edge: List[SubNeighbour]  # x8 edge connections
    # neighbours.corner: List[CornerNeighbour]  # x4 corner connections
    allowed_vertices: List[int]
    __slots__ = ["start_position", "first_displacement_vertex", "first_displacement_triangle", "power",
                 "flags", "min_tesselation", "smoothing_angle", "contents", "face", "lightmap_alpha_start",
                 "lightmap_sample_position_start", "neighbours", "allowed_vertices"]
    _format = "3f3iHhfiH2i" + SubNeighbour._format * 8 + CornerNeighbour._format * 4 + "10i"
    _arrays = {"start_position": [*"xyz"], "allowed_vertices": 10,
               "neighbours": {"edge": {x: {y: SubNeighbour._mapping for y in "AB"} for x in "ABCD"},
                              "corner": {x: CornerNeighbour._mapping for x in "ABCD"}}}
    # TODO: clean up neighbours with {int: _mapping} mappings (generate lists)
    _classes = {"start_position": vector.vec3, "flags": DisplacementFlags, "contents": Contents,
                **{f"neighbours.edge.{x}.{y}": SubNeighbour for x in "ABCD" for y in "AB"},
                **{f"neighbours.corner.{x}": CornerNeighbour for x in "ABCD"}}

    @property
    def num_displacement_vertices(self) -> int:
        return ((1 << self.power) + 1) ** 2

    @property
    def num_displacement_triangles(self) -> int:
        return 2 * (1 << self.power) ** 2


class DisplacementTriangle(shared.UnsignedShort, enum.IntFlag):  # LUMP 48
    SURFACE = 0x01
    WALKABLE = 0x02
    BUILDABLE = 0x04
    SURFPROP1 = 0x08  # use surfaceprop of first material?
    SURFPROP2 = 0x10  # use surfaceprop of second material?


class DisplacementVertex(core.Struct):  # LUMP 33
    """The positional deformation & blend value of a point in a displacement"""
    normal: vector.vec3  # direction of vertex offset from barymetric base
    distance: float      # length to scale deformation vector by
    alpha: float         # [0-1] material blend factor
    __slots__ = ["normal", "distance", "alpha"]
    _format = "5f"
    _arrays = {"normal": [*"xyz"]}
    _classes = {"normal": vector.vec3}


class Face(core.Struct):  # LUMPS 7, 27 & 58
    """makes up Models (including worldspawn), also referenced by LeafFaces"""
    plane: int  # index into Plane lump
    side: int  # "faces opposite to the Node's Plane direction"
    on_node: bool  # if False: Face is in a Leaf
    first_edge: int  # index into the SurfEdge lump
    num_edges: int  # number of SurfEdges after first_edge in this Face
    texture_info: int  # index into the TextureInfo lump
    displacement_info: int  # index into the DisplacementInfo lump (None if -1)
    surface_fog_volume_id: int  # related to QuakeIII vertex-lit fog?
    styles: List[int]  # 4 different lighting states? "switchable lighting info"
    light_offset: int  # index of first pixel in LIGHTING / LIGHTING_HDR
    area: float  # surface area of this face
    lightmap: List[vector.vec2]
    # lightmap.mins: vector.vec2  # dimensions of lightmap segment
    # lightmap.size: vector.vec2  # scalars for lightmap segment
    original_face: int  # OriginalFace this Face came from; -1 if this is an OriginalFace
    primitives: Tuple[int, bool]
    # primitives.allow_dynamic_shadows: bool
    # primitives.count: int  # limit of 2^15 - 1
    first_primitive: int  # index of Primitive (if primitives.count != 0)
    smoothing_groups: int  # lightmap smoothing group
    __slots__ = ["plane", "side", "on_node", "first_edge", "num_edges",
                 "texture_info", "displacement_info", "surface_fog_volume_id", "styles",
                 "light_offset", "area", "lightmap", "original_face",
                 "primitives", "first_primitive", "smoothing_groups"]
    _format = "Hb?i4h4bif5i2HI"
    _arrays = {"styles": 4, "lightmap": {"mins": [*"xy"], "size": [*"xy"]}}
    _bitfields = {"primitives": {"allow_dynamic_shadows": 1, "count": 15}}
    # TODO: ivec2 for lightmap vectors
    _classes = {"lightmap.mins": vector.vec2, "lightmap.size": vector.vec2,
                "primitives.allow_dynamic_shadows": bool}


class Leaf(core.Struct):  # LUMP 10
    """Endpoint of a vis tree branch, a pocket of Faces"""
    contents: Contents
    cluster: int  # index of this Leaf's cluster (leaf group in VISIBILITY lump); -1 for None
    bitfield: core.BitField  # area & flags bitfield
    # bitfield.area  # index into Areas?
    # bitfield.flags  # TODO: LeafFlags enum
    bounds: List[vector.vec3]  # uint16_t, very blocky
    # bounds.mins: vector.vec3
    # bounds.maxs: vector.vec3
    first_leaf_face: int  # index of first LeafFace
    num_leaf_faces: int  # number of LeafFaces
    first_leaf_brush: int  # index of first LeafBrush
    num_leaf_brushes: int  # number of LeafBrushes
    leaf_water_data: int  # index into LeafWaterData; -1 if not submerged
    padding: int  # should be 0; waste of a bitfield
    cube: List[List[int]]  # CompressedLightCube; unsure about orientation / face order
    __slots__ = ["contents", "cluster", "bitfield", "bounds",
                 "first_leaf_face", "num_leaf_faces", "first_leaf_brush",
                 "num_leaf_brushes", "leaf_water_data", "padding", "cube"]
    _format = "ihH6h4H2h24B"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]},
               "cube": {x: [*"rgb", "exponent"] for x in "ABCDEF"}}  # integer keys in _mapping would be nicer
    # TODO: map cube face names to UP, DOWN etc.
    _bitfields = {"bitfield": {"area": 9, "flags": 7}}
    _classes = {"contents": Contents, "bounds.mins": vector.vec3, "bounds.maxs": vector.vec3,
                **{f"cube.{s}": colour.RGBExponent for s in "ABCDEF"}}
    # TODO: "cube": CompressedLightCube, "bitfield.flags": LeafFlags


class LeafAmbientIndex(core.MappedArray):  # LUMP 52
    num_samples: int
    first_sample: int  # index into LeafAmbientSamples
    _format = "2h"
    _mapping = ["num_samples", "first_sample"]


class LeafAmbientSample(core.Struct):  # LUMP 56
    """cube of lighting samples"""
    cube: List[List[int]]  # unsure about orientation / face order
    origin: vector.vec3  # uint8_t; "fixed point fraction of Leaf bounds"
    padding: int  # should be 0
    __slots__ = ["cube", "origin", "padding"]
    _format = "28B"
    _arrays = {"cube": {s: [*"rgb", "exponent"] for s in "ABCDEF"},  # integer keys in _mapping would be nicer
               "origin": [*"xyz"]}
    _classes = {**{f"cube.{s}": colour.RGBExponent for s in "ABCDEF"}, "origin": vector.vec3}
    # TODO: "cube": CompressedLightCube


class LeafWaterData(core.MappedArray):  # LUMP 36
    surface_z: float  # global Z height of the water's surface
    min_z: float  # bottom of the water volume?
    texture_info: int  # index to this LeafWaterData's TextureInfo
    _format = "2fI"
    _mapping = ["surface_z", "min_z", "texture_info"]


class Model(core.Struct):  # LUMP 14
    """Brush based entities; Index 0 is worldspawn"""
    bounds: List[vector.vec3]
    # bounds.mins: vector.vec3
    # bounds.maxs: vector.vec3
    origin: vector.vec3  # center of model, worldspawn is always at 0 0 0
    node: int  # index into Node lump; head of all nodes containing this Model
    first_face: int  # index into Face lump
    num_faces: int  # number of Faces after first_face in this Model
    __slots__ = ["bounds", "origin", "node", "first_face", "num_faces"]
    _format = "9f3i"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}, "origin": [*"xyz"]}
    _classes = {"bounds.mins": vector.vec3, "bounds.maxs": vector.vec3, "origin": vector.vec3}


class Node(core.Struct):  # LUMP 5
    plane: int  # Plane that splits this Node (hence front-child, back-child)
    children: List[int]  # +ve Node, -ve Leaf
    # NOTE: -1 (leaf 1) terminates tree searches
    bounds: List[vector.vec3]  # mins & maxs (uint16_t)
    # bounds.mins: vector.vec3
    # bounds.maxs: vector.vec3
    # NOTE: bounds are generous, rounding up to the nearest 16 units
    first_face: int  # index into Face lump
    num_faces: int  # number of Faces after first_face in this Node
    area: int  # index into Area lump, if all children are in the same area, else -1
    # area is always 0?
    padding: int  # should be 0
    __slots__ = ["plane", "children", "bounds", "first_face", "num_faces",
                 "area", "padding"]
    _format = "3i6h2H2h"
    _arrays = {"children": 2, "bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}
    _classes = {"bounds.mins": vector.vec3, "bounds.maxs": vector.vec3}
    # TODO: ivec3 bounds & AABB bounds class


class Overlay(core.Struct):  # LUMP 45
    id: int
    texture_info: int
    face_count: int  # render order in top 2 bits
    faces: List[int]
    uv: List[float]  # uncertain of order
    points: List[vector.vec3]
    origin: vector.vec3
    normal: vector.vec3
    __slots__ = ["id", "texture_info", "face_count", "faces",
                 "uv", "points", "origin", "normal"]
    _format = "i2h64i22f"
    _arrays = {"faces": 64, "uv": ["left", "right", "top", "bottom"],
               "points": {P: [*"xyz"] for P in "ABCD"}, "origin": [*"xyz"], "normal": [*"xyz"]}
    # TODO: index uv & points w/ {int: _mapping} _arrays
    _classes = {**{f"points.{P}": vector.vec3 for P in "ABCD"}, "origin": vector.vec3, "normal": vector.vec3}


class OverlayFade(core.MappedArray):  # LUMP 60
    """Holds fade distances for the overlay of the same index"""
    _mapping = ["min", "max"]
    _format = "2f"


class Primitive(core.MappedArray):  # LUMP 37
    type: PrimitiveType
    first_index: int  # index into PrimitiveIndex lump
    num_indices: int
    first_vertex: int  # index into PrimitiveVertices lump
    num_vertices: int
    _mapping = ["type", "first_index", "num_indices", "first_vertex", "num_vertices"]
    _format = "5H"
    _classes = {"type": PrimitiveType}


class TextureData(core.Struct):  # LUMP 2
    """Data on this view of a texture (.vmt), indexed by TextureInfo"""
    reflectivity: List[float]  # from .vtf or average colour of view rect?
    name_index: int  # index of texture name in TEXTURE_DATA_STRING_TABLE / TABLE
    size: vector.vec2  # dimensions of full texture
    view: vector.vec2  # dimensions of visible section of texture
    # NOTE: view rect top-left is determined with TextureInfo vectors & some math
    __slots__ = ["reflectivity", "name_index", "size", "view"]
    _format = "3f5i"
    _arrays = {"reflectivity": [*"rgb"], "size": [*"xy"], "view": [*"xy"]}
    _classes = {"size": vector.vec2, "view": vector.vec2}


class TextureInfo(core.Struct):  # LUMP 6
    """Texture projection info & index into TEXTURE_DATA"""
    # NOTE: TextureVector(ProjectionAxis(*s), ProjectionAxis(*t))
    texture: List[Tuple[vector.vec3, float]]  # 2 projection axes
    lightmap: List[Tuple[vector.vec3, float]]  # 2 projection axes
    flags: Surface
    texture_data: int  # index of TextureData
    __slots__ = ["texture", "lightmap", "flags", "texture_data"]
    _format = "16f2i"
    _arrays = {
        "texture": {
            "s": {"axis": [*"xyz"], "offset": None},
            "t": {"axis": [*"xyz"], "offset": None}},
        "lightmap": {
            "s": {"axis": [*"xyz"], "offset": None},
            "t": {"axis": [*"xyz"], "offset": None}}}
    _classes = {
        **{f"{t}.{a}.axis": vector.vec3 for t in ("texture", "lightmap") for a in "st"},
        "flags": Surface}


class WaterOverlay(core.Struct):  # LUMP 50
    id: int
    texture_info: int
    face_count: int  # render order in top 2 bits
    faces: List[int]
    uv: List[float]  # uncertain of order
    points: List[vector.vec3]
    origin: vector.vec3
    normal: vector.vec3
    __slots__ = ["id", "texture_info", "face_count", "faces",
                 "uv", "points", "origin", "normal"]
    _format = "i2h256i22f"
    _arrays = {"faces": 256, "uv": ["left", "right", "top", "bottom"],
               "points": {P: [*"xyz"] for P in "ABCD"},
               "origin": [*"xyz"], "normal": [*"xyz"]}
    _classes = {"origin": vector.vec3, "normal": vector.vec3}


class WorldLight(core.Struct):  # LUMP 15
    origin: vector.vec3  # origin point of this light source
    intensity: vector.vec3  # brightness scalar?
    normal: vector.vec3  # light direction (used by EmitType.SURFACE & EmitType.SPOTLIGHT)
    viscluster: int  # index of Leaf / PVS group
    type: EmitType
    style: int  # lighting style (Face style index?)
    # see core.fgd:
    stop_dot: float  # spotlight penumbra start
    stop_dot2: float  # spotlight penumbra end
    exponent: float
    radius: float
    # falloff for EmitType.SPOTLIGHT & EmitType.POINT:
    # 1 / (constant_attn + linear_attn * dist + quadratic_attn * dist**2)
    # attenuations:
    constant: float
    linear: float
    quadratic: float
    flags: WorldLightFlags
    texture_info: int  # index of TextureInfo
    parent: int  # parent entity ID
    __slots__ = ["origin", "intensity", "normal", "viscluster", "type", "style",
                 "stop_dot", "stop_dot2", "exponent", "radius",
                 "constant", "linear", "quadratic",  # attenuation
                 "flags", "texture_info", "parent"]
    _format = "9f3i7f3i"
    _arrays = {"origin": [*"xyz"], "intensity": [*"xyz"], "normal": [*"xyz"]}
    _classes = {"origin": vector.vec3, "intensity": vector.vec3, "normal": vector.vec3,
                "type": EmitType, "flags": WorldLightFlags}


# special lump classes, in alphabetical order:
class GameLumpHeader(core.MappedArray):
    id: str
    # NOTE: https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/gamebspfile.h#L25
    # -- ^ lists a few possible child lumps:
    # -- dplh: Detail Prop Lighting HDR
    # -- dplt: Detail Prop Lighting
    # -- dprp: Detail Props (procedural grass on displacements)
    # -- sprp: Static Props
    flags: int  # barely used; inconsistently indicates compression?
    version: int
    offset: int
    length: int
    _mapping = ["id", "flags", "version", "offset", "length"]
    _format = "4s2H2i"


class StaticPropv4(core.Struct):  # sprp GAME LUMP (LUMP 35) [version 4]
    """https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/gamebspfile.h#L151"""
    origin: vector.vec3
    angles: List[float]  # pitch, yaw, roll; QAngle; 0, 0, 0 = Facing East (X+)
    model_name: int  # index into GAME_LUMP.sprp.model_names
    first_leaf: int  # index into Leaf lump
    num_leafs: int  # number of Leafs after first_leaf this StaticProp is in
    solid_mode: StaticPropCollision
    flags: StaticPropFlags
    skin: int  # index of this StaticProp's skin in the .mdl
    fade_distance: List[float]  # min & max distances to fade out
    lighting_origin: vector.vec3  # position to sample lighting from
    __slots__ = [
        "origin", "angles", "name_index", "first_leaf", "num_leafs",
        "solid_mode", "flags", "skin", "fade_distance", "lighting_origin"]
    _format = "6f3H2Bi5f"
    _arrays = {
        "origin": [*"xyz"], "angles": [*"yzx"], "fade_distance": ["min", "max"],
        "lighting_origin": [*"xyz"]}
    _classes = {
        "origin": vector.vec3, "solid_mode": StaticPropCollision,
        "flags": StaticPropFlags, "lighting_origin": vector.vec3}
    # TODO: angles QAngle


class GameLump_SPRPv4:  # sprp GameLump (LUMP 35)
    StaticPropClass: object = StaticPropv4
    endianness: str = "little"  # for x360
    model_names: List[str]
    leaves: List[int]
    props: List[object]  # List[StaticPropClass]

    def __init__(self):
        self.model_names = list()
        self.leaves = list()
        self.props = list()

    @classmethod
    def from_bytes(cls, raw_lump: bytes) -> GameLump_SPRPv4:
        return cls.from_stream(io.BytesIO(raw_lump))

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> GameLump_SPRPv4:
        out = cls()
        endian = {"little": "<", "big": ">"}[cls.endianness]
        num_model_names = binary.read_struct(stream, f"{endian}I")
        out.model_names = [
            stream.read(128).replace(b"\0", b"").decode()
            for i in range(num_model_names)]
        num_leaves = binary.read_struct(stream, f"{endian}I")
        assert num_leaves != 1
        out.leaves = binary.read_struct(stream, f"{endian}{num_leaves}H")
        num_props = binary.read_struct(stream, f"{endian}I")
        out.props = lumps.BspLump.from_count(stream, num_props, cls.StaticPropClass)
        tail = stream.read()
        if len(tail) > 0:
            props_bytes = b"".join([prop.as_bytes() for prop in out.props])
            resized = (len(props_bytes) + len(tail)) / num_props
            raise RuntimeError(f"tail of {len(tail)} bytes; StaticPropClass might be {resized} bytes long")
        return out

    def as_bytes(self) -> bytes:
        assert all([
            isinstance(prop, self.StaticPropClass)
            for prop in self.props])
        endian = {"little": "<", "big": ">"}[self.endianness]
        return b"".join([
            struct.pack(f"{endian}I", len(self.model_names)),
            *[
                struct.pack("128s", model_name.encode("ascii"))
                for model_name in self.model_names],
            struct.pack(f"{endian}I", len(self.leaves)),
            struct.pack(f"{endian}{len(self.leaves)}H", *self.leaves),
            struct.pack(f"{endian}I", len(self.props)),
            *[
                prop.as_bytes()
                for prop in self.props]])

    def get_prop_model_name(self, prop_index: int) -> str:
        return self.model_names[self.props[prop_index].model_name]


class StaticPropv5(core.Struct):  # sprp GAME LUMP (LUMP 35) [version 5]
    """https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/gamebspfile.h#L168"""
    origin: vector.vec3
    angles: List[float]  # pitch, yaw, roll; QAngle; 0, 0, 0 = Facing East (X+)
    model_name: int  # index into GAME_LUMP.sprp.model_names
    first_leaf: int  # index into Leaf lump
    num_leafs: int  # number of Leafs after first_leaf this StaticProp is in
    solid_mode: StaticPropCollision
    flags: StaticPropFlags
    skin: int  # index of this StaticProp's skin in the .mdl
    fade_distance: List[float]  # min & max distances to fade out
    lighting_origin: vector.vec3  # position to sample lighting from
    forced_fade_scale: float  # relative to pixels used to render on-screen?
    __slots__ = [
        "origin", "angles", "name_index", "first_leaf", "num_leafs",
        "solid_mode", "flags", "skin", "fade_distance", "lighting_origin",
        "forced_fade_scale"]
    _format = "6f3H2Bi6f"
    _arrays = {
        "origin": [*"xyz"], "angles": [*"yzx"], "fade_distance": ["min", "max"],
        "lighting_origin": [*"xyz"]}
    _classes = {
        "origin": vector.vec3, "solid_mode": StaticPropCollision,
        "flags": StaticPropFlags, "lighting_origin": vector.vec3}
    # TODO: angles QAngle


class GameLump_SPRPv5(GameLump_SPRPv4):  # sprp GameLump (LUMP 35)
    StaticPropClass = StaticPropv5


class StaticPropv6(core.Struct):  # sprp GAME LUMP (LUMP 35) [version 6]
    """https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/gamebspfile.h#L186"""
    origin: vector.vec3
    angles: List[float]  # pitch, yaw, roll; QAngle; 0, 0, 0 = Facing East (X+)
    model_name: int  # index into GAME_LUMP.sprp.model_names
    first_leaf: int  # index into Leaf lump
    num_leafs: int  # number of Leafs after first_leaf this StaticProp is in
    solid_mode: StaticPropCollision
    flags: StaticPropFlags
    skin: int  # index of this StaticProp's skin in the .mdl
    fade_distance: List[float]  # min & max distances to fade out
    lighting_origin: vector.vec3  # position to sample lighting from
    forced_fade_scale: float  # relative to pixels used to render on-screen?
    dx_level: List[int]  # supported directX level, will not render depending on settings
    __slots__ = [
        "origin", "angles", "name_index", "first_leaf", "num_leafs",
        "solid_mode", "flags", "skin", "fade_distance", "lighting_origin",
        "forced_fade_scale", "dx_level"]
    _format = "6f3H2Bi6f2H"
    _arrays = {
        "origin": [*"xyz"], "angles": [*"yzx"], "fade_distance": ["min", "max"],
        "lighting_origin": [*"xyz"], "dx_level": ["min", "max"]}
    _classes = {
        "origin": vector.vec3, "solid_mode": StaticPropCollision,
        "flags": StaticPropFlags, "lighting_origin": vector.vec3}
    # TODO: angles QAngle


class GameLump_SPRPv6(GameLump_SPRPv5):  # sprp GameLump (LUMP 35)
    StaticPropClass = StaticPropv6


class StaticPropv7(core.Struct):  # sprp GAME LUMP (LUMP 35) [version 7]
    """https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/gamebspfile.h#L186"""
    origin: vector.vec3
    angles: List[float]  # pitch, yaw, roll; QAngle; 0, 0, 0 = Facing East (X+)
    model_name: int  # index into GAME_LUMP.sprp.model_names
    first_leaf: int  # index into Leaf lump
    num_leafs: int  # number of Leafs after first_leaf this StaticProp is in
    solid_mode: StaticPropCollision
    flags: StaticPropFlags
    skin: int  # index of this StaticProp's skin in the .mdl
    fade_distance: List[float]  # min & max distances to fade out
    lighting_origin: vector.vec3  # position to sample lighting from
    forced_fade_scale: float  # relative to pixels used to render on-screen?
    dx_level: List[int]  # supported directX level, will not render depending on settings
    diffuse_modulation: colour.RGBExponent
    __slots__ = [
        "origin", "angles", "name_index", "first_leaf", "num_leafs",
        "solid_mode", "flags", "skin", "fade_distance", "lighting_origin",
        "forced_fade_scale", "dx_level", "diffuse_modulation"]
    _format = "6f3H2Bi6f2H4B"
    _arrays = {
        "origin": [*"xyz"], "angles": [*"yzx"], "fade_distance": ["min", "max"],
        "lighting_origin": [*"xyz"], "dx_level": ["min", "max"],
        "diffuse_modulation": [*"rgba"]}
    _classes = {
        "origin": vector.vec3, "solid_mode": StaticPropCollision,
        "flags": StaticPropFlags, "lighting_origin": vector.vec3,
        "diffuse_modulation": colour.RGBExponent}
    # TODO: "angles": QAngle


class GameLump_SPRPv7(GameLump_SPRPv6):  # sprp GameLump (LUMP 35)
    StaticPropClass = StaticPropv7


class TextureDataStringData(list):  # LUMP 43
    def __init__(self, iterable: List[str] = tuple()):
        super().__init__(iterable)

    def as_bytes(self) -> bytes:
        return b"\0".join([
            t.encode("ascii")
            for t in self]) + b"\0"

    @classmethod
    def from_bytes(cls, raw_lump: bytes) -> TextureDataStringData:
        return cls([
            t.decode("ascii", errors="ignore")
            for t in raw_lump[:-1].split(b"\0")])


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = {
    "DISPLACEMENT_TRIANGLES":    {0: DisplacementTriangle},
    "FACE_IDS":                  {0: shared.UnsignedShorts},
    "FACE_MACRO_TEXTURE_INFO":   {0: shared.Shorts},
    "LEAF_BRUSHES":              {0: shared.UnsignedShorts},
    "LEAF_FACES":                {0: shared.UnsignedShorts},
    "PRIMITIVE_INDICES":         {0: shared.UnsignedShorts},
    "SURFEDGES":                 {0: shared.Ints},
    "TEXTURE_DATA_STRING_TABLE": {0: shared.UnsignedShorts},
    "VERTEX_NORMAL_INDICES":     {0: shared.UnsignedShorts}}

LUMP_CLASSES = {
    "AREAS":                     {0: Area},
    "AREA_PORTALS":              {0: AreaPortal},
    "BRUSHES":                   {0: Brush},
    "BRUSH_SIDES":               {0: BrushSide},
    "CLIP_PORTAL_VERTICES":      {0: quake.Vertex},
    "CUBEMAPS":                  {0: Cubemap},
    "DISPLACEMENT_INFO":         {0: DisplacementInfo},
    "DISPLACEMENT_VERTICES":     {0: DisplacementVertex},
    "EDGES":                     {0: quake.Edge},
    "FACES":                     {1: Face},
    "LEAVES":                    {0: Leaf},
    "LEAF_AMBIENT_INDEX":        {0: LeafAmbientIndex},
    "LEAF_AMBIENT_INDEX_HDR":    {0: LeafAmbientIndex},
    "LEAF_AMBIENT_LIGHTING":     {1: LeafAmbientSample},
    "LEAF_AMBIENT_LIGHTING_HDR": {1: LeafAmbientSample},
    "LEAF_WATER_DATA":           {0: LeafWaterData},
    "MODELS":                    {0: Model},
    "NODES":                     {0: Node},
    "ORIGINAL_FACES":            {0: Face},
    "OVERLAY":                   {0: Overlay},
    "OVERLAY_FADES":             {0: OverlayFade},
    "PLANES":                    {0: quake.Plane},
    "PRIMITIVES":                {0: Primitive},
    "PRIMITIVE_VERTICES":        {0: quake.Vertex},
    "TEXTURE_DATA":              {0: TextureData},
    "TEXTURE_INFO":              {0: TextureInfo},
    "VERTEX_NORMALS":            {0: quake.Vertex},
    "VERTICES":                  {0: quake.Vertex},
    "WATER_OVERLAYS":            {0: WaterOverlay},
    "WORLD_LIGHTS":              {0: WorldLight},
    "WORLD_LIGHTS_HDR":          {0: WorldLight}}

SPECIAL_LUMP_CLASSES = {
    "ENTITIES":                 {0: shared.Entities},
    "PAKFILE":                  {0: archives.pkware.Zip},
    # "PHYSICS_COLLIDE":          {0: physics.CollideLump},  # BROKEN .as_bytes()
    "PHYSICS_DISPLACEMENT":     {0: physics.Displacement},
    "TEXTURE_DATA_STRING_DATA": {0: TextureDataStringData},
    "VISIBILITY":               {0: quake2.Visibility}}


GAME_LUMP_HEADER = GameLumpHeader

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = {
    "sprp": {
        4: GameLump_SPRPv4,
        5: GameLump_SPRPv5,
        6: GameLump_SPRPv6,
        7: GameLump_SPRPv7}}
# TODO: more GameLump definitions:
# -- https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/gamebspfile.h#L25


# branch exclusive methods, in alphabetical order:
def face_mesh(bsp, face_index: int) -> List[geometry.Mesh]:
    face = bsp.FACES[face_index]
    normal = bsp.PLANES[face.plane].normal
    # texture
    texture_info = bsp.TEXTURE_INFO[face.texture_info]
    texture_data = bsp.TEXTURE_DATA[texture_info.texture_data]
    colour = (*texture_data.reflectivity, 1)  # vertex colour
    texture_vector = texture.TextureVector(
        texture.ProjectionAxis(*texture_info.texture.s),
        texture.ProjectionAxis(*texture_info.texture.t))
    if texture_data.view.x != 0:
        texture_vector.s.scale = (1 / texture_data.view.x)
    if texture_data.view.y != 0:
        texture_vector.t.scale = (1 / texture_data.view.y)
    lightmap_vector = texture.TextureVector(
        texture.ProjectionAxis(*texture_info.lightmap.s),
        texture.ProjectionAxis(*texture_info.lightmap.t))
    vertices = list()
    first_edge = face.first_edge
    for surfedge in bsp.SURFEDGES[first_edge:(first_edge + face.num_edges)]:
        if surfedge >= 0:  # +ve index
            position = bsp.VERTICES[bsp.EDGES[surfedge][0]]
        else:  # -ve index
            position = bsp.VERTICES[bsp.EDGES[-surfedge][1]]
        texture_uv = texture_vector.uv_at(position)
        # NOTE: not checking if face.lightmap.size is 0x0
        lightmap_uv = lightmap_vector.uv_at(position)
        # TODO: somehow move this mess into .uv_at(position)
        lightmap_uv -= face.lightmap.mins
        lightmap_uv += vector.vec2(0.5, 0.5)
        lightmap_uv = vector.vec2(
            lightmap_uv.x / (face.lightmap.size.x + 1),
            lightmap_uv.y / (face.lightmap.size.y + 1))
        lightmap_uv = vector.vec2(
            max(0, min(lightmap_uv.x, 1)),
            max(0, min(lightmap_uv.y, 1)))
        vertices.append(
            geometry.Vertex(position, normal, texture_uv, lightmap_uv, colour=colour))
    if face.primitives.count == 0:
        polygons = [geometry.Polygon(vertices)]
    else:  # T-junction
        polygons = list()
        offset, length = face.first_primitive, face.primitives.count
        for primitive in bsp.PRIMITIVES[offset:offset+length]:
            offset, length = primitive.first_index, primitive.num_indices
            indices = bsp.PRIMITIVE_INDICES[offset:offset+length]
            if primitive.type == PrimitiveType.TRIANGLE_LIST:
                assert len(indices) % 3 == 0
                for i in range(0, len(indices), 3):
                    polygons.append(geometry.Polygon([
                        vertices[indices[i + j]] for j in range(3)]))
            else:  # TRIANGLE_STRIP
                raise NotImplementedError("TRIANGLE_STRIP Primitive")
    texture_name = bsp.TEXTURE_DATA_STRING_DATA[texture_data.name_index]
    return geometry.Mesh(geometry.Material(texture_name), polygons)


def displacement_indices(power: int) -> List[List[int]]:  # for displacement_mesh
    """returns an array of indices ((2 ** power) + 1) ** 2 long"""
    power2 = 2 ** power
    power2A = power2 + 1
    power2B = power2 + 2
    power2C = power2 + 3
    tris = []
    for line in range(power2):
        line_offset = power2A * line
        for block in range(2 ** (power - 1)):
            offset = line_offset + 2 * block
            if line % 2 == 0:  # |\|/|
                tris.append([offset + 0, offset + power2A, offset + 1])
                tris.append([offset + power2A, offset + power2B, offset + 1])
                tris.append([offset + power2B, offset + power2C, offset + 1])
                tris.append([offset + power2C, offset + 2, offset + 1])
            else:  # |/|\|
                tris.append([offset + 0, offset + power2A, offset + power2B])
                tris.append([offset + 1, offset + 0, offset + power2B])
                tris.append([offset + 2, offset + 1, offset + power2B])
                tris.append([offset + power2C, offset + 2, offset + power2B])
    return tris


def displacement_mesh(bsp, face_index: int) -> geometry.Mesh:
    # TODO: lightmap uvs (DISPLACEMENT_LIGHTMAP_* lumps)
    face = bsp.FACES[face_index]
    assert face.displacement_info != -1, "not a displacement"
    disp_info = bsp.DISPLACEMENT_INFO[face.displacement_info]
    base_mesh = bsp.face_mesh(face_index)
    assert len(base_mesh.polygons) == 1
    assert len(base_mesh.polygons[0].vertices) == 4
    # rotate quad indices; point closest to start should be index 0
    base_quad = {v.position: v for v in base_mesh.polygons[0].vertices}
    quad = list(base_quad.keys())
    if disp_info.start_position in base_quad:
        A = disp_info.start_position
    else:
        A = sorted(base_quad, key=lambda P: (disp_info.start_position - P).magnitude())[0]
    A_index = quad.index(A)
    quad = [*quad[A_index:], *quad[:A_index]]
    A, B, C, D = [base_quad[P] for P in quad]
    # displacement vertices
    offset, length = disp_info.first_displacement_vertex, disp_info.num_displacement_vertices
    disp_verts = bsp.DISPLACEMENT_VERTICES[offset:offset+length]
    power2 = 1 << disp_info.power
    vertices = list()
    for i, disp_vertex in enumerate(disp_verts):
        t1 = i % (power2 + 1) / power2  # y position
        t2 = i // (power2 + 1) / power2  # x position
        bary = A.lerp(D, t1).lerp(B.lerp(C, t1), t2)
        position = bary.position + (disp_vertex.normal * disp_vertex.distance)
        normal = disp_vertex.normal if vector.dot(disp_vertex.normal, A.normal) < 0 else -disp_vertex.normal
        texture_uv = bary.uv0
        lightmap_uv = bary.uv1
        colour = (*A.colour[:3], disp_vertex.alpha)
        vertices.append(geometry.Vertex(position, normal, texture_uv, lightmap_uv, colour=colour))
    polygons = [geometry.Polygon([vertices[i] for i in tri]) for tri in displacement_indices(disp_info.power)]
    return geometry.Mesh(base_mesh.material, polygons)


def model(bsp, model_index: int) -> geometry.Model:
    # entity
    entities = bsp.ENTITIES.search(model=f"*{model_index}")
    model_entity = entities[0] if len(entities) != 0 else dict()
    origin = model_entity.get("origin", "0 0 0")
    origin = vector.vec3(*origin.split())
    pitch, yaw, roll = model_entity.get("angles", "0 0 0").split()
    angles = vector.vec3(roll, pitch, yaw)
    # geometry
    model = bsp.MODELS[model_index]
    face_indices = range(model.first_face, model.first_face + model.num_faces)
    meshes = [
        bsp.face_mesh(i) if bsp.FACES[i].displacement_info == -1 else bsp.displacement_mesh(i)
        for i in face_indices]
    out = geometry.Model(meshes, origin, angles)
    out.entity = model_entity
    return out


def textures_of_brush(bsp, brush_index: int) -> List[str]:
    out = set()
    brush = bsp.BRUSHES[brush_index]
    for brush_side in bsp.BRUSH_SIDES[brush.first_side:brush.first_side + brush.num_sides]:
        texture_info = bsp.TEXTURE_INFO[brush_side.texture_info]
        texture_data = bsp.TEXTURE_DATA[texture_info.texture_data]
        texture_name = bsp.TEXTURE_DATA_STRING_DATA[texture_data.name_index]
        out.add(texture_name)
    return sorted(out)


methods = [quake.leaves_of_node, textures_of_brush, face_mesh, displacement_mesh, model, shared.worldspawn_volume]
methods = {method.__name__: method for method in methods}
