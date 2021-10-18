# https://github.com/ValveSoftware/source-sdk-2013/
import enum
import struct

from . import orange_box
from . import source


FILE_MAGIC = b"VBSP"

BSP_VERSION = 21

GAME_PATHS = ["Blade Symphony", "Counter-Strike: Global Offensive", "Portal 2",
              "Source Filmmaker"]

GAME_VERSIONS = {GAME: BSP_VERSION for GAME in GAME_PATHS}


LUMP = orange_box.LUMP


# struct SourceBspHeader { char file_magic[4]; int version; SourceLumpHeader headers[64]; int revision; };
lump_header_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}


def read_lump_header(file, LUMP: enum.Enum) -> source.SourceLumpHeader:
    file.seek(lump_header_address[LUMP])
    offset, length, version, fourCC = struct.unpack("4I", file.read(16))
    header = source.SourceLumpHeader(offset, length, version, fourCC)
    return header


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = orange_box.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = orange_box.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("WORLD_LIGHTS")
LUMP_CLASSES.pop("WORLD_LIGHTS_HDR")

SPECIAL_LUMP_CLASSES = orange_box.SPECIAL_LUMP_CLASSES.copy()

GAME_LUMP_HEADER = orange_box.GAME_LUMP_HEADER

GAME_LUMP_CLASSES = orange_box.GAME_LUMP_CLASSES.copy()
GAME_LUMP_CLASSES["sprp"].pop(10)

methods = [*orange_box.methods]
