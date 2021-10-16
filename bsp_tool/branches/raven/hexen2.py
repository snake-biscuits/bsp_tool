from ..id_software import quake


FILE_MAGIC = None

BSP_VERSION = 29

GAME_PATHS = ["Hexen 2"]

GAME_VERSIONS = {GAME: BSP_VERSION for GAME in GAME_PATHS}


LUMP = quake.LUMP


# struct QuakeBspHeader { int version; QuakeLumpHeader headers[15]; };
lump_header_address = {LUMP_ID: (4 + i * 8) for i, LUMP_ID in enumerate(LUMP)}


BASIC_LUMP_CLASSES = quake.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = quake.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("MODELS")

SPECIAL_LUMP_CLASSES = quake.SPECIAL_LUMP_CLASSES.copy()


methods = [*quake.methods]
