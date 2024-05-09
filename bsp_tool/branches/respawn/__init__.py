"""Respawn Entertainment was founded by former Infinity Ward members.
Their version of the Source Engine was forked around 2011 from Portal 2.
While some remnants of the 2013 Source SDK remain, much is brand new
(though similarities to CoD 2 & CoD 4's formats exist in Titanfall).

The Titanfall Engine has b"rBSP" file-magic and 128 lumps
~72 of the 128 lumps appear in .bsp_lump files
the naming convention for .bsp_lump files is: "<bsp.filename>.<LUMP_HEX_ID>.bsp_lump"
where <LUMP_HEX_ID> is a lowercase four digit hexadecimal string
e.g. mp_rr_canyonlands.004a.bsp_lump -> 0x4A -> 74 -> VertexUnlitTS

entities are stored across 5 different .ent files per .bsp
the 5 files are: env, fx, script, snd, spawn
NOTE: the ENTITY_PARTITIONS lump may define which of these a .bsp is to use
e.g. mp_rr_canyonlands_env.ent  # kings canyon lighting, fog etc.
each .ent file has a header similar to: ENTITIES02 model_count=28
model_count appears to be the same across all .ent files for a given .bsp

presumably all this file splitting has to do with streaming data into memory"""
# NOTE: CoD 4 FastFiles (*.ff) also decimated .bsps
# -- fastfiles were used for console releases before CoD4 brought them to PC
# NOTE: .ent files for entities was introduced in Quake 3
# NOTE: Level scripting was introduced with QuakeC scripts
# NOTE: Respawn uses Valve's VScript + custom Squirrel .nut scripts in a VM
# -- Likely forked from Left 4 Dead / Left 4 Dead 2
from . import apex_legends
from . import apex_legends50
from . import apex_legends51
from . import apex_legends52
from . import titanfall
from . import titanfall_x360
from . import titanfall2


scripts = [
    apex_legends, apex_legends50, apex_legends51, apex_legends52,
    titanfall, titanfall_x360, titanfall2]

# Trivia:
# All Respawn's games give the error "Not an IBSP file" when FILE_MAGIC is incorrect
# - this text refers to QuakeII FILE_MAGIC, a game which released in 1997.
# - does this mean Apex Legends contains code from the Quake engine? Yeah, probably.
