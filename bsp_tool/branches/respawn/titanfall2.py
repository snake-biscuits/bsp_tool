import enum
import io
import struct
from typing import List

from .. import base
from ..valve import source
from . import titanfall


FILE_MAGIC = b"rBSP"

BSP_VERSION = 37

GAME_PATHS = {"Titanfall 2": "Titanfall2"}

GAME_VERSIONS = {"Titanfall 2": 37}


class LUMP(enum.Enum):
    ENTITIES = 0x0000
    PLANES = 0x0001
    TEXTURE_DATA = 0x0002
    VERTICES = 0x0003
    LIGHTPROBE_PARENT_INFOS = 0x0004
    SHADOW_ENVIRONMENTS = 0x0005
    LIGHTPROBE_BSP_NODES = 0x0006
    LIGHTPROBE_BSP_REF_IDS = 0x0007  # indexes? (Mod_LoadLightProbeBSPRefIdxs)
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
    WORLD_LIGHTS = 0x0036  # versions 1 - 3 supported (0 might cause a crash, idk)
    WORLD_LIGHT_PARENT_INFOS = 0x0037
    UNUSED_56 = 0x0038
    UNUSED_57 = 0x0039
    UNUSED_58 = 0x003A
    UNUSED_59 = 0x003B
    UNUSED_60 = 0x003C
    UNUSED_61 = 0x003D
    UNUSED_62 = 0x003E
    UNUSED_63 = 0x003F
    UNUSED_64 = 0x0040
    UNUSED_65 = 0x0041
    TRICOLL_TRIS = 0x0042
    UNUSED_67 = 0x0043
    TRICOLL_NODES = 0x0044
    TRICOLL_HEADERS = 0x0045
    UNUSED_70 = 0x0046
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
    CM_BRUSH_SIDE_PROPS = 0x005E
    CM_BRUSH_TEX_VECS = 0x005F
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
    PORTAL_EDGE_INTERSECT_EDGE = 0x0072
    PORTAL_EDGE_INTERSECT_AT_VERTEX = 0x0073
    PORTAL_EDGE_INTERSECT_HEADER = 0x0074
    OCCLUSION_MESH_VERTICES = 0x0075
    OCCLUSION_MESH_INDICES = 0x0076
    CELL_AABB_NODES = 0x0077
    OBJ_REFERENCES = 0x0078
    OBJ_REFERENCE_BOUNDS = 0x0079
    LIGHTMAP_DATA_RTL_PAGE = 0x007A
    LEVEL_INFO = 0x007B
    SHADOW_MESH_OPAQUE_VERTICES = 0x007C
    SHADOW_MESH_ALPHA_VERTICES = 0x007D
    SHADOW_MESH_INDICES = 0x007E
    SHADOW_MESH_MESHES = 0x007F


# struct RespawnBspHeader { char file_magic[4]; int version, revision, lump_count; SourceLumpHeader headers[128]; };
lump_header_address = {LUMP_ID: (16 + i * 16) for i, LUMP_ID in enumerate(LUMP)}

# Known lump changes from Titanfall -> Titanfall 2:
# New:
# UNUSED_4 -> LIGHTPROBE_PARENT_INFOS
# UNUSED_5 -> SHADOW_ENVIRONMENTS
# UNUSED_6 -> LIGHTPROBE_BSP_NODES
# UNUSED_7 -> LIGHTPROBE_BSP_REF_IDS
# UNUSED_55 -> WORLD_LIGHT_PARENT_INFOS
# UNUSED_122 -> LIGHTMAP_DATA_RTL_PAGE
# Deprecated:
# LEAF_WATER_DATA
# PHYSICS_LEVEL
# PHYSICS_TRIANGLES

# Rough map of the relationships between lumps:
#              /-> MaterialSort -> TextureData -> TextureDataStringTable -> TextureDataStringData
# Model -> Mesh -> MeshIndex -\-> VertexReservedX -> Vertex
#             \--> .flags (VertexReservedX)     \--> VertexNormal
#              \-> VertexReservedX               \-> .uv

# MeshBounds & Mesh are indexed in paralell?

# ShadowEnvironment -> ShadowMesh -> ShadowMeshIndices -> ShadowMeshOpaqueVertex
#                                                    \-?> ShadowMeshAlphaVertex

# ??? -> Brush -?> Plane

# LightmapHeader -> LIGHTMAP_DATA_SKY
#               \-> LIGHTMAP_DATA_REAL_TIME_LIGHTS

# Portal -?> PortalEdge -> PortalVertex
# PortalEdgeRef -> PortalEdge
# PortalVertRef -> PortalVertex
# PortalEdgeIntersect -> PortalEdge?
#                    \-> PortalVertex

# PortalEdgeIntersectHeader -?> PortalEdgeIntersect ? (parallel indices?)
# NOTE: there are always as many intersect headers as edges
# NOTE: there are also always as many vert refs as edge refs

# ??? WorldLight <-?-> WorldLightParentInfo -?> Model


# engine limits:
class MAX(enum.Enum):
    MODELS = 1024


# classes for lumps, in alphabetical order::
class LightmapPage(base.Struct):  # LUMP 122 (007A)
    data: bytes
    _format = "128s"
    __slots__ = ["data"]


# TODO: LightProbeRef


