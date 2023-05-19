import fnmatch


class Archive:
    def extract_match(self, pattern="*.bsp", path=None):
        for filename in self.search(pattern):
            self.extract(filename, path)

    def search(self, pattern="*.bsp"):
        return fnmatch.filter(self.namelist(), pattern)
