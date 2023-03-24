# https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Titanfall
from __future__ import annotations
import enum
import io
import itertools
import struct
from typing import Any, Dict, List, Union

from .. import base
from .. import shared
from .. import valve_physics
from .. import vector
from ..id_software import quake
from ..valve import source


FILE_MAGIC = b"rBSP"

BSP_VERSION = 29

GAME_PATHS = {"Titanfall": "Titanfall",
              "Titanfall: Online": "TitanfallOnline"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    ENTITIES = 0x0000
    PLANES = 0x0001
    TEXTURE_DATA = 0x0002
    VERTICES = 0x0003
    UNUSED_4 = 0x0004
    UNUSED_5 = 0x0005
    UNUSED_6 = 0x0006
    UNUSED_7 = 0x0007
    UNUSED_8 = 0x0008
    UNUSED_9 = 0x0009
    UNUSED_10 = 0x000A
    UNUSED_11 = 0x000B
    UNUSED_12 = 0x000C
    UNUSED_13 = 0x000D
    MODELS = 0x000E
    UNUSED_15 = 0x000F
    UNUSED_16 = 0x0010
    UNUSED_17 = 0x0011
    UNUSED_18 = 0x0012
    UNUSED_19 = 0x0013
    UNUSED_20 = 0x0014
    UNUSED_21 = 0x0015
    UNUSED_22 = 0x0016
    UNUSED_23 = 0x0017
    ENTITY_PARTITIONS = 0x0018
    UNUSED_25 = 0x0019
    UNUSED_26 = 0x001A
    UNUSED_27 = 0x001B
    UNUSED_28 = 0x001C
    PHYSICS_COLLIDE = 0x001D
    VERTEX_NORMALS = 0x001E
    UNUSED_31 = 0x001F
    UNUSED_32 = 0x0020
    UNUSED_33 = 0x0021
    UNUSED_34 = 0x0022
    GAME_LUMP = 0x0023
    LEAF_WATER_DATA = 0x0024
    UNUSED_37 = 0x0025
    UNUSED_38 = 0x0026
    UNUSED_39 = 0x0027
    PAKFILE = 0x0028  # zip file, contains cubemaps
    UNUSED_41 = 0x0029
    CUBEMAPS = 0x002A
    TEXTURE_DATA_STRING_DATA = 0x002B
    TEXTURE_DATA_STRING_TABLE = 0x002C
    UNUSED_45 = 0x002D
    UNUSED_46 = 0x002E
    UNUSED_47 = 0x002F
    UNUSED_48 = 0x0030
    UNUSED_49 = 0x0031
    UNUSED_50 = 0x0032
    UNUSED_51 = 0x0033
    UNUSED_52 = 0x0034
    UNUSED_53 = 0x0035
    WORLD_LIGHTS = 0x0036
    UNUSED_55 = 0x0037
    UNUSED_56 = 0x0038
    UNUSED_57 = 0x0039
    UNUSED_58 = 0x003A
    UNUSED_59 = 0x003B
    UNUSED_60 = 0x003C
    UNUSED_61 = 0x003D
    PHYSICS_LEVEL = 0x003E  # from L4D2 / 2013 Source SDK? (2011: Portal 2)
    UNUSED_63 = 0x003F
    UNUSED_64 = 0x0040
    UNUSED_65 = 0x0041
    TRICOLL_TRIANGLES = 0x0042
    UNUSED_67 = 0x0043
    TRICOLL_NODES = 0x0044
    TRICOLL_HEADERS = 0x0045
    PHYSICS_TRIANGLES = 0x0046
    VERTEX_UNLIT = 0x0047        # VERTEX_RESERVED_0
    VERTEX_LIT_FLAT = 0x0048     # VERTEX_RESERVED_1
    VERTEX_LIT_BUMP = 0x0049     # VERTEX_RESERVED_2
    VERTEX_UNLIT_TS = 0x004A     # VERTEX_RESERVED_3
    VERTEX_BLINN_PHONG = 0x004B  # VERTEX_RESERVED_4
    VERTEX_RESERVED_5 = 0x004C
    VERTEX_RESERVED_6 = 0x004D
    VERTEX_RESERVED_7 = 0x004E
    MESH_INDICES = 0x004F
    MESHES = 0x0050
    MESH_BOUNDS = 0x0051
    MATERIAL_SORT = 0x0052
    LIGHTMAP_HEADERS = 0x0053
    UNUSED_84 = 0x0054
    CM_GRID = 0x0055
    CM_GRID_CELLS = 0x0056
    CM_GEO_SETS = 0x0057
    CM_GEO_SET_BOUNDS = 0x0058
    CM_PRIMITIVES = 0x0059
    CM_PRIMITIVE_BOUNDS = 0x005A
    CM_UNIQUE_CONTENTS = 0x005B
    CM_BRUSHES = 0x005C
    CM_BRUSH_SIDE_PLANE_OFFSETS = 0x005D
    CM_BRUSH_SIDE_PROPERTIES = 0x005E
    CM_BRUSH_SIDE_TEXTURE_VECTORS = 0x005F
    TRICOLL_BEVEL_STARTS = 0x0060
    TRICOLL_BEVEL_INDICES = 0x0061
    LIGHTMAP_DATA_SKY = 0x0062
    CSM_AABB_NODES = 0x0063
    CSM_OBJ_REFERENCES = 0x0064
    LIGHTPROBES = 0x0065
    STATIC_PROP_LIGHTPROBE_INDICES = 0x0066
    LIGHTPROBE_TREE = 0x0067
    LIGHTPROBE_REFERENCES = 0x0068
    LIGHTMAP_DATA_REAL_TIME_LIGHTS = 0x0069
    CELL_BSP_NODES = 0x006A
    CELLS = 0x006B
    PORTALS = 0x006C
    PORTAL_VERTICES = 0x006D
    PORTAL_EDGES = 0x006E
    PORTAL_VERTEX_EDGES = 0x006F
    PORTAL_VERTEX_REFERENCES = 0x0070
    PORTAL_EDGE_REFERENCES = 0x0071
    PORTAL_EDGE_INTERSECT_AT_EDGE = 0x0072
    PORTAL_EDGE_INTERSECT_AT_VERTEX = 0x0073
    PORTAL_EDGE_INTERSECT_HEADER = 0x0074
    OCCLUSION_MESH_VERTICES = 0x0075
    OCCLUSION_MESH_INDICES = 0x0076
    CELL_AABB_NODES = 0x0077
    OBJ_REFERENCES = 0x0078
    OBJ_REFERENCE_BOUNDS = 0x0079
    UNUSED_122 = 0x007A
    LEVEL_INFO = 0x007B
    SHADOW_MESH_OPAQUE_VERTICES = 0x007C
    SHADOW_MESH_ALPHA_VERTICES = 0x007D
    SHADOW_MESH_INDICES = 0x007E
    SHADOW_MESHES = 0x007F


LumpHeader = source.LumpHeader

# Rough map of the relationships between lumps:
#              /-> MaterialSort -> TextureData -> TextureDataStringTable -> TextureDataStringData
# Model -> Mesh -> MeshIndex -\-> VertexReservedX -> Vertex
#             \--> .flags (VertexReservedX)     \--> VertexNormal
#              \-> VertexReservedX               \-> .uv
# MeshBounds & Mesh are parallel
# NOTE: parallel means each entry is paired with an entry of the same index in the parallel lump
# -- this means you can collect only the data you need, but increases the chance of storing redundant data


# ShadowMesh -> ShadowMeshIndex -> ShadowMeshOpaqueVertex
#           \-> MaterialSort?  \-> ShadowMeshAlphaVertex

# LightmapHeader -> LIGHTMAP_DATA_SKY
#               \-> LIGHTMAP_DATA_REAL_TIME_LIGHTS

# PORTAL LUMPS
#               /-> Cell
#              /--> Plane
# Cell -> Portal -> PortalEdgeReference -> PortalEdge -> PortalVertex
#     \-> LeafWaterData -> TextureData (water material)

# PortalEdgeIntersect -> PortalEdge?
#                    \-> PortalVertex
# PortalEdgeIntersectHeader -> ???
# PortalEdgeIntersectHeader is parallel w/ PortalEdge

# NOTE: Titanfall 2 only seems to care about PortalEdgeIntersectHeader & ignores all other lumps
# -- though this is a code branch that seems to be triggered by something about r1 maps, maybe a flags lump?

# PortalEdgeReference is parallel w/ PortalVertexReference (2x PortalEdges)

# PortalVertexEdges -> PortalEdges (list up to 8 edges each PortalVertex is indexed by)
# PortalVertexEdges is Parallel w/ PortalVertices

# CM_* (presumed: Clip Model)
# the entire GM_GRID lump is always 28 bytes (SpecialLumpClass w/ world bounds & other metadata)

# Grid -> GridCell -> GeoSet
#                 \-?> Primitive

#                   /-> UniqueContents
# GeoSet & Primitive -> .primitive.type / .type -> Brush OR Tricoll

# GeoSet appears to wrap Primitive w/ a count & stradle group (fusing primitives?)

# Primitives is parallel w/ PrimitiveBounds & GeoSets is parallel w/ GeoSetBounds
# PrimitiveBounds & GeoSetBounds use the same "Bounds" type

# CM_BRUSH: brushwork geo
#      /-> BrushSidePlaneOffset -> Plane
# Brush -> BrushSideProperties -> TextureData
#      \-> BrushSideTextureVector

# BrushSideProperties is parallel w/ BrushSideTextureVector (one per brushside)
# len(BrushSideProperties/TextureVectors) = len(Brushes) * 6 + len(BrushSidePlaneOffsets)
# Brush.num_brush_sides (derived) is 6 + Brush.num_plane_offsets

# TRICOLL_* (presumed: Triangle Collision for patches / displacements)
#              /-> Vertices?
# TricollHeader -> TricollTriangle -?> Vertices?
#             \--> TricollNode -> TricollNode -?> TricollLeaf? -?> ???
#              \-> TricollBevelIndices -?> ?

# -?> TricollBevelStarts -?>

# LIGHTPROBE*
# LightProbeTree -?> LightProbeRef -> LightProbe
# -?> StaticPropLightProbeIndex (name implies parallel w/ StaticProps, confirm)


# engine limits:
# NOTE: max map coords are -32768 -> 32768 along each axis (Apex is 64Kx64K, double this limit!)
class MAX:
    MODELS = 1024
    TEXTURE_DATA = 2048
    WORLD_LIGHTS = 4064
    STATIC_PROPS = 40960


# flag enums
class CellSkyFlags(enum.IntFlag):  # used by Cell
    # NOTE: only ever 0, 1, 3 or 5
    UNKNOWN_1 = 0b000
    UNKNOWN_2 = 0b001
    UNKNOWN_3 = 0b010
    UNKNOWN_4 = 0b100


class Contents(enum.IntFlag):
    """Brush flags"""
    # r1/scripts/vscripts/_consts.nut:1159
    EMPTY = 0x00
    SOLID = 0x01
    WINDOW = 0x02  # bulletproof glass etc. (transparent but solid)
    AUX = 0x04  # unused?
    GRATE = 0x08  # allows bullets & vis
    SLIME = 0x10
    WATER = 0x20
    WINDOW_NO_COLLIDE = 0x40
    OPAQUE = 0x80  # blocks AI Line Of Sight, may be non-solid
    TEST_FOG_VOLUME = 0x100  # cannot be seen through, but may be non-solid
    UNUSED_1 = 0x200
    BLOCK_LIGHT = 0x400
    TEAM_1 = 0x800
    TEAM_2 = 0x1000
    IGNORE_NODRAW_OPAQUE = 0x2000  # ignore opaque if Surface.NO_DRAW
    MOVEABLE = 0x4000
    PLAYER_CLIP = 0x10000  # blocks human players
    MONSTER_CLIP = 0x20000
    BRUSH_PAINT = 0x40000
    BLOCK_LOS = 0x80000  # block AI line of sight
    NO_CLIMB = 0x100000
    TITAN_CLIP = 0x200000  # blocks titan players
    BULLET_CLIP = 0x400000
    UNUSED_5 = 0x800000
    ORIGIN = 0x1000000  # removed before bsping an entity
    MONSTER = 0x2000000  # should never be on a brush, only in game
    DEBRIS = 0x4000000
    DETAIL = 0x8000000  # brushes to be added after vis leafs
    TRANSLUCENT = 0x10000000  # auto set if any surface has trans
    LADDER = 0x20000000
    HITBOX = 0x40000000  # use accurate hitboxes on trace


class MeshFlags(enum.IntFlag):
    # source.Surface (source.TextureInfo rolled into titanfall.TextureData?)
    SKY_2D = 0x0002  # TODO: test overriding sky with this in-game
    SKY = 0x0004
    WARP = 0x0008  # Quake water surface?
    TRANSLUCENT = 0x0010  # decals & atmo?
    # titanfall.Mesh.flags
    VERTEX_LIT_FLAT = 0x000     # VERTEX_RESERVED_1
    VERTEX_LIT_BUMP = 0x200     # VERTEX_RESERVED_2
    VERTEX_UNLIT = 0x400        # VERTEX_RESERVED_0
    VERTEX_UNLIT_TS = 0x600     # VERTEX_RESERVED_3
    # VERTEX_BLINN_PHONG = 0x???  # VERTEX_RESERVED_4
    SKIP = 0x20000  # 0x200 in valve.source.Surface (<< 8?)
    TRIGGER = 0x40000  # guessing
    # masks
    MASK_VERTEX = 0x600


TextureDataFlags = MeshFlags  # always the same as Mesh.flags -> MaterialSort -> TextureData.flags


class TraceCollisionGroup(enum.Enum):
    # taken from squirrel (vscript) by BobTheBob
    NONE = 0
    DEBRIS = 1
    DEBRIS_TRIGGER = 2
    PLAYER = 5
    BREAKABLE_GLASS = 6
    NPC = 8
    WEAPON = 12
    PROJECTILE = 14
    BLOCK_WEAPONS = 18
    BLOCK_WEAPONS_AND_PHYSICS = 19


class TraceMask(enum.IntEnum):  # taken from squirrel (vscript) by BobTheBob
    """source.ContentsMask eqiuvalent, exposed to squirrel vscript API"""
    # PHYSICS
    SOLID = Contents.SOLID | Contents.MOVEABLE | Contents.WINDOW | Contents.MONSTER | Contents.GRATE
    PLAYER_SOLID = SOLID | Contents.PLAYER_CLIP
    TITAN_SOLID = SOLID | Contents.TITAN_CLIP  # new
    NPC_SOLID = SOLID | Contents.MONSTER_CLIP
    WATER = Contents.WATER | Contents.SLIME  # removed Contents.MOVEABLE
    # VIS
    OPAQUE = Contents.SOLID | Contents.MOVEABLE | Contents.OPAQUE  # blocks light
    OPAQUE_AND_NPCS = OPAQUE | Contents.MONSTER
    BLOCK_LOS = OPAQUE | Contents.BLOCK_LOS  # blocks AI Line Of Sight; added Contents.OPAQUE
    BLOCK_LOS_AND_NPCS = BLOCK_LOS | Contents.MONSTER
    VISIBLE = OPAQUE | Contents.IGNORE_NODRAW_OPAQUE  # blocks Player Line Of Sight
    VISIBLE_AND_NPCS = OPAQUE_AND_NPCS | Contents.IGNORE_NODRAW_OPAQUE
    # WEAPONS
    SHOT = 1178615859  # source.ContentsMask.SHOT | WATER | Contents.MOVEABLE
    SHOT_BRUSH_ONLY = 71319603  # ! NEW !  SHOT & ~(Contents.HITBOX | Contents.MONSTER)
    SHOT_HULL = 104873995  # source.ContentsMask.SHOT_HULL | Contents.MOVEABLE
    GRENADE = SOLID | Contents.HITBOX | Contents.DEBRIS  # ! NEW !
    # ALTERNATES
    SOLID_BRUSH_ONLY = 16907  # source.ContentsMask.SOLID_BRUSH_ONLY | Contents.UNKNOWN_2
    PLAYER_SOLID_BRUSH_ONLY = SOLID_BRUSH_ONLY | Contents.PLAYER_CLIP
    NPC_SOLID_BRUSH_ONLY = SOLID_BRUSH_ONLY | Contents.MONSTER_CLIP
    NPC_WORLD_STATIC = Contents.SOLID | Contents.WINDOW | Contents.MONSTER_CLIP | Contents.GRATE  # for route rebuilding
    NPC_FLUID = Contents.SOLID | Contents.MOVEABLE | Contents.WINDOW | Contents.MONSTER | Contents.MONSTER_CLIP  # new


class PrimitiveType(enum.IntFlag):
    """Used by CMGeoSet & CMPrimitive to identify collidable children"""
    BRUSH = 0
    TRICOLL = 64


# classes for lumps, in alphabetical order:
class Bounds(base.Struct):  # LUMP 88 & 90 (0058 & 005A)
    """Identified by warmist & rexx#1287"""
    # dcollyawbox_t
    origin: vector.vec3  # uint16_t
    negative_cos: int  # oriented bounding box?
    extents: vector.vec3  # uint16_t
    positive_sin: int  # unsure of use
    __slots__ = ["origin", "negative_cos", "extents", "positive_sin"]
    _format = "8h"
    _arrays = {"origin": [*"xyz"], "extents": [*"xyz"]}
    _classes = {"origin": vector.vec3, "extents": vector.vec3}


class Brush(base.Struct):  # LUMP 92 (005C)
    """A bounding box sliced down into a convex hull by multiple planes"""
    origin: vector.vec3
    num_non_axial_no_discard: int  # number of BrushSideProperties after the axial 6 w/ no DISCARD flag set
    num_plane_offsets: int  # number of BrushSideX in this brush
    # num_brush_sides = 6 + num_plane_offsets
    index: int  # index of this Brush; makes calculating BrushSideX indices easier
    extents: vector.vec3
    # mins = origin - extents
    # maxs = origin + extents
    brush_side_offset: int  # alternatively, num_prior_non_axial
    # first_brush_side = (index * 6 + brush_side_offset)
    __slots__ = ["origin", "num_non_axial_no_discard", "num_plane_offsets", "index", "extents", "brush_side_offset"]
    _format = "3f2Bh3fi"
    _arrays = {"origin": [*"xyz"], "extents": [*"xyz"]}
    _classes = {"origin": vector.vec3, "extents": vector.vec3}


# TODO: use a BitField instead
class BrushSideProperty(shared.UnsignedShort, enum.IntFlag):  # LUMP 94 (005E)
    UNKNOWN_FLAG = 0x8000
    DISCARD = 0x4000  # this side helps define bounds (axial or bevel), but has no polygon
    # NO OTHER FLAGS APPEAR TO BE USED IN R1 / R1:O / R2
    # R5 DEPRECATED CM_BRUSH_SIDE_PROPERTIES

    MASK_TEXTURE_DATA = 0x01FF  # R1 / R1:O / R2 never exceed 512 (0x1FF + 1) TextureData per-map
    # TODO: use a BitField instead


class Cell(base.Struct):  # LUMP 107 (006B)
    """Identified by Fifty#8113 & rexx#1287"""
    # likely part of VISIBILITY system
    # NOTE: inifinity_ward.call_of_duty1 also introduced a Cell lump
    num_portals: int  # index into Portal lump?
    first_portal: int  # number of Portals in this Cell?
    # TODO: confirm always 0xFFFF, 0XFFFF
    flags: int  # skyFlags; visibility related?
    leaf_water_data: int  # index into LeafWaterData; -1 for None
    __slots__ = ["num_portals", "first_portal", "flags", "leaf_water_data"]
    _format = "4h"
    _classes = {"flags": CellSkyFlags}


class CellAABBNode(base.Struct):  # LUMP 119 (0077)
    """Identified by Fifty#8113"""
    origin: vector.vec3
    num_children: int  # number of CellAABBNodes after first_child
    num_obj_refs: int  # number of ObjReferences after first_obj_rf
    total_obj_refs: int  # sum of all obj refs in children
    extents: vector.vec3
    first_child: int  # index into CellAABBNodes
    first_obj_ref: int  # index into ObjReferences
    __slots__ = ["origin", "num_children", "num_obj_refs", "total_obj_refs",
                 "extents", "first_child", "first_obj_ref"]
    _format = "3f2BH3f2H"  # Extreme SIMD
    _arrays = {"origin": [*"xyz"], "extents": [*"xyz"]}
    _classes = {"origin": vector.vec3, "extents": vector.vec3}


class CellBSPNode(base.MappedArray):  # LUMP 106 (006A)
    """Identified by rexx#1287"""
    plane: int  # index into Plane lump
    child: int  # childrenOrCell; presumably type switched w/ sign
    # indexes a child CellBspNode?
    _mapping = ["plane", "child"]
    _format = "2i"


class Cubemap(base.Struct):  # LUMP 42 (002A)
    origin: vector.vec3  # int32_t
    unknown: int  # index? flags?
    __slots__ = ["origin", "unknown"]
    _format = "3iI"
    _arrays = {"origin": [*"xyz"]}
    _classes = {"origin": vector.vec3}


class GeoSet(base.Struct):  # LUMP 87 (0057)
    # Parallel w/ GeoSetBounds
    straddle_group: int  # CMGrid counts straddle groups
    num_primitives: int  # start from primitive.index?
    primitive: List[int]  # embedded Primitive?
    # primitive.unique_contents: int  # index into UniqueContents
    # primitive.index: int  # index into Brushes / TricollHeaders
    # primitive.type: PrimitiveType  # Brushes or Tricoll
    __slots__ = ["straddle_group", "num_primitives", "primitive"]
    _format = "2HI"
    _bitfields = {"primitive": {"unique_contents": 8, "index": 16, "type": 8}}
    _classes = {"primitive.type": PrimitiveType}


# NOTE: only one 28 byte entry per file
class Grid(base.Struct):  # LUMP 85 (0055)
    """splits the map into a grid on the XY-axes"""
    # grid pattern start at mins.xy, increments Y first, then X
    scale: float  # 256 for r1, 704 for r2
    offset: vector.vec2  # position of first GridCell (mins.xy)
    count: vector.vec2  # x * y = number of GridCells in worldspawn
    # count.x * count.y + len(Models) = len(CMGridCells)
    # mins = offset * scale
    # maxs = (offset + count) * scale
    # NOTE: bounds covers Models[0]
    num_straddle_groups: int  # linked to geosets, objects straddling many gridcells?
    base_plane_offset: int  # first plane for brushes to index
    # other planes might be used by portals, unsure
    __slots__ = ["scale", "offset", "count", "num_straddle_groups", "base_plane_offset"]
    _format = "f6i"
    _arrays = {"offset": [*"xy"], "count": [*"xy"]}


class GridCell(base.MappedArray):  # LUMP 86 (0056)
    # GridCells[:Grid.count.x * Grid.count.y]     => Models[0]; broken into cells
    # GridCells[Grid.count.x * Grid.count.y + 1]  => Models[0]; num_geo_sets = 0
    # GridCells[Grid.count.x * Grid.count.y + 2:] => Models[1:]; 1 cell per model
    # x = index / Grid.count.y + Grid.offset.x
    # y = index % Grid.count.x + Grid.offset.y
    # bounds.mins.xy = x * Grid.scale, y * Grid.scale
    # bounds.maxs.xy = (x + 1) * Grid.scale, (y + 1) * scale
    first_geo_set: int
    num_geo_sets: int
    _mapping = ["first_geo_set", "num_geo_sets"]
    _format = "2H"


# NOTE: only one 28 byte entry per file
class LevelInfo(base.Struct):  # LUMP 123 (007B)
    """Identified by Fifty"""
    # implies worldspawn (model[0]) mesh order to be: opaque, decals, transparent, skybox
    first_decal_mesh: int
    first_transparent_mesh: int
    first_sky_mesh: int
    num_static_props: int  # len(bsp.GAME_LUMP.sprp.props)
    sun_angle: vector.vec3  # represents angle of last light_environment
    __slots__ = ["first_decal_mesh", "first_transparent_mesh", "first_sky_mesh", "num_static_props", "sun_angle"]
    _format = "4I3f"
    _arrays = {"sun_angle": [*"xyz"]}
    _classes = {"sun_angle": vector.vec3}


class LightmapHeader(base.MappedArray):  # LUMP 83 (0053)
    type: int  # TODO: LightmapHeaderType enum
    width: int
    height: int
    _mapping = ["type", "width", "height"]
    _format = "I2H"
    # TODO: _classes = {"type": LightmapTypeheader}


class LightProbe(base.Struct):  # LUMP 102 (0066)
    """Identified by rexx"""  # untested
    cube: List[List[int]]  # rgb888 ambient light cube
    sky_dir_sun_vis: List[int]  # ???
    static_light: List[List[int]]  # connection to local static lights
    # static_light.weights: List[int]  # up to 4 scalars; default 0
    # static_light.indices: List[int]  # up to 4 indices; default -1
    __slots__ = ["cube", "sky_dir_sun_vis", "static_light", "padding"]
    _format = "24B4h4B4hI"
    _arrays = {"cube": {x: [*"rgba"] for x in "ABCDEF"}, "sky_dir_sun_vis": 4,
               "static_light": {"weights": 4, "indices": 4}}
    # TODO: map cube face names to UP, DOWN etc.
    # TODO: ambient light cube childClass


class LightProbeRef(base.Struct):  # LUMP 104 (0068)
    origin: List[float]  # coords of LightProbe
    lightprobe: int  # index of this LightProbeRef's LightProbe
    # NOTE: not every lightprobe is indexed
    __slots__ = ["origin", "lightprobe"]
    _format = "3fI"
    _arrays = {"origin": [*"xyz"]}
    _classes = {"origin": vector.vec3}


class LightProbeTree(base.MappedArray):  # LUMP 103 (0067)
    """Identified by rexx"""
    # seems wrong, no clue as to connections
    tag: int  # could be flags but tends to increment (bitfield?)
    num_entries: int  # often looks like a valid float
    # num_entries switches between floats and small ints
    _format = "2I"  # could be too small
    _mapping = ["tag", "num_entries"]


class MaterialSort(base.MappedArray):  # LUMP 82 (0052)
    texture_data: int  # index of this MaterialSort's TextureData
    lightmap_header: int  # index of this MaterialSort's LightmapHeader
    cubemap: int  # index of this MaterialSort's Cubemap
    last_vertex: int  # last indexed vertex in VERTEX_RESERVED_X lump; TODO: verify
    vertex_offset: int  # firstVtxOffset; offset into appropriate VERTEX_RESERVED_X lump
    _mapping = ["texture_data", "lightmap_header", "cubemap", "last_vertex", "vertex_offset"]
    _format = "4hi"


class Mesh(base.Struct):  # LUMP 80 (0050)
    # built on valve.source.Face?
    first_mesh_index: int  # index into MeshIndices
    num_triangles: int  # number of triangles in MeshIndices after first_mesh_index
    first_vertex: int  # index to this Mesh's first VertexReservedX
    num_vertices: int  # lastVertexOffset? off by one
    vertex_type: int  # doesn't correlate w/ VERTEX_RESERVED_X in flags; TODO: MeshVertexType enum
    styles: List[int]  # from source; 4 different lighting states? "switchable lighting info"
    luxel_origin: List[int]  # same as source lightmap mins & size?
    luxel_offset_max: List[int]
    material_sort: int  # index of this Mesh's MaterialSort
    flags: MeshFlags  # (mesh.flags & MeshFlags.MASK_VERTEX).name == "VERTEX_RESERVED_X"
    __slots__ = ["first_mesh_index", "num_triangles", "first_vertex", "num_vertices",
                 "vertex_type", "styles", "luxel_origin", "luxel_offset_max",
                 "material_sort", "flags"]
    _format = "I4H4b2h2BHI"
    _arrays = {"styles": 4, "luxel_origin": 2, "luxel_offset_max": 2}
    _classes = {"flags": MeshFlags}


class MeshBounds(base.Struct):  # LUMP 81 (0051)
    origin: List[float]
    radius: float  # approx. magnitude of extents
    extents: List[float]  # bounds extend symmetrically by this much along each axis
    tan_yaw: float  # no clue what this is used for, AABB + Z rotation?
    # TODO: mins & maxs properties, possibly via a baseclass
    __slots__ = ["origin", "radius", "extents", "tan_yaw"]
    _format = "8f"  # Extreme SIMD
    _arrays = {"origin": [*"xyz"], "extents": [*"xyz"]}
    _classes = {"origin": vector.vec3, "extents": vector.vec3}

    @classmethod
    def from_bounds(cls, mins: List[float], maxs: List[float]) -> MeshBounds:
        out = cls()
        mins = vector.vec3(*mins)
        maxs = vector.vec3(*maxs)
        out.origin = maxs - mins
        out.extents = maxs - out.origin
        out.radius = out.extents.magnitude() + 0.001  # round up a little
        # out.tan_yaw = ...  # just leave as 0 for now
        return out


class Model(base.Struct):  # LUMP 14 (000E)
    """bsp.MODELS[0] is always worldspawn"""
    mins: List[float]  # bounding box mins
    maxs: List[float]  # bounding box maxs
    first_mesh: int  # index of first Mesh
    num_meshes: int  # number of Meshes after first_mesh in this model
    __slots__ = ["mins", "maxs", "first_mesh", "num_meshes"]
    _format = "6f2I"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}


