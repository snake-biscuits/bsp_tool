from __future__ import annotations
import fnmatch
import io
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

    # TODO: isdir, isfile & tree methods for exploring files

    def namelist(self) -> List[str]:
        raise NotImplementedError("ArchiveClass has not defined .namelist()")

    def read(self) -> bytes:
        raise NotImplementedError("ArchiveClass has not defined .read()")

    def search(self, pattern="*.bsp", case_sensitive=False):
        pattern = pattern if case_sensitive else pattern.lower()
        namelist = self.namelist() if case_sensitive else [fn.lower() for fn in self.namelist()]
        return fnmatch.filter(namelist, pattern)

    # TODO: mount & unmount methods for attaching "external files" to ArchiveClass

    @classmethod
    def from_archive(cls, parent_archive: Archive, filename: str) -> Archive:
        """for ArchiveClasses composed of multiple files"""
        # e.g. sega.Gdi tracks or respawn.Vpk data vpks
        return cls.from_bytes(parent_archive.read(filename))

    @classmethod
    def from_bytes(cls, raw_archive: bytes) -> Archive:
        return cls.from_stream(io.BytesIO(raw_archive))

    @classmethod
    def from_file(cls, filename: str) -> Archive:
        # NOTE: don't use "with" if you want to keep the stream open
        archive_file = open(filename, "rb")
        return cls.from_stream(archive_file)

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Archive:
        raise NotImplementedError("ArchiveClass has not defined .from_stream()")
