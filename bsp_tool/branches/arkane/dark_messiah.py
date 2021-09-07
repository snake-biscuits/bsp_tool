# https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Dark_Messiah_of_Might_and_Magic
from ..valve import orange_box


BSP_VERSION = 20
# NOTE: BSP_VERSION is stored as 2 shorts?

GAMES = ["Dark Messiah of Might and Magic"]

LUMP = orange_box.LUMP
lump_header_address = orange_box.lump_header_address

LumpHeader = orange_box.OrangeBoxLumpHeader
read_lump_header = orange_box.read_lump_header

# classes for lumps, in alphabetical order:
# TODO: dheader_t, StaticPropLumpv6, texinfo_t, dgamelump_t, dmodel_t

# classes for special lumps, in alphabetical order:

# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = orange_box.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = orange_box.LUMP_CLASSES.copy()

SPECIAL_LUMP_CLASSES = orange_box.SPECIAL_LUMP_CLASSES.copy()

# GAME_LUMP_CLASSES = {"sprp": {6: lambda raw_lump: shared.GameLump_SPRP(raw_lump, StaticPropLumpv6)}}


methods = [*orange_box.methods]
