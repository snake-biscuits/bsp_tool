__all__ = ["FILE_MAGIC", "cso2", "vindictus"]

from . import cso2  # CounterStrike Online 2
from . import vindictus

__doc__ = """Nexon is a South Korean / Japanese developer
They have worked with both Valve & Respawn's Source Engine (CS:O & TF:O [cancelled])"""

# NOTE: Nexon games are build on source, and use it's FILE_MAGIC
FILE_MAGIC = b"VBSP"
