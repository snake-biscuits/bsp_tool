from __future__ import annotations
import enum
import io
import struct
from typing import List, Tuple

from ... import core
from ... import lumps
from ...utils import binary
from ...utils import vector
from .. import colour
from ..valve import source
from . import titanfall


FILE_MAGIC = b"rBSP"

BSP_VERSION = 37

GAME_PATHS = {
    "Titanfall 2 Tech Test": "Titanfall2_tech_test",
    "Titanfall 2": "Titanfall2"}

GAME_VERSIONS = {
    "Titanfall 2 Tech Test": 36,
    "Titanfall 2": 37}


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
    TRICOLL_TRIANGLES = 0x0042
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
    LIGHTMAP_DATA_RTL_PAGES = 0x007A
    LEVEL_INFO = 0x007B
    SHADOW_MESH_OPAQUE_VERTICES = 0x007C
    SHADOW_MESH_ALPHA_VERTICES = 0x007D
    SHADOW_MESH_INDICES = 0x007E
    SHADOW_MESHES = 0x007F


LumpHeader = source.LumpHeader


# known lump changes from Titanfall -> Titanfall 2:
# new:
# UNUSED_4 -> LIGHTPROBE_PARENT_INFOS
# UNUSED_5 -> SHADOW_ENVIRONMENTS
# UNUSED_6 -> LIGHTPROBE_BSP_NODES
# UNUSED_7 -> LIGHTPROBE_BSP_REF_IDS
# UNUSED_55 -> WORLD_LIGHT_PARENT_INFOS
# UNUSED_122 -> LIGHTMAP_DATA_RTL_PAGES
# deprecated:
# LEAF_WATER_DATA
# PHYSICS_LEVEL
# PHYSICS_TRIANGLES

# Rough map of the relationships between lumps:
#              /-> MaterialSort -> TextureData -> TextureDataStringTable -> TextureDataStringData
# Model -> Mesh -> MeshIndex -\-> VertexReservedX -> Vertex
#             \--> .flags (VertexReservedX)     \--> VertexNormal
#              \-> VertexReservedX               \-> .uv
# MeshBounds & Mesh are parallel
# NOTE: parallel means each entry is paired with an entry of the same index in the parallel lump
# -- this means you can collect only the data you need, but increases the chance of storing redundant data

# ShadowEnvironment -> ShadowMesh
#                  \-> CSMAABBNodes -> CSMObjReferences
# ShadowEnvironments are indexed by entities (light_environment(_volume) w/ lightEnvironmentIndex key)

# LightmapHeader -> LIGHTMAP_DATA_SKY
#               \-> LIGHTMAP_DATA_REAL_TIME_LIGHTS

# PORTAL LUMPS
# Portal -?> PortalEdge -> PortalVertex
# PortalEdgeRef -> PortalEdge
# PortalVertRef -> PortalVertex
# PortalEdgeIntersect -> PortalEdge?
#                    \-> PortalVertex

# PortalEdgeIntersectHeader -> ???
# PortalEdgeIntersectHeader is parallel w/ PortalEdge
# NOTE: titanfall 2 only seems to care about PortalEdgeIntersectHeader & ignores all other lumps
# -- though this is a code branch that seems to be triggered by something about r1 maps, maybe a flags lump?
# NOTE: there are also always as many vert refs as edge refs
# PortalEdgeRef is parallel w/ PortalVertRef (both 2 bytes per entry, so not 2 verts per edge?)

# ??? WorldLight <-?-> WorldLightParentInfo -?> Model / Entity?

# CM_* LUMPS
# GM_GRID holds world bounds & other metadata

# Grid -> GridCell -> GeoSet -> Primitive

#          /-> UniqueContents
# Primitive -> .primitive.type / .type -> Brush OR Tricoll OR StaticProp

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

# LIGHTPROBES
# LightProbeTree -?> LightProbeRef -> LightProbe
# -?> STATIC_PROP_LIGHTPROBE_INDICES
# -?> LightProbeBSPNodes -> ???
#                   \-> LightProbeBspNodes
# -?> LightProbeBSPRefIds -?>
# -?> LightProbeParentInfos -?>


# engine limits:
class MAX(enum.Enum):
    ENTITY_PARTITIONS = 16  # 32 chars per partition name
    MODELS = 1024
    STATIC_PROPS = 57343
    TEXTURES = 2048
    WORLD_LIGHTS = 16352


# flags enums
class PrimitiveType(enum.IntFlag):
    """Identified by Fifty"""
    BRUSH = 0x00
    TRICOLL = 0x40
    PROP = 0x60  # identified by RoyalBlue


# classes for lumps, in alphabetical order::
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


class LightmapPage(core.Struct):  # LUMP 122 (007A)
    """identified by RoyalBlue"""
    indices: List[int]  # indices into WorldLights
    __slots__ = ["indices"]
    _format = "63h"
    _arrays = {"indices": 63}


