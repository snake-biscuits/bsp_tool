"""A library for .bsp file analysis & modification"""
__all__ = ["base", "branches", "load_bsp", "tools", "IdTechBsp", "D3DBsp", "ValveBsp", "RespawnBsp"]

from types import ModuleType
from typing import Union

from . import base  # base.Bsp base class
from . import branches  # all known .bsp variant definitions
from . import tools  # tools for studying .bsps
from .id_software import IdTechBsp
from .infinity_ward import D3DBsp
from .respawn import RespawnBsp
from .valve import ValveBsp


bsp_variant_by_file_magic = {b"IBSP": IdTechBsp,
                             b"rBSP": RespawnBsp,
                             b"VBSP": ValveBsp}


def load_bsp(filename: str, branch: Union[str, ModuleType] = "unknown"):
    # TODO: make legible
    # identify developer variant
    BspVariant = None
    if filename.endswith(".d3dbsp"):
        BspVariant = D3DBsp
    elif not filename.endswith(".bsp"):
        raise RuntimeError(f"{filename} is not a .bsp file!")
    with open(filename, "rb") as bsp_file:  # assuming the requested file exists
        file_magic = bsp_file.read(4)
        bsp_version = int.from_bytes(bsp_file.read(4), "little")  # not always in this position
    if BspVariant != D3DBsp:  # D3DBsp indicated by extension only
        BspVariant = bsp_variant_by_file_magic[file_magic]
    # identify game variant
    if isinstance(branch, ModuleType):
        pass  # goto return
    elif branch.lower() == "unknown":  # assuming branch is a string
        # guess .bsp format from version
        if bsp_version not in branches.by_version:
            raise NotImplementedError(f"{file_magic} version {bsp_version} is not supported")
            # ^ you can avoid this error by forcing a branch:
            # - load_bsp("tests/maps/test2.bsp", branches.valve.orange_box)
        branch = branches.by_version[bsp_version]
    else:  # look up branch by name
        if branch not in branches.by_name:
            raise NotImplementedError(f"{branch} .bsp format is not supported, yet.")
        branch = branches.by_name[branch]
    return BspVariant(branch, filename, autoload=True)
