# https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/bspfile.h
import enum
import io
import struct
from typing import List

from .. import base
from .. import shared
from . import source


BSP_VERSION = 20
# NOTE: v20 Source BSPs differ widely, since many forks are of this version

GAMES = ["Day of Defeat: Source",
         "G String",
         "Garry's Mod",
         "Half-Life 2: Episode 2",
         "Half-Life 2 Update",
         "NEOTOKYO",
         "Portal",
         "Team Fortress 2"]


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
    FACE_IDS = 11  # TF2 branch, for mapping debug & detail prop seed
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
    UNUSED_22 = 22
    UNUSED_23 = 23
    UNUSED_24 = 24
    UNUSED_25 = 25
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


lump_header_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}


def read_lump_header(file, LUMP: enum.Enum) -> source.SourceLumpHeader:
    file.seek(lump_header_address[LUMP])
    offset, length, version, fourCC = struct.unpack("4I", file.read(16))
    header = source.SourceLumpHeader(offset, length, version, fourCC)
    return header

# a rough map of the relationships between lumps:
# Node -> Face -> Plane
#             |-> DisplacementInfo -> DisplacementVertex
#             |-> SurfEdge -> Edge -> Vertex
#
# PRIMITIVES or "water indices" are a leftover from Quake.
# In the Source Engine they are used to correct for "t-junctions".
# "t-junctions" are a type of innacuracy which arises in BSP construction.
# In brush-based .bsp, Constructive Solid Geometry (CSG) operations occur.
# CSG "slices" & can potentially merges brushes, this also helps define visleaves
# (CSG operations are the same as the Boolen Modifier in Blender).
# These "slices" must be applied to brush faces,
# which are stored as a clockwise series of 3D points.
# Some slices create erroneous edges, especially where func_detail meets world.
# The PRIMITIVES lump forces a specific shape to compensate for these errors.
#
# ClipPortalVertices are AreaPortal geometry


# engine limits: (2013 SDK bspfile.h)
class MIN(enum.Enum):
    DISPLACEMENT_POWER = 2


class MAX(enum.Enum):
    # misc:
    CUBEMAP_SAMPLES = 1024
    DISPLACEMENT_POWER = 4
    DISPLACEMENT_CORNER_NEIGHBORS = 4
    ENTITY_KEY, ENTITY_VALUE = 32, 1024  # key value pair sizes
    LIGHTMAPS = 4  # ? left over from Quake / GoldSrc lightmap format ?
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


class MAX_X360(enum.Enum):  # "force static arrays to be very small"
    """#if !defined( BSP_USE_LESS_MEMORY )"""
    ENTITIES = 2
    PLANES = 2
    TEXTURE_DATA = 2
    VERTICES = 2
    VISIBILITY_CLUSTERS = 2
    NODES = 2
    TEXTURE_INFO = 2
    FACES = 2
    LIGHTING_SIZE = 2
    LEAVES = 2
    EDGES = 2
    SURFEDGES = 2
    MODELS = 2
    WORLD_LIGHTS = 2
    LEAF_FACES = 2
    LEAF_BRUSHES = 2
    BRUSHES = 2
    BRUSH_SIDES = 2
    AREAS = 2
    AREA_BYTES = 2
    AREA_PORTALS = 2
    # UNUSED_24 [PORTALVERTS] = 2
    DISPLACEMENT_INFO = 2
    ORIGINAL_FACES = FACES
    VERTEX_NORMALS = 2
    VERTEX_NORMAL_INDICES = 2
    DISPLACEMENT_VERTICES_FOR_ONE = (2 ** MAX.DISPLACEMENT_POWER.value + 1) ** 2
    DISPLACEMENT_VERTICES = DISPLACEMENT_INFO * DISPLACEMENT_VERTICES_FOR_ONE
    LEAF_WATER_DATA = 2
    PRIMITIVES = 2
    PRIMITIVE_VERTICES = 2
    PRIMITIVE_INDICES = 2
    TEXDATA_STRING_DATA = 2
    TEXDATA_STRING_TABLE = 2
    OVERLAYS = 2
    DISPLACEMENT_TRIANGLES_FOR_ONE = 2 ** MAX.DISPLACEMENT_POWER.value * 3
    DISPLACEMENT_TRIANGLES = DISPLACEMENT_INFO * DISPLACEMENT_TRIANGLES_FOR_ONE
    WATER_OVERLAYS = 2
    LIGHTING_HDR_SIZE = LIGHTING_SIZE
    WORLD_LIGHTS_HDR = WORLD_LIGHTS
    FACES_HDR = FACES


# flag enums
class Contents(enum.IntFlag):
    """Brush flags"""
    # src/public/bspflags.h
    # NOTE: compiler gets these flags from a combination of all textures on the brush
    # e.g. any non opaque face means this brush is non-opaque, and will not block vis
    # visible
    EMPTY = 0x00
    SOLID = 0x01
    WINDOW = 0x02
    AUX = 0x04
    GRATE = 0x08  # allows bullets & vis
    SLIME = 0x10
    WATER = 0x20
    MIST = 0x40  # BLOCK_LOS, blocks AI line of sight
    OPAQUE = 0x80  # blocks NPC line of sight, may be non-solid
    TEST_FOG_VOLUME = 0x100  # cannot be seen through, but may be non-solid
    UNUSED_1 = 0x200
    UNUSED_2 = 0x400  # titanfall vertex lump flags?
    TEAM1 = 0x0800
    TEAM2 = 0x1000
    IGNORE_NODRAW_OPAQUE = 0x2000  # ignore opaque if Surface.NODRAW
    MOVEABLE = 0x4000  # pushables
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
    SURFPROP1 = 0x08
    SURFPROP2 = 0x10