class Node(base.Struct):  # LUMP 99 (0063)
    # NOTE: the struct length & positions of mins & maxs take advantage of SIMD 128-bit registers
    mins: List[float]
    unknown_1: int
    maxs: List[float]
    unknown_2: int
    __slots__ = ["mins", "unknown_1", "maxs", "unknown_2"]
    _format = "3fi3fi"  # Extreme SIMD
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}


class ObjRefBounds(base.Struct):  # LUMP 121 (0079)
    # NOTE: introduced in v29, not present in v25
    mins: List[float]
    mins_zero: int  # basically unused
    maxs: List[float]
    maxs_zero: int  # basically unused
    _format = "3fi3fi"  # Extreme SIMD
    __slots__ = ["mins", "mins_zero", "maxs", "maxs_zero"]
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}


class Plane(base.Struct):  # LUMP 1 (0001)
    normal: List[float]  # normal unit vector
    distance: float
    __slots__ = ["normal", "distance"]
    _format = "4f"
    _arrays = {"normal": [*"xyz"]}
    _classes = {"normal": vector.vec3}


class Portal(base.MappedArray):  # LUMP 108 (006C)
    """Identified by rexx#1287"""
    is_reversed: int  # bool?
    type: int  # TODO: see PortalType enum
    num_edges: int  # number of PortalEdges in this Portal
    padding: int  # should be 0
    first_reference: int  # first ??? in this Portal
    cell: int  # index of Cell this portal connects to?
    # do portals link cells together?
    # Cell -> Portal -> (different) Cell?
    plane: int  # Plane this portal lies on?
    # NOTE: valve.source.AreaPortal also indexes planes
    _mapping = ["is_reversed", "type", "num_edges", "padding", "first_reference", "cell", "plane"]
    _format = "4B2hi"
    # TODO: _classes {"type": PortalType}


