from __future__ import annotations

from .. import shared
from ..valve import source
from ..valve import orange_box_x360
from . import titanfall


FILE_MAGIC = b"PSBr"

BSP_VERSION = 29

GAME_PATHS = {"Titanfall": "Titanfall/r1"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = titanfall.LUMP


LumpHeader = orange_box_x360.LumpHeader


# classes for lumps, in alphabetical order:
# NOTE: only one 28 byte entry per file
class Grid(titanfall.Grid):  # LUMP 85 (0055)
    _format = ">f6i"


# NOTE: only one 28 byte entry per file
class LevelInfo(titanfall.LevelInfo):  # LUMP 123 (007B)
    _format = ">4I3f"


# classes for special lumps, in alphabetical order:
# sprp GameLump (LUMP 35) [version 12]
class StaticPropv12(titanfall.StaticPropv12):
    _format = ">6f3H2B2h6f4b4Bif2I"


class GameLump_SPRPv12(titanfall.GameLump_SPRPv12):
    StaticPropClass = StaticPropv12
    endianness = "big"


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = dict()

LUMP_CLASSES = dict()

SPECIAL_LUMP_CLASSES = {
    "ENTITIES":                 {0: shared.Entities},
    "ENTITY_PARTITIONS":        {0: titanfall.EntityPartitions},
    "CM_GRID":                  {0: Grid},
    "LEVEL_INFO":               {0: LevelInfo},
    "TEXTURE_DATA_STRING_DATA": {0: source.TextureDataStringData}}
# TODO: orange_box_x360.PakFile
# TODO: orange_box_x360.PhysicsCollide

GAME_LUMP_HEADER = orange_box_x360.GameLumpHeader

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = {
    "sprp": {
        12: GameLump_SPRPv12}}


methods = titanfall.methods.copy()
