"""A library for .bsp file analysis & modification"""
__all__ = [
    "archives", "autodetect", "base", "branches", "core",
    "extensions", "lightmaps", "lumps", "scene",
    "load_bsp",
    "D3DBsp", "FusionBsp", "Genesis3DBsp", "GoldSrcBsp", "IdTechBsp",
    "InfinityWardBsp", "NexonBsp", "QbismBsp", "QuakeBsp", "Quake64Bsp",
    "RavenBsp", "ReMakeQuakeBsp", "RespawnBsp", "RitualBsp", "ValveBsp"]


from types import ModuleType
# modules
from . import archives
from . import autodetect
from . import base  # base.Bsp
from . import branches
from . import core
from . import extensions
from . import lightmaps
from . import lumps
from . import scene
# BspClasses
from .id_software import FusionBsp, IdTechBsp, QbismBsp
from .id_software import QuakeBsp, Quake64Bsp, ReMakeQuakeBsp
from .infinity_ward import D3DBsp, InfinityWardBsp
from .raven import RavenBsp
from .respawn import RespawnBsp
from .ritual import RitualBsp
from .nexon import NexonBsp
from .valve import GoldSrcBsp, ValveBsp
from .wild_tangent import Genesis3DBsp


def load_bsp(filename: str, force_branch: ModuleType = None) -> base.Bsp:
    """Calculate and return the correct base.Bsp sub-class for the given .bsp"""
    return autodetect.guess_from_filename(filename, force_branch)