class WorldLightv2(base.Struct):  # LUMP 54 (0036)
    __slots__ = ["unknown"]
    _format = "27I"  # 108 bytes
    _arrays = {"unknown": 27}


class WorldLightv3(base.Struct):  # LUMP 54 (0036)
    __slots__ = ["unknown"]
    _format = "28I"  # 112 bytes
    _arrays = {"unknown": 28}


class ShadowEnvironment(base.Struct):
    """Identified w/ BobTheBob; appears linked to dynamic shadows and optimisation"""
    # making modifications caused severe framerate drops (2fps)
    unknown_1: List[int]  # likely indices into other lumps
    first_shadow_mesh: int  # first ShadowMesh in this ShadowEnvironment
    unknown_2: List[int]  # likely indices into other lumps
    num_shadow_meshes: int  # number of ShadowMeshes in this ShadowEnvironment after first_shadow_mesh
    unknown_3: List[int]  # no clue
    __slots__ = ["unknown_1", "first_shadow_mesh", "unknown_2", "num_shadow_meshes", "unknown_3"]
    _format = "6i6H"
    _arrays = {"unknown_1": 2, "unknown_2": 2, "unknown_3": 6}


class StaticPropv13(base.Struct):  # sprp GAME_LUMP (0023)
    """Identified w/ BobTheBob"""
    origin: List[float]  # x, y, z
    angles: List[float]  # pitch, yaw, roll
    scale: float  # indentified by Legion dev DTZxPorter
    model_name: int  # index into GAME_LUMP.sprp.model_names
    solid_mode: int  # bitflags
    flags: int
    unknown: List[int]
    forced_fade_scale: float
    lighting_origin: List[float]  # x, y, z
    cpu_level: List[int]  # min, max (-1 = any)
    gpu_level: List[int]  # min, max (-1 = any)
    diffuse_modulation: List[int]  # RGBA 32-bit colour
    collision_flags: List[int]  # add, remove
    # NOTE: no skin or cubemap
    __slots__ = ["origin", "angles", "scale", "model_name", "solid_mode", "flags",
                 "unknown", "forced_fade_scale", "lighting_origin", "cpu_level",
                 "gpu_level", "diffuse_modulation", "collision_flags"]
    _format = "7fH2B4b4f8b2H"  # 64 bytes
    _arrays = {"origin": [*"xyz"], "angles": [*"yzx"], "unknown": 4,
               "lighting_origin": [*"xyz"], "cpu_level": ["min", "max"],
               "gpu_level": ["min", "max"], "diffuse_modulation": [*"rgba"],
               "collision_flags": ["add", "remove"]}


# classes for special lumps, in alphabetical order:
class GameLump_SPRP:
    """New in Titanfall 2"""
    _static_prop_format: str  # StaticPropClass._format
    model_names: List[str]  # filenames of all .mdl / .rmdl used
    unknown_1: int
    unknown_2: int  # indices?
    props: List[object]  # List[StaticPropClass]

    def __init__(self, raw_sprp_lump: bytes, StaticPropClass: object):
        self._static_prop_format = StaticPropClass._format
        sprp_lump = io.BytesIO(raw_sprp_lump)
        model_names_count = int.from_bytes(sprp_lump.read(4), "little")
        model_names = struct.iter_unpack("128s", sprp_lump.read(128 * model_names_count))
        setattr(self, "model_names", [t[0].replace(b"\0", b"").decode() for t in model_names])
        prop_count, unknown_1, unknown_2 = struct.unpack("3i", sprp_lump.read(12))
        self.unknown_1, self.unknown_2 = unknown_1, unknown_2
        # TODO: if StaticPropClass is None: split into appropriate groups of bytes
        read_size = struct.calcsize(StaticPropClass._format) * prop_count
        props = struct.iter_unpack(StaticPropClass._format, sprp_lump.read(read_size))
        setattr(self, "props", list(map(StaticPropClass.from_tuple, props)))
        # TODO: check if are there any leftover bytes at the end?

    def as_bytes(self) -> bytes:
        # NOTE: additions to .props must be of the correct type (StaticPropClass given to __init__)
        # -- GameLump_SPRP does not perform conversions of any kind!
        return b"".join([len(self.model_names).to_bytes(4, "little"),
                        *[struct.pack("128s", n.encode("ascii")) for n in self.model_names],
                        struct.pack("3I", len(self.props), self.unknown_1, self.unknown_2),
                        *[struct.pack(self._static_prop_format, *p.flat()) for p in self.props]])


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = titanfall.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = titanfall.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("LIGHTPROBE_REFERENCES")  # size doesn't match
LUMP_CLASSES.update({"LIGHTMAP_DATA_REAL_TIME_LIGHTS_PAGE": {0: LightmapPage},
                     "SHADOW_ENVIRONMENTS":                 {0: ShadowEnvironment},
                     "WORLD_LIGHTS":                        {1: titanfall.WorldLight,
                                                             2: WorldLightv2,
                                                             3: WorldLightv3}})

SPECIAL_LUMP_CLASSES = titanfall.SPECIAL_LUMP_CLASSES.copy()

GAME_LUMP_HEADER = source.GameLumpHeader

GAME_LUMP_CLASSES = {"sprp": {13: lambda raw_lump: GameLump_SPRP(raw_lump, StaticPropv13)}}

# branch exclusive methods, in alphabetical order:
methods = [*titanfall.methods]
