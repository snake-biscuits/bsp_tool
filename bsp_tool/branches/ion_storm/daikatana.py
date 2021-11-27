# https://bitbucket.org/daikatana13/daikatana
from ..id_software import quake2


FILE_MAGIC = b"IBSP"

BSP_VERSION = 41

GAME_PATHS = ["Daikatana"]

GAME_VERSIONS = {GAME_PATH: BSP_VERSION for GAME_PATH in GAME_PATHS}


LUMP = quake2.LUMP  # NOTE: ASSUMED

# struct Quake2BspHeader { char file_magic[4]; int version; QuakeLumpHeader headers[19]; };
lump_header_address = {LUMP_ID: (8 + i * 8) for i, LUMP_ID in enumerate(LUMP)}

# A rough map of the relationships between lumps:
# ENTITIES -> MODELS -> NODES -> LEAVES -> LEAF_FACES -> FACES
#                                      \-> LEAF_BRUSHES

# FACES -> SURFEDGES -> EDGES -> VERTICES
#    \--> TEXTURE_INFO -> MIP_TEXTURES
#     \--> LIGHTMAPS
#      \-> PLANES

# LEAF_FACES -> FACES
# LEAF_BRUSHES -> BRUSHES

# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = quake2.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = quake2.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("LEAVES")

SPECIAL_LUMP_CLASSES = quake2.SPECIAL_LUMP_CLASSES.copy()


methods = [*quake2.methods]
