__all__ = ["quake", "quake2", "quake3"]

from . import quake
from . import quake2
from . import quake3
# TODO: Quake 4?
# TODO: Quake Champions?
# TODO: Hexen 2 (no file-magic)

__doc__ = """Id Software's Quake Engine and it's predecessors have formed the basis for many modern engines."""

FILE_MAGIC = b"IBSP"

branches = [quake, quake3]