class LightProbeBSPNode(core.Struct):  # LUMP 6 (0006)
    plane: Tuple[vector.vec3, float]
    # plane.normal: vector.vec3
    # plane.distance: float
    children: List[int]  # +ve: LightProbeBspNode; -ve? some bitfield?
    __slots__ = ["plane", "child"]
    _format = "4f2I"
    _arrays = {
        "plane": {"normal": [*"xyz"], "distance": None},
        "child": ["front", "back"]}
    _classes = {"plane.normal": vector.vec3}


class LightProbeParentInfo(core.Struct):  # LUMP 4 (0004)
    """Identified by RoyalBlue; auto-generated if absent"""
    index: int  # index of self or -1
    first_probe: int  # index into LightProbes
    num_probes: int
    first_reference: int  # index into LightProbeRefs
    num_references: int
    # NOTE: LightProbeTree lump mixes nodes and leaves
    first_tree: int  # index into LightProbeTree
    num_trees: int
    __slots__ = [
        "index", "first_probe", "num_probes",
        "first_reference", "num_references",
        "first_tree", "num_trees"]
    _format = "i6I"


class LightProbeRef(core.Struct):  # LUMP 104 (0068)
    origin: vector.vec3  # coords of LightProbe
    lightprobe: int  # index of this LightProbeRef's LightProbe
    unknown: int
    __slots__ = ["origin", "lightprobe", "unknown"]
    _format = "3fIi"
    _arrays = {"origin": [*"xyz"]}
    _classes = {"origin": vector.vec3}


class Mesh(core.Struct):  # LUMP 80 (0050)
    # built on valve.source.Face?
    first_mesh_index: int  # index into MeshIndices
    num_triangles: int  # number of triangles in MeshIndices after first_mesh_index
    first_vertex: int  # index to this Mesh's first VertexReservedX
    num_vertices: int  # lastVertexOffset? off by one
    vertex_type: int  # VERTEX_RESERVED_X index
    cubemap: int  # index into Cubemaps; -1 if None (Unlit / UnlitTS)
    styles: List[int]  # from source; 4 different lighting states? "switchable lighting info"
    luxel_origin: List[int]  # same as source lightmap mins & size?
    luxel_offset_max: List[int]
    material_sort: int  # index of this Mesh's MaterialSort
    flags: titanfall.MeshFlags  # (mesh.flags & MeshFlags.MASK_VERTEX).name == "VERTEX_RESERVED_X"
    __slots__ = ["first_mesh_index", "num_triangles", "first_vertex", "num_vertices",
                 "vertex_type", "cubemap", "styles", "luxel_origin", "luxel_offset_max",
                 "material_sort", "flags"]
    _format = "I3H6b2h2BHI"
    _arrays = {"styles": 4, "luxel_origin": 2, "luxel_offset_max": 2}
    _classes = {"flags": titanfall.MeshFlags}


class Primitive(core.BitField):  # LUMP 89 (0059)
    """identified by Fifty"""
    type: PrimitiveType
    index: int  # indexed lump depends on type
    unique_contents: int  # index into UniqueContents (Contents flags OR-ed together)
    _fields = {"type": 8, "index": 16, "unique_contents": 8}
    _format = "I"
    _classes = {"type": PrimitiveType}


class WorldLightv2(core.Struct):  # LUMP 54 (0036)
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
    flags: source.WorldLightFlags
    texture_data: int  # index of TextureData
    parent: int  # parent entity ID
    unknown_1: float  # default 0
    unknown_2: float  # default 0.005
    __slots__ = [
        "origin", "intensity", "normal", "shadow_offset", "viscluster",
        "type", "style", "stop_dot", "stop_dot2", "exponent", "radius",
        "constant", "linear", "quadratic",  # attenuation
        "flags", "texture_data", "parent",
        "unknown_1", "unknown_2"]
    _format = "12f3i7f3i2f"  # 108 bytes
    _arrays = {
        "origin": [*"xyz"], "intensity": [*"xyz"],
        "normal": [*"xyz"], "shadow_offset": [*"xyz"]}
    _classes = {
        "origin": vector.vec3, "intensity": vector.vec3, "normal": vector.vec3,
        "shadow_offset": vector.vec3, "type": source.EmitType,
        "flags": titanfall.WorldLightFlags}


