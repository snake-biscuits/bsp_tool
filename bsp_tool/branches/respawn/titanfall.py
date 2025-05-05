# https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Titanfall
from __future__ import annotations
import enum
import io
import math
import struct
from typing import Dict, List, Tuple, Union

from ... import archives
from ... import core
from ... import lumps
from ...utils import binary
from ...utils import editor
from ...utils import physics
from ...utils import geometry
from ...utils import texture
from ...utils import vector
from .. import colour
from .. import shared
from ..id_software import quake
from ..id_software import quake3
# from ..valve import physics as vphysics
from ..valve import sdk_2013
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
    MATERIAL_SORTS = 0x0052
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


# SHADOWS
# ShadowMesh -> ShadowMeshIndex -> ShadowMeshOpaqueVertex
#           \-> MaterialSort?  \-> ShadowMeshAlphaVertex

# CSMAABBNode -> CSMObjReference -> ??? (starts high, out of ObjRefs range)
#            \-> CSMAABBNode

# LightmapHeader -> LIGHTMAP_DATA_SKY
#               \-> LIGHTMAP_DATA_REAL_TIME_LIGHTS

# LIGHTPROBE*
# LightProbeTree -?> LightProbeRef -> LightProbe
# StaticPropLightProbeIndices & StaticProps are parallel

# VIS LUMPS
# CellAABBNodes -> ObjReferences -> Meshes / StaticProp
#              \-> CellAABBNodes

# ObjReferences indices start w/ Model[0] (worldspawn) meshes, then GameLump.sprp.props
# ObjReferences & ObjReferenceBounds are parallel

#            /-> CellBspNode
# CellBspNode -> Cell
#            \-> Plane

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
# GM_GRID holds world bounds & other metadata

# Grid -> GridCell -> GeoSet -> Primitive

#          /-> UniqueContents
# Primitive -> .primitive.type / .type -> Brush OR Tricoll

# GeoSets can contain duplicates (use same .straddle_group)
# GeoSets is parallel w/ GeoSet Bounds
# Primitives is parallel w/ PrimitiveBounds
# PrimitiveBounds & GeoSetBounds use the same "Bounds" type

# CM_BRUSH: brushwork geo
#      /-> BrushSidePlaneOffset -> Plane
# Brush -> BrushSideProperties -> TextureData
#      \-> BrushSideTextureVector

# BrushSideProperties is parallel w/ BrushSideTextureVector (one per brushside)
# len(BrushSideProperties/TextureVectors) = len(Brushes) * 6 + len(BrushSidePlaneOffsets)
# Brush.num_brush_sides (derived) is 6 + Brush.num_plane_offsets

# TRICOLL_* (Triangle Collision for patches / displacements)
#              /-> TextureData
#             /--> Vertices
# TricollHeader -> TricollTriangle -> Vertices
#             \--> TricollNode -?> TricollNode / ???
#              \-> TricollBevelIndices? -?> ?

# TricollBevelStarts is parallel w/ TricollTriangles


# engine limits:
# NOTE: max map coords are -32768 -> 32768 along each axis (Apex is 64Kx64K, double this limit!)
class MAX:
    MODELS = 1024
    TEXTURE_DATA = 2048
    WORLD_LIGHTS = 4064
    STATIC_PROPS = 40960


# flag enums
class BrushSideFlag(enum.IntFlag):  # use by BrushSideProperty
    NONE = 0x00
    REPLACES = 0x20  # axial: replaced by non-axial; non-axial: replaces axial
    ABUTTING = 0x40  # no gap between this and the neighbouring brush


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


class StaticPropCollision(enum.Enum):
    # extends valve.source.StaticPropCollision
    NON_SOLID = 0
    UNKNOWN_1 = 1  # rare, low impact?
    BOUNDING_BOX = 2
    VPHYSICS = 6
    UNKNOWN_7 = 7  # often on large / hero props; more polished than 6?


class PortalType(enum.Enum):
    CELL = 0  # portal connects to another cell
    SKYBOX = 1  # lines up w/ "tools/toolsskybox" brushsides
    # NOTE: if portal.type == PortalType.SKYBOX: portal.cell = len(bsp.CELLS) + 1
    WATER = 2  # occurs on planes matching LeafWaterData surface_z


class PrimitiveType(enum.Enum):
    """Used by CMGeoSet & CMPrimitive to identify collidable children"""
    BRUSH = 0
    TRICOLL = 64


class WorldLightFlags(enum.IntFlag):
    # NOTE: other flags are used
    UNKNOWN_1 = 1 << 2  # 0x04
    UNKNOWN_2 = 1 << 3  # 0x08
    UNKNOWN_3 = 1 << 4  # 0x10
    # NOTE: if 0x08 is set and 0x10 unset, use parent info matrix
    # -- this is a rare combo and only seems to appear on spotlights
    UNKNOWN_4 = 1 << 5  # 0x20
    UNKNOWN_5 = 1 << 6  # 0x40
    UNKNOWN_6 = 1 << 7  # 0x80


# classes for lumps, in alphabetical order:
class Bounds(core.Struct):  # LUMP 68, 88 & 90 (0044, 0058 & 005A)
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

    @property
    def yaw(self) -> float:
        # NOTE: could be backwards
        # -- rotation in Blender is inverted from top orthographic view if I specify Z-axis
        return math.degrees(math.atan2(self.positive_sin / 0x8000, -self.negative_cos / 0x8000))

    def as_model(self) -> geometry.Model:
        aabb = physics.AABB.from_origin_extents(self.origin, self.extents)
        return geometry.Model(
            meshes=aabb.as_model().meshes,
            origin=self.origin,
            angles=vector.vec3(z=self.yaw))


class Brush(core.Struct):  # LUMP 92 (005C)
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


