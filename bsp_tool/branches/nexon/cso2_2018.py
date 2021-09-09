# https://git.sr.ht/~leite/cso2-bsp-converter/tree/master/item/src/bsptypes.hpp
from .. import base
from . import cso2


BSP_VERSION = 100
# NOTE: almost all version numbers match 2013 era maps, this makes detection a pain

LUMP = cso2.LUMP
lump_header_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}
read_lump_header = cso2.read_lump_header


# classes for each lump, in alphabetical order:
class DisplacementInfo(base.Struct):  # LUMP 26
    # NOTE: 10 bytes more than Vindictus
    __slots__ = ["unknown"]  # not yet used
    _format = "242B"
    _arrays = {"unknown": 242}

# TODO: dcubemap_t: 164 bytes
# TODO: Facev1

# special lump classes, in alphabetical order:


BASIC_LUMP_CLASSES = cso2.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = cso2.LUMP_CLASSES.copy()
LUMP_CLASSES.update({"DISPLACEMENT_INFO": {0: DisplacementInfo}})

SPECIAL_LUMP_CLASSES = cso2.SPECIAL_LUMP_CLASSES.copy()

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = cso2.GAME_LUMP_CLASSES.copy()


# branch exclusive methods, in alphabetical order:

methods = [*cso2.methods]
