from __future__ import annotations
import collections
import os
import re
import struct
import time
import types
from typing import Dict, List, Union

from . import branches


LumpHeader = collections.namedtuple("LumpHeader", ["offset", "length", "version", "fourCC"])


class Bsp():
    BSP_VERSION: int
    FILE_MAGIC: bytes = b"XBSP"
    HEADERS: Dict[int, LumpHeader]
    # ^ {LUMP_ID: List[LUMP_struct]}
    associated_files: List[str]  # local to loaded / exported file
    branch: types.ModuleType
    bytesize: int  # of loaded / exported file
    filename: str
    folder: str

    def __init__(self, filename):
        self.BSP_VERSION = 0
        self.bytesize = 0
        self.filename = filename
        self.lump_map = dict()

    @staticmethod
    def load(filename: str, branch: types.ModuleType, include_external: bool = False) -> Bsp:
        bsp = Bsp()
        # load files
        assert filename.endswith(".bsp")
        filename = os.path.realpath(filename)  # make sure we know the folder
        bsp.filename = os.path.basename(filename)
        bsp.folder = os.path.dirname(filename)
        local_files = os.listdir(bsp.folder)
        def is_related(f): return f.startswith(os.path.splitext(bsp.filename)[0])
        bsp.associated_files = [f for f in local_files if is_related(f)]
        file = open(filename, "rb")
        file_magic = file.read(4)
        if file_magic != super().FILE_MAGIC:  # rBSP = Respawn BSP (Titanfall/Apex Legends)
            raise RuntimeError(f"{file} cannot be loaded as ais not a .bsp!")
        bsp.BSP_VERSION = int.from_bytes(file.read(4), "little")

        bsp.set_branch(branch)

        print(f"Loading {bsp.filename} (BSP v{bsp.BSP_VERSION})...")
        # rBSP map revision is before headers, VBSP is after
        file.read()  # move cursor to end of file
        bsp.bytesize = file.tell()

        bsp.loading_errors: List[str] = []
        bsp.lump_map: Dict[int, LumpHeader] = {}
        # ^ {ID: LumpHeader}
        start_time = time.time()

        bsp.load_lumps(file)

        # PROCESS RAW LUMPS (this could be it's own method)
        lump_classes: Dict = bsp._engine_branch.lump_classes
        # ^ {"LUMP_NAME": LumpClass}
        for LUMP, lump_class in lump_classes.items():
            if not hasattr(bsp, f"RAW_{LUMP}"):
                continue  # lump was empty, skip
            try:  # implement -Warn system here
                setattr(bsp, LUMP, [])
                RAW_LUMP = getattr(bsp, f"RAW_{LUMP}")
                for data in struct.iter_unpack(lump_class._format, RAW_LUMP):
                    if len(data) == 1:
                        data = data[0]
                    getattr(bsp, LUMP).append(lump_class(data))
                delattr(bsp, f"RAW_{LUMP}")
            except struct.error:
                struct_size = struct.calcsize(lump_class._format)
                bsp.log.append(f"ERROR PARSING {LUMP}:\n{LUMP} lump is an unusual size ({len(RAW_LUMP)} / {struct_size})." +
                               "Wrong engine branch?")
                delattr(bsp, LUMP)
            except Exception as exc:
                bsp.log.append(f"ERROR PARSING {LUMP}:\n{exc.__class__.__name__}: {exc}")
                # raise exc

        if len(bsp.log) > 0:
            print(*bsp.log, sep="\n")

        # SPECIAL LUMPS

        # ENTITIES
        # TODO: use fgdtools to fully unstringify entities
        # rBSP .bsps have 5 associated entity files beginning with "ENTITIES01\n"
        bsp.ENTITIES: List[Dict[str, str]] = list()
        # ^ [{"key": "value"}]
        for line in bsp.RAW_ENTITIES.decode(errors="ignore").split("\n"):
            if re.match("^[ \t]*$", line):  # line is blank / whitespace
                continue
            if "{" in line:
                ent = dict()
            elif re.match('".*" ".*"', line):
                key, value = line[1:-1].split('" "')  # could extract with regex
                if key not in ent:
                    ent[key] = value
                else:
                    if isinstance(ent[key], list):
                        ent[key].append(value)
                    else:
                        ent[key] = [ent[key], value]
            elif "}" in line:
                bsp.ENTITIES.append(ent)
            elif line == b"\x00".decode():
                continue
            else:
                raise RuntimeError(f"Unexpected line in entities: {line.encode()}")
        del bsp.RAW_ENTITIES

        # GAME LUMP
        # LUMP_GAME_LUMP is compressed in individual segments.
        # The compressed size of a game lump can be determined by subtracting
        # the current game lump's offset with that of the next entry.
        # For this reason, the last game lump is always an empty dummy which
        # only contains the offset.
        ...
        # SURF_EDGES
        if hasattr(bsp, "RAW_SURFEDGES"):
            try:
                _format = bsp._engine_branch.SurfEdge._format
            except Exception:
                _format = branches.orange_box.SurfEdge._format
            # ^ is this try & except still nessecary?
            bsp.SURFEDGES = [s[0] for s in struct.iter_unpack(_format, bsp.RAW_SURFEDGES)]
            del bsp.RAW_SURFEDGES, _format
        # TEXDATA STRING DATA
        if hasattr(bsp, "RAW_TEXDATA_STRING_DATA"):
            tdsd = bsp.RAW_TEXDATA_STRING_DATA.split(b"\0")
            tdsd = [s.decode("ascii", errors="ignore") for s in tdsd]
            bsp.TEXDATA_STRING_DATA = tdsd
            del bsp.RAW_TEXDATA_STRING_DATA, tdsd
        # VISIBILITY
        # bsp.VISIBILITY = [v[0] for v in struct.iter_unpack("i", bsp.RAW_VISIBLITY)]
        # num_clusters = bsp.VISIBILITY[0]
        # for i in range(num_clusters):
        #     i = (2 * i) + 1
        #     pvs_offset = bsp.RAW_VISIBILITY[i]
        #     pas_offset = bsp.RAW_VISIBILITY[i + 1]
        #     # ^ pointers into RLE encoded bits mapping the PVS tree

        file.close()
        unpack_time = time.time() - start_time
        print(f"Loaded  {bsp.filename} in {unpack_time:.2f} seconds")

    def export(self, outfile):
        """Expects outfile to be a file with write bytes capability"""
        raise NotImplementedError()
        # # USE THE LUMP MAP! PRESERVE ORIGINAL FILE'S LUMP ORDER
        # outfile.write(b"VBSP")
        # outfile.write((20).to_bytes(4, "little")) # Engine version
        # offset = 0
        # length = 0
        # # CONVERT INTERNAL LUMPS TO RAW LUMPS
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

    def set_branch(self, branch: Union[str, types.ModuleType]):
        """Calling .set_branch(...) on a loaded .bsp will not convert it!"""
        if not isinstance(branch, (types.ModuleType, str)):
            raise NotImplementedError(f"Cannot load {branch} engine branch .bsp!")
        if isinstance(branch, types.ModuleType):
            # ^ custom python script (module; copy of branch definition script)
            # -- if experimenting / spelunking you can load your own script
            # expected contents of script:
            # - BSP_VERSION: int
            # - LUMP(enum.Enum): NAME_OF_LUMP = int
            # - lump_header_address: {NAME_OF_LUMP: header_offset_into_file}
            # - lump_classes: {"NAME_OF_LUMP": LumpClass}
            branch = branch
            return
        # if game is a string
        if branch.lower() == "unknown":
            try:  # guess .bsp format from version
                branch = branches.by_version[self.bsp_version]
            except KeyError:
                raise NotImplementedError(f"v{self.bsp_version} .bsp is not supported")
        else:
            try:  # lookup named branch / game
                branch = branches.by_name[branch]
            except KeyError:
                raise NotImplementedError(f"{branch} .bsp format is not supported, yet.")
        self.branch = branch
        # attach methods
        for method in getattr(branch, "methods", list()):
            method = types.MethodType(method, self)
            setattr(self, method.__name__, method)
        # could we also attach static methods?
