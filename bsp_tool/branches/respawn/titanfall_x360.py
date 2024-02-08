from __future__ import annotations

from .. import shared
from .. import x360
from ..valve import source
from . import titanfall


FILE_MAGIC = b"PSBr"

BSP_VERSION = 29

GAME_PATHS = {"Titanfall": "Titanfall/r1"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = titanfall.LUMP


LumpHeader = x360.make_big_endian(titanfall.LumpHeader)


# classes for lumps, in alphabetical order:
Grid_x360 = x360.make_big_endian(titanfall.Grid)
LevelInfo_x360 = x360.make_big_endian(titanfall.LevelInfo)


# classes for special lumps, in alphabetical order:
StaticPropv12_x360 = x360.make_big_endian(titanfall.StaticPropv12)


class GameLump_SPRPv12_x360(titanfall.GameLump_SPRPv12):  # sprp GameLump (LUMP 35) [version 12]
    StaticPropClass = StaticPropv12_x360
    endianness = "big"


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = titanfall.BASIC_LUMP_CLASSES.copy()
# big-endian BitField not yet supported
BASIC_LUMP_CLASSES.pop("CM_BRUSH_SIDE_PROPERTIES")
BASIC_LUMP_CLASSES.pop("CM_PRIMITIVES")
BASIC_LUMP_CLASSES.pop("TRICOLL_TRIANGLES")
BASIC_LUMP_CLASSES, LumpClasses = x360.convert_versioned(BASIC_LUMP_CLASSES)
# copy used LumpClasses to globals
for LumpClass_name, LumpClass in LumpClasses.items():
    globals()[LumpClass_name] = LumpClass


LUMP_CLASSES, LumpClasses = x360.convert_versioned(titanfall.LUMP_CLASSES)
# copy used LumpClasses to globals
for LumpClass_name, LumpClass in LumpClasses.items():
    globals()[LumpClass_name] = LumpClass
del LumpClass_name, LumpClass


SPECIAL_LUMP_CLASSES = {"ENTITIES":                 {0: shared.Entities},
                        "ENTITY_PARTITIONS":        {0: titanfall.EntityPartitions},
                        "CM_GRID":                  {0: Grid_x360},
                        "LEVEL_INFO":               {0: LevelInfo_x360},
                        "TEXTURE_DATA_STRING_DATA": {0: source.TextureDataStringData}}
# TODO: orange_box_x360.PakFile_x360
# TODO: orange_box_x360.PhysicsCollide_x360

GAME_LUMP_HEADER = x360.make_big_endian(titanfall.GAME_LUMP_HEADER)

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = {"sprp": {12: GameLump_SPRPv12_x360}}


methods = titanfall.methods.copy()
