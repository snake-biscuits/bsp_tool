# https://developer.valvesoftware.com/wiki/Source_BSP_File_Format
# https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/bspfile.h
# https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/bspflags.h
# https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/bsplib.cpp
from __future__ import annotations
import enum
import io
import itertools
import struct
from typing import List

from .. import base
from .. import shared
from .. import vector
from ..id_software import quake
from ..id_software import quake2


FILE_MAGIC = b"VBSP"

BSP_VERSION = 19

GAME_PATHS = {"Counter-Strike: Source": "counter-strike source/cstrike",
              "Half-Life Deathmatch: Source": "Half-Life 1 Source Deathmatch/hl1mp",
              "Half-Life 2": "Half-Life 2/hl2",
              "Half-Life 2: Episode 1": "half-life 2/episodic"}

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
    DISPLACEMENT_TRIS = 48
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


class LumpHeader(base.MappedArray):
    _mapping = ["offset", "length", "version", "fourCC"]
    _format = "4I"

# changes from GoldSrc -> Source:
# MipTexture.flags -> TextureInfo.flags (Surface enum)


# a rough map of the relationships between lumps:

#                                 /-> SurfEdge -> Edge -> Vertex
# Node -> Leaf -> LeafFace -> Face -> Plane
#                                \--> TextureInfo -> TextureData -> TextureDataStringTable
#                                 \-> DisplacementInfo -> DisplacementVertex

# Leaf -> LeafBrush -> Brush -> BrushSide -> TextureInfo
#                                        \-> Plane

# FaceID is paralell with Faces & lists Hammer ids per face

# Leaf is Parallel with LeafAmbientIndex
# LeafAmbientIndex -> LeafAmbientSample

# ClipPortalVertices are AreaPortal geometry [unverified]


# engine limits: (2013 SDK bspfile.h)
class MIN(enum.Enum):
    DISPLACEMENT_POWER = 2


class MAX(enum.Enum):
    # misc:
    CUBEMAP_SAMPLES = 1024
    DISPLACEMENT_POWER = 4
    DISPLACEMENT_CORNER_NEIGHBORS = 4
    ENTITY_KEY, ENTITY_VALUE = 32, 1024  # key value pair sizes
    LIGHTMAPS = 4  # max lightmap styles?
    LIGHTMAP_DIMENSION_WITH_BORDER_BRUSH = 35  # "vbsp cut limit" +1 (to account for rounding errors)
    LIGHTMAP_DIMENSION_WITHOUT_BORDER_BRUSH = 32
    LIGHTMAP_DIMENSION_WITH_BORDER_DISPLACEMENT = 128
    LIGHTMAP_DIMENSION_WITHOUT_BORDER_DISPLACEMENT = 125
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
    TEXDATA_STRING_DATA = 256000
    TEXDATA_STRING_TABLE = 65536
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


class DisplacementFlags(enum.IntFlag):
    """DisplacementInfo collision flags"""
    UNUSED = 1
    NO_PHYS = 2
    NO_HULL = 4
    NO_RAY = 8


class DispTris(enum.IntFlag):
    """DisplacementTriangle flags"""
    SURFACE = 0x01
    WALKABLE = 0x02
    BUILDABLE = 0x04
    SURFPROP1 = 0x08  # use surfaceprop of first material?
    SURFPROP2 = 0x10  # use surfaceprop of second material?


class EmitType(enum.Enum):
    SURFACE = 0x00  # 90 degree spotlight
    POINT = 0x01
    SPOTLIGHT = 0x02  # spotlight w/ penumbra
    SKY_LIGHT = 0x03  # directional light w/ no falloff (surface must trace to SKY texture)
    QUAKE_LIGHT = 0x04  # linear falloff, non-lambertian
    SKY_AMBIENT = 0x05  # spherical light w/ no falloff (surface must trace to SKY texture)


class SPRP_flags(enum.IntFlag):
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
class Area(base.MappedArray):  # LUMP 20
    num_area_portals: int   # number of AreaPortals after first_area_portal in this Area
    first_area_portal: int  # index of first AreaPortal
    _mapping = ["num_area_portals", "first_area_portal"]
    _format = "2i"


