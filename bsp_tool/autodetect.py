import collections
import fnmatch
import io
import os
from types import ModuleType
from typing import Dict, Tuple

from . import archives  # base.Archive & with_extension
from . import base  # base.Bsp base class
from . import branches  # all known .bsp variant definitions
from .id_software import FusionBsp, IdTechBsp, QbismBsp
from .id_software import QuakeBsp, Quake64Bsp, ReMakeQuakeBsp
from .infinity_ward import D3DBsp, InfinityWardBsp
from .raven import RavenBsp
from .respawn import RespawnBsp
from .ritual import RitualBsp  # TODO: SinBsp
from .nexon import NexonBsp
from .valve import GoldSrcBsp, ValveBsp
from .wild_tangent import Genesis3DBsp


#########
# Hints #
#########


Hints = Dict[str, object]
# ^ {"*.zip": archives.pkware.Zip, "*.d3dbsp": infinity_ward.D3DBsp}


# NOTE: you should only need to sort your hints once
def sorted_hints(hints: Hints) -> collections.OrderedDict:
    """'sophisticated' fnmatch pattern sorter"""
    # NOTE: overlap isn't relevant
    # -- just make sure the most specific patterns come first
    filenames = dict()
    folders = dict()
    complex_hints = dict()
    broad_hints = dict()

    for pattern in hints:
        if "*" not in pattern:  # folder/filename.ext
            filenames[pattern] = hints[pattern]
        elif pattern.endswith("*"):  # folder/*
            folders[pattern] = hints[pattern]
        elif pattern.startswith("*"):  # *.ext
            broad_hints[pattern] = hints[pattern]
        else:  # folder/*.ext
            complex_hints[pattern] = hints[pattern]

    return collections.OrderedDict({
        **filenames,
        **folders,
        **complex_hints,
        **broad_hints})


def guess_with_hints(filename: str, hints: Hints) -> object:
    for pattern in hints:
        if fnmatch.fnmatch(filename, pattern):
            return hints[pattern]
    else:  # if nothing matches it's the caller's problem
        return None


################
# ArchiveClass #
################


# TODO: test:
#  - [x] .bsp not inside archive (local)
#  - [x] .bsp inside archive (Quake/PAK0.PAK/maps/e1m1.bsp) (relative dir)
#  - [ ] .bsp inside nested archives
# BROKEN:
#  - [ ] linux path starting at root ("/")
#  - [ ] windows path starting with a drive ("C://")
# NOTE: could try archives.base.path_tuple, but it conflates "./" with "/"
# -- "../" is also likely to break, we should make that explicit
def naps(full_path: str, hints: Hints = dict(), parent_archive=None) -> Tuple[str]:
    """Nested Archive Path Splitter"""
    archive_hints = sorted_hints({**archives.with_extension, **hints})
    split_path = full_path.replace("\\", "/").split("/")
    filename = ""
    if parent_archive is None:  # os filesystem
        print("! scanning OS files")
        while len(split_path) > 0:
            filename = "/".join([filename, split_path.pop(0)]) if filename != "" else split_path.pop(0)
            print(filename)  # DEBUG
            assert os.path.exists(filename), f"{filename!r} does not exist"
            if os.path.isfile(filename) and len(split_path) > 0:
                archive_class = guess_with_hints(filename, archive_hints)
                assert archive_class is not None, f"couldn't find ArchiveClass for {filename!r}"
                archive = archive_class.from_file(filename)
                print(f"* recursing into {archive}")
                return (filename, *naps("/".join(split_path), hints, archive))
        return (filename,)
    else:  # archive filesystem
        print("! scanning archive files")
        while len(split_path) > 0:
            filename = "/".join([filename, split_path.pop(0)]) if filename != "" else split_path.pop(0)
            print(filename)  # DEBUG
            assert parent_archive.path_exists(filename)
            if parent_archive.is_file(filename):
                if len(split_path) > 0:
                    archive_class = guess_with_hints(filename, archive_hints)
                    assert archive_class is not None, f"couldn't find ArchiveClass for {filename!r}"
                    archive = archive_class.from_archive(parent_archive, filename)
                    print(f"* recursing into {archive}")
                    return (filename, *naps("/".join(split_path), hints, archive))
        return (filename,)