class WorldLightv3(core.Struct):  # LUMP 54 (0036)
    origin: vector.vec3  # origin point of this light source
    intensity: vector.vec3  # brightness scalar?
    normal: vector.vec3  # light direction
    # used by EmitType.SURFACE & EmitType.SPOTLIGHT
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
    flags: source.WorldLightFlags
    texture_data: int  # index of TextureData
    parent: int  # parent entity ID
    unknown_1: float  # default 0
    unknown_2: float  # default 0.005
    unknown_3: float  # default 1.0
    __slots__ = [
        "origin", "intensity", "normal", "shadow_offset", "viscluster",
        "type", "style", "stop_dot", "stop_dot2", "exponent", "radius",
        "constant", "linear", "quadratic",  # attenuation
        "flags", "texture_data", "parent",
        "unknown_1", "unknown_2", "unknown_3"]
    _format = "12f3i7f3i3f"  # 112 bytes
    _arrays = {
        "origin": [*"xyz"], "intensity": [*"xyz"],
        "normal": [*"xyz"], "shadow_offset": [*"xyz"]}
    _classes = {
        "origin": vector.vec3, "intensity": vector.vec3, "normal": vector.vec3,
        "shadow_offset": vector.vec3, "type": source.EmitType,
        "flags": titanfall.WorldLightFlags}


class WorldLightParentInfo(core.Struct):  # LUMP 55 (0037)
    """Identified by RoyalBlue"""
    matrix: List[List[float]]  # 3x Quaternions?
    # could be read as 3 planes
    # each .xyz is a unit vector
    origin: vector.vec3
    unknown_2: vector.vec3  # angles?
    unknown_3: int
    world_light: int  # index into WorldLights
    __slots__ = [
        "matrix", "origin", "unknown_2",
        "unknown_3", "world_light"]
    _format = "18f2h"
    _arrays = {
        "matrix": {a: [*"xyzw"] for a in "ABC"},
        "origin": [*"xyz"], "unknown_2": [*"xyz"]}
    _classes = {
        "origin": vector.vec3, "unknown_2": vector.vec3}

    def __repr__(self) -> str:
        return "\n".join([
            "WorldLightParentInfo(matrix=[",
            *[
                " " * 6 + ", ".join([f"{x:+.4f}" for x in quaternion]) + ","
                for quaternion in self.matrix],
            "    ],",
            f"    origin={self.origin!r},",
            f"    unknown_2={self.unknown_2!r},",
            f"    unknown_3={self.unknown_3},",
            f"    world_light={self.world_light})"])


class ShadowEnvironment(core.Struct):  # LUMP 5 (0005)
    """Identified w/ BobTheBob; linked to dynamic shadows and optimisation"""
    first_csm_aabb_node: int  # index into CSMAABBNodes
    first_csm_obj_reference: int  # index into CSMObjReferences
    first_shadow_mesh: int  # index into ShadowMesh
    # NOTE: not num_xs!
    last_csm_aabb_node: int
    last_csm_obj_reference: int
    last_shadow_mesh: int
    sun_normal: vector.vec3  # angle of linked light_environment
    __slots__ = [
        "first_csm_aabb_node", "first_csm_obj_reference", "first_shadow_mesh",
        "last_csm_aabb_node", "last_csm_obj_reference", "last_shadow_mesh",
        "sun_normal"]
    _format = "6i3f"
    _arrays = {"sun_normal": [*"xyz"]}
    _classes = {"sun_normal": vector.vec3}


# classes for special lumps, in alphabetical order:
class StaticPropv13(core.Struct):  # sprp GAME_LUMP (LUMP 35 / 0023) [version 13]
    """Identified w/ BobTheBob"""
    origin: vector.vec3
    angles: List[float]  # pitch, yaw, roll (Y Z X)
    scale: float  # indentified by Legion dev DTZxPorter
    model_name: int  # index into GAME_LUMP.sprp.model_names
    solid_mode: titanfall.StaticPropCollision
    flags: source.StaticPropFlags
    skin: int
    cubemap: int
    forced_fade_scale: float
    lighting_origin: vector.vec3
    cpu_level: List[int]  # min, max (-1 = any)
    gpu_level: List[int]  # min, max (-1 = any)
    diffuse_modulation: colour.RGBExponent
    collision_flags: List[int]  # add, remove
    __slots__ = [
        "origin", "angles", "scale", "model_name", "solid_mode", "flags",
        "skin", "cubemap", "forced_fade_scale", "lighting_origin", "cpu_level",
        "gpu_level", "diffuse_modulation", "collision_flags"]
    _format = "7fH2B2H4f4b4B2H"  # 64 bytes
    _arrays = {
        "origin": [*"xyz"], "angles": [*"yzx"],
        "lighting_origin": [*"xyz"], "cpu_level": ["min", "max"],
        "gpu_level": ["min", "max"], "diffuse_modulation": [*"rgba"],
        "collision_flags": ["add", "remove"]}
    _classes = {
        "origin": vector.vec3, "solid_mode": titanfall.StaticPropCollision, "flags": source.StaticPropFlags,
        "lighting_origin": vector.vec3, "diffuse_modulation": colour.RGBExponent}
    # TODO: "angles": QAngle