class AreaPortal(base.MappedArray):  # LUMP 21
    # public/bspfile.h dareaportal_t &  utils/vbsp/portals.cpp EmitAreaPortals
    portal_key: int                # for tying to entities
    first_clip_portal_vert: int    # index into the ClipPortalVertex lump
    num_clip_portal_vertices: int  # number of ClipPortalVertices after first_clip_portal_vertex in this AreaPortal
    plane: int                     # index of into the Plane lump
    _mapping = ["portal_key", "other_area", "first_clip_portal_vertex",
                "num_clip_portal_vertices", "plane"]
    _format = "4Hi"


class Brush(base.Struct):  # LUMP 18
    """Assumed to carry over from .vmf"""
    first_side: int  # index into BrushSide lump
    num_sides: int   # number of BrushSides after first_side in this Brush
    contents: int    # contents bitflags
    __slots__ = ["first_side", "num_sides", "contents"]
    _format = "3i"


class BrushSide(base.Struct):  # LUMP 19
    plane: int      # index into Plane lump
    texture_info: int   # index into TextureInfo lump
    displacement_info: int  # index into DisplacementInfo lump
    bevel: int      # bool? indicates if side is a bevel plane (BSPVERSION 7)
    __slots__ = ["plane", "texture_info", "displacement_info", "bevel"]
    _format = "H3h"


class Cubemap(base.Struct):  # LUMP 42
    """Location (origin) & resolution (size)"""
    origin: List[float]  # origin.xyz
    size: int  # texture dimension (each face of a cubemap is square)
    __slots__ = ["origin", "size"]
    _format = "4i"
    _arrays = {"origin": [*"xyz"]}


class DisplacementInfo(base.Struct):  # LUMP 26
    """Holds the information defining a displacement"""
    start_position: List[float]  # rough XYZ of the vertex to orient around
    displacement_vert_start: int  # index of first DisplacementVertex
    displacement_tri_start: int   # index of first DisplacementTriangle
    # ^ length of sequence for each varies depending on power
    power: int  # level of subdivision
    flags: int  # see DisplacementFlags
    min_tesselation: int  # for tesselation shaders / triangle assembley?
    smoothing_angle: float  # ?
    contents: int  # contents bitflags
    map_face: int  # index of Face?
    __slots__ = ["start_position", "displacement_vert_start", "displacement_tri_start",
                 "power", "flags", "min_tesselation", "smoothing_angle", "contents",
                 "map_face", "lightmap_alpha_start", "lightmap_sample_position_start",
                 "edge_neighbours", "corner_neighbours", "allowed_vertices"]
    _format = "3f3iHhfiH2i88c10i"
    _arrays = {"start_position": [*"xyz"], "edge_neighbours": 44,
               "corner_neighbours": 44, "allowed_vertices": 10}
    # TODO: map neighbours with base.Struct subclasses, rather than MappedArrays
    # both the __init__ & flat methods may need some changes to accommodate this

    # def __init__(self, _tuple):
    #     super(base.Struct, self).__init__(_tuple)
    #     self.edge_neighbours = ...
    #     self.corner_neighbours = ...


class DisplacementVertex(base.Struct):  # LUMP 33
    """The positional deformation & blend value of a point in a displacement"""
    vector: List[float]  # direction of vertex offset from barymetric base
    distance: float      # length to scale deformation vector by
    alpha: float         # [0-1] material blend factor
    __slots__ = ["vector", "distance", "alpha"]
    _format = "5f"
    _arrays = {"vector": [*"xyz"]}


class Face(base.Struct):  # LUMP 7
    """makes up Models (including worldspawn), also referenced by LeafFaces"""
    plane: int       # index into Plane lump
    side: int        # "faces opposite to the node's plane direction"
    on_node: bool    # if False, face is in a leaf
    first_edge: int  # index into the SurfEdge lump
    num_edges: int   # number of SurfEdges after first_edge in this Face
    texture_info: int    # index into the TextureInfo lump
    displacement_info: int   # index into the DisplacementInfo lump (None if -1)
    surface_fog_volume_id: int  # t-junctions? QuakeIII vertex-lit fog?
    styles: int      # 4 different lighting states? "switchable lighting info"
    light_offset: int  # index of first pixel in LIGHTING / LIGHTING_HDR
    area: float  # surface area of this face
    lightmap: List[float]
    # lightmap.mins  # dimensions of lightmap segment
    # lightmap.size  # scalars for lightmap segment
    original_face: int  # ORIGINAL_FACES index, -1 if this is an original face
    # NOTE: num_primitives top bit is a flag for shadows, this means a max of 32768 primitives are allowed
    num_primitives: int  # non-zero if t-juncts are present? number of Primitives
    first_primitive_id: int  # index of Primitive
    smoothing_groups: int    # lightmap smoothing group
    __slots__ = ["plane", "side", "on_node", "first_edge", "num_edges",
                 "texture_info", "displacement_info", "surface_fog_volume_id", "styles",
                 "light_offset", "area", "lightmap", "original_face",
                 "num_primitives", "first_primitive_id", "smoothing_groups"]
    _format = "Hb?i4h4bif5i2HI"
    _arrays = {"styles": 4, "lightmap": {"mins": [*"xy"], "size": ["width", "height"]}}


