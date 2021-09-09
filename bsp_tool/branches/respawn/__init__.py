__all__ = ["FILE_MAGIC", "apex_legends", "titanfall", "titanfall2"]

from . import apex_legends
from . import titanfall
from . import titanfall2
# NOTE: Titanfall: Online was a planned f2p spin-off developed with Nexon
# an open beta was held in August & September of 2017[1][2],
# the game was later cancelled in 2018[3].
# sources:
# [1] https://titanfall.fandom.com/wiki/Titanfall_Online
# [2] https://twitter.com/ZhugeEX/status/893143346021105665
# [3] https://kotaku.com/titanfall-online-cancelled-in-south-korea-1827440902

# Titanfall: Online's .bsp format is near identical to titanfall's
# the only difference is all lumps are internal & files are kept in Nexon's .pkg archives
# Files from the Titanfall:Online closed beta can be found in the internet archive:
# https://archive.org/details/titanfall-online_202107

__doc__ = """Respawn Entertainment was founded by former Infinity Ward members.
Their version of the Source Engine was forked around 2010 and is heavily modified"""

# NOTE: All Respawn's games give the error "Not an IBSP file" when FILE_MAGIC is incorrect
# - this text refers to Quake FILE_MAGIC, a game which released in 1996.
# - does this mean Apex Legends contains code from the Quake engine? Yes, yes it does.
FILE_MAGIC = b"rBSP"
