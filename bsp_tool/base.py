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
    loading_errors: List[str]  # list of errors raised loading lumps

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
        # header
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

        for LUMP_enum in self.branch.LUMP:
            # CHECK: is lump external? (are associated_files overriding)
            lump_header = self._read_header(LUMP_enum)
            LUMP_NAME = LUMP_enum.name
            self.HEADERS[LUMP_NAME] = lump_header
            if lump_header.length is None:
                continue
            if LUMP_NAME in self.branch.LUMP_CLASSES:
                LumpClass = self.branch.LUMP_CLASSES[LUMP_NAME]
                try:
                    setattr(self, LUMP_NAME, lumps.BspLump(self.file, lump_header, LumpClass))
                except RuntimeError:  # lump cannot be divided into a whole number of LumpClasses
                    setattr(self, f"RAW_{LUMP_NAME}", lumps.RawBspLump(self.file, lump_header))
            elif LUMP_NAME in self.branch.SPECIAL_LUMP_CLASSES:
                SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP_NAME]
                # TODO: use a method to grab data for lump, should also handle externals
                # NOTE: lumps.BspLump
                self.file.seek(lump_header.offset)
                lump_data = self.file.read(lump_header.length)
                try:
                    setattr(self, LUMP_NAME, SpecialLumpClass(lump_data))
                except Exception:  # TODO: log the exception for debugging
                    setattr(self, f"RAW_{LUMP_NAME}", lumps.RawBspLump(self.file, lump_header))
            else:  # lump structure unknown
                setattr(self, f"RAW_{LUMP_NAME}", lumps.RawBspLump(self.file, lump_header))
        # TODO: try and refactor so the "save lump as raw" case is only on one line
        # TODO: print which lumps loaded to the terminal
        # TODO: (maybe) give a pretty ascii visualisation of the .bsp file
        # -- ^ could be pretty handy for understanding re-saving actually ^

    def save(self):
        """Expects outfile to be a file with write bytes capability"""
        raise NotImplementedError()
        # TODO: check BspLump._changes are all of type LumpClass
        # filename = os.path.join(self.folder, self.filename)
        # if os.path.exists(filename):
        #     if input(f"Overwrite {filename}? (Y/N): ").upper()[0] != "Y":  # ask permission to overwrite
        #         print("Save Aborted")
        #         return
        # USE THE LUMP MAP! PRESERVE ORIGINAL FILE'S LUMP ORDER
        # outfile.write(self.FILE_MAGIC)
        # outfile.write(self.VERSION.to_bytes(4, "little")) # Engine version
        # # CONVERT INTERNAL LUMPS TO RAW LUMPS
        # offset, length = 0, 0
        # def save_lumps(...):
        # ...
        # for LUMP in self._engine_branch.LUMP:
        #     # convert special lumps to raw
        #     if hasattr(self, f"RAW_{LUMP}"):
        #         continue
        #     elif hasattr(self, LUMP):  # if lump in self.branch.LUMP_CLASSES
        #         lump_format = self._engine_branch.lump_classes[LUMP]._format
        #         pack_lump = lambda c: struct.pack(lump_format, *c.flat())
        #         setattr(self, f"RAW_{LUMP}", map(pack_lump, getattr(self, LUMP)))
        #     # seek lump header
        #     outfile.write(offset.to_bytes(4, "little"))
        #     length = len(getattr(self, LUMP.name, "RAW_" + LUMP.name))
        #     offset += length
        #     outfile.write(b"0000") # lump version (actually important)
        #     outfile.write(b"0000") # lump fourCC (only for compressed)
        #     # seek lump start in file
        #     outfile.write(getattr(self, LUMP.name, "RAW_" + LUMP.name))
        # outfile.write(b"0001") # map revision

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
        # if any lump cannot be divided into a whole number of LumpClasses, it remains a RAW_LUMP
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

    def lump_as_bytes(self, lump_name):
        if hasattr(self, f"RAW_{lump_name}"):
            return getattr(self, f"RAW_{lump_name}")
        if not hasattr(self, lump_name):
            return b""  # assume lump is empty
        lump = getattr(self, lump_name)
        if lump_name in self.branch.LUMP_CLASSES:
            LumpClass = self.branch.LUMP_CLASSES[lump_name]
            if hasattr(LumpClass, "flat"):
                return b"".join(map(lambda x: struct.pack(LumpClass._format, *x.flat()), lump))
            else:  # List[int] lump
                return b"".join(map(lambda x: struct.pack(LumpClass._format, x), lump))
        elif lump_name in self.branch.SPECIAL_LUMP_CLASSES:
            return lump.as_bytes()
        else:
            raise RuntimeError(f"Don't know how to convert {lump_name} lump to bytes")
