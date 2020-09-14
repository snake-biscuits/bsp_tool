import collections
import lzma
import os
import re
import struct
import time
import types

from . import mods


lump_header = collections.namedtuple("lump_header",
                    ["offset", "length", "version", "fourCC"])

def read_lump(file, header_address):
    file.seek(header_address)
    offset = int.from_bytes(file.read(4), "little")
    length = int.from_bytes(file.read(4), "little")
    version = int.from_bytes(file.read(4), "little")
    fourCC = int.from_bytes(file.read(4), "little")
    if length == 0:
        return
    file.seek(offset)
    data = file.read(length)
    if fourCC != 0: # lump is compressed
        source_lzma_header = struct.unpack("3I5c", data[:17])
        actual_size = source_lzma_header[1]
        compressed_size = source_lzma_header[2]
        properties = b"".join(source_lzma_header[3:])
        _filter = lzma._decode_filter_properties(lzma.FILTER_LZMA1, properties)
        decompressor = lzma.LZMADecompressor(lzma.FORMAT_RAW, None, [_filter])
        data = decompressor.decompress(data[17:])
        if len(data) != actual_size:
            data = data[:actual_size]
    return data


class bsp():
    def __init__(self, filename, game="unknown", lump_files=False):
        # NOTE FILES RELATED TO THIS .BSP
        if not filename.endswith(".bsp"):
            filename += ".bsp"
        self.filename = os.path.basename(filename)
        self.folder = os.path.dirname(filename)
        local_files = os.listdir(self.folder)
        is_related = lambda n: n.startswith(os.path.splitext(self.filename)[0])
        self.associated_files = [n for n in local_files if is_related(n)]
        # BEGIN READING .BSP FILE
        file = open(filename, "rb")
        file_magic = file.read(4)
        if file_magic == b"rBSP": # rBSP = Respawn BSP (Titanfall/Apex Legends)
            lump_files = True # most lumps are external
        elif file_magic not in (b"VBSP", b"rBSP"): 
            # note that on consoles file_magic is big endian
            raise RuntimeError(f"{file} is not a .bsp!")
        # GET SPECIFIC .BSP FORMAT
        self.bsp_version = int.from_bytes(file.read(4), "little")
        if game.lower() == "unknown": # guess .bsp format from version
            try:
                mod = mods.by_version[self.bsp_version]
            except:
                raise NotImplementedError(f"v{self.bsp_version} .bsp is not supported")
        elif isinstance(game, types.ModuleType):
            mod = game # "game" is a python script
            # this script is expected to contain:
            # - bsp_version
            # - LUMP(enum.Enum) - NAME_OF_LUMP = header_number
            # - lump_header_address - {NAME_OF_LUMP: header_offset_into_file}
            # - methods - {"function": function}
            # - lump_classes - {"NAME_OF_LUMP": lump_class}  
        else:
            try:
                mod = mods.by_name[game]
            except KeyError:
                raise NotImplementedError(f"{game} .bsp is not supported")
        self.mod = mod
        # ATTACH METHODS DEFINED BY IN self.mod
        class_method = lambda function: lambda *args: function(self, *args)
        for method_name, method in mod.methods.items():
            setattr(self, method_name, class_method(method))
        print(f"Loading {self.filename} (BSP v{self.bsp_version})...")
        # rBSP map revision is before headers, VBSP is after
        file.read() # move cursor to end of file
        self.bytesize = file.tell()

        self.log = []
        self.lump_map = {}
        start_time = time.time()
        # TODO: store .bsp lumps as INTERNAL_ when lump_files == True
        for ID in self.mod.LUMP:
            lump_filename = f"{self.filename}.{ID.value:04x}.bsp_lump"
            # ^ rBSP .bsp_lump naming convention
            if lump_files == True and lump_filename in self.associated_files:
                # vBSP lumpfiles have headers, rBSP lumpfiles are headerless
                # mp_drydock only has 72 bsp_lump files
                # however other lumps within mp_drydock.bsp itself contain data
                data = open(f"{os.path.join(self.folder, lump_filename)}", "rb").read()
##                self.log.append(f"overwrote {ID.name} lump with external .bsp_lump")
            else:
                if lump_files == True and file_magic != b'rBSP':
                    self.log.append(f"external  {ID.name} lump not found")
                data = read_lump(file, self.mod.lump_header_address[ID])
            if data is not None: # record the .bsp lump headers (could be implemented better)
                file.seek(self.mod.lump_header_address[ID])
                self.lump_map[ID] = lump_header(*[int.from_bytes(file.read(4), "little") for i in range(4)])
                setattr(self, "RAW_" + ID.name, data)
            # else: # lump is empty

        # begin processing lumps
        lump_classes = self.mod.lump_classes # self.mod is a module
        for LUMP, lump_class in lump_classes.items():
            if not hasattr(self, f"RAW_{LUMP}"):
                continue # skip unused lumps
            try: # implement -Warn system here
                setattr(self, LUMP, [])
                RAW_LUMP = getattr(self, f"RAW_{LUMP}")
                for data in struct.iter_unpack(lump_class._format, RAW_LUMP):
                    if len(data) == 1:
                        data = data[0]
                    getattr(self, LUMP).append(lump_class(data))
                delattr(self, f"RAW_{LUMP}")
            except struct.error as exc:
                struct_size = struct.calcsize(lump_class._format)
                self.log.append(f"ERROR PARSING {LUMP}:\n{LUMP} lump is an unusual size ({len(RAW_LUMP)} / {struct_size}). Wrong mod?")
                delattr(self, LUMP)
