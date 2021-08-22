"""Counter-Strike: Source"""

from . import orange_box


BSP_VERSION = 19  # & 20

GAMES = ["Counter-Strike: Source"]

LUMP = orange_box.LUMP
lump_header_address = orange_box.lump_header_address

LumpHeader = orange_box.LumpHeader
read_lump_header = orange_box.read_lump_header

# classes for each lump, in alphabetical order:

# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = orange_box.BASIC_LUMP_CLASSES.copy()
LUMP_CLASSES = orange_box.LUMP_CLASSES.copy()
SPECIAL_LUMP_CLASSES = orange_box.SPECIAL_LUMP_CLASSES.copy()

methods = [*orange_box.methods]