class PortalIndexSet(base.Struct):  # LUMP 114 & 115 (0072 & 0073)
    """Identified by rexx#1287"""
    # PortalVertexSet / PortalEdgeSet
    index: List[int]  # -1 for None; essentially variable length
    __slots__ = ["index"]
    _format = "8h"
    _arrays = {"index": 8}


class PortalEdgeIntersectHeader(base.MappedArray):  # LUMP 116 (0074)
    """Confirmed by rexx#1287"""
    start: int  # unsure what this indexes
    count: int
    _mapping = ["start", "count"]
    _format = "2I"


class Primitive(base.BitField):  # LUMP 89 (0059)
    """identified by Fifty"""
    # same as the BitField component of GeoSet?
    unique_contents: int  # index into UniqueContents (Contents flags &ed together)
    index: int  # indexed lump depends on type
    type: PrimitiveType
    _fields = {"unique_contents": 8, "index": 16, "type": 8}
    _format = "I"
    _classes = {"flags": PrimitiveType}


class ShadowMesh(base.Struct):  # LUMP 127 (007F)
    """SHADOW_MESH_INDICES offset is end of previous ShadowMesh"""
    vertex_offset: int  # add each index in SHADOW_MESH_INDICES[prev_end:prev_end + num_triangles * 3]
    num_triangles: int  # number of triangles in SHADOW_MESH_INDICES
    is_opaque: int  # indexes ShadowMeshAlphaVertex if 0, ShadowMeshVertex if 1
    material_sort: int  # index into MaterialSort; -1 for None
    __slots__ = ["vertex_offset", "num_triangles", "is_opaque", "material_sort"]
    _format = "2I2h"
    _classes = {"is_opaque": bool}


