"""A library for .bsp file analysis & modification"""
__all__ = ["base", "branches", "load_bsp", "tools", "IdTechBsp", "D3DBsp", "ValveBsp", "RespawnBsp"]

import difflib
import os
from types import ModuleType
from typing import Union

from . import base  # base.Bsp base class
from . import branches  # all known .bsp variant definitions
from .id_software import IdTechBsp
from .infinity_ward import D3DBsp
from .respawn import RespawnBsp
from .valve import ValveBsp


developers_by_file_magic = {b"IBSP": "id Software",  # also Infinity Ward
                            b"rBSP": "Respawn Entertainment",
                            b"VBSP": "Valve Software"}


def get_developer(filename: str) -> str:
    developer = "Unknown"
    if filename.endswith(".d3dbsp"):
        developer = "Infinity Ward"
    elif not filename.endswith(".bsp"):
        raise RuntimeError(f"{filename} is not a .bsp file!")
    with open(filename, "rb") as bsp_file:
        file_magic = bsp_file.read(4)
        bsp_version = int.from_bytes(bsp_file.read(4), "little")
        # NOTE: bsp_version is not always in this position
    if developer != "Infinity Ward":
        developer = developers_by_file_magic[file_magic]
        if file_magic == b"IBSP" and bsp_version == 59:  # CoD1 bsp_version
            developer = "Infinity Ward"
    return developer


def load_bsp(filename: str, branch: Union[str, ModuleType] = "Unknown"):
    # TODO: make legible
    # TODO: default branches for certain criteria
    # identify developer variant
    if not os.path.exists(filename):
        raise FileNotFoundError(f".bsp file '{filename}' does not exist.")
    variants = {"id Software": IdTechBsp,
                "Infinity Ward": D3DBsp,
                "Respawn Entertainment": RespawnBsp,
                "Valve Software": ValveBsp}  # catches Nexon Source branch
    BspVariant = variants[get_developer(filename)]
    with open(filename, "rb") as bsp_file:
        file_magic = bsp_file.read(4)
        bsp_version = int.from_bytes(bsp_file.read(4), "little")
        # NOTE: bsp_version is not always in this position
    if isinstance(branch, ModuleType):
        return BspVariant(branch, filename, autoload=True)
    elif isinstance(branch, str):
        branch = branch.lower()
        branch = "".join(filter(str.isalnum, branch))
        # ^ "Counter-Strike: Online 2" -> "counterstrikeonline2"
        if branch != "unknown":
            if branch not in branches.by_name:
                close_matches = difflib.get_close_matches(branch, branches.by_name)
                if len(close_matches) == 0:
                    raise NotImplementedError(f"{branch} .bsp format is not supported, yet.")
                else:
                    print(f'"{branch}" is not a known branch, trying "{close_matches[0]}"...')
                    branch = close_matches[0]
            branch = branches.by_name[branch]
        else:
            if bsp_version not in branches.by_version:
                # TODO: Give a warning and use a default
                raise NotImplementedError(f"{file_magic} version {bsp_version} is not supported")
            branch = branches.by_version[bsp_version]
            return BspVariant(branch, filename, autoload=True)