class BrushSideProperty(core.BitField):  # LUMP 94 (005E)
    flags: BrushSideFlag
    texture_data: int  # TextureData of this BrushSide
    # NOTE: unsure of exact split, assuming MAX.TEXTURE_DATA == 512
    _fields = {"flags": 7, "texture_data": 9}
    _format = "H"
    _classes = {"flags": BrushSideFlag}


class Cell(core.Struct):  # LUMP 107 (006B)
    """Identified by Fifty#8113 & rexx#1287"""
    # NOTE: inifinity_ward.call_of_duty1 also introduced a Cell lump
    num_portals: int  # index into Portal lump?
    first_portal: int  # number of Portals in this Cell?
    # TODO: confirm always 0xFFFF, 0XFFFF
    flags: int  # skyFlags; visibility related?
    leaf_water_data: int  # index into LeafWaterData; -1 for None
    __slots__ = ["num_portals", "first_portal", "flags", "leaf_water_data"]
    _format = "4h"
    _classes = {"flags": CellSkyFlags}


class CellAABBNode(core.Struct):  # 119 (0077)
    """Identified by Fifty#8113"""
    origin: vector.vec3
    num_children: int
    num_obj_refs: int
    total_obj_refs: int  # total ObjReferences across all children
    extents: vector.vec3
    first_child: int  # index into CellAABBNodes
    first_obj_ref: int  # index into ObjReferences
    __slots__ = ["origin", "num_children", "num_obj_refs", "total_obj_refs",
                 "extents", "first_child", "first_obj_ref"]
    _format = "3f2BH3f2H"  # Extreme SIMD
    _arrays = {"origin": [*"xyz"], "extents": [*"xyz"]}
    _classes = {"origin": vector.vec3, "extents": vector.vec3}


class CellBSPNode(core.MappedArray):  # LUMP 106 (006A)
    """Identified by rexx#1287"""
    plane: int  # index of Plane that splits this Node
    child: int  # indexes CellBspNodes if plane != -1 else Cells
    _mapping = ["plane", "child"]
    _format = "2i"


class CSMAABBNode(core.Struct):  # LUMP 99 (0063)
    """Identified by Fifty#8113"""
    mins: vector.vec3
    num_children: int
    num_obj_refs: int
    total_obj_refs: int  # total CSMObjReferences across all children
    maxs: vector.vec3
    first_child: int  # index into CSMAABBNodes
    first_obj_ref: int  # index into CSMObjReferences
    __slots__ = ["mins", "num_children", "num_obj_refs", "total_obj_refs",
                 "maxs", "first_child", "first_obj_ref"]
    _format = "3f2BH3f2H"  # Extreme SIMD
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}


class Cubemap(core.Struct):  # LUMP 42 (002A)
    origin: vector.vec3  # int32_t
    unknown: int  # index? flags?
    __slots__ = ["origin", "unknown"]
    _format = "3iI"
    _arrays = {"origin": [*"xyz"]}
    _classes = {"origin": vector.vec3}


class GeoSet(core.Struct):  # LUMP 87 (0057)
    # Parallel w/ GeoSetBounds
    straddle_group: int
    # if == 0: only touches parent GridCell
    # if != 0: touches multiple GridCells & might be cached already
    num_primitives: int  # special case if 1 (see below)
    primitive: List[int]
    # primitive.type: PrimitiveType  # 0 if num_primitives > 1
    # primitive.index: int  # index into Primitives if num_primitives > 1
    # primitive.unique_contents: int  # index into UniqueContents
    __slots__ = ["straddle_group", "num_primitives", "primitive"]
    _format = "2HI"
    _bitfields = {"primitive": {"type": 8, "index": 16, "unique_contents": 8}}
    _classes = {"primitive.type": PrimitiveType}


# NOTE: only one 28 byte entry per file
class Grid(core.Struct):  # LUMP 85 (0055)
    """splits the map into a grid on the XY-axes"""
    # grid pattern start at mins.xy, increments Y first, then X
    scale: float  # 256 for r1, 704 for r2
    offset: vector.vec2  # position of first GridCell (mins.xy)
    count: vector.vec2  # x * y = number of GridCells in worldspawn
    # count.x * count.y + len(Models) = len(CMGridCells)
    # mins = offset * scale
    # maxs = (offset + count) * scale
    # NOTE: bounds covers Models[0]
    num_straddle_groups: int  # linked to GeoSets, for objects in multiple GridCells?
    first_brush_plane: int  # index of first Plane indexed by Brushes
    # other planes might be used by portals, unsure
    __slots__ = ["scale", "offset", "count", "num_straddle_groups", "first_brush_plane"]
    _format = "f6i"
    _arrays = {"offset": [*"xy"], "count": [*"xy"]}


class GridCell(core.MappedArray):  # LUMP 86 (0056)
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
class LevelInfo(core.Struct):  # LUMP 123 (007B)
    """Identified by Fifty"""
    # implies worldspawn (model[0]) mesh order to be: opaque, decals, transparent, skybox
    first_decal_mesh: int
    first_transparent_mesh: int
    first_sky_mesh: int
    num_static_props: int  # len(bsp.GAME_LUMP.sprp.props)
    sun_normal: vector.vec3  # vector matching angles of last indexed light_environment entity
    __slots__ = ["first_decal_mesh", "first_transparent_mesh", "first_sky_mesh", "num_static_props", "sun_normal"]
    _format = "4I3f"
    _arrays = {"sun_normal": [*"xyz"]}
    _classes = {"sun_normal": vector.vec3}


class LightmapHeader(core.MappedArray):  # LUMP 83 (0053)
    type: int  # TODO: LightmapHeaderType enum
    width: int
    height: int
    _mapping = ["type", "width", "height"]
    _format = "I2H"
    # TODO: _classes = {"type": LightmapTypeheader}