class Leaf(base.Struct):  # LUMP 10
    """Endpoint of a vis tree branch, a pocket of Faces"""
    contents: int  # Contents flags
    cluster: int   # index of this Leaf's cluster (leaf group in VISIBILITY lump)
    area_flags: int  # area & flags bitfield (short area:9; short flags:7;)
    # why was this done when the struct is padded by one short anyway?
    mins: List[float]  # bounding box minimums along XYZ axes
    maxs: List[float]  # bounding box maximums along XYZ axes
    first_leaf_face: int   # index of first LeafFace
    num_leaf_faces: int    # number of LeafFaces
    first_leaf_brush: int  # index of first LeafBrush
    num_leaf_brushes: int  # number of LeafBrushes
    leaf_water_data_id: int  # -1 if this leaf isn't submerged
    padding: int  # should be 0
    cube: List[List[int]]  # CompressedLightCube; unsure about orientation / face order
    __slots__ = ["contents", "cluster", "area_flags", "mins", "maxs",
                 "first_leaf_face", "num_leaf_faces", "first_leaf_brush",
                 "num_leaf_brushes", "leaf_water_data_id", "cube"]
    _format = "i8h4H2h24B"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"],
               "cube": {x: [*"rgbe"] for x in "ABCDEF"}}  # integer keys in _mapping would be nicer

    @property
    def area(self):
        return self.area_flags >> 7

    @area.setter
    def area(self, new_area: int):
        self.area_flags = (new_area & 0x1FF) << 7 + self.flags

    @property
    def flags(self):
        return self.area_flags & 0x7F

    @flags.setter
    def flags(self, new_flags: int):
        self.area_flags = self.area << 7 + new_flags & 0x7F


class LeafAmbientIndex(base.MappedArray):  # LUMP 52
    num_samples: int
    first_sample: int
    _format = "2h"
    _mapping = ["num_samples", "first_sample"]


class LeafAmbientSample(base.MappedArray):  # LUMP 56
    """cube of lighting samples"""
    cube: List[List[int]]  # unsure about orientation / face order
    vector: List[int]
    padding: int
    __slots__ = ["cube", "vector", "padding"]
    _format = "28B"
    _arrays = {"cube": {x: [*"rgbe"] for x in "ABCDEF"},  # integer keys in _mapping would be nicer
               "vector": [*"xyz"]}


class LeafWaterData(base.MappedArray):  # LUMP 36
    surface_z: float  # global Z height of the water's surface
    min_z: float  # bottom of the water volume?
    texture_data: int  # index to this LeafWaterData's TextureData
    _format = "2fI"
    _mapping = ["surface_z", "min_z", "texture_data"]


class Model(base.Struct):  # LUMP 14
    """Brush based entities; Index 0 is worldspawn"""
    mins: List[float]  # bounding box minimums along XYZ axes
    maxs: List[float]  # bounding box maximums along XYZ axes
    origin: List[float]  # center of model, worldspawn is always at 0 0 0
    head_node: int   # index into Node lump
    first_face: int  # index into Face lump
    num_faces: int   # number of Faces after first_face in this Model
    __slots__ = ["mins", "maxs", "origin", "head_node", "first_face", "num_faces"]
    _format = "9f3i"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"], "origin": [*"xyz"]}


class Node(base.Struct):  # LUMP 5
    plane: int            # index into Plane lump
    children: List[int]   # 2 indices; Node if positive, Leaf if negative
    mins: List[float]     # bounding box minimums along XYZ axes
    maxs: List[float]     # bounding box maximums along XYZ axes
    first_face: int       # index into Face lump
    num_faces: int        # number of Faces after first_face in this Node
    area: int             # index into Area lump, if all children are in the same area, else -1
    padding: int          # should be empty
    __slots__ = ["plane", "children", "mins", "maxs", "first_face", "num_faces",
                 "area", "padding"]
    # area is appears to always be 0
    # however leaves correctly connect to all areas
    _format = "3i6h2H2h"
    _arrays = {"children": 2, "mins": [*"xyz"], "maxs": [*"xyz"]}


