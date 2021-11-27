# https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Dark_Messiah_of_Might_and_Magic
import enum
import struct

from ..valve import orange_box
from ..valve import source


FILE_MAGIC = b"VBSP"

BSP_VERSION = (20, 4)  # int.from_bytes(struct.pack("2H", 20, 4), "little")

GAME_PATHS = ["Dark Messiah of Might and Magic Multi-Player"]

GAME_VERSIONS = {GAME_PATH: BSP_VERSION for GAME_PATH in GAME_PATHS}


LUMP = orange_box.LUMP

# struct DarkMessiahBspHeader { char file_magic[4]; short version[2]; SourceLumpHeader headers[64]; int revision;};
lump_header_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}


def read_lump_header(file, LUMP: enum.Enum) -> source.SourceLumpHeader:
    file.seek(lump_header_address[LUMP])
    offset, length, version, fourCC = struct.unpack("4I", file.read(16))
    header = source.SourceLumpHeader(offset, length, version, fourCC)
    return header


# TODO: StaticPropLumpv6


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = orange_box.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = orange_box.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("WORLD_LIGHTS")  # sdk_2013?
LUMP_CLASSES.pop("WORLD_LIGHTS_HDR")

SPECIAL_LUMP_CLASSES = orange_box.SPECIAL_LUMP_CLASSES.copy()

GAME_LUMP_HEADER = orange_box.GAME_LUMP_HEADER

GAME_LUMP_CLASSES = {"sprp": {6: lambda raw_lump: source.GameLump_SPRP(raw_lump, None)}}


methods = [*orange_box.methods]
