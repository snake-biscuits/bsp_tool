__all__ = ["FILE_MAGIC", "apex_legends", "titanfall", "titanfall2"]

from . import apex_legends
from . import titanfall
from . import titanfall2

__doc__ = """Respawn Entertainment was founded by former Infinity Ward members.
Their version of the Source Engine was forked around 2010 and is heavily modified"""

# NOTE: All Respawn's games give the error "Not an IBSP file" when FILE_MAGIC is incorrect
# - this text refers to Quake FILE_MAGIC, a game which released in 1996.
# - does this mean Apex Legends contains code from the Quake engine? Yes, yes it does.
FILE_MAGIC = b"rBSP"