class Overlay(base.Struct):  # LUMP 45
    id: int
    texture_info: int
    face_count: int  # render order in top 2 bits
    faces: List[int]
    uv: List[float]  # uncertain of order
    points: List[List[float]]
    origin: List[float]
    normal: List[float]
    __slots__ = ["id", "texture_info", "face_count", "faces",
                 "uv", "points", "origin", "normal"]
    _format = "i2h64i22f"
    _arrays = {"faces": 64, "uv": ["left", "right", "top", "bottom"],
               "points": {P: [*"xyz"] for P in "ABCD"}}


class OverlayFade(base.MappedArray):  # LUMP 60
    """Holds fade distances for the overlay of the same index"""
    _mapping = ["min", "max"]
    _format = "2f"


class Primitive(base.MappedArray):  # LUMP 37
    type: int
    first_index: int  # index into PrimitiveIndex lump
    num_indices: int
    first_vertex: int  # index into PrimitiveVertices lump
    num_vertices: int
    _mapping = ["type", "first_index", "num_indices", "first_vertex", "num_vertices"]
    _format = "B4H"


class TextureData(base.Struct):  # LUMP 2
    """Data on this view of a texture (.vmt), indexed by TextureInfo"""
    reflectivity: List[float]
    name_index: int  # index of texture name in TEXTURE_DATA_STRING_TABLE / TABLE
    size: List[int]  # dimensions of full texture
    view: List[int]  # dimensions of visible section of texture
    __slots__ = ["reflectivity", "name_index", "size", "view"]
    _format = "3f5i"
    _arrays = {"reflectivity": [*"rgb"], "size": ["width", "height"], "view": ["width", "height"]}


class TextureInfo(base.Struct):  # LUMP 6
    """Texture projection info & index into TEXTURE_DATA"""
    texture: List[List[float]]  # 2 texture projection vectors
    lightmap: List[List[float]]  # 2 lightmap projection vectors
    flags: int  # Surface flags
    texture_data: int  # index of TextureData
    __slots__ = ["texture", "lightmap", "flags", "texture_data"]
    _format = "16f2i"
    _arrays = {"texture": {"s": [*"xyz", "offset"], "t": [*"xyz", "offset"]},
               "lightmap": {"s": [*"xyz", "offset"], "t": [*"xyz", "offset"]}}
    # ^ nested MappedArrays; texture.s.x, texture.t.x


class WaterOverlay(base.Struct):  # LUMP 50
    id: int
    texture_info: int
    face_count: int  # render order in top 2 bits
    faces: List[int]
    uv: List[float]  # uncertain of order
    points: List[List[float]]
    origin: List[float]
    normal: List[float]
    __slots__ = ["id", "texture_info", "face_count", "faces",
                 "uv", "points", "origin", "normal"]
    _format = "i2h256i22f"
    _arrays = {"faces": 256, "uv": ["left", "right", "top", "bottom"],
               "points": {P: [*"xyz"] for P in "ABCD"}}


class WorldLight(base.Struct):  # LUMP 15
    """A static light"""
    origin: List[float]  # origin point of this light source
    intensity: float     # light strength scalar
    normal: List[float]  # light direction (used by EmitType.SURFACE & EmitType.SPOTLIGHT)
    cluster: int  # viscluster (leaf group)
    emit_type: int  # EmitType
    style: int  # lighting style
    # see base.fgd:
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
    # ^ these factor into some equation...
    flags: int  # WorldLightFlags
    texture_info: int  # index of TextureInfo
    owner: int  # parent entity ID
    __slots__ = ["origin", "intensity", "normal", "cluster", "emit_type", "style",
                 "stop_dot", "stop_dot2", "exponent", "radius",
                 "constant", "linear", "quadratic",  # attenuation
                 "flags", "texture_info", "owner"]
    _format = "9f3i7f3i"
    _arrays = {"origin": [*"xyz"], "intensity": [*"xyz"], "normal": [*"xyz"]}


