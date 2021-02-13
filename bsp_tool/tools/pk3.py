"""Tools for opening and searching .pk3 & .iwd archives"""
import fnmatch
import os
import zipfile


class Pk3(zipfile.ZipFile):
    """Quake & Call of Duty 1 .bsps are stored in .pk3 files, which are basically .zip archives"""
    def extract_match(self, pattern="*.bsp", path=None):
        for filename in self.search(pattern):
            self.extract(filename, path)

    def search(self, pattern="*.bsp"):
        return fnmatch.filter(self.namelist(), pattern)


class Iwd(Pk3):
    """Call of Duty 2 & 4 store data in .iwd files, these also appear to be .zip archives"""


def search_folder(folder, pattern="*.bsp", archive="*.pk3"):
    for pk3_filename in fnmatch.filter(os.listdir(folder), archive):
        print(pk3_filename)
        pk3 = Pk3(os.path.join(folder, pk3_filename))
        print(*["\t" + bsp for bsp in pk3.search(pattern)], sep="\n", end="\n\n")
