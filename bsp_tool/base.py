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
    _engine_branch: types.ModuleType
    associated_files: List[str]
    bsp_version: int
    bytesize: int
    filename: str
    folder: str
    log: List[str]
    lump_map: Dict[int, LumpHeader]
    # LUMP List[LUMP_struct]

    def __init__(self, filename: str, game: Union[str, types.ModuleType] = "unknown", external_lumps: bool = False):
        assert filename.endswith(".bsp")
        filename = os.path.realpath(filename)  # make sure we know the folder
        self.filename = os.path.basename(filename)
        self.folder = os.path.dirname(filename)
        local_files = os.listdir(self.folder)
        def is_related(f): return f.startswith(os.path.splitext(self.filename)[0])
        self.associated_files = [f for f in local_files if is_related(f)]
        file = open(filename, "rb")
        file_magic = file.read(4)
        if file_magic == b"rBSP":  # rBSP = Respawn BSP (Titanfall/Apex Legends)
            external_lumps = True  # most lumps are external
        elif file_magic not in (b"VBSP", b"rBSP"):
            # note that on consoles file_magic is big endian (reversed)
            raise RuntimeError(f"{file} is not a .bsp!")
        self.bsp_version = int.from_bytes(file.read(4), "little")

        self.set_branch(game)

        print(f"Loading {self.filename} (BSP v{self.bsp_version})...")
        # rBSP map revision is before headers, VBSP is after
        file.read()  # move cursor to end of file
        self.bytesize = file.tell()

        self.log: List[str] = []
        self.lump_map: Dict[int, LumpHeader] = {}
        # ^ {ID: LumpHeader}
        start_time = time.time()
        # TODO: store .bsp lumps as INTERNAL_ when external_lumps == True
        for ID in self._engine_branch.LUMP:
            lump_filename = f"{self.filename}.{ID.value:04x}.bsp_lump"
            # ^ rBSP .bsp_lump naming convention
            if external_lumps is True and lump_filename in self.associated_files:
                # vBSP lumpfiles have headers, rBSP lumpfiles are headerless
                # mp_drydock only has 72 bsp_lump files
                # however other lumps within mp_drydock.bsp itself contain data
                data = open(f"{os.path.join(self.folder, lump_filename)}", "rb").read()
                # self.log.append(f"overwrote {ID.name} lump with external .bsp_lump")
            else:
                if external_lumps is True and file_magic != b"rBSP":
                    self.log.append(f"external  {ID.name} lump not found")
                data = read_lump(file, self._engine_branch.lump_header_address[ID])
            if data is not None:  # record the .bsp lump headers (could be implemented better)
                file.seek(self._engine_branch.lump_header_address[ID])
                self.lump_map[ID] = LumpHeader(*[int.from_bytes(file.read(4), "little") for i in range(4)])
                setattr(self, "RAW_" + ID.name, data)
            # else: # lump is empty

        # PROCESS RAW LUMPS (this could be it's own method)
        lump_classes: Dict = self._engine_branch.lump_classes
        # ^ {"LUMP_NAME": LumpClass}
        for LUMP, lump_class in lump_classes.items():
            if not hasattr(self, f"RAW_{LUMP}"):
                continue  # lump was empty, skip
            try:  # implement -Warn system here
                setattr(self, LUMP, [])
                RAW_LUMP = getattr(self, f"RAW_{LUMP}")
                for data in struct.iter_unpack(lump_class._format, RAW_LUMP):
                    if len(data) == 1:
                        data = data[0]
                    getattr(self, LUMP).append(lump_class(data))
                delattr(self, f"RAW_{LUMP}")
            except struct.error:
                struct_size = struct.calcsize(lump_class._format)
                self.log.append(f"ERROR PARSING {LUMP}:\n{LUMP} lump is an unusual size ({len(RAW_LUMP)} / {struct_size})." +
                                "Wrong engine branch?")
                delattr(self, LUMP)
            except Exception as exc:
                self.log.append(f"ERROR PARSING {LUMP}:\n{exc.__class__.__name__}: {exc}")
                # raise exc

        if len(self.log) > 0:
            print(*self.log, sep="\n")

        # SPECIAL LUMPS

        # ENTITIES
        # TODO: use fgdtools to fully unstringify entities
        # rBSP .bsps have 5 associated entity files beginning with "ENTITIES01\n"
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
                else:
                    if isinstance(ent[key], list):
                        ent[key].append(value)
                    else:
                        ent[key] = [ent[key], value]
            elif "}" in line:
                self.ENTITIES.append(ent)
            elif line == b"\x00".decode():
                continue
            else:
                raise RuntimeError(f"Unexpected line in entities: {line.encode()}")
        del self.RAW_ENTITIES

        # GAME LUMP
        # LUMP_GAME_LUMP is compressed in individual segments.
        # The compressed size of a game lump can be determined by subtracting
        # the current game lump's offset with that of the next entry.
        # For this reason, the last game lump is always an empty dummy which
        # only contains the offset.
        ...
        # SURF_EDGES
        if hasattr(self, "RAW_SURFEDGES"):
            try:
                _format = self._engine_branch.SurfEdge._format
            except Exception:
                _format = branches.orange_box.SurfEdge._format
            # ^ is this try & except still nessecary?
            self.SURFEDGES = [s[0] for s in struct.iter_unpack(_format, self.RAW_SURFEDGES)]
            del self.RAW_SURFEDGES, _format
        # TEXDATA STRING DATA
        if hasattr(self, "RAW_TEXDATA_STRING_DATA"):
            tdsd = self.RAW_TEXDATA_STRING_DATA.split(b"\0")
            tdsd = [s.decode("ascii", errors="ignore") for s in tdsd]
            self.TEXDATA_STRING_DATA = tdsd
            del self.RAW_TEXDATA_STRING_DATA, tdsd
        # VISIBILITY
        # self.VISIBILITY = [v[0] for v in struct.iter_unpack("i", self.RAW_VISIBLITY)]
        # num_clusters = self.VISIBILITY[0]
        # for i in range(num_clusters):
        #     i = (2 * i) + 1
        #     pvs_offset = self.RAW_VISIBILITY[i]
        #     pas_offset = self.RAW_VISIBILITY[i + 1]
        #     # ^ pointers into RLE encoded bits mapping the PVS tree

        file.close()
        unpack_time = time.time() - start_time
        print(f"Loaded  {self.filename} in {unpack_time:.2f} seconds")

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

    def set_branch(self, game: Union[str, types.ModuleType]):
        """Warning! calling .set_branch on a loaded .bsp will not convert it!"""
        if not isinstance(game, (types.ModuleType, str)):
            raise NotImplementedError(f"Cannot load {game} engine branch .bsp!")
        if isinstance(game, types.ModuleType):
            # ^ custom python script (module; copy of branch definition script)
            # -- if experimenting / spelunking the user can use a script "live"
            # expected contents:
            # - bsp_version: int
            # - LUMP(enum.Enum) - NAME_OF_LUMP = header_number: int
            # - lump_header_address - {NAME_OF_LUMP: header_offset_into_file}
            # - lump_classes - {"NAME_OF_LUMP": lump_class}
            branch = game
            return
        # game is a string
        if game.lower() == "unknown":
            try:  # guess .bsp format from version
                branch = branches.by_version[self.bsp_version]
            except KeyError:
                raise NotImplementedError(f"v{self.bsp_version} .bsp is not supported")
        else:
            try:  # lookup named branch / game
                branch = branches.by_name[game]
            except KeyError:
                raise NotImplementedError(f"{game} .bsp format is not supported, yet.")
        self._engine_branch = branch
        # attach methods
        for method in getattr(branch, "methods", list()):
            method = types.MethodType(method, self)
            setattr(self, method.__name__, method)
        # could we also attach static methods?
