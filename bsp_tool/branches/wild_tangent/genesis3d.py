# https://github.com/RealityFactory/Genesis3D/blob/master/World/Gbspfile.h
import enum
from typing import List

from .. import base
from .. import time
from .. import vector
from ..id_software import quake


FILE_MAGIC = b"GBSP"

BSP_VERSION = 15

GAME_PATHS = {"Amsterdoom": "Amsterdoom"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


# NOTE: id-based "CHUNKS"; file header is a chunk
class LUMP(enum.Enum):
    HEADER = 0
    MODELS = 1
    NODES = 2
    BNODES = 3
    LEAVES = 4
    CLUSTERS = 5
    AREAS = 6
    AREA_PORTALS = 7
    LEAF_SIDES = 8
    PORTALS = 9
    PLANES = 10
    FACES = 11
    LEAF_FACES = 12
    INDICES = 13
    VERTICES = 14
    RGB_VERTICES = 15
    ENTITIES = 16
    TEXTURE_INFO = 17
    TEXTURES = 18
    TEXTURE_DATA = 19
    LIGHTING = 20
    VISIBILITY = 21
    SKY = 22
    PALETTES = 23
    MOTIONS = 24
    END = 0xFFFF


class LumpHeader(base.MappedArray):
    id: int
    size: int  # sizeof(LumpClass)
    count: int  # num_elements
    # derived by Genesis3DBsp._preload
    offset: int  # "chunk" headers & data appear inline
    length: int  # size * count
    _mapping = ["id", "size", "count"]
    _format = "3I"


# TODO: a rough map of the relationships between lumps:


# classes for lumps, in alphabetical order:
class Header(base.Struct):  # LUMP 0
    magic: bytes
    padding: bytes  # 4 NULL bytes
    version: int
    timestamp: List[int]
    __slots__ = ["magic", "padding", "version", "time"]
    _format = "4s4sI8H"
    _arrays = {"time": ["year", "month", "day_of_week", "day",
                        "hour", "minute", "second", "millisecond"]}
    _classes = {"time": time.SystemTime}


class Sky(base.Struct):  # LUMP 22
    axis: vector.vec3  # axis of rotation
    degrees_per_minute: float
    textures: List[int]  # indices into Textures
    draw_scale: float
    __slots__ = ["axis", "degrees_per_minute", "textures", "draw_scale"]
    _format = "4f6If"
    _arrays = {"axis": [*"xyz"], "textures": 6}
    _classes = {"axis": vector.vec3}


# {"LUMP_NAME": LumpClass}
BASIC_LUMP_CLASSES = dict()

LUMP_CLASSES = {"PLANES": quake.Plane,
                "SKY": Sky}

SPECIAL_LUMP_CLASSES = {"HEADER": Header}


methods = dict()
