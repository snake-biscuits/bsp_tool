from .. import x360
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
StaticPropv8_x360 = x360.make_big_endian(left4dead.StaticPropv8)
StaticPropv9_x360 = x360.make_big_endian(left4dead2.StaticPropv9)
StaticPropv10_x360 = x360.make_big_endian(sdk_2013.StaticPropv10)
StaticPropv11_x360 = x360.make_big_endian(sdk_2013.StaticPropv11)


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = orange_box_x360.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = orange_box_x360.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("WORLD_LIGHTS")
LUMP_CLASSES.pop("WORLD_LIGHTS_HDR")

SPECIAL_LUMP_CLASSES = orange_box_x360.SPECIAL_LUMP_CLASSES.copy()

GAME_LUMP_HEADER = orange_box_x360.GAME_LUMP_HEADER

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = {"sprp": orange_box_x360.GAME_LUMP_CLASSES["sprp"].copy()}
GAME_LUMP_CLASSES["sprp"].update({8: lambda raw_lump: orange_box_x360.GameLump_SPRP_x360(raw_lump, StaticPropv8_x360),
                                  9: lambda raw_lump: orange_box_x360.GameLump_SPRP_x360(raw_lump, StaticPropv9_x360),
                                  10: lambda raw_lump: orange_box_x360.GameLump_SPRP_x360(raw_lump, StaticPropv10_x360),
                                  11: lambda raw_lump: orange_box_x360.GameLump_SPRP_x360(raw_lump, StaticPropv11_x360)})


methods = [*orange_box_x360.methods]
