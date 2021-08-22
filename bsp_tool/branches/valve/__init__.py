__all__ = ["FILE_MAGIC", "alien_swarm", "branches", "cs_go", "cs_source", "forks",
           "goldsrc", "left4dead", "orange_box"]

from . import alien_swarm
from . import cs_go
from . import cs_source
from . import goldsrc  # Most GoldSrc Games
from . import left4dead
from . import orange_box  # Most Source Engine Games
# TODO: Portal 2

__doc__ = """Valve Software developed the GoldSrc Engine, building on Id Software's Quake & Quake II Engines.
This variant powered Half-Life & CS:1.6. In developing Half-Life 2 they created the Source Engine."""

# TRIVIA: when FILE_MAGIC is incorrect Source engine games give the error message: "Not an IBSP file"
# - this refers to the IdTech 2 FILE_MAGIC, pre-dating Half-Life 1!
FILE_MAGIC = b"VBSP"
# NOTE: GoldSrcBsp has no FILE_MAGIC

branches = [alien_swarm, cs_go, cs_source, goldsrc, orange_box, left4dead]
