from . import left4dead
from . import left4dead2
from . import orange_box_x360
from . import sdk_2013


FILE_MAGIC = b"PSBV"

BSP_VERSION = 21

GAME_PATHS = {"Portal 2": "Portal2/portal2"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = sdk_2013.LUMP


LumpHeader = orange_box_x360.LumpHeader


# TODO: Known lump changes from Orange Box (x360) -> Source SDK 2013 (x360):


# special lump classes, in alphabetical order:
# sprp GAME LUMP (LUMP 35) [version 8]
class StaticPropv8(left4dead.StaticPropv8):
    _format = ">6f3H2Bi6f8B"


class GameLump_SPRPv8(left4dead.GameLump_SPRPv8):
    StaticPropClass = StaticPropv8
    endianness = "big"


# sprp GAME LUMP (LUMP 35) [version 9]
# NOTE: failing for Portal 2
class StaticPropv9(left4dead2.StaticPropv9):
    _format = ">6f3H2Bi6f8BI"


class GameLump_SPRPv9(left4dead2.GameLump_SPRPv9):
    StaticPropClass = StaticPropv9
    endianness = "big"
    # model_names appears to be absent?
    # "empty" lumps consist of 3 seemingly random integers?


# sprp GAME LUMP (LUMP 35) [version 10]
class StaticPropv10(sdk_2013.StaticPropv10):
    _format = ">6f3H2Bi6f8B2I"


class GameLump_SPRPv10(sdk_2013.GameLump_SPRPv10):
    StaticPropClass = StaticPropv10
    endianness = "big"


# sprp GAME LUMP (LUMP 35) [version 11]
class StaticPropv11(sdk_2013.StaticPropv11):
    _format = ">6f3H2Bi6f8BIfi"


class GameLump_SPRPv11(sdk_2013.GameLump_SPRPv11):
    StaticPropClass = StaticPropv11
    endianness = "big"


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = orange_box_x360.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = orange_box_x360.LUMP_CLASSES.copy()
# LUMP_CLASSES.pop("WORLD_LIGHTS")
# LUMP_CLASSES.pop("WORLD_LIGHTS_HDR")

SPECIAL_LUMP_CLASSES = orange_box_x360.SPECIAL_LUMP_CLASSES.copy()

GAME_LUMP_HEADER = orange_box_x360.GameLumpHeader

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = {
    "sprp": {
        4:  orange_box_x360.GameLump_SPRPv4,
        5:  orange_box_x360.GameLump_SPRPv5,
        6:  orange_box_x360.GameLump_SPRPv6,
        7:  orange_box_x360.GameLump_SPRPv10,  # 7* / Left4Dead v7
        8:  GameLump_SPRPv8,
        9:  GameLump_SPRPv9,
        10: GameLump_SPRPv10,
        11: GameLump_SPRPv11}}


methods = orange_box_x360.methods.copy()