# TODO: step down through the NAP to get the file


############
# BspClass #
############


# TODO: clues based on parent archive / folders in path (e.g. "baseq3")
BspClass_for_pattern = {
    "*.d3dbsp": D3DBsp,
    "*.i3d/*.bsp": InfinityWardBsp,
    "*.pk3/*.bsp": IdTechBsp,
    "*_dir.vpk/*.bsp": ValveBsp}  # OR RespawnBsp
# TODO: bzip decompression for "*.bsp.bz2" ValveBsps


BspClass_for_magic = {
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
    b"RBSP": RavenBsp,  # OR SinBsp
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


# TODO: use Hints to help guess BspClass branch
def guess_from_archive_file(filename: str, archive, force_branch: ModuleType = None) -> base.Bsp:
    # TODO: use BspClass.from_archive to link associated files
    if filename not in archive.namelist():
        raise FileNotFoundError(f"couldn't find {filename!r} in archive: {archive!r}'")
    return guess_from_bytes(filename, archive.read(filename), force_branch)


def guess_from_filename(filename: str, force_branch: ModuleType = None) -> base.Bsp:
    # verify path
    if not os.path.exists(filename):
        raise FileNotFoundError(f".bsp file '{filename}' does not exist.")
    elif os.path.getsize(filename) == 0:  # HL2/ d2_coast_02.bsp
        raise RuntimeError(f"{filename} is an empty file")
    with open(filename, "rb") as bsp_file:
        return guess_from_stream(filename, bsp_file, force_branch)


def guess_from_stream(filename: str, bsp_file: io.BytesIO, force_branch: ModuleType = None) -> base.Bsp:
    """Calculate and return the correct base.Bsp sub-class for the given .bsp"""
    # parse header
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
    # identify BspClass
    if filename.lower().endswith(".d3dbsp"):  # CoD2 & CoD4
        assert file_magic == b"IBSP", "Mystery .d3dbsp!"
        assert version in InfinityWard_versions, "Unexpected .d3dbsp format version!"
        if version >= branches.infinity_ward.modern_warfare.BSP_VERSION:
            BspClass = D3DBsp
        else:
            BspClass = InfinityWardBsp
    elif filename.lower().endswith(".bsp"):
        if file_magic not in BspClass_for_magic:  # Quake / GoldSrc
            version = int.from_bytes(file_magic, "little")
            if version in Quake_versions:
                BspClass = QuakeBsp
                file_magic = None
            elif version in GoldSrc_versions:
                BspClass = GoldSrcBsp
                file_magic = None
            else:
                # TODO: check for encrypted Tactical Intervention .bsp
                raise NotImplementedError(f"Unknown file_magic: {file_magic}")
        else:
            if file_magic == b"IBSP" and version in InfinityWard_versions:  # early CoD
                BspClass = InfinityWardBsp
            elif version in Nexon_versions:  # CS:O2
                BspClass = NexonBsp
            else:
                BspClass = BspClass_for_magic[file_magic]
    else:  # invalid extension
        raise RuntimeError(f"{filename} is not a .bsp file!")
    # identify branch script
    if force_branch is None:
        branch_script = branches.identify[(file_magic, version)]
    else:
        branch_script = force_branch
    # TODO: warn on branches w/ overlapping (magic, version)
    # -- could try to resolve w/ sprp version
    # TODO: ata4's bspsrc uses unique entity classnames to identify branches
    # -- need this for identifying variants with overlapping identifiers
    return BspClass.from_file(branch_script, filename)  # might raise errors


def guess_from_bytes(filename: str, raw_bsp: bytes, force_branch: ModuleType = None) -> base.Bsp:
    return guess_from_stream(filename, io.BytesIO(raw_bsp), force_branch)
