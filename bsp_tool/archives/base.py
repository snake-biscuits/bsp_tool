from __future__ import annotations
import fnmatch
import io
import os
from typing import Dict, List, Tuple


def path_tuple(path: str) -> Tuple[str]:
    out = tuple(path.replace("\\", "/").strip("/").split("/"))
    if len(out) > 1 and out[0] == ".":
        return out[1:]
    else:
        return out


class Archive:
    ext = None
    external_filenames: Dict[str, io.BytesIO]

    def __init__(self):
        self.external_filenames = dict()

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

    def is_dir(self, filename: str) -> bool:
        all_dirs = {path_tuple(fn)[:-1] for fn in self.namelist()}
        all_dirs.update({tuple_[:i] for tuple_ in all_dirs for i in range(1, len(tuple_))})
        all_dirs.update({path_tuple(root) for root in (".", "./", "/")})
        return path_tuple(filename) in all_dirs

    def is_file(self, filename: str) -> bool:
        return filename in self.namelist()

    def listdir(self, folder: str) -> List[str]:
        if not self.is_dir(folder):
            raise FileNotFoundError(f"no such directory: {folder}")
        folder_tuple = path_tuple(folder)
        if folder_tuple in {path_tuple(root) for root in (".", "./", "/")}:
            folder_tuple = tuple()  # empty
        namelist_tuples = map(path_tuple, self.namelist())
        folder_contents = list()
        for tuple_ in namelist_tuples:
            if tuple_[:-1] == folder_tuple:
                folder_contents.append(tuple_[-1])  # file
            elif tuple_[:len(folder_tuple)] == folder_tuple:
                subfolder = tuple_[len(folder_tuple)] + "/"
                if subfolder not in folder_contents:
                    folder_contents.append(subfolder)
        return folder_contents

    def mount_file(self, filename: str, archive=None):
        if archive is None:
            self.external_files[filename] = open(filename, "rb")
        else:
            self.external_files[filename] = io.BytesIO(archive.read(filename))

    def namelist(self) -> List[str]:
        # NOTE: we assume namelist only contains filenames, no folders
        raise NotImplementedError("ArchiveClass has not defined .namelist()")

    def path_exists(self, filename: str) -> bool:
        return self.is_file(filename) or self.is_dir(filename)

    def read(self, filename: str) -> bytes:
        raise NotImplementedError("ArchiveClass has not defined .read()")

    def search(self, pattern="*.bsp", case_sensitive=False):
        pattern = pattern if case_sensitive else pattern.lower()
        namelist = self.namelist() if case_sensitive else [fn.lower() for fn in self.namelist()]
        return fnmatch.filter(namelist, pattern)

    def tree(self, folder: str = ".", depth: int = 0):
        """namelist pretty printer"""
        for filename in self.listdir(folder):
            print(f"{'  ' * depth}{filename}")
            full_filename = os.path.join(folder, filename)
            if self.is_dir(full_filename):
                self.tree(full_filename, depth + 1)

    def unmount_file(self, filename: str):
        self.external_files.pop(filename)

    @classmethod
    def from_archive(cls, parent_archive: Archive, filename: str) -> Archive:
        """for ArchiveClasses composed of multiple files"""
        # TODO: mount extra files
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