# special lump classes, in alphabetical order:
class GameLumpHeader(base.MappedArray):
    id: str
    # NOTE: https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/gamebspfile.h#L25
    # -- ^ lists a few possible child lumps:
    # -- dplh: Detail Prop Lighting HDR
    # -- dplt: Detail Prop Lighting
    # -- dprp: Detail Props (procedural grass on displacements)
    # -- sprp: Static Props
    flags: int  # use unknown
    version: int
    offset: int
    length: int
    _mapping = ["id", "flags", "version", "offset", "length"]
    _format = "4s2H2i"


class GameLump_SPRP:
    """use `lambda raw_lump: GameLump_SPRP(raw_lump, StaticPropvXX)` to implement"""
    StaticPropClass: object  # StaticPropvX
    model_names: List[str]
    leaves: List[int]
    props: List[object] | List[bytes]  # List[StaticPropClass]

    def __init__(self, raw_sprp_lump: bytes, StaticPropClass: object):
        sprp_lump = io.BytesIO(raw_sprp_lump)
        model_name_count = int.from_bytes(sprp_lump.read(4), "little")
        model_names = struct.iter_unpack("128s", sprp_lump.read(128 * model_name_count))
        setattr(self, "model_names", [t[0].replace(b"\0", b"").decode() for t in model_names])
        leaf_count = int.from_bytes(sprp_lump.read(4), "little")
        leaves = itertools.chain(*struct.iter_unpack("H", sprp_lump.read(2 * leaf_count)))
        setattr(self, "leaves", list(leaves))
        prop_count = int.from_bytes(sprp_lump.read(4), "little")
        if StaticPropClass is None:
            raw_props = sprp_lump.read()
            if len(raw_props) == 0:
                setattr(self, "props", [])
            else:
                prop_size = len(raw_props) // prop_count
                props = list()
                for i in range(prop_count):
                    props.append(raw_props[i * prop_size:(i + 1) * prop_size])
                setattr(self, "props", props)
        else:
            read_size = struct.calcsize(StaticPropClass._format) * prop_count
            props = struct.iter_unpack(StaticPropClass._format, sprp_lump.read(read_size))
            setattr(self, "props", list(map(StaticPropClass.from_tuple, props)))
        here = sprp_lump.tell()
        end = sprp_lump.seek(0, 2)
        assert here == end, "Had some leftover bytes; StaticPropClass._format is incorrect!"

    def as_bytes(self) -> bytes:
        if len(self.props) > 0:
            prop_bytes = [struct.pack(self.StaticPropClass._format, *p.flat()) for p in self.props]
        else:
            prop_bytes = []
        return b"".join([int.to_bytes(len(self.model_names), 4, "little"),
                         *[struct.pack("128s", n) for n in self.model_names],
                         int.to_bytes(len(self.leaves), 4, "little"),
                         *[struct.pack("H", L) for L in self.leaves],
                         int.to_bytes(len(self.props), 4, "little"),
                         *prop_bytes])


class StaticPropv4(base.Struct):  # sprp GAME LUMP (LUMP 35)
    """https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/gamebspfile.h#L151"""
    origin: List[float]  # origin.xyz
    angles: List[float]  # origin.yzx  QAngle; Z0 = East
    model_name: int  # index into GAME_LUMP.sprp.model_names
    first_leaf: int  # index into Leaf lump
    num_leafs: int  # number of Leafs after first_leaf this StaticPropv10 is in
    solid_mode: int  # collision flags enum
    flags: int  # other flags
    skin: int  # index of this StaticProp's skin in the .mdl
    fade_distance: List[float]  # min & max distances to fade out
    lighting_origin: List[float]  # xyz position to sample lighting from
    __slots__ = ["origin", "angles", "name_index", "first_leaf", "num_leafs",
                 "solid_mode", "flags", "skin", "fade_distance", "lighting_origin"]
    _format = "6f3H2Bi5f"
    _arrays = {"origin": [*"xyz"], "angles": [*"yzx"], "fade_distance": ["min", "max"],
               "lighting_origin": [*"xyz"]}


