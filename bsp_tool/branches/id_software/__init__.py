__all__ = ["quake", "quake3"]

from . import quake
from . import quake3
# TODO: Quake 2, 4, Live & Champions

__doc__ = """Id Software's Quake Engine and it's predecessors have formed the basis for many modern engines."""

FILE_MAGIC = b"IBSP"

branches = [quake, quake3]
