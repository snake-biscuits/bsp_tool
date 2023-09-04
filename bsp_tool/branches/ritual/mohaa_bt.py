# https://github.com/wfowler1/LibBSP
from ..id_software import quake
from . import mohaa


FILE_MAGIC = b"EALA"

BSP_VERSION = 21

GAME_PATHS = {"Medal of Honor: Allied Assault - Breakthrough": "MoHAA/maintt"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = mohaa.LUMP

LumpHeader = quake.LumpHeader


# TODO: Known lump changes from Allied Assault -> Breakthrough:

# a rough map of the relationships between lumps:
#
#               /-> Shader
# Model -> Brush -> BrushSide
#      \-> Face -> MeshVertex
#             \--> Texture
#              \-> Vertex


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = mohaa.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = mohaa.LUMP_CLASSES.copy()

SPECIAL_LUMP_CLASSES = mohaa.SPECIAL_LUMP_CLASSES.copy()


methods = mohaa.methods.copy()
