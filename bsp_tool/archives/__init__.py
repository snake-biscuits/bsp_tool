"""Tools for opening and searching archives containing game assets (specifically .bsp)"""
__all__ = [
    "alcohol", "base", "bluepoint", "cdrom", "gearbox", "golden_hawk",
    "id_software", "infinity_ward", "ion_storm", "mame", "nexon", "padus",
    "pi_studios", "pkware", "respawn", "sega", "utoplanet", "valve"]

import fnmatch
import os
from typing import Dict, List

from . import alcohol  # Mds
from . import base
from . import bluepoint  # Bpk
from . import cdrom  # Iso
from . import gearbox  # Nightfire007
from . import golden_hawk  # Cue
from . import id_software  # Pak & Pk3
from . import infinity_ward  # FastFile & Iwd
from . import ion_storm  # Dat & Pak
from . import mame  # Chd
from . import nexon  # Hfs, PakFile & Pkg
from . import padus  # Cdi
from . import pi_studios  # Bpk
from . import pkware  # Zip
from . import respawn  # RPak & Vpk
from . import sega  # Gdi & GDRom
from . import utoplanet  # Apk
from . import valve  # Vpk


with_extension = {
    "*.007": gearbox.Nightfire007,
    "*.apk": utoplanet.Apk,
    "*.bpk": bluepoint.Bpk,  # OR pi_studios.Bpk
    "*.cdi": padus.Cdi,
    "*.chd": mame.Chd,
    "*.cue": golden_hawk.Cue,
    "*.dat": ion_storm.Dat,
    "*.ff": infinity_ward.FastFile,
    "*.gdi": sega.Gdi,
    "*.hfs": nexon.Hfs,
    "*.iso": cdrom.Iso,
    "*.iwd": infinity_ward.Iwd,
    "*.mds": alcohol.Mds,
    "*.pak": id_software.Pak,  # OR ion_storm.Pak
    "*.pk3": id_software.Pk3,
    "*.pkg": nexon.Pkg,
    "*.rpak": respawn.rpak.RPak,
    "*.vpk": valve.Vpk,
    "*.zip": pkware.Zip,
    "*_dir.vpk": respawn.Vpk}  # OR valve.Vpk
# NOTE: sega.GDRom extends other disc-images (mame.Chd, padus.Cdi & sega.Gdi)
# NOTE: nexon.PakFile only exists as the PAKFILE lump of NexonBsp


# batch operations
# TODO: ignore r".*_[0-9]+\.vpk" when looking for respawn.Vpk
# -- this also applies for some valve.Vpk
def search_folder(archive_class: base.Archive, path: str, pattern: str = "*.bsp") -> Dict[str, List[str]]:
    """check all archives in this folder for files matching pattern"""
    findings = dict()
    for archive_filename in fnmatch.filter(os.listdir(path), archive_class.ext):
        archive_file = archive_class(os.path.join(path, archive_filename))
        matching_files = [f for f in archive_file.search(pattern)]
        if len(matching_files) != 0:
            findings[archive_filename] = matching_files
    return findings


def extract_folder(archive_class: base.Archive, path: str, pattern: str = "*.bsp", to_path: str = None):
    """extract all files in archives in this folder which match pattern"""
    for archive_filename in fnmatch.filter(os.listdir(path), archive_class.ext):
        archive_file = archive_class(os.path.join(path, archive_filename))
        archive_file.extract_match(pattern=pattern, to_path=to_path)