class ShadowMeshAlphaVertex(base.Struct):  # LUMP 125 (007D)
    """"Identified by rexx#1287"""
    # seems to get paired w/ a material sort, might explain which material is used?
    position: List[float]
    uv: List[float]
    _format = "5f"
    __slots__ = ["position", "uv"]
    _arrays = {"position": [*"xyz"], "uv": [*"uv"]}
    _classes = {"position": vector.vec3, "uv": vector.vec2}


class TextureData(base.Struct):  # LUMP 2 (0002)
    """Hybrid of Source TextureData & TextureInfo"""
    reflectivity: List[float]  # matches .vtf reflectivity.rgb (always? black in r2)
    name_index: int  # index of material name in TEXTURE_DATA_STRING_DATA / TABLE
    size: List[int]  # dimensions of full texture
    view: List[int]  # dimensions of visible section of texture
    flags: int  # matches .flags of Mesh indexing this TextureData (Mesh->MaterialSort->TextureData)
    __slots__ = ["reflectivity", "name_index", "size", "view", "flags"]
    _format = "3f6i"
    _arrays = {"reflectivity": [*"rgb"],
               "size": ["width", "height"], "view": ["width", "height"]}
    _classes = {"flags": TextureDataFlags}
    # TODO: rgb24 reflectivity & width-height vec2 for size & view