class LightProbe(core.Struct):  # LUMP 101 (0065)
    """Identified by rexx"""  # untested
    cube: List[List[int]]  # rgb888 ambient light cube
    sky_dir_sun_vis: List[int]  # ???
    static_light: List[List[int]]  # connection to local static lights
    # static_light.weights: List[int]  # up to 4 scalars; default 0
    # static_light.indices: List[int]  # up to 4 indices; default -1
    padding: int
    __slots__ = ["cube", "sky_dir_sun_vis", "static_light", "padding"]
    _format = "24B4h4B4hI"
    _arrays = {"cube": {x: [*"rgba"] for x in "ABCDEF"}, "sky_dir_sun_vis": 4,
               "static_light": {"weights": 4, "indices": 4}}
    # TODO: map cube face names to UP, DOWN etc.
    # TODO: ambient light cube childClass


class LightProbeRef(core.Struct):  # LUMP 104 (0068)
    origin: List[float]  # coords of LightProbe
    lightprobe: int  # index of this LightProbeRef's LightProbe
    # NOTE: not every lightprobe is indexed
    __slots__ = ["origin", "lightprobe"]
    _format = "3fI"
    _arrays = {"origin": [*"xyz"]}
    _classes = {"origin": vector.vec3}


class LightProbeTree(core.MappedArray):  # LUMP 103 (0067)
    """Identified by rexx"""
    tag: int  # bitfield?
    num_entries: int  # float (node) or small int (leaf)
    _format = "2I"
    _mapping = ["tag", "num_entries"]


class MaterialSort(core.MappedArray):  # LUMP 82 (0052)
    texture_data: int  # index of this MaterialSort's TextureData
    lightmap_header: int  # index of this MaterialSort's LightmapHeader
    cubemap: int  # index of this MaterialSort's Cubemap
    last_vertex: int  # last indexed vertex in VERTEX_RESERVED_X lump; TODO: verify
    vertex_offset: int  # firstVtxOffset; offset into appropriate VERTEX_RESERVED_X lump
    _mapping = ["texture_data", "lightmap_header", "cubemap", "last_vertex", "vertex_offset"]
    _format = "4hi"


class Mesh(core.Struct):  # LUMP 80 (0050)
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


class MeshBounds(core.Struct):  # LUMP 81 (0051)
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


class Model(core.Struct):  # LUMP 14 (000E)
    """bsp.MODELS[0] is always worldspawn"""
    mins: vector.vec3  # bounding box mins
    maxs: vector.vec3  # bounding box maxs
    first_mesh: int  # index of first Mesh
    num_meshes: int  # number of Meshes after first_mesh in this model
    __slots__ = ["mins", "maxs", "first_mesh", "num_meshes"]
    _format = "6f2I"
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}


class ObjRefBounds(core.Struct):  # LUMP 121 (0079)
    # NOTE: introduced in v29, not present in v25
    mins: vector.vec3
    mins_zero: int  # basically unused
    maxs: vector.vec3
    maxs_zero: int  # basically unused
    _format = "3fi3fi"  # Extreme SIMD
    __slots__ = ["mins", "mins_zero", "maxs", "maxs_zero"]
    _arrays = {"mins": [*"xyz"], "maxs": [*"xyz"]}
    _classes = {"mins": vector.vec3, "maxs": vector.vec3}


class Portal(core.MappedArray):  # LUMP 108 (006C)
    """Identified by rexx#1287"""
    is_reversed: int  # bool?
    type: PortalType
    num_edges: int  # number of PortalEdges in this Portal
    padding: int  # should be 0
    first_reference: int  # first ??? in this Portal
    cell: int  # index into Cells
    # NOTE: if type == 1; cell index is too high
    plane: int  # index of Plane this Portal lies on
    _mapping = ["is_reversed", "type", "num_edges", "padding", "first_reference", "cell", "plane"]
    _format = "4B2hi"
    _classes = {"type": PortalType}


class PortalIndexSet(core.Struct):  # LUMP 114 & 115 (0072 & 0073)
    """Identified by rexx#1287"""
    # PortalVertexSet / PortalEdgeSet
    index: List[int]  # -1 for None; essentially variable length
    __slots__ = ["index"]
    _format = "8h"
    _arrays = {"index": 8}


class PortalEdgeIntersectHeader(core.MappedArray):  # LUMP 116 (0074)
    """Confirmed by rexx#1287"""
    start: int  # unsure what this indexes
    count: int
    _mapping = ["start", "count"]
    _format = "2I"


class Primitive(core.BitField):  # LUMP 89 (0059)
    """identified by Fifty"""
    # same as the BitField component of GeoSet?
    type: PrimitiveType
    index: int  # indexed lump depends on type
    unique_contents: int  # index into UniqueContents (Contents flags OR-ed together)
    _fields = {"type": 8, "index": 16, "unique_contents": 8}
    _format = "I"
    _classes = {"type": PrimitiveType}


class ShadowMesh(core.Struct):  # LUMP 127 (007F)
    """SHADOW_MESH_INDICES offset is end of previous ShadowMesh"""
    vertex_offset: int  # index into ShadowMeshAlpha / OpaqueVertices
    # first_index = sum(sm.num_triangles * 3 for sm in bsp.SHADOW_MESH_INDICES[:index])
    num_triangles: int  # number of triangles in ShadowMeshIndices
    is_opaque: bool  # indexes ShadowMeshAlphaVertex if 0, ShadowMeshVertex if 1
    material_sort: int  # index into MaterialSort; -1 for None
    __slots__ = ["vertex_offset", "num_triangles", "is_opaque", "material_sort"]
    _format = "2I2h"
    _classes = {"is_opaque": bool}


class ShadowMeshAlphaVertex(core.Struct):  # LUMP 125 (007D)
    """"Identified by rexx#1287"""
    # seems to get paired w/ a material sort, might explain which material is used?
    position: List[float]
    uv: List[float]
    _format = "5f"
    __slots__ = ["position", "uv"]
    _arrays = {"position": [*"xyz"], "uv": [*"uv"]}
    _classes = {"position": vector.vec3, "uv": vector.vec2}


