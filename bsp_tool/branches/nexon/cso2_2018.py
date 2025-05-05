"""2018-onwards format"""
# https://git.sr.ht/~leite/cso2-bsp-converter/tree/master/item/src/bsptypes.hpp
from ... import core
from . import cso2


FILE_MAGIC = b"VBSP"

BSP_VERSION = 100

GAME_PATHS = {"Counter-Strike: Online 2": "CSO2"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = cso2.LUMP


LumpHeader = cso2.LumpHeader


# classes for each lump, in alphabetical order:
class DisplacementInfo(core.Struct):  # LUMP 26
    # NOTE: 10 bytes more than Vindictus
    __slots__ = ["unknown"]  # not yet used
    _format = "242B"
    _arrays = {"unknown": 242}

# TODO: dcubemap_t: 164 bytes
# TODO: Facev1


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = cso2.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = cso2.LUMP_CLASSES.copy()
LUMP_CLASSES.update({
    "DISPLACEMENT_INFO": {0: DisplacementInfo}})

SPECIAL_LUMP_CLASSES = cso2.SPECIAL_LUMP_CLASSES.copy()

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = cso2.GAME_LUMP_CLASSES.copy()


methods = cso2.methods.copy()
