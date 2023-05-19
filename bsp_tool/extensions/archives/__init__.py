"""Tools for opening and searching .iwd & .pk3 archives"""
__all__ = ["base", "bluepoint", "gearbox", "id_software", "infinity_ward",
           "nexon", "respawn", "utoplanet", "valve"]
import fnmatch
import os

from . import base
# zipfile.ZipFile-like archive interfaces, grouped by developer
from . import bluepoint  # Bpk
from . import gearbox  # Nightfire007
from . import id_software  # Pak Pk3
from . import infinity_ward  # Iwd FastFile
from . import nexon  # Pkg Hfs
from . import respawn  # Vpk
from . import utoplanet  # Apk
from . import valve  # Vpk


# TODO: Bluepoint .bpk loader (Titanfall for the Xbox360)

# NOTE: you could access raw .bsp files with Zipfile.read("filename.bsp"), but bsp_tool doesn't accept open files
# -- e1m1 = IdTechBsp(quake, "maps/e1m1.bsp", autoload=False)
# -- e1m1.file = pak0.read("maps/e1m1.bsp")
# -- e1m1._preload()


# batch operations
# TODO: pass in archive classes, not just filename filters
def search_folder(folder, pattern="*.bsp", archive="*.pk3"):
    for pk3_filename in fnmatch.filter(os.listdir(folder), archive):
        print(pk3_filename)
        pk3 = id_software.Pk3(os.path.join(folder, pk3_filename))
        print(*["\t" + bsp for bsp in pk3.search(pattern)], sep="\n", end="\n\n")


def extract_folder(folder, pattern="*.bsp", path=None, archive="*.pk3"):
    for archive_filename in fnmatch.filter(os.listdir(folder), archive):
        archive_file = id_software.Pk3(os.path.join(folder, archive_filename))  # works on any zip-like format
        archive_file.extract_match(pattern=pattern, path=path)