class StaticPropv5(base.Struct):  # sprp GAME LUMP (LUMP 35) [version 5]
    """https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/gamebspfile.h#L168"""
    origin: List[float]  # origin.xyz
    angles: List[float]  # origin.yzx  QAngle; Z0 = East
    model_name: int  # index into GAME_LUMP.sprp.model_names
    first_leaf: int  # index into Leaf lump
    num_leafs: int  # number of Leafs after first_leaf this StaticPropv10 is in
    solid_mode: int  # collision flags enum
    flags: int  # other flags
    skin: int  # index of this StaticProp's skin in the .mdl
    fade_distance: List[float]  # min & max distances to fade out
    lighting_origin: List[float]  # xyz position to sample lighting from
    forced_fade_scale: float  # relative to pixels used to render on-screen?
    __slots__ = ["origin", "angles", "name_index", "first_leaf", "num_leafs",
                 "solid_mode", "flags", "skin", "fade_distance", "lighting_origin",
                 "forced_fade_scale"]
    _format = "6f3H2Bi6f"
    _arrays = {"origin": [*"xyz"], "angles": [*"yzx"], "fade_distance": ["min", "max"],
               "lighting_origin": [*"xyz"]}


class StaticPropv6(base.Struct):  # sprp GAME LUMP (LUMP 35) [version 6]
    """https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/gamebspfile.h#L186"""
    origin: List[float]  # origin.xyz
    angles: List[float]  # origin.yzx  QAngle; Z0 = East
    model_name: int  # index into GAME_LUMP.sprp.model_names
    first_leaf: int  # index into Leaf lump
    num_leafs: int  # number of Leafs after first_leaf this StaticPropv10 is in
    solid_mode: int  # collision flags enum
    flags: int  # other flags
    skin: int  # index of this StaticProp's skin in the .mdl
    fade_distance: List[float]  # min & max distances to fade out
    lighting_origin: List[float]  # xyz position to sample lighting from
    forced_fade_scale: float  # relative to pixels used to render on-screen?
    dx_level: List[int]  # supported directX level, will not render depending on settings
    __slots__ = ["origin", "angles", "name_index", "first_leaf", "num_leafs",
                 "solid_mode", "flags", "skin", "fade_distance", "lighting_origin",
                 "forced_fade_scale", "dx_level"]
    _format = "6f3H2Bi6f2H"
    _arrays = {"origin": [*"xyz"], "angles": [*"yzx"], "fade_distance": ["min", "max"],
               "lighting_origin": [*"xyz"], "dx_level": ["min", "max"]}


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = {"DISPLACEMENT_TRIS":         {0: shared.UnsignedShorts},
                      "FACE_IDS":                  {0: shared.UnsignedShorts},
                      "FACE_MACRO_TEXTURE_INFO":   {0: shared.Shorts},
                      "LEAF_BRUSHES":              {0: shared.UnsignedShorts},
                      "LEAF_FACES":                {0: shared.UnsignedShorts},
                      "PRIMITIVE_INDICES":         {0: shared.UnsignedShorts},
                      "SURFEDGES":                 {0: shared.Ints},
                      "TEXTURE_DATA_STRING_TABLE": {0: shared.UnsignedShorts},
                      "VERTEX_NORMAL_INDICES":     {0: shared.UnsignedShorts}}

LUMP_CLASSES = {"AREAS":                     {0: Area},
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
                "OVERLAY":                   {0: Overlay},
                "OVERLAY_FADES":             {0: OverlayFade},
                "ORIGINAL_FACES":            {0: Face},
                "PLANES":                    {0: quake.Plane},
                "PRIMITIVES":                {0: Primitive},
                "PRIMITIVE_VERTICES":        {0: quake.Vertex},
                "TEXTURE_DATA":              {0: TextureData},
                "TEXTURE_INFO":              {0: TextureInfo},
                "VERTICES":                  {0: quake.Vertex},
                "VERTEX_NORMALS":            {0: quake.Vertex},
                "WATER_OVERLAYS":            {0: WaterOverlay},
                "WORLD_LIGHTS":              {0: WorldLight},
                "WORLD_LIGHTS_HDR":          {0: WorldLight}}

SPECIAL_LUMP_CLASSES = {"ENTITIES":                 {0: shared.Entities},
                        "TEXTURE_DATA_STRING_DATA": {0: shared.TextureDataStringData},
                        "PAKFILE":                  {0: shared.PakFile},
                        "PHYSICS_COLLIDE":          {0: shared.physics.CollideLump},
                        "VISIBILITY":               {0: quake2.Visibility}}


GAME_LUMP_HEADER = GameLumpHeader

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = {"sprp": {4: lambda raw_lump: GameLump_SPRP(raw_lump, StaticPropv4),
                              5: lambda raw_lump: GameLump_SPRP(raw_lump, StaticPropv5),
                              6: lambda raw_lump: GameLump_SPRP(raw_lump, StaticPropv6)}}
