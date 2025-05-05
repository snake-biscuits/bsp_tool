import enum
from typing import List

from ... import core
from ...utils import vector
from .. import colour
from ..valve import orange_box
from ..valve import sdk_2013
from ..valve import source


FILE_MAGIC = b"VBSP"

BSP_VERSION = 20

GAME_PATHS = {
    "Fairy Tale Busters": "Merubasu/shadowland"}
# NOTE: supported by Jabroni Brawl 3

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
    PHYSICS_LEVEL = 62  # used by orange_box_x360 for L4D2 maps
    UNUSED_63 = 63


LumpHeader = source.LumpHeader

# a rough map of the relationships between lumps:

#                     /-> SurfEdge -> Edge -> Vertex
# Leaf -> Node -> Face -> Plane
#                     \-> DisplacementInfo -> DisplacementVertex

# ClipPortalVertices are AreaPortal geometry [citation neeeded]


# classes for special lumps, in alphabetical order:
class StaticPropv11(core.Struct):  # sprp GAME LUMP (LUMP 35) [version 11]
    """https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/gamebspfile.h#L186"""
    # older spec than sdk_2013's? might need to rethink the sdk_2013 script
    origin: List[float]  # origin.xyz
    angles: List[float]  # origin.yzx  QAngle; Z0 = East
    model_name: int  # index into GAME_LUMP.sprp.model_names
    first_leaf: int  # index into GAME_LUMP.sprp.leaves -> Leaf lump
    num_leafs: int  # number of Leaves after first_leaf this StaticProp is in
    # incorrect:
    solid_mode: int  # collision flags enum
    flags: int  # other flags
    skin: int  # index of this StaticProp's skin in the .mdl
    fade_distance: List[float]  # min & max distances to fade out
    lighting_origin: List[float]  # xyz position to sample lighting from
    forced_fade_scale: float  # relative to pixels used to render on-screen?
    cpu_level: List[int]  # min, max (-1 = any)
    gpu_level: List[int]  # min, max (-1 = any)
    diffuse_modulation: List[int]  # RGBA 32-bit colour
    flags_2: int  # values unknown
    # correct:
    scale: float
    __slots__ = [
        "origin", "angles", "name_index", "first_leaf", "num_leafs",
        "solid_mode", "flags", "skin", "fade_distance", "lighting_origin",
        "forced_fade_scale", "cpu_level", "gpu_level", "diffuse_modulation",
        "flags_2", "scale"]
    _format = "6f3H2Bi6f8BIf"
    _arrays = {
        "origin": [*"xyz"], "angles": [*"yzx"],
        "fade_distance": ["min", "max"],
        "lighting_origin": [*"xyz"],
        "cpu_level": ["min", "max"], "gpu_level": ["min", "max"],
        "diffuse_modulation": [*"rgba"]}
    _classes = {
        "origin": vector.vec3, "solid_mode": source.StaticPropCollision,
        "flags": source.StaticPropFlags, "lighting_origin": vector.vec3,
        "diffuse_modulation": colour.RGBExponent}
    # TODO: "angles": QAngle


class GameLump_SPRPv11(sdk_2013.GameLump_SPRPv11):  # sprp GAME LUMP (LUMP 35) [version 11]
    StaticPropClass = StaticPropv11


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = orange_box.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = orange_box.LUMP_CLASSES.copy()

SPECIAL_LUMP_CLASSES = orange_box.SPECIAL_LUMP_CLASSES.copy()

GAME_LUMP_HEADER = orange_box.GAME_LUMP_HEADER

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = {
    "sprp": {
        7: GameLump_SPRPv11}}


methods = orange_box.methods.copy()
