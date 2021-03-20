"""Counter-Strike: Source"""

from . import orange_box


BSP_VERSION = 19

LUMP = orange_box.LUMP
lump_header_address = orange_box.lump_header_address
LumpHeader = orange_box.LumpHeader
read_lump_header = orange_box.read_lump_header

# classes for each lump, in alphabetical order: [XX / 64]

LUMP_CLASSES = orange_box.LUMP_CLASSES.copy()
# LUMP_CLASSES.update({"LUMP_NAME": LumpClass})
SPECIAL_LUMP_CLASSES = orange_box.SPECIAL_LUMP_CLASSES.copy()

methods = orange_box.methods
