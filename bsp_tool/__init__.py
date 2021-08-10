"""A library for .bsp file analysis & modification"""
__all__ = ["base", "branches", "load_bsp", "lumps", "tools",
           "IdTechBsp", "D3DBsp", "ValveBsp", "RespawnBsp"]

import difflib
import os
from types import ModuleType
from typing import Union

from . import base  # base.Bsp base class
from . import branches  # all known .bsp variant definitions
from . import lumps  # handles loading data dynamically
from .id_software import IdTechBsp
from .infinity_ward import D3DBsp
from .respawn import RespawnBsp
from .valve import ValveBsp


developers_by_file_magic = {b"IBSP": "id Software",  # also Infinity Ward
                            b"rBSP": "Respawn Entertainment",
                            b"VBSP": "Valve Software"}
# NOTE: GoldSrc has no file_magic, just jumps straight to version


def get_developer(filename: str) -> str:
    """returns assumed developer of .bsp format for given filename"""
    developer = "Unknown"
    if filename.endswith(".d3dbsp"):
        developer = "Infinity Ward"
    elif not filename.endswith(".bsp"):
        raise RuntimeError(f"{filename} is not a .bsp file!")
    with open(filename, "rb") as bsp_file:
        file_magic = bsp_file.read(4)
        if file_magic not in developers_by_file_magic:
            # TODO: check if GoldSrc
            raise RuntimeError(f"'{filename}' is not a valid .bsp file")
        bsp_version = int.from_bytes(bsp_file.read(4), "little")
        # NOTE: bsp_version is not always in this position
    if developer != "Infinity Ward":
        developer = developers_by_file_magic[file_magic]
        if file_magic == b"IBSP" and bsp_version == 59:  # CoD1 bsp_version
            developer = "Infinity Ward"
    return developer


def load_bsp(filename: str, branch: Union[str, ModuleType] = "Unknown"):
    """Calculate and return the correct base.Bsp sub-class for the given .bsp"""
    if not os.path.exists(filename):
        raise FileNotFoundError(f".bsp file '{filename}' does not exist.")
    # identify developer
    variants = {"id Software": IdTechBsp,
                "Infinity Ward": D3DBsp,
                "Respawn Entertainment": RespawnBsp,
                "Valve Software": ValveBsp}  # catches Nexon Source branch
    BspVariant = variants[get_developer(filename)]
    # check header
    with open(filename, "rb") as bsp_file:
        file_magic = bsp_file.read(4)
        bsp_version = int.from_bytes(bsp_file.read(4), "little")
        # NOTE: bsp_version is not always in this position
    if isinstance(branch, ModuleType):
        return BspVariant(branch, filename, autoload=True)
    elif isinstance(branch, str):
        # TODO: default to other methods on fail
        branch = branch.lower()
        branch = "".join(filter(str.isalnum, branch))
        # ^ "Counter-Strike: Online 2" -> "counterstrikeonline2"
        if branch != "unknown":
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
        else:
            if bsp_version not in branches.by_version:
                raise NotImplementedError(f"{file_magic} version {bsp_version} is not supported")
            branch = branches.by_version[bsp_version]
            return BspVariant(branch, filename, autoload=True)
