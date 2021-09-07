"""Counter-Strike: Source"""
import enum
import struct

from . import orange_box


BSP_VERSION = 19  # & 20

GAMES = ["Counter-Strike: Source"]

LUMP = orange_box.LUMP
lump_header_address = orange_box.lump_header_address


def read_lump_header(file, LUMP: enum.Enum) -> orange_box.OrangeBoxLumpHeader:
    file.seek(lump_header_address[LUMP])
    offset, length, version, fourCC = struct.unpack("4I", file.read(16))
    header = orange_box.OrangeBoxLumpHeader(offset, length, version, fourCC)
    return header


# classes for each lump, in alphabetical order:

# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = orange_box.BASIC_LUMP_CLASSES.copy()
LUMP_CLASSES = orange_box.LUMP_CLASSES.copy()
SPECIAL_LUMP_CLASSES = orange_box.SPECIAL_LUMP_CLASSES.copy()
GAME_LUMP_CLASSES = orange_box.GAME_LUMP_CLASSES.copy()

methods = [*orange_box.methods]
