"""All three creditted programmers worked on Heavy Metal F.A.K.K. 2
Some also went on to work on MoH:AA expansions & some Valve titles"""
from ..id_software import quake2


FILE_MAGIC = b"RBSP"  # Ubertools?
# NOTE: 1 b"IBSP" map exists, will it play?

BSP_VERSION = 1

GAME_PATHS = ["SiN", "SiN Gold"]

GAME_VERSIONS = {GAME: BSP_VERSION for GAME in GAME_PATHS}


LUMP = quake2.LUMP


# struct Quake2BspHeader { char file_magic[4]; int version; QuakeLumpHeader headers[19]; };
lump_header_address = {LUMP_ID: (8 + i * 8) for i, LUMP_ID in enumerate(LUMP)}


# {"LUMP": LumpClass}
BASIC_LUMP_CLASSES = quake2.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = quake2.LUMP_CLASSES.copy()

SPECIAL_LUMP_CLASSES = quake2.SPECIAL_LUMP_CLASSES.copy()


methods = [*quake2.methods]
