import fnmatch
import os
from typing import List, Tuple


class Archive:
    ext = None

    def extract(self, filename, to_path=None):
        if filename not in self.namelist():
            raise FileNotFoundError(f"Couldn't find {filename!r} to extract")
        to_path = "./" if to_path is None else to_path
        out_filename = os.path.join(to_path, filename)
        os.makedirs(os.path.dirname(out_filename), exist_ok=True)
        with open(out_filename, "rb") as out_file:
            out_file.write(self.read(filename))

    def extract_all(self, to_path=None):
        for filename in self.namelist():
            self.extract(filename, to_path)

    def extract_all_matching(self, pattern="*.bsp", to_path=None, case_sensitive=False):
        for filename in self.search(pattern, case_sensitive):
            self.extract(filename, to_path)

    def listdir(self, folder: str) -> List[str]:
        def path_tuple(path: str) -> Tuple[str]:
            return tuple(path.replace("\\", "/").strip("/").split("/"))
        if folder.replace("\\", "/") in "./":
            return self.namelist()
        folder_tuple = path_tuple(folder)
        namelist_tuples = map(path_tuple, self.namelist())
        return [tuple_[-1] for tuple_ in namelist_tuples if tuple_[:-1] == folder_tuple]

    def search(self, pattern="*.bsp", case_sensitive=False):
        pattern = pattern if case_sensitive else pattern.lower()
        namelist = self.namelist() if case_sensitive else [fn.lower() for fn in self.namelist()]
        return fnmatch.filter(namelist, pattern)