##                raise exc
            except Exception as exc:
                self.log.append(f"ERROR PARSING {LUMP}:\n{exc.__class__.__name__}: {exc}")
##                raise exc

        if self.log != []:
            print(*self.log, sep="\n")

        ### SPECIAL LUMPS ###
        #-- ENTITIES --#
        # TODO: use fgdtools to fully unstringify entities
        # rBSP .bsps have 5 associated entity files beginning with "ENTITIES01\n"
        self.ENTITIES = self.RAW_ENTITIES.decode(errors="ignore")
        entities = []
        indent = 0
        for line in self.ENTITIES.split("\n"):
            if re.match("^[ \t]*$", line): # whitespace
                continue
            if "{" in line:
                ent = dict()
            elif re.match('".*" ".*"', line):
                key, value = line[1:-1].split('" "')
                if key not in ent:
                    ent[key] = value
                else:
                    if isinstance(ent[key], list):
                        ent[key].append(value)
                    else:
                        ent[key] = [ent[key], value]
            elif "}" in line:
                entities.append(ent)
            elif line == b"\x00".decode():
                continue
            else:
                raise RuntimeError(f"Unexpected line in entities: {line.encode()}")
        self.ENTITIES = entities
        del self.RAW_ENTITIES, entities
        #-- GAME LUMP --#
        # LUMP_GAME_LUMP is compressed in individual segments.
        # The compressed size of a game lump can be determined by subtracting
        # the current game lump's offset with that of the next entry.
        # For this reason, the last game lump is always an empty dummy which
        # only contains the offset.
        ...
        #-- SURF_EDGES --#
        if hasattr(self, "RAW_SURFEDGES"):
            try:
                _format = self.mod.surf_edge._format
            except:
                _format = mods.team_fortress2.surf_edge._format
            self.SURFEDGES = [s[0] for s in struct.iter_unpack(_format, self.RAW_SURFEDGES)]
            del self.RAW_SURFEDGES, _format
        #-- TEXDATA STRING DATA --#
        if hasattr(self, "RAW_TEXDATA_STRING_DATA"):
            tdsd = self.RAW_TEXDATA_STRING_DATA.split(b"\0")
            tdsd = [s.decode("ascii", errors="ignore") for s in tdsd]
            self.TEXDATA_STRING_DATA = tdsd
            del self.RAW_TEXDATA_STRING_DATA, tdsd
        #-- VISIBILITY --#
##        self.VISIBILITY = [v[0] for v in struct.iter_unpack("i", self.RAW_VISIBLITY)]
##        num_clusters = self.VISIBILITY[0]
##        for i in range(num_clusters):
##            i = (2 * i) + 1
##            pvs_offset = self.RAW_VISIBILITY[i]
##            pas_offset = self.RAW_VISIBILITY[i + 1]
##            # pointers into RLE encoded bits mapping the PVS tree

        file.close()
        unpack_time = time.time() - start_time
        print(f"Loaded  {self.filename} in {unpack_time:.2f} seconds")

    def export(self, outfile):
        """Expects outfile to be a file with write bytes capability"""
        raise NotImplementedError()
##        # USE THE LUMP MAP! PRESERVE ORIGINAL FILE'S LUMP ORDER
##        outfile.write(b"VBSP")
##        outfile.write((20).to_bytes(4, "little")) # Engine version
##        offset = 0
##        length = 0
##        # CONVERT INTERNAL LUMPS TO RAW LUMPS
##        for LUMP in self.mod.LUMP:
##            # special lumps:
##            #  - ENTITIES
##            #  - GAME_LUMP
##            #  - SURF_EDGES
##            #  - VISIBILITY
##            if hasattr(self, f"RAW_{LUMP}"):
##                continue
##            elif hasattr(self, LUMP):
##                lump_format = self.mod.lump_classes[LUMP]._format
##                pack_lump = lambda c: struct.pack(lump_format, *c.flat())
##                setattr(self, f"RAW_{LUMP}", map(pack_lump, getattr(self, LUMP)))
##            # seek lump header
##            outfile.write(offset.to_bytes(4, "little"))
##            length = len(getattr(self, ID.name, "RAW_" + ID.name))
##            offset += length
##            outfile.write(b"0000") # lump version (actually important)
##            outfile.write(b"0000") # lump fourCC (only for compressed)
##            # seek lump start in file
##            outfile.write(getattr(self, ID.name, "RAW_" + ID.name))
##        outfile.write(b"0001") # map revision
