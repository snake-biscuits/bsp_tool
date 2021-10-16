# https://developer.valvesoftware.com/wiki/Source_BSP_File_Format
from ..valve import source


FILE_MAGIC = b"VBSP"

BSP_VERSION = 17  # technically older than HL2's Source Engine branch

GAME_PATHS = ["Vampire The Masquerade - Bloodlines"]

GAME_VERSIONS = {GAME: BSP_VERSION for GAME in GAME_PATHS}


LUMP = source.LUMP

# struct SourceBspHeader { char file_magic[4]; int version; SourceLumpHeader headers[64]; int revision; };
lump_header_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}


read_lump_header = source.read_lump_header


# classes for lumps, in alphabetical order:
# TODO: dface_t


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = source.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = source.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("FACES")
LUMP_CLASSES.pop("ORIGINAL_FACES")

SPECIAL_LUMP_CLASSES = source.SPECIAL_LUMP_CLASSES.copy()
SPECIAL_LUMP_CLASSES.pop("PHYSICS_COLLIDE")

GAME_LUMP_CLASSES = source.GAME_LUMP_CLASSES.copy()


methods = [*source.methods]