class TextureVector(base.Struct):  # LUMP 95 (005F)
    s: List[float]  # S vector
    t: List[float]  # T vector
    __slots__ = ["s", "t"]
    _format = "8f"
    _arrays = {"s": [*"xyz", "offset"], "t": [*"xyz", "offset"]}
    # TODO: vec3 for texvec components
    # TODO: def uv_at(point: vector.vec3) -> vector.vec2:
    # --  """calculate uv coords from these texture vectors"""


class TricollHeader(base.Struct):  # LUMP 69 (0045)
    """Identified by rexx#1287"""
    flags: int  # TODO: TricollHeaderFlags enum
    texinfo_flags: int  # TextureDataFlags? always 0?
    texture_data: int  # for surfaceproperties & flags?
    num_vertices: int  # vertices are indexed by TricollTriangles?
    num_triangles: int
    num_bevels: int
    first_vertex: int  # index into Vertices? TricollTriangle for order
    first_triangle: int  # index into TricollTriangles; also indexes TricollBevelStarts?
    first_node: int  # index into TricollNodes
    first_bevel: int  # index into TricollBevelIndices?
    origin: vector.vec3
    scale: float
    __slots__ = ["flags", "texinfo_flags", "texture_data", "num_vertices",
                 "num_triangles", "num_bevels", "first_vertex", "first_triangle",
                 "first_node", "first_bevel", "origin", "scale"]
    _format = "6h4i4f"
    _arrays = {"origin": [*"xyz"]}
    _classes = {"origin": vector.vec3}


class TricollTriangle(base.BitField):  # LUMP 66 (0042)
    """Identified by Fifty"""
    A: int  # vertex index?
    B: int
    C: int
    unknown: int  # {0..31}, bank of indexable space?
    _fields = {"A": 9, "B": 9, "C": 9, "unknown": 5}
    _format = "I"


class TricollLeaf(base.MappedArray):  # LUMP ?? (00??)
    """Identified by rexx #1287"""
    first_unknown: int  # TODO: figure out what is being indexed
    num_unknowns: int  # TricollTriangles? Primitives?
    _mapping = ["first_unknown", "num_unknowns"]
    _format = "2h"


class TricollNode(base.Struct):  # LUMP 68 (0044)
    """Identified by rexx #1287"""
    origin: vector.vec3
    extents: vector.vec3
    # mins = origin - extents
    # maxs = origin + extents
    children: List[int]  # +ve for TricollNode; -ve for TricollLeaf?
    __slots__ = ["origin", "extents", "children"]
    _format = "6f4h"
    _arrays = {"origin": [*"xyz"], "extents": [*"xyz"], "children": 4}
    _classes = {"origin": vector.vec3, "extents": vector.vec3}


class WorldLight(source.WorldLight):  # LUMP 54 (0036)
    """pretty basic extension of valve.source.WorldLight"""
    origin: vector.vec3  # origin point of this light source
    intensity: vector.vec3  # brightness scalar?
    normal: vector.vec3  # light direction (used by EmitType.SURFACE & EmitType.SPOTLIGHT)
    shadow_cast_offset: vector.vec3  # new in titanfall
    unused: int  # formerly viscluster index?
    type: source.EmitType
    style: int  # lighting style (Face style index?)
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
    flags: source.WorldLightFlags
    texture_data: int  # index of TextureData
    owner: int  # parent entity ID
    __slots__ = ["origin", "intensity", "normal", "shadow_cast_offset", "unused",
                 "type", "style", "stop_dot", "stop_dot2", "exponent", "radius",
                 "constant", "linear", "quadratic",  # attenuation
                 "flags", "texture_data", "owner"]
    _format = "12f3i7f3i"  # 100 bytes
    _arrays = {"origin": [*"xyz"], "intensity": [*"xyz"], "normal": [*"xyz"], "shadow_cast_offset": [*"xyz"]}
    _classes = {"origin": vector.vec3, "intensity": vector.vec3, "normal": vector.vec3,
                "shadow_cast_offset": vector.vec3, "type": source.EmitType, "flags": source.WorldLightFlags}


# special vertices
class VertexBlinnPhong(base.Struct):  # LUMP 75 (004B)
    """Not used in any official map"""
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    colour: List[int]
    uv: List[float]
    tangent: List[float]  # 4 x 4 matrix? list of 4 quaternions?
    __slots__ = ["position_index", "normal_index", "colour", "uv", "lightmap", "tangent"]
    _format = "2I4B20f"  # 92 bytes
    _arrays = {"colour": [*"rgba"], "uv": [*"uv"], "lightmap": {"uv": [*"uv"]}, "tangent": 16}


class VertexLitBump(base.Struct):  # LUMP 73 (0049)
    """Common Worldspawn Geometry"""
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    uv: List[float]  # albedo uv coords
    colour: List[int]
    lightmap: List[float]
    # lightmap.uv: List[float]  # lightmap uv coords
    # lightmap.step: List[float]  # lightmap offset?
    tangent: List[int]  # indices to some vectors, but which lump are they stored in?
    __slots__ = ["position_index", "normal_index", "albedo_uv", "colour", "lightmap", "tangent"]
    _format = "2I2f4B4f2i"  # 44 bytes
    _arrays = {"albedo_uv": [*"uv"], "colour": [*"rgba"],
               "lightmap": {"uv": [*"uv"], "step": [*"xy"]},
               "tangent": [*"st"]}
    _classes = {"lightmap.step": vector.vec2}
    # TODO: albedo_uv vec2


