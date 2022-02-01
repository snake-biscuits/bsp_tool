from ..id_software import quake


FILE_MAGIC = None

BSP_VERSION = 29

GAME_PATHS = {"Hexen II": "Hexen 2"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = quake.LUMP


LumpHeader = quake.LumpHeader


BASIC_LUMP_CLASSES = quake.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = quake.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("MODELS")

SPECIAL_LUMP_CLASSES = quake.SPECIAL_LUMP_CLASSES.copy()


methods = [*quake.methods]