# TODO: more GameLump definitions:
# -- https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/gamebspfile.h#L25


# branch exclusive methods, in alphabetical order:
def vertices_of_face(bsp, face_index: int) -> List[float]:
    """Format: [Position, Normal, TexCoord, LightCoord, Colour]"""
    # TODO: primitives
    face = bsp.FACES[face_index]
    uvs, uv2s = [], []
    first_edge = face.first_edge
    edges = []
    positions = []
    for surfedge in bsp.SURFEDGES[first_edge:(first_edge + face.num_edges)]:
        if surfedge >= 0:  # index is positive
            edge = bsp.EDGES[surfedge]
            positions.append(bsp.VERTICES[bsp.EDGES[surfedge][0]])
            # ^ utils/vrad/trace.cpp:637
        else:  # index is negative
            edge = bsp.EDGES[-surfedge][::-1]  # reverse
            positions.append(bsp.VERTICES[bsp.EDGES[-surfedge][1]])
            # ^ utils/vrad/trace.cpp:635
        edges.append(edge)
    positions = t_junction_fixer(bsp, face, positions, edges)
    texture_info = bsp.TEXTURE_INFO[face.texture_info]
    texture_data = bsp.TEXTURE_DATA[texture_info.texture_data]
    texture = texture_info.texture
    lightmap = texture_info.lightmap

    # texture vector -> uv calculation discovered in:
    # github.com/VSES/SourceEngine2007/blob/master/src_main/engine/matsys_interface.cpp
    # SurfComputeTextureCoordinate & SurfComputeLightmapCoordinate
    for P in positions:
        # texture UV
        uv = [vector.dot(P, texture.s[:3]) + texture.s.offset,
              vector.dot(P, texture.t[:3]) + texture.t.offset]
        uv[0] /= texture_data.view.width if texture_data.view.width != 0 else 1
        uv[1] /= texture_data.view.height if texture_data.view.height != 0 else 1
        uvs.append(vector.vec2(*uv))
        # lightmap UV
        uv2 = [vector.dot(P, lightmap.s[:3]) + lightmap.s.offset,
               vector.dot(P, lightmap.t[:3]) + lightmap.t.offset]
        if any([(face.lightmap.mins.x == 0), (face.lightmap.mins.y == 0)]):
            uv2 = [0, 0]  # invalid / no lighting
        else:
            uv2[0] -= face.lightmap.mins.x
            uv2[1] -= face.lightmap.mins.y
            uv2[0] /= face.lightmap.size.x
            uv2[1] /= face.lightmap.size.y
        uv2s.append(uv2)
    normal = [bsp.PLANES[face.plane].normal] * len(positions)  # X Y Z
    colour = [texture_data.reflectivity] * len(positions)  # R G B
    return list(zip(positions, normal, uvs, uv2s, colour))


def t_junction_fixer(bsp, face: int, positions: List[List[float]], edges: List[List[float]]) -> List[List[float]]:
    # TODO: look at primitives system
    # https://github.com/magcius/noclip.website/blob/master/src/SourceEngine/BSPFile.ts#L1052
    # https://github.com/magcius/noclip.website/blob/master/src/SourceEngine/BSPFile.ts#L1537
    # report to bsp.log rather than printing
    # bsp may need a method wrapper to give a warning to check the logs
    # face_index = bsp.FACES.index(face)
    # first_edge = face.first_edge
    if {positions.count(P) for P in positions} != {1}:
        # print(f"Face #{face_index} has interesting edges (t-junction?):")
        # print("\tAREA:", f"{face.area:.3f}")
        # center = sum(map(vector.vec3, positions), start=vector.vec3()) / len(positions)
        # print("\tCENTER:", f"({center:.3f})")
        # print("\tSURFEDGES:", bsp.SURFEDGES[first_edge:first_edge + face.num_edges])
        # print("\tEDGES:", edges)
        # loops = [(e[0] == edges[i-1][1]) for i, e in enumerate(edges)]
        # if not all(loops):
        #     print("\tWARINNG! EDGES do not loop!")
        #     print("\tLOOPS:", loops)
        # print("\tPOSITIONS:", [bsp.VERTICES.index(P) for P in positions])

        # PATCH
        # -- if you see 1 index between 2 indentical indicies:
        # -- compress the 3 indices down to just the first
        repeats = [i for i, P in enumerate(positions) if positions.count(P) != 1]
        # if len(repeats) > 0:
        #     print("\tREPEATS:", repeats)
        #     print([bsp.VERTICES.index(P) for P in positions], "-->")
        if len(repeats) == 2:
            index_a, index_b = repeats
            if index_b - index_a == 2:
                # edge goes out to one point and doubles back; delete it
                positions.pop(index_a + 1)
                positions.pop(index_a + 1)
            # what about Ts around the ends?
            print([bsp.VERTICES.index(P) for P in positions])
        else:
            if repeats[1] == repeats[0] + 1 and repeats[1] == repeats[2] - 1:
                positions.pop(repeats[1])
                positions.pop(repeats[1])
            print([bsp.VERTICES.index(P) for P in positions])
    return positions


