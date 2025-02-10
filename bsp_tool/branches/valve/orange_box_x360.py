from __future__ import annotations

from .. import shared
# from . import physics
from . import orange_box
from . import source


FILE_MAGIC = b"PSBV"

BSP_VERSION = 20

GAME_PATHS = {
    "Half-Life 2": "OrangeBox/hl2",
    "Half-Life 2: Episode 1": "OrangeBox/episodic",
    "Half-Life 2: Episode 2": "OrangeBox/ep2",
    "Left 4 Dead": "Left4Dead/left4dead",
    "Left 4 Dead 2": "Left4Dead2/left4dead2",
    "Portal": "OrangeBox/portal",
    "Team Fortress 2": "OrangeBox/tf"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = orange_box.LUMP


class LumpHeader(source.LumpHeader):
    _format = ">4I"


# classes for each lump, in alphabetical order:
# TODO: Leaf (bitfields are flipped)
# TODO: DisplacementInfo
# TODO: Primitive
# -- see https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/bspfile.h
# "#if !defined( BSP_USE_LESS_MEMORY )" & "#if defined( _X360 )" defines specifically


# special lump classes, in alphabetical order:
class GameLumpHeader(source.GameLumpHeader):
    _format = ">4s2H2i"


# sprp GAME LUMP (LUMP 35) [version 4]
class StaticPropv4(source.StaticPropv4):
    """big-endian source.StaticPropv4"""
    _format = ">6f3H2Bi5f"


class GameLump_SPRPv4(source.GameLump_SPRPv4):
    StaticPropClass = StaticPropv4
    endianness = "big"


# sprp GAME LUMP (LUMP 35) [version 5]
class StaticPropv5(source.StaticPropv5):
    """big-endian source.StaticPropv5"""
    _format = ">6f3H2Bi6f"


class GameLump_SPRPv5(source.GameLump_SPRPv5):
    StaticPropClass = StaticPropv5
    endianness = "big"


# sprp GAME LUMP (LUMP 35) [version 6]
class StaticPropv6(source.StaticPropv6):
    """big-endian source.StaticPropv6"""
    _format = ">6f3H2Bi6f2H"


class GameLump_SPRPv6(source.GameLump_SPRPv6):
    StaticPropClass = StaticPropv6
    endianness = "big"


# sprp GAME LUMP (LUMP 35) [version 7*/10]
# NOTE: orange_box.StaticPropv10 overrides source.StaticPropv7 (7*)
# -- Left4Dead (Xbox 360) uses v7, & appears to be a new format...
class StaticPropv10(orange_box.StaticPropv10):
    """big-endian orange_box.StaticPropv10"""
    _format = ">6f3HBi6f2Hi2H"


class GameLump_SPRPv10(orange_box.GameLump_SPRPv10):
    StaticPropClass = StaticPropv10
    endianness = "big"


# TODO: PakFile
# TODO: PhysicsCollide
# TODO: PhysicsDisplacement


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = dict()

LUMP_CLASSES = dict()

SPECIAL_LUMP_CLASSES = {
    "ENTITIES":                 {0: shared.Entities},
    "TEXTURE_DATA_STRING_DATA": {0: source.TextureDataStringData}}

GAME_LUMP_HEADER = GameLumpHeader

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = {
    "sprp": {
        4:  GameLump_SPRPv4,
        5:  GameLump_SPRPv5,
        6:  GameLump_SPRPv6,
        7:  GameLump_SPRPv10,  # 7* / Left4Dead v7
        10: GameLump_SPRPv10}}


methods = orange_box.methods.copy()
