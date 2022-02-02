from . import orange_box_x360
from . import sdk_2013


FILE_MAGIC = b"PSBV"

BSP_VERSION = 21

GAME_PATHS = {"Portal 2": "Portal2/portal2"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = sdk_2013.LUMP


LumpHeader = orange_box_x360.LumpHeader


# TODO: Known lump changes from Orange Box (x360) -> Source SDK 2013 (x360):


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = orange_box_x360.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = orange_box_x360.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("WORLD_LIGHTS")
LUMP_CLASSES.pop("WORLD_LIGHTS_HDR")

SPECIAL_LUMP_CLASSES = orange_box_x360.SPECIAL_LUMP_CLASSES.copy()

GAME_LUMP_HEADER = orange_box_x360.GAME_LUMP_HEADER

GAME_LUMP_CLASSES = orange_box_x360.GAME_LUMP_CLASSES.copy()
GAME_LUMP_CLASSES["sprp"].pop(10)

methods = [*orange_box_x360.methods]
