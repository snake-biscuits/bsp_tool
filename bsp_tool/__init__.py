"""A library for .bsp file analysis & modification"""
__all__ = ["base", "branches", "load_bsp", "lumps",
           "D3DBsp", "FusionBsp", "Genesis3DBsp", "GoldSrcBsp", "IdTechBsp",
           "InfinityWardBsp", "QbismBsp", "QuakeBsp", "Quake64Bsp", "RavenBsp",
           "ReMakeQuakeBsp", "RespawnBsp", "RitualBsp", "ValveBsp"]

import os
from types import ModuleType

from . import base  # base.Bsp base class
from . import branches  # all known .bsp variant definitions
from . import lumps
from .id_software import FusionBsp, IdTechBsp, QbismBsp, QuakeBsp, Quake64Bsp, ReMakeQuakeBsp
from .infinity_ward import D3DBsp, InfinityWardBsp
from .raven import RavenBsp
from .respawn import RespawnBsp
from .ritual import RitualBsp
from .nexon import NexonBsp
from .valve import GoldSrcBsp, ValveBsp
from .wild_tangent import Genesis3DBsp


BspVariant_for_magic = {
    b" 46Q": Quake64Bsp,
    b"2015": RitualBsp,
    b"2PSB": ReMakeQuakeBsp,
    b"BSP2": ReMakeQuakeBsp,
    b"EALA": RitualBsp,
    b"EF2!": RitualBsp,
    b"FAKK": RitualBsp,
    b"FBSP": FusionBsp,
    b"GBSP": Genesis3DBsp,
    b"IBSP": IdTechBsp,  # OR InfinityWardBsp OR D3DBsp
    b"PSBr": RespawnBsp,  # Xbox360
    b"PSBV": ValveBsp,  # Xbox360
    b"QBSP": QbismBsp,
    b"rBSP": RespawnBsp,
    b"RBSP": RavenBsp,
    b"VBSP": ValveBsp}  # OR NexonBsp
# NOTE: if no file_magic is present:
# - QuakeBsp
# - GoldSrcBsp
# - 256-bit XOR encoded Tactical Intervention .bsp

# detect GoldSrcBsp
GoldSrc_versions = {
    *branches.valve.goldsrc.GAME_VERSIONS.values(),
    *branches.gearbox.blue_shift.GAME_VERSIONS.values(),
    *branches.gearbox.nightfire.GAME_VERSIONS.values()}
# detect InfinityWardBsp / D3DBsp
InfinityWard_versions = {v for s in branches.infinity_ward.scripts for v in s.GAME_VERSIONS.values()}
# detect NexonBsp
Nexon_versions = {
    *branches.nexon.cso2.GAME_VERSIONS.values(),
    *branches.nexon.cso2_2018.GAME_VERSIONS.values()}
# NOTE: cso2 & cso2_2018 are both v100, but cso2_2018 will not use the LIGHTING lump
# -- cso2_2018 also uses around 4x as many bytes-per-texel for lightmaps
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
        if file_magic in (b" 46Q", b"2PSB", b"BSP2"):
            version = None
        elif file_magic == b"\0" * 4:  # might be Genesis3DBsp
            try:  # GBSP_CHUNK_HEADER
                assert int.from_bytes(bsp_file.read(4), "little") == 0x1C
                assert int.from_bytes(bsp_file.read(4), "little") == 0x01
                file_magic = bsp_file.read(4)
                bsp_file.seek(4, 1)  # skip 4 trailing null bytes
                version = int.from_bytes(bsp_file.read(4), "little")
            except AssertionError:
                raise RuntimeError("bsp file begins with null bytes")
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
        if file_magic not in BspVariant_for_magic:  # Quake / GoldSrc
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
        else:
            if file_magic == b"IBSP" and version in InfinityWard_versions:  # early CoD
                BspVariant = InfinityWardBsp
            elif version in Nexon_versions:  # CS:O2
                BspVariant = NexonBsp
            else:
                BspVariant = BspVariant_for_magic[file_magic]
    else:  # invalid extension
        raise RuntimeError(f"{filename} is not a .bsp file!")
    # identify branch script
    if branch_script is None:
        branch_script = branches.identify[(file_magic, version)]
    # TODO: ata4's bspsrc uses unique entity classnames to identify branches
    # -- need this for identifying variants with overlapping identifiers
    return BspVariant(branch_script, filename, autoload=True)  # might raise errors


# TODO: write a generator that walks a path for .bsps, including inside .pk3, .bz2, .iwd & .zip
# -- this should greatly simplify testing theories / support against whole games
# TODO: allow loading .bsp files from bytestreams
# -- base.Bsp @classmethod .from_stream(stream: bytes | io.BytesIO) alternate __init__?
# -- requires faking both self.folder (need to hook to some ZipFile method) & overriding self.file
