"""Id Software's Quake Engine and it's predecessors have formed the basis for many modern engines."""
from . import qfusion  # Open source community source port
from . import quake
from . import quake2
from . import quake3
from . import remake_quake  # ReMakeQuake is an abandoned mod that created the BSP2 / BSP29a format
from . import remake_quake_old  # deprecated, but still supported


scripts = [qfusion, quake, quake2, quake3, remake_quake, remake_quake_old]
