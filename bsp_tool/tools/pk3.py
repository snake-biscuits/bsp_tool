import fnmatch
import zipfile


class Pk3(zipfile.Zipfile):
    """Quake & CoD .bsps are stored in .pk3 files, which are renamed .zips"""
    def extract_match(self, pattern="*.bsp", path=None):
        for filename in self.search(pattern):
            self.extract(filename, path)

    def search(self, pattern="*.bsp"):
        return fnmatch.filter(self.namelist(), pattern)