class TextureData(core.Struct):  # LUMP 2 (0002)
    """Hybrid of Source TextureData & TextureInfo"""
    reflectivity: List[float]  # matches .vtf reflectivity.rgb (always? black in r2)
    name_index: int  # index of material name in TEXTURE_DATA_STRING_DATA / TABLE
    size: List[int]  # dimensions of full texture
    view: List[int]  # dimensions of visible section of texture
    flags: TextureDataFlags  # matches .flags of Mesh indexing this TextureData (Mesh->MaterialSort->TextureData)
    __slots__ = ["reflectivity", "name_index", "size", "view", "flags"]
    _format = "3f6i"
    _arrays = {"reflectivity": [*"rgb"],
               "size": ["width", "height"], "view": ["width", "height"]}
    _classes = {"flags": TextureDataFlags}
    # TODO: rgb24 reflectivity & width-height vec2 for size & view


class TextureVector(core.Struct):  # LUMP 95 (005F)
    # NOTE: texture.TextureVector(texture.ProjectionAxis(*s), texture.ProjectionAxis(*t))
    s: List[float]  # S vector
    t: List[float]  # T vector
    __slots__ = ["s", "t"]
    _format = "8f"
    _arrays = {"s": {"axis": [*"xyz"], "offset": None},
               "t": {"axis": [*"xyz"], "offset": None}}
    _classes = {f"{a}.axis": vector.vec3 for a in "st"}


class TricollHeader(core.Struct):  # LUMP 69 (0045)
    """Identified by rexx#1287"""
    flags: int  # always 0?
    texture_flags: TextureDataFlags  # copy of texture_data.flags
    texture_data: int  # probably for surfaceproperties & decals
    num_vertices: int  # Vertices indexed by TricollTriangles
    num_triangles: int  # number of TricollTriangles in this TricollHeader
    # num_nodes is derived from the following formula:
    # 2 * (num_triangles - (num_triangles + 3) % 6 + 3) // 3
    num_bevel_indices: int
    first_vertex: int  # index into Vertices, added as an offset to TricollTriangles
    first_triangle: int  # index into TricollTriangles;
    first_node: int  # index into TricollNodes
    first_bevel_index: int  # index into TricollBevelIndices?
    origin: vector.vec3  # true origin is -(origin / scale)
    scale: float  # 0.0 for patches
    __slots__ = ["flags", "texture_flags", "texture_data",
                 "num_vertices", "num_triangles", "num_bevel_indices",
                 "first_vertex", "first_triangle", "first_node", "first_bevel_index",
                 "origin", "scale"]
    _format = "6h4i4f"
    _arrays = {"origin": [*"xyz"]}
    _classes = {"texture_flags": TextureDataFlags, "origin": vector.vec3}
    # TODO: "flags": TricollHeaderFlags

    @property
    def num_nodes(self) -> int:
        return 2 * (self.num_triangles - (self.num_triangles + 3) % 6 + 3) // 3


class TricollTriangle(core.BitField):  # LUMP 66 (0042)
    """Identified by Fifty & RoyalBlue"""
    A: int  # indexes VERTICES[header.first_vertex + A]
    B: int  # indexes VERTICES[header.first_vertex + A + B]
    C: int  # indexes VERTICES[header.first_vertex + A + C]
    flags: int  # seems related to shape & orientation
    _fields = {"flags": 8, "C": 7, "B": 7, "A": 10}
    _format = "I"
    # TODO: _classes = {"flags": TricollTriangleFlags}


class WorldLight(source.WorldLight):  # LUMP 54 (0036)
    """pretty basic extension of valve.source.WorldLight"""
    origin: vector.vec3  # origin point of this light source
    intensity: vector.vec3  # brightness scalar?
    normal: vector.vec3  # light direction (used by EmitType.SURFACE & EmitType.SPOTLIGHT)
    shadow_offset: vector.vec3  # new in titanfall
    viscluster: int  # unused
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
    flags: WorldLightFlags
    texture_data: int  # index of TextureData
    parent: int  # parent entity ID
    __slots__ = [
        "origin", "intensity", "normal", "shadow_offset", "viscluster",
        "type", "style", "stop_dot", "stop_dot2", "exponent", "radius",
        "constant", "linear", "quadratic",  # attenuation
        "flags", "texture_data", "parent"]
    _format = "12f3i7f3i"  # 100 bytes
    _arrays = {
        "origin": [*"xyz"], "intensity": [*"xyz"],
        "normal": [*"xyz"], "shadow_offset": [*"xyz"]}
    _classes = {
        "origin": vector.vec3, "intensity": vector.vec3, "normal": vector.vec3,
        "shadow_offset": vector.vec3, "type": source.EmitType, "flags": WorldLightFlags}


# special vertices
class VertexBlinnPhong(core.Struct):  # LUMP 75 (004B)
    """Not used in any official map"""
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    colour: colour.RGBA32  # typically white
    albedo_uv: vector.vec2
    lightmap: List[vector.vec2]
    # lightmap.uv: vector.vec2
    tangent: List[float]  # 4 x 4 matrix? list of 4 quaternions?
    __slots__ = ["position_index", "normal_index", "colour", "albedo_uv", "lightmap", "tangent"]
    _format = "2I4B20f"  # 92 bytes
    _arrays = {"colour": [*"rgba"], "albedo_uv": [*"uv"], "lightmap": {"uv": [*"uv"]}, "tangent": 16}
    _classes = {"albedo_uv": vector.vec2, "lightmap.uv": vector.vec2, "colour": colour.RGBA32}