class Surface(enum.IntFlag):
    """TextureInfo flags"""
    # src/public/bspflags.h
    # NOTE: compiler gets these flags from the texture
    LIGHT = 0x0001  # value will hold the light strength ???
    SKY_2D = 0x0002  # don't draw, indicates we should skylight + draw 2d sky but not draw the 3D skybox
    SKY = 0x0004  # don't draw, but add to skybox
    WARP = 0x0008  # turbulent water warp
    TRANSLUCENT = 0x0010
    NO_PORTAL = 0x0020  # the surface can not have a portal placed on it
    TRIGGER = 0x0040  # xbox hack to work around elimination of trigger surfaces, which breaks occluders
    NODRAW = 0x0080
    HINT = 0x0100  # make a bsp split on this face
    SKIP = 0x0200  # don't split on this face, allows for non-closed brushes
    NO_LIGHT = 0x0400  # fon't calculate light
    BUMPLIGHT = 0x0800  # calculate three lightmaps for the surface for bumpmapping (ssbump?)
    NO_SHADOWS = 0x1000
    NO_DECALS = 0x2000
    NO_CHOP = 0x4000	 # don't subdivide patches on this surface
    HITBOX = 0x8000  # surface is part of a hitbox


# classes for each lump, in alphabetical order:
class Leaf(base.Struct):  # LUMP 10
    """Endpoint of a vis tree branch, a pocket of Faces"""
    contents: int  # contents bitflags
    cluster: int   # index of this Leaf's cluster (parent node?) (visibility?)
    area_flags: int  # area + flags (short area:9; short flags:7;)
    # area and flags are held in the same float
    # area = leaf[2] & 0xFF80 >> 7 # 9 bits
    # flags = leaf[2] & 0x007F # 7 bits
    # TODO: automatically split area & flags, merging back for flat()
    # why was this done when the struct is padded by one short anyway?
    mins: List[float]  # bounding box minimums along XYZ axes
    maxs: List[float]  # bounding box maximums along XYZ axes
    first_leaf_face: int   # index of first LeafFace
    num_leaf_faces: int    # number of LeafFaces
    first_leaf_brush: int  # index of first LeafBrush
    num_leaf_brushes: int  # number of LeafBrushes
    leaf_water_data_id: int  # -1 if this leaf isn't submerged
    padding: int  # should be empty
    __slots__ = ["contents", "cluster", "area_flags", "mins", "maxs",
                 "first_leaf_face", "num_leaf_faces", "first_leaf_brush",
                 "num_leaf_brushes", "leaf_water_data_id", "padding"]
    _format = "i8h4H2h"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}


# classes for special lumps, in alphabetical order:
class PhysicsDisplacement(list):  # LUMP 28
    def __init__(self, raw_lump: bytes):
        lump = io.BytesIO(raw_lump)
        count = int.from_bytes(lump.read(2), "little")
        data_sizes = list(*struct.unpack(f"{count}H", lump.read(count * 2)))
        physics_data = list()
        for size in data_sizes:
            physics_data.append(lump.read(size))
        super().__init__(physics_data)

    def as_bytes(self) -> bytes:
        count = len(self).to_bytes(2, "little")
        sizes = map(lambda s: s.to_bytes(2, "little"), [len(d) for d in self])
        return b"".join(count, *sizes, *self)


class StaticPropv10(base.Struct):  # sprp GAME LUMP (LUMP 35)
    origin: List[float]  # origin.xyz
    angles: List[float]  # origin.yzx  QAngle; Z0 = East
    name_index: int  # index into AME_LUMP.sprp.model_names
    first_leaf: int  # index into Leaf lump
    num_leafs: int  # number of Leafs after first_leaf this StaticPropv10 is in
    solid_mode: int  # collision flags enum
    skin: int  # index of this StaticProp's skin in the .mdl
    fade_distance: List[float]  # min & max distances to fade out
    lighting_origin: List[float]  # xyz position to sample lighting from
    forced_fade_scale: float  # relative to pixels used to render on-screen?
    dx_level: List[int]  # supported directX level, will not render depending on settings
    flags: int  # other flags
    lightmap: List[int]  # dimensions of this StaticProp's lightmap (GAME_LUMP.static prop lighting?)
    __slots__ = ["origin", "angles", "name_index", "first_leaf", "num_leafs",
                 "solid_mode", "skin", "fade_distance", "lighting_origin",
                 "forced_fade_scale", "dx_level", "flags", "lightmap"]
    _format = "6f3HBi6f2Hi2H"
    _arrays = {"origin": [*"xyz"], "angles": [*"yzx"], "fade_distance": ["min", "max"],
               "lighting_origin": [*"xyz"], "dx_level": ["min", "max"],
               "lightmap": ["width", "height"]}


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = source.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = source.LUMP_CLASSES.copy()
LUMP_CLASSES.update({"LEAVES": {1: Leaf}})

SPECIAL_LUMP_CLASSES = source.SPECIAL_LUMP_CLASSES.copy()

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = source.GAME_LUMP_CLASSES.copy()
GAME_LUMP_CLASSES["sprp"].update({7: lambda raw_lump: shared.GameLump_SPRP(raw_lump, StaticPropv10),  # 7*
                                 10: lambda raw_lump: shared.GameLump_SPRP(raw_lump, StaticPropv10)})


# branch exclusive methods, in alphabetical order:


methods = [*source.methods]