def displacement_indices(power: int) -> List[List[int]]:  # not directly a method
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
                tris.extend([offset + 0, offset + power2A, offset + 1])
                tris.extend([offset + power2A, offset + power2B, offset + 1])
                tris.extend([offset + power2B, offset + power2C, offset + 1])
                tris.extend([offset + power2C, offset + 2, offset + 1])
            else:  # |/|\|
                tris.extend([offset + 0, offset + power2A, offset + power2B])
                tris.extend([offset + 1, offset + 0, offset + power2B])
                tris.extend([offset + 2, offset + 1, offset + power2B])
                tris.extend([offset + power2C, offset + 2, offset + power2B])
    return tris


def vertices_of_displacement(bsp, face_index: int) -> List[List[float]]:
    """Format: [Position, Normal, TexCoord, LightCoord, Colour]"""
    face = bsp.FACES[face_index]
    if face.displacement_info == -1:
        raise RuntimeError(f"Face #{face_index} is not a displacement!")
    base_vertices = bsp.vertices_of_face(face_index)
    if len(base_vertices) != 4:
        raise RuntimeError(f"Face #{face_index} does not have 4 corners (probably t-junctions)")
    disp_info = bsp.DISPLACEMENT_INFO[face.displacement_info]
    start = vector.vec3(*disp_info.start_position)
    base_quad = [vector.vec3(*P) for P, N, uv, uv2, rgb in base_vertices]
    # rotate so the point closest to start on the quad is index 0
    if start not in base_quad:
        start = sorted(base_quad, key=lambda P: (start - P).magnitude())[0]
    starting_index = base_quad.index(start)

    def rotated(q):
        return q[starting_index:] + q[:starting_index]

    A, B, C, D = rotated(base_quad)
    AD = D - A
    BC = C - B
    quad = rotated(base_vertices)
    uvA, uvB, uvC, uvD = [vector.vec2(*uv) for P, N, uv, uv2, rgb in quad]
    uvAD = uvD - uvA
    uvBC = uvC - uvB
    uv2A, uv2B, uv2C, uv2D = [vector.vec2(*uv2) for P, N, uv, uv2, rgb in quad]
    uv2AD = uv2D - uv2A
    uv2BC = uv2C - uv2B
    power2 = 2 ** disp_info.power
    disp_verts = bsp.DISPLACEMENT_VERTICES[disp_info.displacement_vert_start:]
    disp_verts = disp_verts[:(power2 + 1) ** 2]
    vertices = []
    for index, disp_vertex in enumerate(disp_verts):
        t1 = index % (power2 + 1) / power2
        t2 = index // (power2 + 1) / power2
        bary_vert = vector.lerp(A + (AD * t1), B + (BC * t1), t2)
        # ^ interpolates across the base_quad to find the barymetric point
        displacement_vert = [x * disp_vertex.distance for x in disp_vertex.vector]
        true_vertex = [a + b for a, b in zip(bary_vert, displacement_vert)]
        texture_uv = vector.lerp(uvA + (uvAD * t1), uvB + (uvBC * t1), t2)
        lightmap_uv = vector.lerp(uv2A + (uv2AD * t1), uv2B + (uv2BC * t1), t2)
        normal = base_vertices[0][1]
        colour = base_vertices[0][4]
        vertices.append((true_vertex, normal, texture_uv, lightmap_uv, colour))
    return vertices


# TODO: vertices_of_model (walk the node tree)
# TODO: vertices_of_node

methods = [vertices_of_face, vertices_of_displacement, shared.worldspawn_volume]
