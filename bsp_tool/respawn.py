from collections import namedtuple
import enum  # for type hints
import os
import struct
from types import ModuleType
from typing import Dict

from . import base
from .base import LumpHeader
from .branches import shared


ExternalLumpHeader = namedtuple("ExternalLumpHeader", ["offset", "length", "version", "fourCC", "filename", "filesize"])


class RespawnBsp(base.Bsp):
    # https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Titanfall
    # https://raw.githubusercontent.com/Wanty5883/Titanfall2/master/tools/TitanfallMapExporter.py
    FILE_MAGIC = b"rBSP"
    # NOTE: respawn .bsp files are usually stored in .vpk files
    # -- Respawn's .vpk format is different to Valve's
    # -- You'll need the Titanfall specific .vpk tool to extract maps

    def __init__(self, branch: ModuleType, filename: str = "untitled.bsp", autoload: bool = True):
        super(RespawnBsp, self).__init__(branch, filename)
        # NOTE: bsp revision appears before headers, not after (as in Valve's variant)

    def read_lump(self, LUMP: enum.Enum) -> (LumpHeader, bytes):
        """Only reads lumps stored in the main .bsp file"""
        # header
        self.file.seek(self.branch.lump_header_address[LUMP])
        offset, length, version, fourCC = struct.unpack("4i", self.file.read(16))
        header = LumpHeader(offset, length, version, fourCC)
        if length == 0:
            return header, None
        # lump data
        self.file.seek(offset)
        data = self.file.read(length)
        return header, data

    def parse_lump(self, LUMP, data):
        """Convert lump data to LumpClass / SpecialLumpClass"""
        # TODO: simplify exception handling
        # TODO: simplify loading lumps of type List[int]
        if LUMP in self.branch.LUMP_CLASSES:
            LumpClass = self.branch.LUMP_CLASSES[LUMP]
            try:
                setattr(self, LUMP, list())
                for _tuple in struct.iter_unpack(LumpClass._format, data):
                    if len(_tuple) == 1:  # if ._format is 1 variable, return the 1 variable, not a len(1) tuple
                        _tuple = _tuple[0]  # there has to be a better way than this
                    getattr(self, LUMP).append(LumpClass(_tuple))
                # TODO: setattr(self, LUMP, [*map(LumpClass, struct.iter_unpack(LumpClass._format, lump_data))])
            except struct.error:  # lump cannot be divided into a whole number of LumpClasses
                struct_size = struct.calcsize(LumpClass._format)
                self.loading_errors.append(f"ERROR PARSING {LUMP}:\n"
                                           f"{LUMP} lump is an unusual size ({len(data)} / {struct_size})."
                                           " Wrong engine branch?")
                setattr(self, "RAW_" + LUMP, data)
                delattr(self, LUMP)
            except Exception as exc:  # assuming some error occured initialising a LumpClass
                self.loading_errors.append(f"ERROR PARSING {LUMP}:\n{exc.__class__.__name__}: {exc}")
                # TODO: save a traceback for debugging
        elif LUMP in self.branch.SPECIAL_LUMP_CLASSES:
            setattr(self, LUMP, self.branch.SPECIAL_LUMP_CLASSES[LUMP](data))
            # ^ self.SPECIAL_LUMP = SpecialLumpClass(data)
        else:
            setattr(self, "RAW_" + LUMP, data)

    def load_lumps(self):
        for LUMP in self.branch.LUMP:
            # external .bsp.00XX.bsp_lump lump
            lump_filename = f"{self.filename}.{LUMP.value:04x}.bsp_lump"
            if lump_filename in self.associated_files:  # .bsp_lump file exists
                self.file.seek(self.branch.lump_header_address[LUMP])  # internal .bsp lump header
                offset, length, version, fourCC = struct.unpack("4i", self.file.read(16))
                with open(os.path.join(self.folder, lump_filename), "rb") as lump_file:
                    data = lump_file.read()
                lump_filesize = len(data)
                header = ExternalLumpHeader(offset, length, version, fourCC, lump_filename, lump_filesize)
            # internal .bsp lump
            else:
                header, data = self.read_lump(LUMP)
            self.HEADERS[LUMP.name] = header
            if data is not None:
                self.parse_lump(LUMP.name, data)
        # .ent files
        for ent_filetype in ("env", "fx", "script", "snd", "spawn"):
            entity_file = f"{self.filename[:-4]}_{ent_filetype}.ent"  # e.g. "mp_glitch_env.ent"
            if entity_file in self.associated_files:
                with open(os.path.join(self.folder, entity_file), "rb") as ent_file:
                    lump_name = f"ENTITIES_{ent_filetype}"
                    self.HEADERS[lump_name] = ent_file.readline().decode().rstrip("\n")
                    # Titanfall:  ENTITIES01
                    # Apex Legends:  ENTITIES02 model_count=0
                    setattr(self, lump_name, shared.Entities(ent_file.read()))
                    # each .ent file also has a null byte at the very end

    def save_as(self, filename=""):
        if filename == "":
            filename = os.path.join(self.folder, self.filename)
        outfile = open(filename, "wb")
        outfile.write(struct.pack("4s3I", self.FILE_MAGIC, self.BSP_VERSION, 30, 127))
        # ^ file-magic, bsp format version, map revision, lump count - 1
        # TODO: get map revision when loading the .bsp
        # - requires overriding the base.Bsp load() method
        lump_order = sorted([L for L in self.branch.LUMP if self.HEADERS[L.name].length != 0],
                            key=lambda L: self.HEADERS[L.name].offset)
        # ^ order of all internal lumps
        lump_offsets = dict()
        # ^ {"lump.name": offset}
        offset = 16 + (128 * 16)  # first byte after main .bsp header
        raw_lumps = self.raw_lumps()
        for lump in lump_order:
            # TODO: make sure each lump is padded to start at the next multiple of 4 bytes
            lump_offsets[lump.name] = offset
            offset += len(raw_lumps[lump.name])
        del offset
        external_lumps = set()
        # ^ {"lump.name"}
        for lump in self.branch.LUMP:
            old_header = self.HEADERS[lump.name]
            if isinstance(old_header, ExternalLumpHeader):
                external_lumps.add(lump.name)  # write to .bsp_lump, not main .bsp
                # NOTE: so far external rBSP lumps seem to have an offset of the final .bsp filesize
            if old_header.length == 0:
                lump_length = 0
            else:
                lump_length = len(raw_lumps[lump.name])
            lump_offset = lump_offsets.get(lump.name, old_header.offset)
            # ^ get new lump_offset from raw_lumps, if calculated
            outfile.write(struct.pack("4I", lump_offset, lump_length, old_header.version, 0))
            # ^ offset, length, version, fourCC
            # fourCC is 0 because we aren't encoding
        # TODO: write raw_lumps to main .bsp / external .bsp_lump files

    def raw_lumps(self) -> Dict[str, bytes]:
        raw_lumps = dict()
        # ^ {"lump.name": b"raw lump data"}
        for lump in self.branch.LUMP:
            if self.HEADERS[lump.name].length == 0:  # does this also skip external lumps?
                continue
            if hasattr(self, f"RAW_{lump.name}"):
                raw_lump = getattr(self, f"RAW_{lump.name}")
            elif lump.name in self.branch.LUMP_CLASSES:
                _format = self.branch.LUMP_CLASSES[lump.name]._format
                raw_lump = b"".join([struct.pack(_format, *x) for x in getattr(self, lump.name)])
            elif lump.name in self.branch.SPECIAL_LUMP_CLASSES:
                raw_lump = getattr(self, lump.name).as_bytes()
            else:
                raise RuntimeError(f"Don't know how to export {lump.name} lump!")
            raw_lumps[lump.name] = raw_lump
        return raw_lumps
