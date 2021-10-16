"""Id Software's Quake Engine and it's predecessors have formed the basis for many modern engines."""
from . import quake
from . import quake2
from . import quake3
# TODO: quake4 (IdTech4 == no .bsp?)
# TODO: quake_champions (proprietary archives)
# TODO: hexen2 (extends quake)


scripts = [quake, quake2, quake3]
