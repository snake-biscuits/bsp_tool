from ..id_software import quake
from ..id_software import quake2


FILE_MAGIC = b"IBSP"

BSP_VERSION = 46

GAME_PATHS = {"Soldier of Fortune": "SoF"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = quake2.LUMP


LumpHeader = quake.LumpHeader


BASIC_LUMP_CLASSES = quake2.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = quake2.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("FACES")
LUMP_CLASSES.pop("LEAVES")

SPECIAL_LUMP_CLASSES = quake2.SPECIAL_LUMP_CLASSES.copy()


methods = [*quake2.methods]
