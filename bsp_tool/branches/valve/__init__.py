__all__ = ["FILE_MAGIC", "cs_go", "cs_source", "orange_box"]

# TODO: Goldsrc
from . import cs_go
from . import cs_source
from . import orange_box  # Most Source Engine Games
# NOTE: v20 Source BSPs differ widely, since many forks are of this version

__doc__ = """Valve Software developed the GoldSrc Engine, building on Id Software's Quake & Quake II Engines.
This variant powered Half-Life & CS:1.6. In developing Half-Life 2 they created the Source Engine."""

# TRIVIA: Source engine games give the error "Not an IBSP file" when FILE_MAGIC is incorrect
# - this refers to Quake FILE_MAGIC
FILE_MAGIC = b"VBSP"