class VertexLitFlat(base.Struct):  # LUMP 72 (0048)
    """Uncommon Worldspawn Geometry"""
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    albedo_uv: List[float]  # albedo uv coords
    colour: List[int]
    lightmap: List[float]
    # lightmap.uv: List[float]  # lightmap uv coords
    # lightmap.step: List[float]  # lightmap offset?
    __slots__ = ["position_index", "normal_index", "albedo_uv", "colour", "lightmap"]
    _format = "2I2f4B4f"
    _arrays = {"albedo_uv": [*"uv"], "colour": [*"rgba"],
               "lightmap": {"uv": [*"uv"], "step": [*"xy"]}}
    _classes = {"lightmap.step": vector.vec2}
    # TODO: albedo_uv vec2


class VertexUnlit(base.Struct):  # LUMP 71 (0047)
    """Tool Brushes"""
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    albedo_uv: List[float]  # albedo uv coords
    colour: List[int]  # usually white (0xFFFFFFFF)
    __slots__ = ["position_index", "normal_index", "albedo_uv", "colour"]
    _format = "2I2f4B"  # 20 bytes
    _arrays = {"albedo_uv": [*"uv"], "colour": [*"rgba"]}
    # TODO: _classes = {"uv": vec2, "colour": PixelRGBA32}


class VertexUnlitTS(base.Struct):  # LUMP 74 (004A)
    """Glass"""
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    albedo_uv: List[float]  # uv coords
    colour: List[int]
    tangent: List[int]  # indices to some vectors, but which lump are they stored in?
    __slots__ = ["position_index", "normal_index", "albedo_uv", "colour", "tangent"]
    _format = "2I2f4B2i"  # 28 bytes
    _arrays = {"albedo_uv": [*"uv"], "colour": [*"rgba"], "tangent": [*"st"]}
    # TODO: uv vec2


VertexReservedX = Union[VertexBlinnPhong, VertexLitBump, VertexLitFlat, VertexUnlit, VertexUnlitTS]  # type hint


# classes for special lumps, in alphabetical order:
class EntityPartitions(list):
    """name of each used .ent file"""  # [0] = "01*"; .0000.bsp_lump?
    def __init__(self, raw_lump: bytes):
        super().__init__(raw_lump.decode("ascii")[:-1].split(" "))

    def as_bytes(self) -> bytes:
        return " ".join(self).encode("ascii") + b"\0"


class GameLump_SPRP(source.GameLump_SPRP):  # sprp GameLump (LUMP 35)
    """use `lambda raw_lump: GameLump_SPRP(raw_lump, StaticPropvXX)` to implement"""
    StaticPropClass: object  # StaticPropv12
    model_names: List[str]
    leaves: List[int]
    # NOTE: both unknown_1 & unknown_2 are new
    # -- they might mark first_translucent_prop & first_alphatest_prop
    unknown_1: int
    unknown_2: int
    props: List[object] | List[bytes]  # List[StaticPropClass]

    def __init__(self, raw_sprp_lump: bytes, StaticPropClass: object):
        sprp_lump = io.BytesIO(raw_sprp_lump)
        self.StaticPropClass = StaticPropClass
        model_name_count = int.from_bytes(sprp_lump.read(4), "little")
        model_names = struct.iter_unpack("128s", sprp_lump.read(128 * model_name_count))
        setattr(self, "model_names", [t[0].replace(b"\0", b"").decode() for t in model_names])
        leaf_count = int.from_bytes(sprp_lump.read(4), "little")  # usually 0
        leaves = list(struct.iter_unpack("H", sprp_lump.read(2 * leaf_count)))
        setattr(self, "leaves", leaves)
        prop_count, unknown_1, unknown_2 = struct.unpack("3i", sprp_lump.read(12))
        self.unknown_1, self.unknown_2 = unknown_1, unknown_2
        if StaticPropClass is not None:
            read_size = struct.calcsize(StaticPropClass._format) * prop_count
            props = struct.iter_unpack(StaticPropClass._format, sprp_lump.read(read_size))
            setattr(self, "props", list(map(StaticPropClass.from_tuple, props)))
        else:
            prop_bytes = sprp_lump.read()
            prop_size = len(prop_bytes) // prop_count
            # NOTE: will break if prop_size does not divide evenly by prop_count
            setattr(self, "props", list(struct.iter_unpack(f"{prop_size}s", prop_bytes)))
        here = sprp_lump.tell()
        end = sprp_lump.seek(0, 2)
        assert here == end, "Had some leftover bytes, bad format"

    def as_bytes(self) -> bytes:
        if len(self.props) > 0:
            prop_bytes = [struct.pack(self.StaticPropClass._format, *p.as_tuple()) for p in self.props]
        else:
            prop_bytes = []
        return b"".join([len(self.model_names).to_bytes(4, "little"),
                         *[struct.pack("128s", n.encode("ascii")) for n in self.model_names],
                         len(self.leaves).to_bytes(4, "little"),
                         *[struct.pack("H", L) for L in self.leaves],
                         struct.pack("3I", len(self.props), self.unknown_1, self.unknown_2),
                         *prop_bytes])


class StaticPropv12(base.Struct):  # sprp GAME_LUMP (LUMP 35 / 0023) [version 12]
    """appears to extend valve.left4dead.StaticPropv8"""
    origin: List[float]  # x, y, z
    angles: List[float]  # pitch, yaw, roll
    model_name: int  # index into GAME_LUMP.sprp.model_names
    first_leaf: int
    num_leaves: int  # NOTE: Titanfall doesn't have visleaves?
    solid_mode: int  # bitflags
    flags: int
    skin: int
    # NOTE: BobTheBob's definition varies here:
    # int skin; float fade_min, fade_max; Vector lighting_origin;
    cubemap: int  # index of this StaticProp's Cubemap
    unknown: int
    forced_fade_scale: float
    cpu_level: List[int]  # min, max (-1 = any)
    gpu_level: List[int]  # min, max (-1 = any)
    diffuse_modulation: List[int]  # RGBA 32-bit colour
    scale: float
    disable_x360: int  # 4 byte bool
    collision_flags: List[int]  # add, remove
    __slots__ = ["origin", "angles", "model_name", "first_leaf", "num_leaves",
                 "solid_mode", "flags", "skin", "cubemap", "unknown",
                 "forced_fade_scale", "cpu_level", "gpu_level",
                 "diffuse_modulation", "scale", "disable_x360", "collision_flags"]
    _format = "6f3H2Bi2h4i2f8bfI2H"
    _arrays = {"origin": [*"xyz"], "angles": [*"yzx"], "unknown": 6, "fade_distance": ["min", "max"],
               "cpu_level": ["min", "max"], "gpu_level": ["min", "max"],
               "diffuse_modulation": [*"rgba"], "collision_flags": ["add", "remove"]}
    _classes = {"origin": vector.vec3}
    # TODO: Qangle vec3 type (0-360 pitch yaw roll), rgb32 diffuse_modulation


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = {"CM_BRUSH_SIDE_PLANE_OFFSETS": {0: shared.UnsignedShorts},
                      "CM_BRUSH_SIDE_PROPERTIES":    {0: BrushSideProperty},
                      "CM_PRIMITIVES":               {0: Primitive},
                      "CM_UNIQUE_CONTENTS":          {0: shared.UnsignedInts},  # source.Contents? test against vmts?
                      "CSM_OBJ_REFERENCES":          {0: shared.UnsignedShorts},
                      "MESH_INDICES":                {0: shared.UnsignedShorts},
                      "OBJ_REFERENCES":              {0: shared.UnsignedShorts},
                      "OCCLUSION_MESH_INDICES":      {0: shared.Shorts},
                      "PORTAL_EDGE_REFERENCES":      {0: shared.UnsignedShorts},
                      "PORTAL_VERTEX_REFERENCES":    {0: shared.UnsignedShorts},
                      "SHADOW_MESH_INDICES":         {0: shared.UnsignedShorts},
                      "TEXTURE_DATA_STRING_TABLE":   {0: shared.UnsignedInts},
                      "TRICOLL_BEVEL_STARTS":        {0: shared.UnsignedShorts},
                      "TRICOLL_BEVEL_INDICES":       {0: shared.UnsignedInts},
                      "TRICOLL_TRIANGLES":           {2: TricollTriangle}}