class Unknown3(core.Struct):  # sprp GAME_LUMP (LUMP 35 / 0023)
    """all assumptions"""
    # NOTE: doesn't appear in smaller maps
    # -- could be to help with floating point precision
    unknown_1: List[float]  # SIMD aligned?
    unknown_2: List[int]
    __slots__ = ["unknown_1", "unknown_2"]
    _format = "12f4i"  # 64 bytes
    _arrays = {"unknown_1": 12, "unknown_2": 4}


class GameLump_SPRPv13(titanfall.GameLump_SPRPv12):  # sprp GameLump (LUMP 35) [version 13]
    StaticPropClass: object = StaticPropv13
    Unknown3Class: object = Unknown3
    # little endian only
    model_names: List[str]  # filenames of all .mdl / .rmdl used
    unknown_1: int  # first_transparent?
    unknown_2: int  # first_alpha_sort?
    props: List[StaticPropv13]
    unknown_3: List[Unknown3]

    def __init__(self):
        self.model_names = list()
        self.unknown_1 = 0
        self.unknown_2 = 0
        self.props = list()
        self.unknown_3 = list()

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> GameLump_SPRPv13:
        out = cls()
        endian = {"little": "<", "big": ">"}[cls.endianness]
        num_model_names = binary.read_struct(stream, f"{endian}I")
        out.model_names = [
            stream.read(128).replace(b"\0", b"").decode()
            for i in range(num_model_names)]
        num_props = binary.read_struct(stream, f"{endian}I")
        out.unknown_1 = binary.read_struct(stream, f"{endian}I")
        out.unknown_2 = binary.read_struct(stream, f"{endian}I")
        out.props = lumps.BspLump.from_count(stream, num_props, cls.StaticPropClass)
        if (num_model_names, num_props, out.unknown_1, out.unknown_2) == (0,) * 4:
            assert len(stream.read(4)) == 0  # should be end of stream
            return out
        num_unknown_3 = binary.read_struct(stream, f"{endian}I")
        out.unknown_3 = lumps.BspLump.from_count(stream, num_unknown_3, cls.Unknown3Class)
        tail = stream.read()
        if len(tail) > 0:
            raise RuntimeError(f"sprp lump has a tail of {len(tail)} bytes")
        return out

    def as_bytes(self) -> bytes:
        assert all([
            isinstance(prop, self.StaticPropClass)
            for prop in self.props])
        assert all([
            isinstance(unknown_3, self.Unknown3Class)
            for unknown_3 in self.unknown_3])
        endian = {"little": "<", "big": ">"}[self.endianness]
        return b"".join([
            struct.pack(f"{endian}I", len(self.model_names)),
            *[
                struct.pack("128s", model_name.encode("ascii"))
                for model_name in self.model_names],
            struct.pack(f"{endian}I", len(self.props)),
            struct.pack(f"{endian}I", self.unknown_1),
            struct.pack(f"{endian}I", self.unknown_2),
            *[
                prop.as_bytes()
                for prop in self.props],
            struct.pack(f"{endian}I", len(self.unknown_3)),
            *[
                unknown_3.as_bytes()
                for unknown_3 in self.unknown_3]])


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = titanfall.BASIC_LUMP_CLASSES.copy()
BASIC_LUMP_CLASSES.update({
    "CM_PRIMITIVES": {0: Primitive}})

LUMP_CLASSES = titanfall.LUMP_CLASSES.copy()
LUMP_CLASSES.update({
    "CM_GEO_SETS":              {0: GeoSet},
    "LIGHTMAP_DATA_RTL_PAGES":  {0: LightmapPage},
    "LIGHTPROBE_BSP_NODES":     {2: LightProbeBSPNode},
    "LIGHTPROBE_PARENT_INFOS":  {0: LightProbeParentInfo},
    "LIGHTPROBE_REFERENCES":    {0: LightProbeRef},
    "MESHES":                   {0: Mesh},
    "SHADOW_ENVIRONMENTS":      {0: ShadowEnvironment},
    "WORLD_LIGHTS": {
        1: titanfall.WorldLight,
        2: WorldLightv2,
        3: WorldLightv3},
    "WORLD_LIGHT_PARENT_INFOS": {3: WorldLightParentInfo}})

SPECIAL_LUMP_CLASSES = titanfall.SPECIAL_LUMP_CLASSES.copy()

GAME_LUMP_HEADER = source.GameLumpHeader

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = {
    "sprp": {
        13: GameLump_SPRPv13}}


def geo_set_primitives(bsp, geo_set_index: int) -> List[Tuple[Primitive, titanfall.Bounds]]:
    # copied from respawn.titanfall to use correct Primitive class
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


methods = titanfall.methods.copy()
methods.update({
    "geo_set_primitives": geo_set_primitives})
