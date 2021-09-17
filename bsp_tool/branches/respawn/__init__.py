__all__ = ["FILE_MAGIC", "apex_legends", "titanfall", "titanfall2"]

from . import apex_legends
from . import titanfall
from . import titanfall2

__doc__ = """Respawn Entertainment was founded by former Infinity Ward members.
Their version of the Source Engine was forked around 2010 and is heavily modified

The Titanfall Engine has b"rBSP" file-magic and 128 lumps
~72 of the 128 lumps appear in .bsp_lump files
the naming convention for these files is: "<bsp.filename>.<LUMP_HEX_ID>.bsp_lump"
where <LUMP_HEX_ID> is a lowercase four digit hexadecimal string
e.g. mp_rr_canyonlands.004a.bsp_lump -> 0x4A -> 74 -> VertexUnlitTS

entities are stored across 5 different .ent files per .bsp
the 5 files are: env, fx, script, snd, spawn
NOTE: the ENTITY_PARTITIONS lump may define which of these a .bsp is to use
e.g. mp_rr_canyonlands_env.ent  # kings canyon lighting, fog etc.
each .ent file has a header similar to: ENTITIES02 model_count=28
model_count appears to be the same across all .ent files for a given .bsp

presumably all this file splitting has to do with streaming data into memory"""

FILE_MAGIC = b"rBSP"

# Trivia:
# All Respawn's games give the error "Not an IBSP file" when FILE_MAGIC is incorrect
# - this text refers to Quake FILE_MAGIC, a game which released in 1996.
# - does this mean Apex Legends contains code from the Quake engine? Yeah, probably.
