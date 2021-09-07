# https://valvedev.info/tools/bspfix/
# https://developer.valvesoftware.com/wiki/Hl_bs.fgd
from ..valve import goldsrc  # fork


BSP_VERSION = 30

GAMES = ["Half-Life/bshift"]  # Half-Life: Blue Shift

LUMP = goldsrc.LUMP
# NOTE: different headers?
lump_header_address = {LUMP_ID: (4 + i * 8) for i, LUMP_ID in enumerate(LUMP)}

MAX = goldsrc.MAX
Contents = goldsrc.Contents

BASIC_LUMP_CLASSES = goldsrc.BASIC_LUMP_CLASSES.copy()
LUMP_CLASSES = goldsrc.LUMP_CLASSES.copy()
# PLANES lump failing
SPECIAL_LUMP_CLASSES = goldsrc.SPECIAL_LUMP_CLASSES.copy()
# ENTITIES lump failing

methods = [*goldsrc.methods]
