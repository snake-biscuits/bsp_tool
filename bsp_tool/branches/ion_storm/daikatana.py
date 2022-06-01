# https://bitbucket.org/daikatana13/daikatana
from ..id_software import quake
from ..id_software import quake2


FILE_MAGIC = b"IBSP"

BSP_VERSION = 41

GAME_PATHS = {"Daikatana": "Daikatana"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = quake2.LUMP  # NOTE: this is an assumption


LumpHeader = quake.LumpHeader

# A rough map of the relationships between lumps:
# ENTITIES -> MODELS -> NODES -> LEAVES -> LEAF_FACES -> FACES
#                                      \-> LEAF_BRUSHES -> BRUSHES

#      /-> PLANES
# FACES -> SURFEDGES -> EDGES -> VERTICES
#     \--> TEXTURE_INFO
#      \-> LIGHTMAPS

# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = quake2.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = quake2.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("LEAVES")

SPECIAL_LUMP_CLASSES = quake2.SPECIAL_LUMP_CLASSES.copy()


methods = [*quake2.methods]
