# https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Vindictus
"""Vindictus. A MMO-RPG built in the Source Engine. Also known as Mabinogi Heroes"""
from __future__ import annotations
import enum
# import io
from typing import List

from ... import core
# from ... import lumps
from ...utils import vector
# from ...utils.binary import read_struct
from ..valve import source
from . import vindictus69


FILE_MAGIC = b"VBSP"

BSP_VERSION = 20

GAME_PATHS = {"Vindictus": "Vindictus/en-US"}
# NOTE: AU version & US version merged in 2012

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    ENTITIES = 0
    PLANES = 1
    TEXTURE_DATA = 2
    VERTICES = 3
    VISIBILITY = 4
    NODES = 5
    TEXTURE_INFO = 6
    FACES = 7
    LIGHTING = 8
    OCCLUSION = 9
    LEAVES = 10
    FACEIDS = 11
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
    DISPLACEMENT_LIGHTMAP_ALPHAS = 32
    DISPLACEMENT_VERTICES = 33
    DISPLACEMENT_LIGHTMAP_SAMPLE_POSITIONS = 34
    GAME_LUMP = 35
    LEAF_WATER_DATA = 36
    PRIMITIVES = 37
    PRIMITIVE_VERTICES = 38
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
    PHYSICS_COLLIDE_SURFACE = 49
    WATER_OVERLAYS = 50
    LEAF_AMBIENT_INDEX_HDR = 51
    LEAF_AMBIENT_INDEX = 52
    LIGHTING_HDR = 53
    WORLD_LIGHTS_HDR = 54
    LEAF_AMBIENT_LIGHTING_HDR = 55
    LEAF_AMBIENT_LIGHTING = 56
    XZIP_PAKFILE = 57
    FACES_HDR = 58
    MAP_FLAGS = 59
    OVERLAY_FADES = 60
    UNUSED_61 = 61
    UNUSED_62 = 62
    UNUSED_63 = 63


LumpHeader = source.LumpHeader


# classes for special lumps, in alphabetical order:
class GameLump_SPRPv6(vindictus69.GameLump_SPRPv6):  # sprp GameLump (LUMP 35) [version 6]
    StaticPropClass = source.StaticPropv6


class StaticPropv7(core.Struct):
    origin: vector.vec3
    angles: List[float]  # pitch, yaw, roll; QAngle; 0, 0, 0 = Facing East (X+)
    model_name: int  # index into GAME_LUMP.sprp.model_names
    first_leaf: int  # index into Leaf lump
    num_leafs: int  # number of Leafs after first_leaf this StaticProp is in
    solid_mode: source.StaticPropCollision
    flags: source.StaticPropFlags
    skin: int  # index of this StaticProp's skin in the .mdl
    fade_distance: List[float]  # min & max distances to fade out
    unknown: bytes  # seems to build on previous entry's unknown; could be indices
    forced_fade_scale: float  # relative to pixels used to render on-screen?
    dx_level: List[int]  # unsure; might be unused
    __slots__ = ["origin", "angles", "name_index", "first_leaf", "num_leafs",
                 "solid_mode", "flags", "skin", "fade_distance", "unknown",
                 "forced_fade_scale", "dx_level"]
    _format = "6f3H2Bi2f12sf2H"
    _arrays = {"origin": [*"xyz"], "angles": [*"yzx"], "fade_distance": ["min", "max"],
               "dx_level": ["min", "max"]}
    _classes = {"origin": vector.vec3, "solid_mode": source.StaticPropCollision,
                "flags": source.StaticPropFlags}
    # TODO: angles QAngle


class GameLump_SPRPv7(GameLump_SPRPv6):  # sprp GameLump (LUMP 35) [version 7]
    StaticPropClass = StaticPropv7


class StaticPropv8(core.Struct):
    """New in March 2025"""
    origin: vector.vec3
    angles: List[float]  # pitch, yaw, roll; QAngle; 0, 0, 0 = Facing East (X+)
    model_name: int  # index into GAME_LUMP.sprp.model_names
    first_leaf: int  # index into Leaf lump
    num_leafs: int  # number of Leafs after first_leaf this StaticProp is in
    solid_mode: source.StaticPropCollision
    flags: source.StaticPropFlags
    skin: int  # index of this StaticProp's skin in the .mdl
    fade_distance: List[float]  # min & max distances to fade out
    unknown_1: bytes  # seems to build on previous entry's unknown; could be indices
    forced_fade_scale: float  # relative to pixels used to render on-screen?
    dx_level: List[int]  # unsure; might be unused
    unknown_2: bytes  # 8 bytes; could be some kind of flag
    __slots__ = [
        "origin", "angles", "name_index", "first_leaf", "num_leafs",
        "solid_mode", "flags", "skin", "fade_distance", "unknown_1",
        "forced_fade_scale", "dx_level", "unknown_2"]
    _format = "6f3H2Bi2f12sf2H8s"
    _arrays = {
        "origin": [*"xyz"], "angles": [*"yzx"],
        "fade_distance": ["min", "max"],
        "dx_level": ["min", "max"]}
    _classes = {
        "origin": vector.vec3, "solid_mode": source.StaticPropCollision,
        "flags": source.StaticPropFlags}
    # TODO: angles QAngle


class GameLump_SPRPv8(GameLump_SPRPv7):  # sprp GameLump (LUMP 35) [version 8]
    """New in March 2025"""
    StaticPropClass = StaticPropv8


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = vindictus69.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = vindictus69.LUMP_CLASSES.copy()

SPECIAL_LUMP_CLASSES = vindictus69.SPECIAL_LUMP_CLASSES.copy()

GAME_LUMP_HEADER = vindictus69.GameLumpHeader

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = {
    "sprp": {
        6: GameLump_SPRPv6,
        7: GameLump_SPRPv7,
        8: GameLump_SPRPv8}}


methods = vindictus69.methods.copy()
