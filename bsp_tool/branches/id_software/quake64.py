"""QuakeCon 2021 PC Re-release of Midway's Nintendo 64 port of Quake"""
# Installation: Steam > Quake (Re-release) > Addons > Quake 64
# https://github.com/sezero/quakespasm/blame/master/Quake/bspfile.h
import enum
from typing import List

from ... import core
from ...utils import vector
from . import quake


FILE_MAGIC = b" 46Q"

BSP_VERSION = None

GAME_PATHS = {
    "Quake 64": "C://Users/%USERPROFILE%/Saved Games/Nightdive Studios/q64"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    ENTITIES = 0
    PLANES = 1
    MIP_TEXTURES = 2
    VERTICES = 3
    VISIBILITY = 4
    NODES = 5
    TEXTURE_INFO = 6
    FACES = 7
    LIGHTING = 8  # 8bpp 0x00-0xFF black-white
    CLIP_NODES = 9
    LEAVES = 10
    LEAF_FACES = 11
    EDGES = 12
    SURFEDGES = 13
    MODELS = 14


class LumpHeader(core.MappedArray):
    _mapping = ["offset", "length"]
    _format = "2I"


# special lump classes, in alphabetical order:
class MipTexture(core.Struct):  # LUMP 2
    name: str  # texture name
    size: vector.vec2  # width & height
    shift: int  # ?
    offsets: List[int]  # offset from entry start to texture
    __slots__ = ["name", "size", "shift", "offsets"]
    _format = "16s7I"
    _arrays = {
        "size": [*"xy"],
        "offsets": ["full", "half", "quarter", "eighth"]}
    _classes = {"size": vector.vec2}


class MipTextureLump(quake.MipTextureLump):  # LUMP 2
    MipTextureClass = MipTexture


# {"LUMP": LumpClass}
BASIC_LUMP_CLASSES = quake.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = quake.LUMP_CLASSES.copy()

SPECIAL_LUMP_CLASSES = quake.SPECIAL_LUMP_CLASSES.copy()
SPECIAL_LUMP_CLASSES.update({
    "MIP_TEXTURES": MipTextureLump})


methods = quake.methods.copy()
