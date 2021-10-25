from ..id_software import quake2


FILE_MAGIC = b"IBSP"

BSP_VERSION = 46

GAME_PATHS = ["Soldier of Fortune "]

GAME_VERSIONS = {GAME: BSP_VERSION for GAME in GAME_PATHS}


LUMP = quake2.LUMP


# struct Quake2BspHeader { char file_magic[4]; int version; QuakeLumpHeader headers[19]; };
lump_header_address = {LUMP_ID: (8 + i * 8) for i, LUMP_ID in enumerate(LUMP)}


BASIC_LUMP_CLASSES = quake2.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = quake2.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("FACES")
LUMP_CLASSES.pop("LEAVES")

SPECIAL_LUMP_CLASSES = quake2.SPECIAL_LUMP_CLASSES.copy()


methods = [*quake2.methods]
