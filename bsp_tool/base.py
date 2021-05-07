from __future__ import annotations

import collections
import enum  # for type hints
import os
import struct
from types import MethodType, ModuleType
from typing import Dict, List

from . import lumps


# NOTE: LumpHeaders must have these attrs, but how they are read / order will vary
LumpHeader = collections.namedtuple("LumpHeader", ["offset", "length", "version", "fourCC"])
ExternalLumpHeader = collections.namedtuple("ExternalLumpHeader", ["offset", "length", "version", "fourCC",
                                                                   "filename", "filesize"])
# NOTE: if fourCC != 0: lump is compressed  (fourCC value == uncompressed size)


class Bsp:
    """Bsp base class"""
    FILE_MAGIC: bytes = b"XBSP"
    HEADERS: Dict[str, LumpHeader]
    # ^ {"LUMP_NAME": LumpHeader}
    VERSION: int = 0  # .bsp format version
    associated_files: List[str]  # files in the folder of loaded file with similar names
    branch: ModuleType  # soft copy of "branch script"
    bsp_file_size: int = 0  # size of .bsp in bytes
    filename: str
    folder: str
    loading_errors: Dict[str, Exception]
    # ^ {"LUMP_NAME": Exception encountered}

    def __init__(self, branch: ModuleType, filename: str = "untitled.bsp", autoload: bool = True):
        if not filename.endswith(".bsp"):
            raise RuntimeError("Not a .bsp")
        filename = os.path.realpath(filename)
        self.folder, self.filename = os.path.split(filename)
        self.set_branch(branch)
        self.HEADERS = dict()
        if autoload:
            if os.path.exists(filename):
                self._preload()
            else:
                print(f"{filename} not found, creating a new .bsp")
                self.HEADERS = {L.name: LumpHeader(0, 0, 0, 0) for L in self.branch.LUMP}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.file.close()

    def __repr__(self):
        version = f"({self.FILE_MAGIC.decode('ascii', 'ignore')} version {self.BSP_VERSION})"
        return f"<{self.__class__.__name__} {self.filename} {version} at 0x{id(self):016X}>"

    def _read_header(self, LUMP: enum.Enum) -> LumpHeader:
        """Reads bytes of lump"""
        self.file.seek(self.branch.lump_header_address[LUMP])
        offset, length, version, fourCC = struct.unpack("4I", self.file.read(16))
        # TODO: use a read & write function / struct.iter_unpack
        # -- this could potentially allow for simplified subclasses
        # -- e.g. LumpHeader(*struct.unpack("4I", self.file.read(16)))  ->  self.LumpHeader(self.file)
        header = LumpHeader(offset, length, version, fourCC)
        return header

    def _preload(self):
        """Loads filename using the format outlined in this .bsp's branch defintion script"""
        local_files = os.listdir(self.folder)
        def is_related(f): return f.startswith(os.path.splitext(self.filename)[0])
        self.associated_files = [f for f in local_files if is_related(f)]
        # open .bsp
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        file_magic = self.file.read(4)
        if file_magic != self.FILE_MAGIC:
            raise RuntimeError(f"{self.file} is not a valid .bsp!")
        self.BSP_VERSION = int.from_bytes(self.file.read(4), "little")
        self.file.seek(0, 2)  # move cursor to end of file
        self.bsp_file_size = self.file.tell()

        self.loading_errors: Dict[str, Exception] = dict()
        for LUMP_enum in self.branch.LUMP:
            # CHECK: is lump external? (are associated_files overriding)
            lump_header = self._read_header(LUMP_enum)
            LUMP_NAME = LUMP_enum.name
            self.HEADERS[LUMP_NAME] = lump_header
            if lump_header.length == 0:
                continue
            try:
                if LUMP_NAME == "GAME_LUMP":
                    GameLumpClasses = getattr(self.branch, "GAME_LUMP_CLASSES", dict())
                    BspLump = lumps.GameLump(self.file, lump_header, GameLumpClasses)
                elif LUMP_NAME in self.branch.LUMP_CLASSES:
                    LumpClass = self.branch.LUMP_CLASSES[LUMP_NAME]
                    BspLump = lumps.create_BspLump(self.file, lump_header, LumpClass)
                elif LUMP_NAME in self.branch.SPECIAL_LUMP_CLASSES:
                    SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP_NAME]
                    if not isinstance(lump_header, ExternalLumpHeader):
                        self.file.seek(lump_header.offset)
                        lump_data = self.file.read(lump_header.length)
                    else:
                        lump_data = open(lump_header.filename, "rb").read()
                    BspLump = SpecialLumpClass(lump_data)
                elif LUMP_NAME in self.branch.BASIC_LUMP_CLASSES:
                    LumpClass = self.branch.BASIC_LUMP_CLASSES[LUMP_NAME]
                    BspLump = lumps.create_BasicBspLump(self.file, lump_header, LumpClass)
                else:
                    BspLump = lumps.create_RawBspLump(self.file, lump_header)
            except Exception as exc:
                self.loading_errors[LUMP_NAME] = exc
                BspLump = lumps.create_RawBspLump(self.file, lump_header)
            setattr(self, LUMP_NAME, BspLump)

    def save_as(self, filename: str):
        """Expects outfile to be a file with write bytes capability"""
        raise NotImplementedError()
        # os.makedirs(os.path.dirname(os.path.realpath(filename)), exist_ok=True)
        # outfile = open(filename, "wb")
        # # try to preserve the original order of lumps
        # outfile.write(self.FILE_MAGIC)
        # outfile.write(self.VERSION.to_bytes(4, "little"))  # .bsp format version
        # for LUMP in self.branch.LUMP:
        #     pass  # calculate and write each header
        #     # adapting each header to bytes could be hard
        # # write the contents of each lump
        # outfile.write(b"0001") # map revision
        # # write contents of lumps

    def save(self):
        self.save_as(os.path.join(self.folder, self.filename))

    def set_branch(self, branch: ModuleType):
        """Calling .set_branch(...) on a loaded .bsp will not convert it!"""
        # branch is a "branch script" that has been imported into python
        # if writing your own "branch script", see branches/README.md for a guide
        self.branch = branch
        # attach methods
        for method in getattr(branch, "methods", list()):
            method = MethodType(method, self)
            setattr(self, method.__name__, method)
        # NOTE: does not remove methods from former branch
        # could we also attach static methods?

    def lump_as_bytes(self, LUMP_name: str) -> bytes:
        # NOTE: if a lump failed to read correctly, converting to bytes will fail
        # -- this is because LumpClasses are expected
        if not hasattr(self, LUMP_name):
            return b""  # lump is empty / deleted
        lump_entries = getattr(self, LUMP_name)
        if LUMP_name in self.branch.BASIC_LUMP_CLASSES:
            _format = self.branch.BASIC_LUMP_CLASSES[LUMP_name]._format
            raw_lump = struct.pack(f"{len(lump_entries)}{_format}", *lump_entries)
        elif LUMP_name in self.branch.LUMP_CLASSES:
            _format = self.branch.LUMP_CLASSES[LUMP_name]._format
            raw_lump = b"".join([struct.pack(_format, *x.flat()) for x in lump_entries])
        elif LUMP_name in self.branch.SPECIAL_LUMP_CLASSES:
            raw_lump = lump_entries.as_bytes()
        else:  # assume lump_entries is RawBspLump
            raw_lump = bytes(lump_entries)
        return raw_lump
