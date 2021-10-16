# https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Dark_Messiah_of_Might_and_Magic
import enum
import struct

from ..valve import orange_box
from ..valve import source


FILE_MAGIC = b"VBSP"

BSP_VERSION = 20  # NOTE: BSP_VERSION is stored as 2 shorts?

GAME_PATHS = ["Dark Messiah of Might and Magic"]

GAME_VERSIONS = {GAME: BSP_VERSION for GAME in GAME_PATHS}


LUMP = orange_box.LUMP

# struct DarkMessiahBspHeader { char file_magic[4]; short version[2]; SourceLumpHeader headers[64]; int revision;};
lump_header_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}


def read_lump_header(file, LUMP: enum.Enum) -> source.SourceLumpHeader:
    file.seek(lump_header_address[LUMP])
    offset, length, version, fourCC = struct.unpack("4I", file.read(16))
    header = source.SourceLumpHeader(offset, length, version, fourCC)
    return header

# classes for lumps, in alphabetical order:
# TODO: dheader_t, texinfo_t, dgamelump_t, dmodel_t

# classes for special lumps, in alphabetical order:
# TODO: StaticPropLumpv6


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = orange_box.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = orange_box.LUMP_CLASSES.copy()

SPECIAL_LUMP_CLASSES = orange_box.SPECIAL_LUMP_CLASSES.copy()

# GAME_LUMP_CLASSES = {"sprp": {6: lambda raw_lump: shared.GameLump_SPRP(raw_lump, StaticPropLumpv6)}}


methods = [*orange_box.methods]
