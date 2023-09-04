"""All three creditted programmers worked on Heavy Metal F.A.K.K. 2
Some also went on to work on MoH:AA expansions & some Valve titles"""
# https://github.com/id-Software/Quake-III-Arena/blob/master/code/bspc/l_bsp_sin.h
from ..id_software import quake
from ..id_software import quake2


FILE_MAGIC = b"RBSP"
# NOTE: b"IBSP" v41 is also SiN

BSP_VERSION = 1

GAME_PATHS = {"SiN": "SiN", "SiN Gold": "SiN"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = quake2.LUMP

LumpHeader = quake.LumpHeader


# {"LUMP": LumpClass}
BASIC_LUMP_CLASSES = quake2.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = quake2.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("FACES")
LUMP_CLASSES.pop("TEXTURE_INFO")

SPECIAL_LUMP_CLASSES = quake2.SPECIAL_LUMP_CLASSES.copy()


methods = quake2.methods.copy()