LUMP_CLASSES = {"CELLS":                             {0: Cell},
                "CELL_AABB_NODES":                   {0: CellAABBNode},
                "CELL_BSP_NODES":                    {0: CellBSPNode},
                "CM_BRUSHES":                        {0: Brush},
                "CM_BRUSH_SIDE_TEXTURE_VECTORS":     {0: TextureVector},
                "CM_GEO_SETS":                       {0: GeoSet},
                "CM_GEO_SET_BOUNDS":                 {0: Bounds},
                "CM_GRID_CELLS":                     {0: GridCell},
                "CM_PRIMITIVE_BOUNDS":               {0: Bounds},
                "CSM_AABB_NODES":                    {0: Node},
                "CUBEMAPS":                          {0: Cubemap},
                "LEAF_WATER_DATA":                   {1: source.LeafWaterData},
                "LIGHTMAP_HEADERS":                  {1: LightmapHeader},
                "LIGHTPROBES":                       {0: LightProbe},
                "LIGHTPROBE_REFERENCES":             {0: LightProbeRef},
                "LIGHTPROBE_TREE":                   {0: LightProbeTree},
                "MATERIAL_SORT":                     {0: MaterialSort},
                "MESHES":                            {0: Mesh},
                "MESH_BOUNDS":                       {0: MeshBounds},
                "MODELS":                            {0: Model},
                "OBJ_REFERENCE_BOUNDS":              {0: ObjRefBounds},
                "OCCLUSION_MESH_VERTICES":           {0: quake.Vertex},
                "PLANES":                            {1: Plane},
                "PORTALS":                           {0: Portal},
                "PORTAL_EDGES":                      {0: quake.Edge},
                "PORTAL_EDGE_INTERSECT_AT_EDGE":     {0: PortalIndexSet},
                "PORTAL_EDGE_INTERSECT_AT_VERTEX":   {0: PortalIndexSet},
                "PORTAL_EDGE_INTERSECT_HEADER":      {0: PortalEdgeIntersectHeader},
                "PORTAL_VERTEX_EDGES":               {0: PortalIndexSet},  # unsure
                "PORTAL_VERTICES":                   {0: quake.Vertex},
                "SHADOW_MESHES":                     {0: ShadowMesh},
                "SHADOW_MESH_ALPHA_VERTICES":        {0: ShadowMeshAlphaVertex},
                "SHADOW_MESH_OPAQUE_VERTICES":       {0: quake.Vertex},
                "TEXTURE_DATA":                      {1: TextureData},
                "TRICOLL_HEADERS":                   {1: TricollHeader},
                "TRICOLL_LEAVES":                    {1: TricollLeaf},
                "TRICOLL_NODES":                     {1: TricollNode},
                "VERTEX_BLINN_PHONG":                {0: VertexBlinnPhong},
                "VERTEX_LIT_BUMP":                   {1: VertexLitBump},
                "VERTEX_LIT_FLAT":                   {1: VertexLitFlat},
                "VERTEX_NORMALS":                    {0: quake.Vertex},
                "VERTEX_UNLIT":                      {0: VertexUnlit},
                "VERTEX_UNLIT_TS":                   {0: VertexUnlitTS},
                "VERTICES":                          {0: quake.Vertex},
                "WORLD_LIGHTS":                      {1: WorldLight}}

SPECIAL_LUMP_CLASSES = {"CM_GRID":                   {0: Grid.from_bytes},
                        "ENTITY_PARTITIONS":         {0: EntityPartitions},
                        "ENTITIES":                  {0: shared.Entities},
                        # NOTE: .ent files are handled directly by the RespawnBsp class
                        "LEVEL_INFO":                {0: LevelInfo.from_bytes},
                        "PAKFILE":                   {0: shared.PakFile},
                        "PHYSICS_COLLIDE":           {0: valve_physics.CollideLump},
                        "TEXTURE_DATA_STRING_DATA":  {0: shared.TextureDataStringData}}
# TODO: LightProbeParentInfos/BspNodes/RefIds & StaticPropLightProbeIndices may all be Special

GAME_LUMP_HEADER = source.GameLumpHeader

GAME_LUMP_CLASSES = {"sprp": {12: lambda raw_lump: GameLump_SPRP(raw_lump, StaticPropv12)}}


# branch exclusive methods, in alphabetical order:
def vertices_of_mesh(bsp, mesh_index: int) -> List[VertexReservedX]:
    """gets the VertexReservedX linked to bsp.MESHES[mesh_index]"""
    # https://raw.githubusercontent.com/Wanty5883/Titanfall2/master/tools/TitanfallMapExporter.py (McSimp)
    mesh = bsp.MESHES[mesh_index]
    material_sort = bsp.MATERIAL_SORT[mesh.material_sort]
    start = mesh.first_mesh_index
    finish = start + mesh.num_triangles * 3
    indices = [material_sort.vertex_offset + i for i in bsp.MESH_INDICES[start:finish]]
    VERTEX_LUMP = getattr(bsp, (MeshFlags(mesh.flags) & MeshFlags.MASK_VERTEX).name)
    return [VERTEX_LUMP[i] for i in indices]


def vertices_of_model(bsp, model_index: int) -> List[VertexReservedX]:
    """gets the VertexReservedX linked to every Mesh in bsp.MODELS[model_index]"""
    # NOTE: model 0 is worldspawn, other models are referenced by entities
    out = list()
    model = bsp.MODELS[model_index]
    for i in range(model.first_mesh, model.num_meshes):
        out.extend(bsp.vertices_of_mesh(i))
    return out


def replace_texture(bsp, texture: str, replacement: str):
    """Substitutes a texture name in the .bsp (if it is present)"""
    texture_index = bsp.TEXTURE_DATA_STRING_DATA.index(texture)  # fails if texture is not in bsp
    bsp.TEXTURE_DATA_STRING_DATA.insert(texture_index, replacement)
    bsp.TEXTURE_DATA_STRING_DATA.pop(texture_index + 1)
    bsp.TEXTURE_DATA_STRING_TABLE = list()
    offset = 0  # starting index of texture name in raw TEXTURE_DATA_STRING_DATA
    for texture_name in bsp.TEXTURE_DATA_STRING_DATA:
        bsp.TEXTURE_DATA_STRING_TABLE.append(offset)
        offset += len(texture_name) + 1  # +1 for null byte


def find_mesh_by_texture(bsp, texture: str) -> Mesh:
    """This is a generator, will yeild one Mesh at a time.  Very innefficient!"""
    texture_index = bsp.TEXTURE_DATA_STRING_DATA.index(texture)  # fails if texture is not in bsp
    for texture_data_index, texture_data in enumerate(bsp.TEXTURE_DATA):
        if texture_data.name_index != texture_index:
            continue
        for material_sort_index, material_sort in enumerate(bsp.MATERIAL_SORT):
            if material_sort.texture_data != texture_data_index:
                continue
            for mesh in bsp.MESHES:
                if mesh.material_sort == material_sort_index:
                    yield mesh


def get_mesh_texture(bsp, mesh_index: int) -> str:
    """Returns the name of the .vmt applied to bsp.MESHES[mesh_index]"""
    mesh = bsp.MESHES[mesh_index]
    material_sort = bsp.MATERIAL_SORT[mesh.material_sort]
    texture_data = bsp.TEXTURE_DATA[material_sort.texture_data]
    return bsp.TEXTURE_DATA_STRING_DATA[texture_data.name_index]


