from collections import namedtuple
import enum  # for type hints
import os
import struct
from types import ModuleType
from typing import Dict, List

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
        self.REVISION = int.from_bytes(self.file.read(4), "little")
        # next 4 bytes should be int(127)
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
        """Defaults to overriding the original file"""
        if filename == "":
            filename = os.path.join(self.folder, self.filename)
        outfile = open(filename, "wb")
        outfile.write(struct.pack("4s3I", self.FILE_MAGIC, self.BSP_VERSION, self.REVISION, 127))
        # NOTE: some preprocessing checks / automation could be done here
        # - e.g. change TEXDATA_STRING_TABLE to match RAW_TEXDATA_STRING_DATA
        # - sort entities into .ent files based on classname
        # -- for r2+ .ent calcluate the model count
        lump_order = sorted([L for L in self.branch.LUMP], key=lambda L: self.HEADERS[L.name].offset)
        headers = dict()
        # ^ {"lump.name": LumpHeader / ExternalLumpHeader}
        external_lumps = {L.name for L in self.branch.LUMP if isinstance(self.HEADERS[L.name], ExternalLumpHeader)}
        # NOTE: external rBSP lumps seem to have an offsets past the final .bsp filesize
        # -- current theory: lumps are split into seperate files after compilation
        # -- external lumps also have a length of 0 in headers, likely indicating their abscense from the .bsp
        current_offset = 16 + (16 * 128)  # first byte after headers
        raw_lumps: Dict[str, bytes] = self.raw_lumps()
        # {"lump.name": b"raw lump data]"}
        for lump in lump_order:
            if lump.name not in raw_lumps:
                headers[lump.name] = LumpHeader(0, 0, 0, 0)
                continue
            if current_offset % 4 != 0:  # pad to start at the next multiple of 4 bytes
                current_offset += 4 - current_offset % 4
            offset = current_offset
            length = len(raw_lumps[lump.name])
            version = self.HEADERS[lump.name].version
            # ^ this will change when multi-version support is added
            fourCC = 0
            if lump.name in external_lumps:
                external_lump_filename = f"{os.path.basename(filename)}.{lump.value:04x}.bsp_lump"
                header = ExternalLumpHeader(offset, 0, version, fourCC, external_lump_filename, length)
            else:
                header = LumpHeader(offset, length, version, fourCC)
            headers[lump.name] = header
            current_offset += length
        # write headers
        for lump in self.branch.LUMP:
            offset, length, version, fourCC = headers[lump.name][:4]
            outfile.write(struct.pack("4I", offset, length, version, fourCC))
            # ^ offset, length, version, fourCC
            # fourCC is 0 because we aren't encoding
        # write lump contents
        for lump in lump_order:
            if lump.name not in raw_lumps:
                continue
            if lump.name in external_lumps:
                external_lump = f"{filename}.{lump.value:04x}.bsp_lump"
                with open(external_lump, "wb") as out_lumpfile:
                    out_lumpfile.write(raw_lumps[lump.name])
            else:
                padding_length = headers[lump.name].offset - outfile.tell()
                # NOTE: padding_length should not exceed 3
                if padding_length > 0:
                    outfile.write(b"\x00" * padding_length)
                outfile.write(raw_lumps[lump.name])
        outfile.close()
        # write .ent lumps
        for ent_variant in ("env", "fx", "script", "snd", "spawn"):
            ent_filename = f"{os.path.splitext(filename)[0]}_{ent_variant}.ent"
            with open(ent_filename, "wb") as ent_file:
                ent_file.write(self.HEADERS[f"ENTITIES_{ent_variant}"].encode("ascii"))
                ent_file.write(b"\n")
                ent_file.write(getattr(self, f"ENTITIES_{ent_variant}").as_bytes())

    def raw_lumps(self) -> Dict[str, bytes]:
        raw_lumps = dict()
        # ^ {"lump.name": b"raw lump data"}
        for lump in self.branch.LUMP:
            if not hasattr(self, lump.name) and not hasattr(self, f"RAW_{lump.name}"):
                continue  # ignore absent lumps
            if hasattr(self, f"RAW_{lump.name}"):
                raw_lump = getattr(self, f"RAW_{lump.name}")
            elif lump.name in self.branch.LUMP_CLASSES:
                lump_data = getattr(self, lump.name)
                _format = self.branch.LUMP_CLASSES[lump.name]._format
                if hasattr(self.branch.LUMP_CLASSES[lump.name], "flat"):
                    raw_lump = b"".join([struct.pack(_format, *x.flat()) for x in lump_data])
                else:  # assuming LumpClass(int)
                    raw_lump = struct.pack(f"{len(lump_data)}{_format}", *lump_data)
            elif lump.name in self.branch.SPECIAL_LUMP_CLASSES:
                raw_lump = getattr(self, lump.name).as_bytes()
            else:
                raise RuntimeError(f"Don't know how to export {lump.name} lump!")
            raw_lumps[lump.name] = raw_lump
        return raw_lumps
