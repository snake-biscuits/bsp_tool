from __future__ import annotations

import collections
import enum  # for type hints
import os
import struct
from types import MethodType, ModuleType
from typing import Dict, List, Union

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
    loading_errors: Dict[str, Exception]  # errors raised loading lumps

    def __init__(self, branch: ModuleType, filename: str = "untitled.bsp", autoload: bool = True):
        if not filename.endswith(".bsp"):
            raise RuntimeError("Not a .bsp")
        filename = os.path.realpath(filename)
        self.filename = os.path.basename(filename)
        self.folder = os.path.dirname(filename)
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
        version_string = f"({self.FILE_MAGIC.decode('ascii', 'ignore')} version {self.BSP_VERSION})"
        print(f"Opening {self.filename} {version_string}...")
        # read headers
        # TODO: define headers in branch script as a base.Struct (overriding a default)
        # however, keep using ExternalLumpHeaders? could be overly complicated
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
            if LUMP_NAME in self.branch.LUMP_CLASSES:
                LumpClass = self.branch.LUMP_CLASSES[LUMP_NAME]
                try:
                    setattr(self, LUMP_NAME, lumps.BspLump(self.file, lump_header, LumpClass))
                except RuntimeError:  # lump cannot be divided into a whole number of LumpClasses
                    setattr(self, LUMP_NAME, lumps.RawBspLump(self.file, lump_header))
            if LUMP_NAME in self.branch.SPECIAL_LUMP_CLASSES:
                SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP_NAME]
                # TODO: use a method to grab data for lump, should also handle externals
                # NOTE: lumps.BspLump
                self.file.seek(lump_header.offset)
                lump_data = self.file.read(lump_header.length)
                try:
                    BspLump = SpecialLumpClass(lump_data)
                except Exception:
                    # TODO: log the exception for debugging
                    BspLump = lumps.create_BspLump(self.file, lump_header)  # default to raw lump (bytes)
            elif LUMP_NAME in self.branch.BASIC_LUMP_CLASSES:
                LumpClass = self.branch.BASIC_LUMP_CLASSES[LUMP_NAME]
                try:
                    BspLump = lumps.create_BasicBspLump(self.file, lump_header, LumpClass)
                except Exception as exc:
                    self.loading_errors[LUMP_NAME] = exc
                    BspLump = lumps.create_RawBspLump(self.file, lump_header)
            else:  # LumpClass / RawBspLump
                LumpClass = self.branch.LUMP_CLASSES.get(LUMP_NAME, None)
                try:
                    BspLump = lumps.create_BspLump(self.file, lump_header, LumpClass)
                except Exception as exc:
                    self.loading_errors[LUMP_NAME] = exc
                    BspLump = lumps.create_RawBspLump(self.file, lump_header)
            setattr(self, LUMP_NAME, BspLump)
        # TODO: try and refactor so the "save lump as raw" case is only on one line
        # TODO: print which lumps loaded to the terminal
        # TODO: (maybe) give a pretty ascii visualisation of the .bsp file
        # -- ^ could be pretty handy for understanding re-saving actually ^
        if len(self.loading_errors) > 0:
            print(*[f"{L}: {e}" for L, e in self.loading_errors.items()], sep="\n")

    def save_as(self, filename: str):
        """Expects outfile to be a file with write bytes capability"""
        raise NotImplementedError()
        # if os.path.exists(filename):
        #     if input(f"Overwrite {filename}? (Y/N): ").upper()[0] != "Y":  # ask permission to overwrite
        #         print("Save Aborted")
        #         return
        # # try to preserve the original order of lumps
        # outfile.write(self.FILE_MAGIC)
        # outfile.write(self.VERSION.to_bytes(4, "little"))  # .bsp format version
        # for LUMP in self._engine_branch.LUMP:
        #     # convert special lumps to raw
        #     if hasattr(self, LUMP.name):
        #         continue
        #     elif hasattr(self, LUMP.name):  # if lump in self.branch.LUMP_CLASSES
        #         lump_format = self._engine_branch.lump_classes[LUMP]._format
        #         pack_lump = lambda c: struct.pack(lump_format, *c.flat())
        #         setattr(self, LUMP.name, map(pack_lump, getattr(self, LUMP)))
        #     # seek lump header
        #     outfile.write(offset.to_bytes(4, "little"))
        #     length = len(getattr(self, LUMP.name, None))
        #     offset += length
        #     outfile.write(b"\x00\x00\x00\x00") # lump version (actually important)
        #     outfile.write(b"\x00\x00\x00\x00") # lump fourCC (only for compressed)
        #     # seek lump start in file
        #     outfile.write(getattr(self, LUMP.name))
        # outfile.write(b"0001") # map revision

    def save(self):
        self.save_as(os.path.join(self.folder, self.filename))

    def set_branch(self, branch: Union[str, ModuleType]):
        """Calling .set_branch(...) on a loaded .bsp will not convert it!"""
        # branch is a imported branch definition
        # you can write your own script, expected contents are:
        # - BSP_VERSION: int
        # - LUMP(enum.Enum): NAME_OF_LUMP = int
        # - lump_header_address: {NAME_OF_LUMP: header_offset_into_file}
        # - LUMP_CLASSES: {"NAME_OF_LUMP": LumpClass}
        # - SPECIAL_LUMP_CLASSES: {"NAME_OF_LUMP": LumpClass}
        # each LumpClass needs a ._format attr
        # a lump is converted to a list of LumpClasses with:
        # - [*map(LumpClass, struct.iter_unpack(LumpClass._format: str, lump.read(): bytes))]
        # the failure is also logged, along with the sizes of the LumpClass._format & lump data
        # TODO: build new BspLump objects, keeping any changes made
        # NOTE: this doesn't mean changing formats, could cause major issues!
        # -- will require some clear debug warnings / checks
        self.branch = branch
        # attach methods
        # NOTE: does not remove methods from former branch
        for method in getattr(branch, "methods", list()):
            method = MethodType(method, self)
            setattr(self, method.__name__, method)
        # could we also attach static methods?

    def lump_as_bytes(self, lump_name: str) -> bytes:
        # NOTE: if a lump failed to read correctly, converting to bytes will fail
        # -- this is because LumpClasses are expected
        if not hasattr(self, lump_name):
            return b""  # lump is empty / deleted
        lump_entries = getattr(self, lump_name)
        if lump_name in self.branch.BASIC_LUMP_CLASSES:
            _format = self.branch.BASIC_LUMP_CLASSES[lump_name]._format
            raw_lump = struct.pack(f"{len(lump_entries)}{_format}", *lump_entries)
        elif lump_name in self.branch.LUMP_CLASSES:
            _format = self.branch.LUMP_CLASSES[lump_name]._format
            raw_lump = b"".join([struct.pack(_format, *x.flat()) for x in lump_entries])
        elif lump_name in self.branch.SPECIAL_LUMP_CLASSES:
            raw_lump = lump_entries.as_bytes()
        else:  # assume lump_entries is just bytes
            raw_lump = b"".join(lump_entries)
        return raw_lump