def search_all_entities(bsp, **search: Dict[str, str]) -> Dict[str, List[Dict[str, str]]]:
    """search_all_entities(key="value") -> {"LUMP": [{"key": "value", ...}]}"""
    out = dict()
    for LUMP_name in ("ENTITIES", *(f"ENTITIES_{s}" for s in ("env", "fx", "script", "snd", "spawn"))):
        entity_lump = getattr(bsp, LUMP_name, shared.Entities(b""))
        results = entity_lump.search(**search)
        if len(results) != 0:
            out[LUMP_name] = results
    return out


def shadow_meshes_as_obj(bsp) -> str:
    """almost working"""
    # TODO: figure out how SHADOW_MESH_ALPHA_VERTICES are indexed
    # TODO: what does ShadowMesh.unknown relate to? alpha indexing?
    out = [f"# generated with bsp_tool from {bsp.filename}",
           "# SHADOW_MESH_OPAQUE_VERTICES"]
    for v in bsp.SHADOW_MESH_OPAQUE_VERTICES:
        out.append(f"v {v.x} {v.y} {v.z}")
    if hasattr(bsp, "SHADOW_MESH_ALPHA_VERTICES"):
        out.append("# SHADOW_MESH_ALPHA_VERTICES")
        for v in bsp.SHADOW_MESH_ALPHA_VERTICES:
            out.append(f"v {v.x} {v.y} {v.z}\nvt {v.unknown[0]} {v.unknown[1]}")
    # TODO: group by ShadowEnvironment if titanfall2
    end = 0
    for i, mesh in enumerate(bsp.SHADOW_MESHES):
        out.append(f"o mesh_{i}")
        for j in range(mesh.num_triangles):
            start = end + j * 3
            tri = bsp.SHADOW_MESH_INDICES[start:start + 3]
            v_tri = [x + 1 + mesh.vertex_offset for x in tri]
            if not mesh.is_opaque:  # AlphaVertices
                # TODO: figure out what to do with material sort
                # -- usemtl material_sort.texture_data.name?
                v_tri = [f"{i + len(bsp.SHADOW_MESH_OPAQUE_VERTICES)}/{i}" for i in v_tri]  # v/vt
            out.append(f"f {' '.join(map(str, v_tri))}")
        end = start + 3
    return "\n".join(out)


def occlusion_mesh_as_obj(bsp) -> str:
    out = [f"# generated with bsp_tool from {bsp.filename}",
           "# OCCLUSION MESH"]
    for v in bsp.OCCLUSION_MESH_VERTICES:
        out.append(f"v {v.x} {v.y} {v.z}")
    for i in range(0, len(bsp.OCCLUSION_MESH_INDICES), 3):
        tri = [str(x + 1) for x in bsp.OCCLUSION_MESH_INDICES[i:i + 3]]
        out.append(f"f {' '.join(tri)}")
    return "\n".join(out)


def portals_as_prt(bsp) -> str:
    out = ["PRT1", str(len(bsp.CELLS)), str(len(bsp.PORTALS))]
    for ci, cell in enumerate(bsp.CELLS):
        for pi in range(cell.first_portal, cell.first_portal + cell.num_portals):
            portal = bsp.PORTALS[pi]
            refs = bsp.PORTAL_EDGE_REFERENCES[portal.first_reference:portal.first_reference + portal.num_edges]
            winding = [bsp.PORTAL_VERTICES[bsp.PORTAL_EDGES[r // 2][r & 1]] for r in refs]
            # windings are a mess in mp_box, but r2/mp_lobby looks ok
            # checking vertices are on plane & sorting verts didn't do much
            # normal = bsp.PLANES[portal.plane].normal
            # winding = vector.sort_clockwise(winding, normal)
            out.append(" ".join([f"{len(winding)} {ci} {portal.cell}", *[f"({v.x} {v.y} {v.z})" for v in winding]]))
    return "\n".join(out)


def get_brush_sides(bsp, brush_index: int) -> Dict[str, Any]:
    if brush_index > len(bsp.CM_BRUSHES):
        raise IndexError("brush index out of range")
    out = dict()
    brush = bsp.CM_BRUSHES[brush_index]
    first = 6 * brush.index + brush.brush_side_offset
    last = first + 6 + brush.num_plane_offsets
    out["properties"] = bsp.CM_BRUSH_SIDE_PROPERTIES[first:last]
    out["texture_vectors"] = bsp.CM_BRUSH_SIDE_TEXTURE_VECTORS[first:last]
    out["textures"] = [p & BrushSideProperty.MASK_TEXTURE_DATA for p in out["properties"]]
    out["textures"] = [bsp.TEXTURE_DATA_STRING_DATA[bsp.TEXTURE_DATA[tdi].name_index] for tdi in out["textures"]]
    # brush bounds -> geo
    origin = vector.vec3(*brush.origin)
    extents = vector.vec3(*brush.extents)
    mins, maxs = origin - extents, origin + extents
    brush_planes = list()  # [(normal: vec3, distance: float)]
    # axial planes
    for axis, min_dist, max_dist in zip("xyz", mins, maxs):
        brush_planes.append((vector.vec3(**{axis: 1}), max_dist))
        brush_planes.append((vector.vec3(**{axis: -1}), -min_dist))
    # non-axial planes
    for i in range(brush.num_plane_offsets):
        brush_plane_offset = brush.brush_side_offset + i - bsp.CM_BRUSH_SIDE_PLANE_OFFSETS[brush.brush_side_offset + i]
        normal, distance = bsp.PLANES[bsp.CM_GRID.base_plane_offset + brush_plane_offset]
        brush_planes.append((-normal, -distance))
    out["planes"] = brush_planes
    # NOTE: which planes are used is likely filtered by brush side properties
    return out


# "debug" methods for investigating the compile process
def debug_TextureData(bsp):
    print("# TD_index  TD.name  TextureData.flags")
    for i, td in enumerate(bsp.TEXTURE_DATA):
        print(f"{i:02d} {bsp.TEXTURE_DATA_STRING_DATA[td.name_index]:<48s} {td.flags!r}")


def debug_unused_TextureData(bsp):
    used_texture_datas = {bsp.MATERIAL_SORT[m.material_sort].texture_data for m in bsp.MESHES}
    return used_texture_datas.difference({*range(len(bsp.TEXTURE_DATA))})


def debug_Mesh_stats(bsp):
    print("# index  vertex_lump  texture_data_index  texture  mesh_indices_range")
    for i, model in enumerate(bsp.MODELS):
        print(f"# MODELS[{i}]")
        for j in range(model.first_mesh, model.first_mesh + model.num_meshes):
            mesh = bsp.MESHES[j]
            material_sort = bsp.MATERIAL_SORT[mesh.material_sort]
            texture_data = bsp.TEXTURE_DATA[material_sort.texture_data]
            texture_name = bsp.TEXTURE_DATA_STRING_DATA[texture_data.name_index]
            vertex_lump = (MeshFlags(mesh.flags) & MeshFlags.MASK_VERTEX).name
            indices = bsp.MESH_INDICES[mesh.first_mesh_index:mesh.first_mesh_index + mesh.num_triangles * 3]

            def reduce_to_ranges(numbers: List[int]) -> (int, int):  # generator
                sorted_numbers = sorted(set(numbers))
                for a, b in itertools.groupby(enumerate(sorted_numbers), lambda ix: ix[0] - ix[1]):
                    b = list(b)
                    yield b[0][1], b[-1][1]

            _range = ", ".join([f"({s}->{e})" for s, e in reduce_to_ranges(sorted(indices))])
            print(f"{j:02d} {vertex_lump:<15s} {material_sort.texture_data:02d} {texture_name:<48s} {_range}")


methods = [vertices_of_mesh, vertices_of_model, replace_texture, find_mesh_by_texture, get_mesh_texture,
           search_all_entities, shared.worldspawn_volume, shadow_meshes_as_obj, occlusion_mesh_as_obj, get_brush_sides,
           debug_TextureData, debug_unused_TextureData, debug_Mesh_stats, portals_as_prt]