class VertexLitBump(core.Struct):  # LUMP 73 (0049)
    """Common Worldspawn Geometry"""
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    albedo_uv: vector.vec2
    colour: colour.RGBA32  # typically white
    lightmap: List[vector.vec2]
    # lightmap.uv: vector.vec2
    # lightmap.step: vector.vec2  # always (0, 0)
    tangent: List[int]  # indices to some vectors, but which lump are they stored in?
    __slots__ = ["position_index", "normal_index", "albedo_uv", "colour", "lightmap", "tangent"]
    _format = "2I2f4B4f2i"  # 44 bytes
    _arrays = {"albedo_uv": [*"uv"], "colour": [*"rgba"],
               "lightmap": {"uv": [*"uv"], "step": [*"xy"]},
               "tangent": [*"st"]}
    _classes = {"albedo_uv": vector.vec2, "lightmap.uv": vector.vec2,
                "lightmap.step": vector.vec2, "colour": colour.RGBA32}


class VertexLitFlat(core.Struct):  # LUMP 72 (0048)
    """Uncommon Worldspawn Geometry"""
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    albedo_uv: vector.vec2  # albedo uv coords
    colour: colour.RGBA32  # typically white
    lightmap: List[vector.vec2]
    # lightmap.uv: vector.vec2  # lightmap uv coords
    # lightmap.step: vector.vec2  # lightmap offset?
    __slots__ = ["position_index", "normal_index", "albedo_uv", "colour", "lightmap"]
    _format = "2I2f4B4f"
    _arrays = {"albedo_uv": [*"uv"], "colour": [*"rgba"],
               "lightmap": {"uv": [*"uv"], "step": [*"xy"]}}
    _classes = {"albedo_uv": vector.vec2, "lightmap.uv": vector.vec2,
                "lightmap.step": vector.vec2, "colour": colour.RGBA32}


class VertexUnlit(core.Struct):  # LUMP 71 (0047)
    """Tool Brushes"""
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    albedo_uv: vector.vec2
    colour: colour.RGBA32  # typically white
    __slots__ = ["position_index", "normal_index", "albedo_uv", "colour"]
    _format = "2I2f4B"  # 20 bytes
    _arrays = {"albedo_uv": [*"uv"], "colour": [*"rgba"]}
    _classes = {"albedo_uv": vector.vec2, "colour": colour.RGBA32}


class VertexUnlitTS(core.Struct):  # LUMP 74 (004A)
    """Glass"""
    position_index: int  # index into Vertex lump
    normal_index: int  # index into VertexNormal lump
    albedo_uv: vector.vec2
    colour: colour.RGBA32  # typically white
    tangent: List[int]  # indices to some vectors, but which lump are they stored in?
    __slots__ = ["position_index", "normal_index", "albedo_uv", "colour", "tangent"]
    _format = "2I2f4B2i"  # 28 bytes
    _arrays = {"albedo_uv": [*"uv"], "colour": [*"rgba"], "tangent": [*"st"]}
    _classes = {"albedo_uv": vector.vec2, "colour": colour.RGBA32}


VertexReservedX = Union[VertexBlinnPhong, VertexLitBump, VertexLitFlat, VertexUnlit, VertexUnlitTS]  # type hint


# classes for special lumps, in alphabetical order:
class EntityPartitions(list):
    """name of each used .ent file"""
    # always starts with "01*", probably indicates the internal entity lump
    def __init__(self, iterable: List[str] = tuple()):
        super().__init__(iterable)

    def as_bytes(self) -> bytes:
        return " ".join(self).encode("ascii") + b"\0"

    @classmethod
    def from_bytes(cls, raw_lump: bytes) -> EntityPartitions:
        return cls(raw_lump.decode("ascii")[:-1].split(" "))


class StaticPropv12(core.Struct):  # sprp GAME_LUMP (LUMP 35 / 0023) [version 12]
    """appears to extend valve.left4dead.StaticPropv8"""
    origin: vector.vec3  # x, y, z
    angles: List[float]  # pitch, yaw, roll
    model_name: int  # index into GAME_LUMP.sprp.model_names
    first_leaf: int
    num_leaves: int  # NOTE: Titanfall doesn't have visleaves?
    solid_mode: StaticPropCollision
    flags: source.StaticPropFlags
    skin: int
    # NOTE: BobTheBob's definition varies here:
    # int skin; float fade_min, fade_max; Vector lighting_origin;
    cubemap: int  # index of this StaticProp's Cubemap
    fade_distance: List[float]  # min, max
    lighting_origin: vector.vec3
    forced_fade_scale: float
    cpu_level: List[int]  # min, max (-1 = any)
    gpu_level: List[int]  # min, max (-1 = any)
    diffuse_modulation: colour.RGBExponent
    disable_x360: bool
    scale: float
    collision_flags: List[int]  # add, remove
    __slots__ = [
        "origin", "angles", "model_name", "first_leaf", "num_leaves",
        "solid_mode", "flags", "skin", "cubemap", "fade_distance",
        "lighting_origin", "forced_fade_scale", "cpu_level", "gpu_level",
        "diffuse_modulation", "disable_x360", "scale", "collision_flags"]
    _format = "6f3H2B2h6f4b4Bif2I"
    _arrays = {
        "origin": [*"xyz"], "angles": [*"yzx"],
        "fade_distance": ["min", "max"], "lighting_origin": [*"xyz"],
        "cpu_level": ["min", "max"], "gpu_level": ["min", "max"],
        "diffuse_modulation": [*"rgba"], "collision_flags": ["add", "remove"]}
    _classes = {
        "origin": vector.vec3, "solid_mode": StaticPropCollision, "flags": source.StaticPropFlags,
        "lighting_origin": vector.vec3, "diffuse_modulation": colour.RGBExponent, "disable_x360": bool}
    # TODO: "angles": QAngle, "collision_flags": CollisionFlag


