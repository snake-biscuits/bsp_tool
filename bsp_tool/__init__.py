"""A library for .bsp file analysis & modification"""
__all__ = ["base", "branches", "load_bsp", "lumps", "tools",
           "GoldSrcBsp", "ValveBsp", "QuakeBsp", "IdTechBsp",
           "D3DBsp", "RespawnBsp", "UberBsp"]

import difflib
import os
from types import ModuleType
from typing import Union

from . import base  # base.Bsp base class
from . import branches  # all known .bsp variant definitions
from . import lumps  # handles loading data dynamically
from .id_software import QuakeBsp, IdTechBsp
from .infinity_ward import D3DBsp
from .respawn import RespawnBsp
from .ritual import UberBsp
from .valve import GoldSrcBsp, ValveBsp


# NOTE: Quake Live branch_script should be quake3, but auto-detect defaults to quake2 on BSP_VERSION
# NOTE: CoD1 auto-detect by version defaults to ApexLegends


developers_by_file_magic = {b"FAKK": UberBsp,
                            b"IBSP": IdTechBsp,  # or D3DBsp
                            b"rBSP": RespawnBsp,
                            b"VBSP": ValveBsp}
# HACK: GoldSrcBsp has no file-magic, substituting BSP_VERSION
goldsrc_versions = [branches.valve.goldsrc.BSP_VERSION, branches.gearbox.bshift.BSP_VERSION]
developers_by_file_magic.update({v.to_bytes(4, "little"): GoldSrcBsp for v in goldsrc_versions})

developers_by_file_magic.update({branches.id_software.quake.BSP_VERSION.to_bytes(4, "little"): QuakeBsp})

cod_ibsp_versions = [getattr(branches.infinity_ward, b).BSP_VERSION for b in branches.infinity_ward.__all__]


def guess_by_file_magic(filename: str) -> (base.Bsp, int):
    """returns BspVariant & version"""
    if os.path.getsize(filename) == 0:  # HL2/ d2_coast_02.bsp
        raise RuntimeError(f"{filename} is an empty file")
    BspVariant = None
    if filename.endswith(".d3dbsp"):
        BspVariant = D3DBsp
    elif filename.endswith(".bsp"):
        with open(filename, "rb") as bsp_file:
            file_magic = bsp_file.read(4)
            if file_magic not in developers_by_file_magic:
                raise RuntimeError(f"'{filename}' does not resemble a .bsp file")
            bsp_version = int.from_bytes(bsp_file.read(4), "little")
        BspVariant = developers_by_file_magic[file_magic]
        if BspVariant == GoldSrcBsp:
            bsp_version = int.from_bytes(file_magic, "little")
        # D3DBsp has b"IBSP" file_magic
        if file_magic == b"IBSP" and bsp_version in cod_ibsp_versions:
            BspVariant = D3DBsp
    else:  # invalid extension
        raise RuntimeError(f"{filename} is not a .bsp file!")
    return BspVariant, bsp_version


def load_bsp(filename: str, branch: Union[str, ModuleType] = "Unknown"):
    """Calculate and return the correct base.Bsp sub-class for the given .bsp"""
    if not os.path.exists(filename):
        raise FileNotFoundError(f".bsp file '{filename}' does not exist.")
    BspVariant, bsp_version = guess_by_file_magic(filename)
    if isinstance(branch, ModuleType):
        return BspVariant(branch, filename, autoload=True)
    elif isinstance(branch, str):
        # TODO: default to other methods on fail
        branch: str = branches.simplify_name(branch)
        if branch != "unknown":  # not default
            if branch not in branches.by_name:
                close_matches = difflib.get_close_matches(branch, branches.by_name)
                if len(close_matches) == 0:
                    raise NotImplementedError(f"'{branch}' .bsp format is not supported, yet.")
                else:
                    print(f"'{branch}'.bsp format is not supported. Assumed branches:",
                          "\n".join(close_matches),
                          f"Trying '{close_matches[0]}'...", sep="\n")
                    branch: str = close_matches[0]
            branch: ModuleType = branches.by_name[branch]  # "name" -> branch_script
        # guess branch by format version
        else:
            if bsp_version not in branches.by_version:
                raise NotImplementedError(f"{BspVariant} v{bsp_version} is not supported!")
            branch: ModuleType = branches.by_version[bsp_version]
        return BspVariant(branch, filename, autoload=True)
    else:
        raise TypeError(f"Cannot use branch of type `{branch.__class__.__name__}`")
