from __future__ import annotations
import collections
import os
import re
import struct
from types import MethodType, ModuleType
from typing import Dict, List, Union


LumpHeader = collections.namedtuple("LumpHeader", ["offset", "length", "version", "fourCC"])


class Bsp():
    FILE_MAGIC: bytes = b"XBSP"
    HEADERS: Dict[str, LumpHeader] = dict()
    VERSION: int = 0
    associated_files: List[str]  # local to loaded / exported file
    branch: ModuleType
    filesize: int = 0  # of loaded / exported file
    filename: str
    folder: str

    def __init__(self, branch: ModuleType,  filename: str = "untitled.bsp"):
        self.set_branch(branch)
        if not self.filename.endswith(".bsp"):
            raise RuntimeError("Not a .bsp")
        filename = os.path.realpath(filename)
        self.filename = os.path.basename(filename)
        self.folder = os.path.dirname(filename)
        if os.path.exists(filename):
            self.load()

    def __enter__(self):
        self.load()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.file.close()

    def load_lumps(self):
        """Load every lump from open self.file"""
        for ID in self.branch.LUMP:  # load every lump, either as RAW_<LUMPNAME> or as <LUMPNAME> with classes
            LUMP = ID.name
            lump_header, lump_data = self.read_lump(self.branch.lump_header_address[ID])
            self.LUMP_HEADERS[LUMP] = lump_header
            if lump_data is not None:
                if LUMP in self.branch.lump_classes:
                    LumpClass = self.branch.lump_classes[ID.name]
                try:  # implement -Warn system here
                    setattr(self, LUMP, list())
                    for _tuple in struct.iter_unpack(LumpClass._format, lump_data):
                        if len(_tuple) == 1:  # if ._format is 1 variable, return the 1 variable, not a len(1) tuple
                            _tuple = _tuple[0]  # there has to be a better way
                        getattr(self, ID.name).append(LumpClass(_tuple))
                    # WHY NOT: setattr(self, LUMP, [*map(LumpClass, struct.iter_unpack(LumpClass._format, lump_data))])
                except struct.error:  # lump cannot be divided into a whole number of LumpClasses
                    struct_size = struct.calcsize(LumpClass._format)
                    self.loading_errors.append(f"ERROR PARSING {LUMP}:\n"
                                               f"{LUMP} lump is an unusual size ({len(lump_data)} / {struct_size})."
                                               " Wrong engine branch?")
                    delattr(self, LUMP)
                except Exception as exc:
                    self.loading_errors.append(f"ERROR PARSING {LUMP}:\n{exc.__class__.__name__}: {exc}")
                    # save the exception for debugging? (traceback etc.)
                else:  # lump structure unknown
                    # TODO: check a list of SPECIAL LUMP translating functions here
                    self.setattr(self, f"RAW_{LUMP}", lump_data)

    def load(self):
        """Loads filename using the format outlined in this .bsp's branch defintion script"""
        local_files = os.listdir(self.folder)
        def is_related(f): return f.startswith(os.path.splitext(self.filename)[0])
        self.associated_files = [f for f in local_files if is_related(f)]
        file = open(os.path.join(self.folder, self.filename), "rb")
        file_magic = file.read(4)
        if file_magic != self.FILE_MAGIC:
            raise RuntimeError(f"{file} is not a valid .bsp!")
        self.BSP_VERSION = int.from_bytes(file.read(4), "little")
        print(f"Loading {self.filename} ({self.FILE_MAGIC} version {self.BSP_VERSION})...")
        file.read()  # move cursor to end of file
        self.filesize = file.tell()

        self.loading_errors: List[str] = []
        self.load_lumps(file)  # load most basic lumps
        if len(self.loading_errors) > 0:
            print(*self.loading_errors, sep="\n")

        # SPECIAL LUMPS (should have methods for loading these in 'self.branch')
        # ENTITIES
        # TODO: use fgd-tools to fully unstringify entities
        self.ENTITIES: List[Dict[str, str]] = list()
        # ^ [{"key": "value"}]
        for line in self.RAW_ENTITIES.decode(errors="ignore").split("\n"):
            if re.match("^[ \t]*$", line):  # line is blank / whitespace
                continue
            if "{" in line:
                ent = dict()
            elif re.match('".*" ".*"', line):
                key, value = line[1:-1].split('" "')  # could extract with regex
                if key not in ent:
                    ent[key] = value
                else:  # don't override, share a list
                    if isinstance(ent[key], list):
                        ent[key].append(value)
                    else:
                        ent[key] = [ent[key], value]
            elif "}" in line:
                self.ENTITIES.append(ent)
            elif line == b"\x00".decode():
                continue  # ignore raw bytes, might be related to lump alignment
            else:
                raise RuntimeError(f"Unexpected line in entities: {line.encode()}")
        del self.RAW_ENTITIES
        # GAME LUMP
        # LUMP_GAME_LUMP is compressed in individual segments.
        # The compressed size of a game lump can be determined by subtracting
        # the current game lump's offset with that of the next entry.
        # For this reason, the last game lump is always an empty dummy which
        # only contains the offset.
        # SURF_EDGES
        if hasattr(self, "RAW_SURFEDGES"):
            self.SURFEDGES = [s[0] for s in struct.iter_unpack(self.branch.SurfEdge._format, self.RAW_SURFEDGES)]
            del self.RAW_SURFEDGES, _format
        # TEXDATA STRING DATA
        if hasattr(self, "RAW_TEXDATA_STRING_DATA"):
            tdsd = self.RAW_TEXDATA_STRING_DATA.split(b"\0")
            tdsd = [s.decode("ascii", errors="ignore") for s in tdsd]
            self.TEXDATA_STRING_DATA = tdsd
            del self.RAW_TEXDATA_STRING_DATA, tdsd
        # VISIBILITY
        # bsp.VISIBILITY = [v[0] for v in struct.iter_unpack("i", bsp.RAW_VISIBLITY)]
        # num_clusters = bsp.VISIBILITY[0]
        # for i in range(num_clusters):
        #     i = (2 * i) + 1
        #     pvs_offset = bsp.RAW_VISIBILITY[i]
        #     pas_offset = bsp.RAW_VISIBILITY[i + 1]
        #     # ^ pointers into RLE encoded bits mapping the PVS tree

        file.close()
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
        #     # special lumps:
        #     #  - ENTITIES
        #     #  - GAME_LUMP
        #     #  - SURF_EDGES
        #     #  - VISIBILITY
        #     if hasattr(self, f"RAW_{LUMP}"):
        #         continue
        #     elif hasattr(self, LUMP):
        #         lump_format = self._engine_branch.lump_classes[LUMP]._format
        #         pack_lump = lambda c: struct.pack(lump_format, *c.flat())
        #         setattr(self, f"RAW_{LUMP}", map(pack_lump, getattr(self, LUMP)))
        #     # seek lump header
        #     outfile.write(offset.to_bytes(4, "little"))
        #     length = len(getattr(self, ID.name, "RAW_" + ID.name))
        #     offset += length
        #     outfile.write(b"0000") # lump version (actually important)
        #     outfile.write(b"0000") # lump fourCC (only for compressed)
        #     # seek lump start in file
        #     outfile.write(getattr(self, ID.name, "RAW_" + ID.name))
        # outfile.write(b"0001") # map revision

    def set_branch(self, branch: Union[str, ModuleType]):
        """Calling .set_branch(...) on a loaded .bsp will not convert it!"""
        # branch is a imported branch definition
        # you can write your own script, expected contents are:
        # - BSP_VERSION: int
        # - LUMP(enum.Enum): NAME_OF_LUMP = int
        # - lump_header_address: {NAME_OF_LUMP: header_offset_into_file}
        # - lump_classes: {"NAME_OF_LUMP": LumpClass}
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
