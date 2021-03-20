from . import vindictus


BSP_VERSION = 100  # assumed

LUMP = vindictus.LUMP
lump_header_address = vindictus.lump_header_address
LumpHeader = vindictus.LumpHeader
read_lump_header = vindictus.read_lump_header

LUMP_CLASSES = vindictus.LUMP_CLASSES.copy()
SPECIAL_LUMP_CLASSES = vindictus.SPECIAL_LUMP_CLASSES.copy()

methods = vindictus.methods