class GameLump_SPRPv12(sdk_2013.GameLump_SPRPv11):  # sprp GameLump (LUMP 35) [version 12]
    StaticPropClass: object = StaticPropv12
    endianness: str = "little"  # for x360
    model_names: List[str]
    leaves: List[int]
    unknown_1: int  # first_transparent_prop?
    unknown_2: int  # first_alphatest_prop?
    props: List[StaticPropv12]

    def __init__(self):
        self.model_names = list()
        self.leaves = list()
        self.unknown_1 = 0
        self.unknown_2 = 0
        self.props = list()

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> GameLump_SPRPv12:
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
        out.unknown_1 = binary.read_struct(stream, f"{endian}I")
        out.unknown_2 = binary.read_struct(stream, f"{endian}I")
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
            struct.pack(f"{endian}I", self.unknown_1),
            struct.pack(f"{endian}I", self.unknown_2),
            *[
                prop.as_bytes()
                for prop in self.props]])


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = {
    "CM_BRUSH_SIDE_PLANE_OFFSETS":     {0: shared.UnsignedShorts},
    "CM_BRUSH_SIDE_PROPERTIES":        {0: BrushSideProperty},
    "CM_PRIMITIVES":                   {0: Primitive},
    "CM_UNIQUE_CONTENTS":              {0: shared.UnsignedInts},  # source.Contents? test against vmts?
    "CSM_OBJ_REFERENCES":              {0: shared.UnsignedShorts},
    "MESH_INDICES":                    {0: shared.UnsignedShorts},
    "OBJ_REFERENCES":                  {0: shared.UnsignedShorts},
    "OCCLUSION_MESH_INDICES":          {0: shared.Shorts},
    "PORTAL_EDGES":                    {0: shared.UnsignedShorts},
    "PORTAL_EDGE_REFERENCES":          {0: shared.UnsignedShorts},
    "PORTAL_VERTEX_REFERENCES":        {0: shared.UnsignedShorts},
    "SHADOW_MESH_INDICES":             {0: shared.UnsignedShorts},
    "STATIC_PROP_LIGHT_PROBE_INDICES": {0: shared.UnsignedInts},
    "TEXTURE_DATA_STRING_TABLE":       {0: shared.UnsignedInts},
    "TRICOLL_BEVEL_STARTS":            {0: shared.UnsignedShorts},
    "TRICOLL_BEVEL_INDICES":           {0: shared.UnsignedInts},
    "TRICOLL_TRIANGLES":               {2: TricollTriangle}}

LUMP_CLASSES = {
    "CELLS":                             {0: Cell},
    "CELL_AABB_NODES":                   {0: CellAABBNode},
    "CELL_BSP_NODES":                    {0: CellBSPNode},
    "CM_BRUSHES":                        {0: Brush},
    "CM_BRUSH_SIDE_TEXTURE_VECTORS":     {0: TextureVector},
    "CM_GEO_SETS":                       {0: GeoSet},
    "CM_GEO_SET_BOUNDS":                 {0: Bounds},
    "CM_GRID_CELLS":                     {0: GridCell},
    "CM_PRIMITIVE_BOUNDS":               {0: Bounds},
    "CSM_AABB_NODES":                    {0: CSMAABBNode},
    "CUBEMAPS":                          {0: Cubemap},
    "LEAF_WATER_DATA":                   {1: source.LeafWaterData},
    "LIGHTMAP_HEADERS":                  {1: LightmapHeader},
    "LIGHTPROBES":                       {0: LightProbe},
    "LIGHTPROBE_REFERENCES":             {0: LightProbeRef},
    "LIGHTPROBE_TREE":                   {0: LightProbeTree},
    "MATERIAL_SORTS":                    {0: MaterialSort},
    "MESHES":                            {0: Mesh},
    "MESH_BOUNDS":                       {0: MeshBounds},
    "MODELS":                            {0: Model},
    "OBJ_REFERENCE_BOUNDS":              {0: ObjRefBounds},
    "OCCLUSION_MESH_VERTICES":           {0: quake.Vertex},
    "PLANES":                            {1: quake3.Plane},
    "PORTALS":                           {0: Portal},
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
    "TRICOLL_NODES":                     {1: Bounds},
    "VERTEX_BLINN_PHONG":                {0: VertexBlinnPhong},
    "VERTEX_LIT_BUMP":                   {1: VertexLitBump},
    "VERTEX_LIT_FLAT":                   {1: VertexLitFlat},
    "VERTEX_NORMALS":                    {0: quake.Vertex},
    "VERTEX_UNLIT":                      {0: VertexUnlit},
    "VERTEX_UNLIT_TS":                   {0: VertexUnlitTS},
    "VERTICES":                          {0: quake.Vertex},
    "WORLD_LIGHTS":                      {1: WorldLight}}

SPECIAL_LUMP_CLASSES = {
    "CM_GRID":                   {0: Grid},
    "ENTITY_PARTITIONS":         {0: EntityPartitions},
    "ENTITIES":                  {0: shared.Entities},
    # NOTE: .ent files are handled directly by the RespawnBsp class
    "LEVEL_INFO":                {0: LevelInfo},
    "PAKFILE":                   {0: archives.pkware.Zip},
    # "PHYSICS_COLLIDE":           {0: vphysics.CollideLump},  # BROKEN .as_bytes()
    "TEXTURE_DATA_STRING_DATA":  {0: source.TextureDataStringData}}
# TODO: LightProbeParentInfos/BspNodes & RefIds may all be Special

GAME_LUMP_HEADER = source.GameLumpHeader

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = {
    "sprp": {
        12: GameLump_SPRPv12}}


# methods for interfacing with lumps from this branch:
def lit_vertex(bsp, vertex: Union[VertexLitBump, VertexLitFlat]) -> geometry.Vertex:
    position = bsp.VERTICES[vertex.position_index]
    normal = bsp.VERTEX_NORMALS[vertex.normal_index]
    # uv2 = vertex.lightmap.step  # always (0, 0)
    return geometry.Vertex(position, normal, vertex.albedo_uv, vertex.lightmap.uv, colour=vertex.colour.as_floats())


