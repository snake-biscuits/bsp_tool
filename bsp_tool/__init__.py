"""A library for .bsp file analysis & modification"""
__all__ = ["base", "branches", "tools"]
from . import base
from . import branches
from . import tools


def load_bsp(filename: str):
    # detect file magic (developer)
    # detect .bsp format number (release)
    # create appropriate Bsp sub-class
    ...
    # this function should be attached to transitioning to creating .bsp files, rather than simply loading them.
    # beyond that, compiling could be interesting, particularly parellellised lightmap generation
    # (calculate per face texure, assemble & link afterwards)
