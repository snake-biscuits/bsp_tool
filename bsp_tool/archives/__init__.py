"""Tools for opening and searching archives containing game assets (specifically .bsp)"""
__all__ = [
    "base", "bluepoint", "cdrom", "gearbox", "id_software", "infinity_ward",
    "nexon", "padus", "pi_studios", "respawn", "sega", "utoplanet", "valve"]
import fnmatch
import os
from typing import Dict, List

from . import base
from . import bluepoint  # Bpk
from . import cdrom  # Iso, but indirectly
from . import gearbox  # Nightfire007
from . import id_software  # Pak & Pk3
from . import infinity_ward  # Iwd & FastFile
from . import nexon  # Hfs & Pkg
from . import padus  # Cdi
from . import pi_studios  # Bpk
from . import respawn  # RPak & Vpk
from . import sega  # GDRom
from . import utoplanet  # Apk
from . import valve  # Vpk


# batch operations
# TODO: ignore r".*_[0-9]+\.vpk"
def search_folder(archive_class, path, pattern="*.bsp") -> Dict[str, List[str]]:
    findings = dict()
    for archive_filename in fnmatch.filter(os.listdir(path), archive_class.ext):
        archive_file = archive_class(os.path.join(path, archive_filename))
        matching_files = [f for f in archive_file.search(pattern)]
        if len(matching_files) != 0:
            findings[archive_filename] = matching_files
    return findings


def extract_folder(archive_class, path, pattern="*.bsp", to_path=None):
    for archive_filename in fnmatch.filter(os.listdir(path), archive_class.ext):
        archive_file = archive_class(os.path.join(path, archive_filename))
        archive_file.extract_match(pattern=pattern, to_path=to_path)