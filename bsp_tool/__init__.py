"""A library for .bsp file analysis & modification"""
__all__ = ["base", "branches", "load_bsp", "lumps", "tools",
           "D3DBsp", "GoldSrcBsp", "IdTechBsp", "InfinityWardBsp",
           "QuakeBsp", "RavenBsp", "RespawnBsp", "RitualBsp", "ValveBsp"]

import os
from types import ModuleType

from . import base  # base.Bsp base class
from . import branches  # all known .bsp variant definitions
from . import lumps
from .id_software import QuakeBsp, IdTechBsp
from .infinity_ward import InfinityWardBsp, D3DBsp
from .raven import RavenBsp
from .respawn import RespawnBsp
from .ritual import RitualBsp
from .valve import GoldSrcBsp, ValveBsp


BspVariant_from_file_magic = {b"2015": RitualBsp,
                              b"EF2!": RitualBsp,
                              b"FAKK": RitualBsp,
                              b"IBSP": IdTechBsp,  # + InfinityWardBsp + D3DBsp
                              b"rBSP": RespawnBsp,
                              b"RBSP": RavenBsp,
                              b"VBSP": ValveBsp}
# NOTE: if no file_magic is present:
# - QuakeBsp
# - GoldSrcBsp
# - 256-bit XOR encoded Tactical Intervention .bsp

# detect GoldSrcBsp
GoldSrc_versions = {*branches.valve.goldsrc.GAME_VERSIONS.values(),
                    *branches.gearbox.blue_shift.GAME_VERSIONS.values(),
                    *branches.gearbox.nightfire.GAME_VERSIONS.values()}
# detect InfinityWardBsp / D3DBsp
InfinityWard_versions = {v for s in branches.infinity_ward.scripts for v in s.GAME_VERSIONS.values()}
# detect QuakeBsp
Quake_versions = {*branches.id_software.quake.GAME_VERSIONS.values()}


def load_bsp(filename: str, branch_script: ModuleType = None) -> base.Bsp:
    """Calculate and return the correct base.Bsp sub-class for the given .bsp"""
    # TODO: OPTION: use filepath to guess game / branch
    # verify path
    if not os.path.exists(filename):
        raise FileNotFoundError(f".bsp file '{filename}' does not exist.")
    elif os.path.getsize(filename) == 0:  # HL2/ d2_coast_02.bsp
        raise RuntimeError(f"{filename} is an empty file")
    # parse header
    with open(filename, "rb") as bsp_file:
        file_magic = bsp_file.read(4)
        version = int.from_bytes(bsp_file.read(4), "little")
        if version > 0xFFFF:
            version = (version & 0xFFFF, version >> 16)  # major, minor
    # identify BspVariant
    if filename.lower().endswith(".d3dbsp"):  # CoD2 & CoD4
        assert file_magic == b"IBSP", "Mystery .d3dbsp!"
        assert version in InfinityWard_versions, "Unexpected .d3dbsp format version!"
        if version >= branches.infinity_ward.call_of_duty4.BSP_VERSION:
            BspVariant = D3DBsp
        else:
            BspVariant = InfinityWardBsp
    elif filename.lower().endswith(".bsp"):
        if file_magic not in BspVariant_from_file_magic:  # Quake / GoldSrc
            version = int.from_bytes(file_magic, "little")
            file_magic = None
            if version in Quake_versions:
                BspVariant = QuakeBsp
            elif version in GoldSrc_versions:
                BspVariant = GoldSrcBsp
            elif file_magic == b"BSP2":
                raise NotImplementedError("BSP2 format is not yet supported")
            elif file_magic == b"FBSP":
                raise NotImplementedError("FBSP format is not yet supported")
            else:
                raise NotImplementedError("TODO: Check if encrypted Tactical Intervention .bsp")
        else:
            if file_magic == b"IBSP" and version in InfinityWard_versions:  # CoD
                BspVariant = InfinityWardBsp
            else:
                BspVariant = BspVariant_from_file_magic[file_magic]
    else:  # invalid extension
        raise RuntimeError(f"{filename} is not a .bsp file!")
    # identify branch script
    # TODO: ata4's bspsrc uses unique entity classnames to identify branches
    # -- need this for identifying variants with overlapping versions
    # -- e.g. (b"VBSP", 20) & (b"VBSP", 21)
    if branch_script is None:
        branch_script = branches.script_from_file_magic_and_version[(file_magic, version)]
    return BspVariant(branch_script, filename, autoload=True)  # might raise errors
