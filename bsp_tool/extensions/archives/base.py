import fnmatch


class Archive:
    ext = None

    def extract_match(self, pattern="*.bsp", to_path=None):
        for filename in self.search(pattern):
            self.extract(filename, to_path)

    def search(self, pattern="*.bsp"):
        return fnmatch.filter(self.namelist(), pattern)
