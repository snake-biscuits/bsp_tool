from collections import namedtuple
import enum  # for type hints
import os
import struct
from types import ModuleType

from . import base
from .base import LumpHeader
from .branches import respawn, shared


ExternalLumpHeader = namedtuple("ExternalLumpHeader", ["offset", "length", "version", "fourCC", "filename", "filesize"])


class RespawnBsp(base.Bsp):
    # https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Titanfall
    # https://raw.githubusercontent.com/Wanty5883/Titanfall2/master/tools/TitanfallMapExporter.py
    FILE_MAGIC = b"rBSP"
    branch = respawn.titanfall2  # default branch
    # NOTE: these files are usually stored in .vpk files
    # -- Respawn's .vpk format is different to Valve's
    # -- You'll need the Titanfall specific .vpk tool to extract maps

    def __init__(self, branch: ModuleType = branch, filename: str = "untitled.bsp", autoload: bool = True):
        super(RespawnBsp, self).__init__(branch, filename)
        # NOTE: bsp revision appears before headers, not after (as in Valve's variant)

    def read_lump(self, LUMP: enum.Enum) -> (LumpHeader, bytes):  # just .bsp internal lumps
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
        """convert lump data to LumpClasses"""
        if LUMP in self.branch.LUMP_CLASSES:
            LumpClass = self.branch.LUMP_CLASSES[LUMP]
            try:
                setattr(self, LUMP, list())
                for _tuple in struct.iter_unpack(LumpClass._format, data):
                    if len(_tuple) == 1:  # if ._format is 1 variable, return the 1 variable, not a len(1) tuple
                        _tuple = _tuple[0]  # ^ there has to be a better way than this
                    getattr(self, LUMP).append(LumpClass(_tuple))
                # WHY NOT: setattr(self, LUMP, [*map(LumpClass, struct.iter_unpack(LumpClass._format, lump_data))])
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
            lump_filename = f"{self.filename}.{LUMP.value:04x}.bsp_lump"
            if lump_filename in self.associated_files:  # .bsp_lump file exists
                with open(os.path.join(self.folder, lump_filename), "rb") as lump_file:
                    data = lump_file.read()
                # the .bsp_lump file has no header, this is just the matching header in the .bsp
                # unsure how / if headers for external .bsp_lump affect anything
                self.file.seek(self.branch.lump_header_address[LUMP])  # internal .bsp lump header
                offset, length, version, fourCC = struct.unpack("4i", self.file.read(16))
                lump_filesize = len(data)
                header = ExternalLumpHeader(offset, length, version, fourCC, lump_filename, lump_filesize)
                # TODO: save contents of matching .bsp lump as INTERNAL_<LUMPNAME> / RAW_INTERNAL_<LUMPNAME>
            else:  # .bsp internal lump
                header, data = self.read_lump(LUMP)
            self.HEADERS[LUMP.name] = header
            if data is not None:
                self.parse_lump(LUMP.name, data)
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
        # look at self.HEADERS & self.associated_files to see which lumps are saved externally
