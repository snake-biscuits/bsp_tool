# https://github.com/ValveSoftware/source-sdk-2013/
import enum
import struct

from . import orange_box
from . import source


BSP_VERSION = 21

GAMES = ["Counter-Strike: Global Offensive", "Blade Symphony", "Portal 2",
         "Source Filmmaker"]
GAME_VERSIONS = {game: BSP_VERSION for game in GAMES}

LUMP = orange_box.LUMP
lump_header_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}


def read_lump_header(file, LUMP: enum.Enum) -> source.SourceLumpHeader:
    file.seek(lump_header_address[LUMP])
    offset, length, version, fourCC = struct.unpack("4I", file.read(16))
    header = source.SourceLumpHeader(offset, length, version, fourCC)
    return header


# classes for each lump, in alphabetical order:

# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = orange_box.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = orange_box.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("WORLD_LIGHTS")
LUMP_CLASSES.pop("WORLD_LIGHTS_HDR")

SPECIAL_LUMP_CLASSES = orange_box.SPECIAL_LUMP_CLASSES.copy()

GAME_LUMP_CLASSES = orange_box.GAME_LUMP_CLASSES.copy()
GAME_LUMP_CLASSES["sprp"].pop(10)

methods = [*orange_box.methods]
