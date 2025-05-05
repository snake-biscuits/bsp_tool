# https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Dark_Messiah_of_Might_and_Magic
from ..valve import orange_box
from ..valve import source


FILE_MAGIC = b"VBSP"

BSP_VERSION = (20, 4)

GAME_PATHS = {
    "Dark Messiah of Might and Magic Multi-Player": "Dark Messiah of Might and Magic Multi-Player"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = orange_box.LUMP


LumpHeader = source.LumpHeader


# special lump classes, in alphabetical order:
# TODO: StaticPropLumpv6


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = orange_box.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = orange_box.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("WORLD_LIGHTS")  # sdk_2013 + uint32 illuminate_players (0, 1, 2 enum)
LUMP_CLASSES.pop("WORLD_LIGHTS_HDR")  # TODO: check .fgd for illuminate players enum

SPECIAL_LUMP_CLASSES = orange_box.SPECIAL_LUMP_CLASSES.copy()

GAME_LUMP_HEADER = orange_box.GAME_LUMP_HEADER

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = {
    "sprp": {6: source.GameLump_SPRPv6}}


methods = orange_box.methods.copy()
