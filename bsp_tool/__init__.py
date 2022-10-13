"""A library for .bsp file analysis & modification"""
__all__ = ["base", "branches", "load_bsp", "lumps", "D3DBsp", "FusionBsp",
           "GoldSrcBsp", "IdTechBsp", "InfinityWardBsp", "QuakeBsp", "RavenBsp",
           "ReMakeQuakeBsp", "RespawnBsp", "RitualBsp", "ValveBsp"]

import os
from types import ModuleType

from . import base  # base.Bsp base class
from . import branches  # all known .bsp variant definitions
from . import lumps
from .id_software import FusionBsp, IdTechBsp, QuakeBsp, ReMakeQuakeBsp
from .infinity_ward import D3DBsp, InfinityWardBsp
from .raven import RavenBsp
from .respawn import RespawnBsp
from .ritual import RitualBsp
from .valve import GoldSrcBsp, ValveBsp


BspVariant_from_file_magic = {b"2015": RitualBsp,
                              b"2PSB": ReMakeQuakeBsp,
                              b"BSP2": ReMakeQuakeBsp,
                              b"EALA": RitualBsp,
                              b"EF2!": RitualBsp,
                              b"FAKK": RitualBsp,
                              b"FBSP": FusionBsp,
                              b"IBSP": IdTechBsp,  # + InfinityWardBsp + D3DBsp
                              b"PSBr": RespawnBsp,  # Xbox360
                              b"PSBV": ValveBsp,  # Xbox360
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
        if file_magic in (b"2PSB", b"BSP2"):
            version = None
        # elif file_magic == b"BSP2":
        #     return ReMakeQuakeBsp(branches.id_software.remake_quake, filename)
        # endianness
        elif file_magic in (b"PSBr", b"PSBV"):  # big endian
            version = int.from_bytes(bsp_file.read(4), "big")
        else:
            version = int.from_bytes(bsp_file.read(4), "little")
        if version is not None and version > 0xFFFF:  # 2 part version
            version = (version & 0xFFFF, version >> 16)  # major, minor
    # identify BspVariant
    if filename.lower().endswith(".d3dbsp"):  # CoD2 & CoD4
        assert file_magic == b"IBSP", "Mystery .d3dbsp!"
        assert version in InfinityWard_versions, "Unexpected .d3dbsp format version!"
        if version >= branches.infinity_ward.modern_warfare.BSP_VERSION:
            BspVariant = D3DBsp
        else:
            BspVariant = InfinityWardBsp
    elif filename.lower().endswith(".bsp"):
        if file_magic not in BspVariant_from_file_magic:  # Quake / GoldSrc
            version = int.from_bytes(file_magic, "little")
            if version in Quake_versions:
                BspVariant = QuakeBsp
                file_magic = None
            elif version in GoldSrc_versions:
                BspVariant = GoldSrcBsp
                file_magic = None
            else:
                # TODO: check for encrypted Tactical Intervention .bsp
                raise NotImplementedError(f"Unknown file_magic: {file_magic}")
        else:  # Call of Duty
            if file_magic == b"IBSP" and version in InfinityWard_versions:
                BspVariant = InfinityWardBsp
            else:
                BspVariant = BspVariant_from_file_magic[file_magic]
    else:  # invalid extension
        raise RuntimeError(f"{filename} is not a .bsp file!")
    # TODO: ata4's bspsrc uses unique entity classnames to identify branches
    # -- need this for identifying variants with overlapping identifiers
    # identify branch script
    if branch_script is None:
        branch_script = branches.script_from_file_magic_and_version[(file_magic, version)]
    return BspVariant(branch_script, filename, autoload=True)  # might raise errors


# TODO: write a generator that walks a path for .bsps, including inside .pk3, .bz2, .iwd & .zip
# -- this should greatly simplify testing theories / support against whole games
# TODO: allow loading .bsp files from bytestreams
# -- base.Bsp @classmethod .from_stream(stream: bytes | io.BytesIO) alternate __init__?
# -- requires faking both self.folder (need to hook to some ZipFile method) & overriding self.file