def unlit_vertex(bsp, vertex: Union[VertexUnlit, VertexUnlitTS]) -> geometry.Vertex:
    position = bsp.VERTICES[vertex.position_index]
    normal = bsp.VERTEX_NORMALS[vertex.normal_index]
    return geometry.Vertex(position, normal, vertex.albedo_uv, colour=vertex.colour.as_floats())


def mesh(bsp, mesh_index: int) -> geometry.Mesh:
    mesh = bsp.MESHES[mesh_index]
    # material
    material_sort = bsp.MATERIAL_SORTS[mesh.material_sort]
    texture_data = bsp.TEXTURE_DATA[material_sort.texture_data]
    material = geometry.Material(bsp.TEXTURE_DATA_STRING_DATA[texture_data.name_index])
    # indices
    start, length = mesh.first_mesh_index, mesh.num_triangles * 3
    indices = [material_sort.vertex_offset + i for i in bsp.MESH_INDICES[start:start + length]]
    # vertices
    vertex_lump = (mesh.flags & MeshFlags.MASK_VERTEX).name
    converter = bsp.lit_vertex if vertex_lump.split("_")[1] == "LIT" else bsp.unlit_vertex
    VERTEX_LUMP = getattr(bsp, vertex_lump)
    vertices = [converter(VERTEX_LUMP[i]) for i in indices]
    return geometry.Mesh(material, geometry.triangle_soup(vertices))


def model(bsp, model_index: int) -> geometry.Model:
    # entity
    # NOTE: not all brush entities are in the ENTITIES block
    entities = [e for es in bsp.search_all_entities(model=f"*{model_index}").values() for e in es]
    model_entity = entities[0] if len(entities) != 0 else dict()
    origin = model_entity.get("origin", "0 0 0")
    origin = vector.vec3(*origin.split())
    pitch, yaw, roll = model_entity.get("angles", "0 0 0").split()
    angles = vector.vec3(roll, pitch, yaw)
    # geometry
    model = bsp.MODELS[model_index]
    start, length = model.first_mesh, model.num_meshes
    out = geometry.Model([bsp.mesh(i) for i in range(start, start + length)], origin, angles)
    out.entity = model_entity
    return out


def tricoll_model(bsp, tricoll_header_index: int) -> geometry.Model:
    header = bsp.TRICOLL_HEADERS[tricoll_header_index]
    if header.scale != 0.0:
        origin = -header.origin / header.scale  # seems most accurate for observed misc_models
    else:
        origin = header.origin
    # NOTE: afaik angles cannot be recovered, good luck identifying misc_models
    # material
    texture_data = bsp.TEXTURE_DATA[header.texture_data]
    material = geometry.Material(bsp.TEXTURE_DATA_STRING_DATA[texture_data.name_index])
    # geometry
    triangles = list()
    no_normal = vector.vec3(0, 0, 0)
    start, length = header.first_triangle, header.num_triangles
    for tri in bsp.TRICOLL_TRIANGLES[start:start + length]:
        triangles.append([
            geometry.Vertex(bsp.VERTICES[header.first_vertex + i] - origin, no_normal)
            for i in (tri.A, tri.A + tri.B, tri.A + tri.C)])
    mesh = geometry.Mesh(material, [*map(geometry.Polygon, triangles)])
    return geometry.Model([mesh], origin)


def search_all_entities(bsp, **search: Dict[str, str]) -> Dict[str, List[Dict[str, str]]]:
    """search_all_entities(key="value") -> {"LUMP": [{"key": "value", ...}]}"""
    out = dict()
    for LUMP_name in ("ENTITIES", *(f"ENTITIES_{s}" for s in ("env", "fx", "script", "snd", "spawn"))):
        entity_lump = getattr(bsp, LUMP_name, shared.Entities(b""))
        results = entity_lump.search(**search)
        if len(results) != 0:
            out[LUMP_name] = results
    return out


def shadow_mesh(bsp, shadow_mesh_index: int) -> geometry.Mesh:
    no_normal = vector.vec3(0, 0, 0)
    shadow_mesh = bsp.SHADOW_MESHES[shadow_mesh_index]
    # material
    if shadow_mesh.material_sort == -1:
        material = geometry.Material("shadow")  # placeholder, might have a special material in-engine
    else:
        material_sort = bsp.MATERIAL_SORTS[shadow_mesh.material_sort]
        texture_data = bsp.TEXTURE_DATA[material_sort.texture_data]
        material = geometry.Material(bsp.TEXTURE_DATA_STRING_DATA[texture_data.name_index])
    # indices
    start = sum(sm.num_triangles * 3 for sm in bsp.SHADOW_MESHES[:shadow_mesh_index])
    length = shadow_mesh.num_triangles * 3
    indices = [shadow_mesh.vertex_offset + i for i in bsp.SHADOW_MESH_INDICES[start:start + length]]
    # vertices
    # TODO: convert each vertex once, then index
    if shadow_mesh.is_opaque:
        vertices = [geometry.Vertex(bsp.SHADOW_MESH_OPAQUE_VERTICES[i], no_normal) for i in indices]
    else:
        vertices = [bsp.SHADOW_MESH_ALPHA_VERTICES[i] for i in indices]
        vertices = [geometry.Vertex(v.position, no_normal, v.uv) for v in vertices]
    return geometry.Mesh(material, geometry.triangle_soup(vertices))


def occlusion_mesh(bsp) -> geometry.Mesh:
    material = geometry.Material("tools/toolsoccluder")
    indices = bsp.OCCLUSION_MESH_INDICES
    no_normal = vector.vec3(0, 0, 0)
    vertices = [geometry.Vertex(v, no_normal) for v in bsp.OCCLUSION_MESH_VERTICES]
    return geometry.Mesh(material, geometry.triangle_soup([vertices[i] for i in indices]))


