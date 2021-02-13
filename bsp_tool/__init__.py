"""A library for .bsp file analysis & modification"""
__all__ = ["base", "branches", "load_bsp", "tools", "IdTechBsp", "D3DBsp", "ValveBsp", "RespawnBsp"]

from types import ModuleType
from typing import Union

from . import base  # base.Bsp base class
from . import branches  # all known .bsp variant definitions
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
        # NOTE: Call of Duty 1 has .bsp files in .pk3 archives
        # -- later games instead use .d3dbsp in .iwd archives
        BspVariant = D3DBsp
    elif not filename.endswith(".bsp"):
        raise RuntimeError(f"{filename} is not a .bsp file!")
    # -- check file-magic & bsp format version
    with open(filename, "rb") as bsp_file:
        file_magic = bsp_file.read(4)
        bsp_version = int.from_bytes(bsp_file.read(4), "little")  # not always in this position
    # -- get engine branch from file magic (D3DBsp is IBSP but also .d3dbsp)
    if BspVariant != D3DBsp:
        BspVariant = bsp_variant_by_file_magic[file_magic]
        if file_magic == b"IBSP" and bsp_version == branches.infinity_ward.call_of_duty1.BSP_VERSION:
            BspVariant = D3DBsp  # CoD 1 uses the .bsp extension & b"IBSP" file-magic
    # -- choose the branch script
    if isinstance(branch, ModuleType):
        pass  # use the provided branch script
    # guess .bsp format from version
    elif branch.lower() == "unknown":
        branch = branch.lower()
        if bsp_version not in branches.by_version:
            raise NotImplementedError(f"{file_magic} version {bsp_version} is not supported")
            # ^ if you got this error, force a branch!
            # e.g. >>> load_bsp("tests/maps/test2.bsp", branches.valve.orange_box)
        branch = branches.by_version[bsp_version]
    # lookup branch by name
    else:
        branch = branch.lower()
        if branch not in branches.by_name:
            raise NotImplementedError(f"{branch} .bsp format is not supported, yet.")
        branch = branches.by_name[branch]
    return BspVariant(branch, filename, autoload=True)
