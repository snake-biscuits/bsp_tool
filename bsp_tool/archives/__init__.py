"""Tools for opening and searching archives containing game assets (specifically .bsp)"""
__all__ = [
    "base", "bluepoint", "gearbox", "id_software", "infinity_ward", "nexon",
    "pi_studios", "respawn", "utoplanet", "valve"]
import fnmatch
import os
from typing import Dict, List

from . import base
from . import bluepoint
from . import gearbox
from . import id_software
from . import infinity_ward
from . import nexon
from . import pi_studios
from . import respawn
from . import utoplanet
from . import valve


# NOTE: you could access raw .bsp files with ZipFile.read("filename.bsp"), but bsp_tool doesn't accept open files
# -- e1m1 = IdTechBsp(quake, "maps/e1m1.bsp", autoload=False)
# -- e1m1.file = pak0.read("maps/e1m1.bsp")
# -- e1m1._preload()
# NOTE: would need to develop a new method of checking related files


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
