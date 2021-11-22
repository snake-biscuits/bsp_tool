"""A library for .bsp file analysis & modification"""
__all__ = ["base", "branches", "load_bsp", "lumps", "tools",
           "ArkaneBsp", "GoldSrcBsp", "IdTechBsp", "InfinityWardBsp",
           "QuakeBsp", "RavenBsp", "RespawnBsp", "RitualBsp", "ValveBsp"]

import os
from types import ModuleType

from . import base  # base.Bsp base class
from . import branches  # all known .bsp variant definitions
from . import lumps
from .arkane import ArkaneBsp
from .id_software import QuakeBsp, IdTechBsp
from .infinity_ward import InfinityWardBsp
from .raven import RavenBsp
from .respawn import RespawnBsp
from .ritual import RitualBsp
from .valve import GoldSrcBsp, ValveBsp


BspVariant_from_file_magic = {b"2015": RitualBsp,
                              b"EF2!": RitualBsp,
                              b"FAKK": RitualBsp,
                              b"IBSP": IdTechBsp,  # or InfinityWardBsp
                              b"rBSP": RespawnBsp,
                              b"RBSP": RavenBsp,
                              b"VBSP": ValveBsp}  # and ArkaneBsp
# NOTE: if no file_magic is present, options are:
# - GoldSrcBsp
# - QuakeBsp
# - 256-bit XOR encoded Tactical Intervention .bsp

GoldSrc_versions = {*branches.valve.goldsrc.GAME_VERSIONS.values(),
                    *branches.gearbox.blue_shift.GAME_VERSIONS.values(),
                    *branches.gearbox.nightfire.GAME_VERSIONS.values()}
InfinityWard_versions = {v for s in branches.infinity_ward.scripts for v in s.GAME_VERSIONS.values()}
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
    # identify BspVariant
    if filename.lower().endswith(".d3dbsp"):  # CoD2
        assert file_magic == b"IBSP", "Mystery .d3dbsp!"
        assert version in InfinityWard_versions, "Unexpected .d3dbsp format version!"
        BspVariant = InfinityWardBsp
    elif filename.lower().endswith(".bsp"):
        if file_magic not in BspVariant_from_file_magic:  # Quake / GoldSrc
            version = int.from_bytes(file_magic, "little")
            file_magic = None
            if version in Quake_versions:
                BspVariant = QuakeBsp
            elif version in GoldSrc_versions:
                BspVariant = GoldSrcBsp
            else:
                raise NotImplementedError("TODO: Check if encrypted Tactical Intervention .bsp")
        else:
            if file_magic == b"IBSP" and version in InfinityWard_versions:  # CoD
                BspVariant = InfinityWardBsp
            elif file_magic == b"VBSP" and version > 0xFFFF:  # Dark Messiah
                version = (version & 0xFFFF, version >> 16)  # major, minor
                BspVariant = ArkaneBsp
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