def portals_as_prt(bsp) -> str:
    out = [
        "PRT1",
        f"{len(bsp.CELLS)}",  # TODO: skip unindexed cells?
        f"{len([p for p in bsp.PORTALS if p.type == PortalType.CELL])}"]
    for i, cell in enumerate(bsp.CELLS):
        start, length = cell.first_portal, cell.num_portals
        for portal in bsp.PORTALS[start:start + length]:
            if portal.type != PortalType.CELL:
                continue  # ignore SKYBOX & WATER portals
            start, length = portal.first_reference, portal.num_edges
            start = portal.first_reference
            end = start + portal.num_edges
            polygon = [
                bsp.PORTAL_VERTICES[i]
                for i in bsp.PORTAL_VERTEX_REFERENCES[start:end]]
            out.append(" ".join([
                f"{len(polygon)} {i} {portal.cell}",
                *[
                    f"({vertex.x} {vertex.y} {vertex.z})"
                    for vertex in polygon]]))
    return "\n".join(out)


def portal_mesh(bsp, portal_index: int) -> geometry.Mesh:
    # NOTE: Portal -> PortalVertexRef -> PortalVertex
    # -- ignoring PortalEdge for now
    material = geometry.Material("portal")
    portal = bsp.PORTALS[portal_index]
    normal = bsp.PLANES[portal.plane].normal
    start = portal.first_reference
    end = start + portal.num_edges
    vertices = [
        bsp.PORTAL_VERTICES[i]
        for i in bsp.PORTAL_VERTEX_REFERENCES[start:end]]
    vertices = [
        geometry.Vertex(position, normal)
        for position in vertices]
    polygon = geometry.Polygon(vertices)
    return geometry.Mesh(material, polygons=[polygon])


def brush(bsp, brush_index: int) -> editor.Brush:
    brush = bsp.CM_BRUSHES[brush_index]
    aabb = physics.AABB.from_origin_extents(brush.origin, brush.extents)
    planes = physics.Brush.from_bounds(aabb).axial_planes  # +XYZ -XYZ
    planes = [planes[0], planes[3], planes[1], planes[4], planes[2], planes[5]]  # +X -X +Y -Y +Z -Z
    for i in range(brush.num_plane_offsets):
        offset = brush.brush_side_offset + i
        brush_plane_offset = offset - bsp.CM_BRUSH_SIDE_PLANE_OFFSETS[offset]
        normal, distance = bsp.PLANES[bsp.CM_GRID.first_brush_plane + brush_plane_offset]
        planes.append(physics.Plane(normal, distance))
    start = 6 * brush.index + brush.brush_side_offset
    length = 6 + brush.num_plane_offsets
    properties = bsp.CM_BRUSH_SIDE_PROPERTIES[start:start + length]
    shaders = [bsp.TEXTURE_DATA_STRING_DATA[bsp.TEXTURE_DATA[p.texture_data].name_index] for p in properties]
    texture_vectors = [
        texture.TextureVector(texture.ProjectionAxis(*tv.s), texture.ProjectionAxis(*tv.t))
        for tv in bsp.CM_BRUSH_SIDE_TEXTURE_VECTORS[start:start + length]]
    brush_sides = list()
    for plane, shader, texture_vector, property_ in zip(planes, shaders, texture_vectors, properties):
        brush_sides.append(editor.BrushSide(plane, shader, texture_vector))
        brush_sides[-1].flags = property_.flags
    return editor.Brush(brush_sides)


def grid_cell_bounds(bsp, grid_cell_index: int) -> physics.AABB:
    grid = bsp.CM_GRID
    num_worldspawn_grid_cells = grid.count.x * grid.count.y
    assert 0 <= grid_cell_index < num_worldspawn_grid_cells
    x = grid_cell_index % grid.count.x
    y = grid_cell_index // grid.count.x
    mins = vector.vec3(
        (x + grid.offset.x) * grid.scale,
        (y + grid.offset.y) * grid.scale)
    mins.z = -32768
    maxs = mins + vector.vec3(grid.scale, grid.scale)
    maxs.z = +32768
    return physics.AABB.from_mins_maxs(mins, maxs)


def geo_set_primitives(bsp, geo_set_index: int) -> List[Tuple[Primitive, Bounds]]:
    out = list()
    geo_set = bsp.CM_GEO_SETS[geo_set_index]
    if geo_set.num_primitives == 1:
        primitive = Primitive.from_int(geo_set.primitive.as_int())
        bounds = bsp.CM_GEO_SET_BOUNDS[geo_set_index]
        out = [(primitive, bounds)]
    else:
        start = geo_set.primitive.index
        end = start + geo_set.num_primitives
        for i in range(start, end):
            primitive = bsp.CM_PRIMITIVES[i]
            bounds = bsp.CM_PRIMITIVE_BOUNDS[i]
            out.append((primitive, bounds))
    return out


def grid_cell_primitives(bsp, grid_cell_index: int) -> List[Tuple[Primitive, Bounds]]:
    out = list()
    grid_cell = bsp.CM_GRID_CELLS[grid_cell_index]
    start = grid_cell.first_geo_set
    end = start + grid_cell.num_geo_sets
    for i in range(start, end):
        out.extend(bsp.geo_set_primitives(i))
    return out


methods = [shared.worldspawn_volume, search_all_entities,  # entities
           lit_vertex, mesh, model, tricoll_model, unlit_vertex,  # geo
           shadow_mesh, occlusion_mesh,  # other geo
           brush,  # brushes
           geo_set_primitives, grid_cell_bounds, grid_cell_primitives,  # physics
           portals_as_prt, portal_mesh]  # vis
methods = {method.__name__: method for method in methods}
