from __future__ import annotations
import fnmatch
import io
import os
import struct
from types import MethodType, ModuleType
from typing import Any, Dict, List

from . import external


class Bsp:
    """Bsp base class"""
    branch: ModuleType  # soft copy of "branch script"
    endianness: str = "little"
    extras: Dict[str, external.File]
    file_magic: bytes = b"XBSP"
    # NOTE: XBSP is not a real bsp variant! this is just a placeholder
    filesize: int = 0  # size of .bsp in bytes
    filename: str
    folder: str
    version: int | (int, int) = 0  # .bsp format version
    headers: Dict[str, Any]
    # ^ {"LUMP.name": LumpHeader}
    # NOTE: header type is self.branch.LumpHeader
    loading_errors: Dict[str, Exception]
    # ^ {"LUMP.name": Error("details")}
    signature: bytes = b""  # compiler signature; sometimes found between header & data

    def __init__(self, branch: ModuleType, filepath: str = "untitled.bsp"):
        if not filepath.lower().endswith(".bsp"):
            raise RuntimeError("Not a .bsp")
        self.folder, self.filename = os.path.split(filepath)
        self.set_branch(branch)
        self.headers = dict()
        self.extras = dict()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.file.close()

    def __repr__(self):
        branch_script = ".".join(self.branch.__name__.split(".")[-2:])
        if isinstance(self.version, tuple):
            major, minor = self.version
            version_number = f"{major}.{minor}"
        else:
            version_number = self.version
        version = f"({self.file_magic.decode('ascii', 'ignore')} version {version_number})"
        return f"<{self.__class__.__name__} '{self.filename}' {branch_script} {version}>"

    def _get_signature(self, header_length: int):
        """check for a signature between header & data"""
        # TODO: check for other conspicuous gaps between lumps (> 4 byte padding)
        lumps_start = min(h.offset for h in self.headers.values() if h.length != 0)
        if lumps_start > header_length:
            self.file.seek(header_length)
            self.signature = self.file.read(lumps_start - header_length)

    def _tail(self) -> bytes:
        """for catching appended XBSP data"""
        # NOTE: lumps_end can be greater than self.filesize
        # -- specifically for RespawnBsp vXX.1 (Apex Legends season 10+)
        lumps_end = max(h.offset + h.length for h in self.headers.values())
        self.file.seek(lumps_end)
        return self.file.read()

    def _header_generator(self, offset: int = 4) -> (str, Any):
        """iterator for reading headers from self.file"""
        for LUMP in self.branch.LUMP:
            self.file.seek(offset + struct.calcsize(self.branch.LumpHeader._format) * LUMP.value)
            lump_header = self.branch.LumpHeader.from_stream(self.file)
            self.headers[LUMP.name] = lump_header
            yield (LUMP.name, lump_header)

    def extra_patterns(self) -> List[str]:
        """filename patterns for files to mount (e.g. 'mp_thaw.*.bsp_lump')"""
        return list()

    def lump_as_bytes(self, lump_name: str) -> bytes:
        """convert the named lump back into bytes"""
        # NOTE: LumpClasses are derived from branch, not lump data!
        if not hasattr(self, lump_name):
            return b""  # lump is empty / deleted
        lump_entries = getattr(self, lump_name)
        all_mapped_lumps = {*self.branch.BASIC_LUMP_CLASSES,
                            *self.branch.LUMP_CLASSES,
                            *self.branch.SPECIAL_LUMP_CLASSES}
        # RawBspLump -> bytes
        if lump_name not in all_mapped_lumps or lump_name in self.loading_errors:
            return bytes(lump_entries)
        # BasicBspLump -> bytes
        if lump_name in self.branch.BASIC_LUMP_CLASSES:
            BasicLumpClass = self.branch.BASIC_LUMP_CLASSES[lump_name]
            if hasattr(BasicLumpClass, "as_int"):  # core.BitField
                lump_entries = [x.as_int() for x in lump_entries]
            raw_lump = struct.pack(f"{len(lump_entries)}{BasicLumpClass._format}", *lump_entries)
        # BspLump -> bytes
        elif lump_name in self.branch.LUMP_CLASSES:
            _format = self.branch.LUMP_CLASSES[lump_name]._format
            raw_lump = b"".join([struct.pack(_format, *x.as_tuple()) for x in lump_entries])
        # SpecialLumpClass -> bytes
        elif lump_name in self.branch.SPECIAL_LUMP_CLASSES:
            raw_lump = lump_entries.as_bytes()
        return raw_lump

    def mount_file(self, filename: str, external_file: external.File):
        self.extras[filename] = external_file

    def save_as(self, filename: str):
        """Expects outfile to be a file with write bytes capability"""
        raise NotImplementedError()
        # os.makedirs(os.path.dirname(os.path.realpath(filename)), exist_ok=True)
        # outfile = open(filename, "wb")
        # # try to preserve the original order of lumps
        # outfile.write(self.file_magic)
        # outfile.write(self.version.to_bytes(4, "little"))  # .bsp format version
        # for LUMP in self.branch.LUMP:
        #     pass  # calculate and write each header
        # # write the contents of each lump
        # outfile.write(b"0001") # map revision
        # # write contents of lumps

    def save(self):
        # NOTE: save_as must copy all lumps into memory (w/ lump_as_bytes) and close self.file
        # -- otherwise a write conflict will occur
        # NOTE: you should really be making backups anyway
        self.save_as(os.path.join(self.folder, self.filename))

    def set_branch(self, branch: ModuleType):
        """Calling .set_branch(...) on a loaded .bsp will not convert it!"""
        # branch is a "branch script" that has been imported into python
        # if writing your own "branch script", see branches/README.md for a guide
        if hasattr(self, "branch"):
            for method_name in getattr(branch, "methods", dict()):
                delattr(self, method_name)
        self.branch = branch
        # attach methods
        for method_name, method in getattr(branch, "methods", dict()).items():
            method = MethodType(method, self)
            setattr(self, method_name, method)

    def unmount_file(self, filename: str):
        self.extras.pop(filename)

    @classmethod
    def from_archive(cls, branch: ModuleType, filepath: str, parent_archive) -> Bsp:
        bsp = cls.from_bytes(branch, filepath, parent_archive.read(filepath))
        extras = [
            filename
            for filename in parent_archive.listdir(bsp.folder)
            for pattern in bsp.extra_patterns()
            if fnmatch.fnmatch(filename.lower(), pattern.lower())]
        for filename in extras:
            full_filename = os.path.join(bsp.folder, filename)
            external_file = external.File.from_archive(full_filename, parent_archive)
            bsp.mount_file(filename, external_file)
        return bsp

    @classmethod
    def from_bytes(cls, branch: ModuleType, filepath: str, raw_bsp: bytes) -> Bsp:
        return cls.from_stream(branch, filepath, io.BytesIO(raw_bsp))

    @classmethod
    def from_file(cls, branch: ModuleType, filepath: str) -> Bsp:
        bsp = cls.from_stream(branch, filepath, open(filepath, "rb"))
        extras = [
            filename
            for filename in os.listdir(bsp.folder)
            for pattern in bsp.extra_patterns()
            if fnmatch.fnmatch(filename.lower(), pattern.lower())]
        for filename in extras:
            full_filename = os.path.join(bsp.folder, filename)
            external_file = external.File.from_file(full_filename)
            bsp.mount_file(filename, external_file)
        return bsp

    @classmethod
    def from_stream(cls, branch: ModuleType, filepath: str, stream: io.BytesIO) -> Bsp:
        raise NotImplementedError()
