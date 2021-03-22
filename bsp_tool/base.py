from __future__ import annotations

import collections
import enum  # for type hints
import os
import struct
from types import MethodType, ModuleType
from typing import Dict, List, Union


LumpHeader = collections.namedtuple("LumpHeader", ["offset", "length", "version", "fourCC"])  # Valve lump header
# TODO: streamline lump header definition
# - version matters, different struct definitions have to be accounted for
# - a fourCC other than 0 means a lump is compressed (stored uncompressed size)
# - the game lump has sub headers where fourCC defines lump type


class Bsp():
    FILE_MAGIC: bytes = b"XBSP"
    HEADERS: Dict[str, LumpHeader]
    # ^ {"LUMP_NAME": LumpHeader}
    VERSION: int = 0
    associated_files: List[str]  # local to loaded / exported file
    branch: ModuleType
    filesize: int = 0  # of loaded / exported file
    filename: str
    folder: str

    def __init__(self, branch: ModuleType, filename: str = "untitled.bsp", autoload: bool = True):
        self.HEADERS = dict()
        self.set_branch(branch)
        if not filename.endswith(".bsp"):
            raise RuntimeError("Not a .bsp")
        filename = os.path.realpath(filename)
        self.filename = os.path.basename(filename)
        self.folder = os.path.dirname(filename)
        if autoload:
            if os.path.exists(filename):
                self.load()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.file.close()

    def __repr__(self):
        version = f"({self.FILE_MAGIC.decode('ascii', 'ignore')} version {self.BSP_VERSION})"
        return f"<{self.__class__.__name__} {self.filename} {version} at 0x{id(self):016X}>"

    def read_lump(self, LUMP: enum.Enum) -> (LumpHeader, bytes):
        # header
        self.file.seek(self.branch.lump_header_address[LUMP])
        offset, length, version, fourCC = struct.unpack("4i", self.file.read(16))
        header = LumpHeader(offset, length, version, fourCC)
        if header.length == 0:
            return header, None
        # data
        self.file.seek(header.offset)
        data = self.file.read(header.length)
        return header, data

    def load_lumps(self):
        """Load every lump from self.file (self.file must already be open!)"""
        for LUMP_enum in self.branch.LUMP:
            lump_header, lump_data = self.read_lump(LUMP_enum)
            LUMP = LUMP_enum.name
            self.HEADERS[LUMP] = lump_header
            if lump_data is None:
                continue
            if LUMP in self.branch.LUMP_CLASSES:
                LumpClass = self.branch.LUMP_CLASSES[LUMP]
                try:
                    setattr(self, LUMP, list())
                    for _tuple in struct.iter_unpack(LumpClass._format, lump_data):
                        if len(_tuple) == 1:
                            # if ._format is 1 variable, return the 1 variable, not a len(1) tuple
                            # there has to be a better way than this
                            _tuple = _tuple[0]
                        getattr(self, LUMP).append(LumpClass(_tuple))
                    # WHY NOT: setattr(self, LUMP, [*map(LumpClass, struct.iter_unpack(LumpClass._format, lump_data))])
                except struct.error:  # lump cannot be divided into a whole number of LumpClasses
                    struct_size = struct.calcsize(LumpClass._format)
                    self.loading_errors.append(f"ERROR PARSING {LUMP}:\n"
                                               f"{LUMP} lump is an unusual size ({len(lump_data)} / {struct_size})."
                                               " Wrong engine branch?")
                    delattr(self, LUMP)
                    setattr(self, f"RAW_{LUMP}", lump_data)
                except Exception as exc:  # likely an error with initialising LumpClass
                    self.loading_errors.append(f"ERROR PARSING {LUMP}:\n{exc.__class__.__name__}: {exc}")
                    setattr(self, f"RAW_{LUMP}", lump_data)
                    # TODO: save a copy of the traceback for debugging
            elif LUMP in self.branch.SPECIAL_LUMP_CLASSES:
                try:
                    setattr(self, LUMP, self.branch.SPECIAL_LUMP_CLASSES[LUMP](lump_data))
                    # ^ self.SPECIAL_LUMP = SpecialLumpClass(data)
                except Exception as exc:
                    self.loading_errors.append(f"ERROR PARSING {LUMP}:\n{exc.__class__.__name__}: {exc}")
                    setattr(self, f"RAW_{LUMP}", lump_data)
                    # TODO: save a copy of the traceback for debugging
            else:  # lump structure unknown
                setattr(self, f"RAW_{LUMP}", lump_data)

    def load(self):
        """Loads filename using the format outlined in this .bsp's branch defintion script"""
        local_files = os.listdir(self.folder)
        def is_related(f): return f.startswith(os.path.splitext(self.filename)[0])
        self.associated_files = [f for f in local_files if is_related(f)]
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        file_magic = self.file.read(4)
        if file_magic != self.FILE_MAGIC:
            raise RuntimeError(f"{self.file} is not a valid .bsp!")
        self.BSP_VERSION = int.from_bytes(self.file.read(4), "little")
        version = f"({self.FILE_MAGIC.decode('ascii', 'ignore')} version {self.BSP_VERSION})"
        print(f"Loading {self.filename} {version}...")
        self.file.seek(0, 2)  # move cursor to end of file
        self.filesize = self.file.tell()

        self.loading_errors: List[str] = []
        self.load_lumps()
        if len(self.loading_errors) > 0:
            print(*self.loading_errors, sep="\n")

        self.file.close()
        print(f"Loaded  {self.filename}")

    def save(self):
        """Expects outfile to be a file with write bytes capability"""
        raise NotImplementedError()
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
        self.branch = branch
        # attach methods
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
