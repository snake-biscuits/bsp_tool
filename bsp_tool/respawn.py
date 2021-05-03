from collections import namedtuple
import enum  # for type hints
import os
import struct
from types import ModuleType
from typing import Dict

from . import base
from . import lumps
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
    # -- https://noskill.gitbook.io/titanfall2/how-to-start-modding/modding-introduction/modding-tools

    def __init__(self, branch: ModuleType, filename: str = "untitled.bsp", autoload: bool = True):
        super(RespawnBsp, self).__init__(branch, filename, autoload)
        # NOTE: bsp revision appears before headers, not after (as in Valve's variant)

    def _read_header(self, LUMP: enum.Enum) -> (LumpHeader, bytes):
        """Read a lump from self.file, while it is open (during __init__ only)"""
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
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        file_magic = self.file.read(4)
        if file_magic != self.FILE_MAGIC:
            raise RuntimeError(f"{self.file} is not a valid .bsp!")
        self.BSP_VERSION = int.from_bytes(self.file.read(4), "little")
        self.REVISION = int.from_bytes(self.file.read(4), "little")  # just for rBSP
        assert int.from_bytes(self.file.read(4), "little") == 127
        self.file.seek(0, 2)  # move cursor to end of file
        self.bsp_file_size = self.file.tell()

        self.loading_errors: Dict[str, Exception] = dict()
        # internal & external lumps
        # TODO: break down into a _load_lump method, allowing reloading
        for LUMP in self.branch.LUMP:  # external .bsp.00XX.bsp_lump lump
            external = False
            lump_filename = f"{self.filename}.{LUMP.value:04x}.bsp_lump"
            lump_header = self._read_header(LUMP)
            if lump_filename in self.associated_files:  # .bsp_lump file exists
                external = True
                lump_filename = os.path.join(self.folder, lump_filename)
                lump_filesize = os.path.getsize(os.path.join(self.folder, lump_filename))
                assert lump_header.length == lump_filesize, "huh. that's never happened before"
                lump_header = ExternalLumpHeader(*lump_header, lump_filename, lump_filesize)
            self.HEADERS[LUMP.name] = lump_header
            if lump_header.length == 0:
                continue  # skip empty lumps
            if LUMP.name in self.branch.SPECIAL_LUMP_CLASSES:
                SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP.name]
                if not external:
                    self.file.seek(lump_header.offset)
                    lump_data = self.file.read(lump_header.length)
                else:
                    lump_data = open(lump_header.filename, "rb").read()
                try:
                    BspLump = SpecialLumpClass(lump_data)
                except Exception as exc:
                    self.loading_errors[LUMP.name] = exc
                    BspLump = lumps.create_RawBspLump(self.file, lump_header)
            elif LUMP.name in self.branch.BASIC_LUMP_CLASSES:
                LumpClass = self.branch.BASIC_LUMP_CLASSES[LUMP.name]
                BspLump = lumps.create_BasicBspLump(self.file, lump_header, LumpClass)
            else:  # LumpClass / RawBspLump
                LumpClass = self.branch.LUMP_CLASSES.get(LUMP.name, None)
                try:
                    BspLump = lumps.create_BspLump(self.file, lump_header, LumpClass)
                except Exception as exc:
                    self.loading_errors[LUMP.name] = exc
                    BspLump = lumps.create_RawBspLump(self.file, lump_header)
            setattr(self, LUMP.name, BspLump)
        # TODO: (maybe) give a pretty ascii visualisation of the .bsp file
        # -- ^ could be pretty handy for understanding re-saving actually ^

        # .ent files
        for ent_filetype in ("env", "fx", "script", "snd", "spawn"):
            entity_file = f"{self.filename[:-4]}_{ent_filetype}.ent"  # e.g. "mp_glitch_env.ent"
            if entity_file in self.associated_files:
                with open(os.path.join(self.folder, entity_file), "rb") as ent_file:
                    LUMP_name = f"ENTITIES_{ent_filetype}"
                    self.HEADERS[LUMP_name] = ent_file.readline().decode().rstrip("\n")
                    # Titanfall:  ENTITIES01
                    # Apex Legends:  ENTITIES02 model_count=0
                    setattr(self, LUMP_name, shared.Entities(ent_file.read()))
                    # each .ent file also has a null byte at the very end

    def save_as(self, filename: str, single_file: bool = False):
        lump_order = sorted([L for L in self.branch.LUMP], key=lambda L: self.HEADERS[L.name].offset)
        # ^ {"lump.name": LumpHeader / ExternalLumpHeader}
        external_lumps = {L.name for L in self.branch.LUMP if isinstance(self.HEADERS[L.name], ExternalLumpHeader)}
        if single_file:
            external_lumps = set()
        raw_lumps: Dict[str, bytes] = dict()
        # ^ {"LUMP.name": b"raw lump data]"}
        for LUMP in self.branch.LUMP:
            lump_bytes = self.lump_as_bytes(LUMP.name)
            if lump_bytes != b"":  # don't write empty lumps
                raw_lumps[LUMP.name] = lump_bytes
        # recalculate headers
        current_offset = 16 + (16 * 128)  # first byte after headers
        headers = dict()
        for LUMP in lump_order:
            if LUMP.name not in raw_lumps:
                version = self.HEADERS[LUMP.name].version  # PHYSICSLEVEL needs version preserved
                headers[LUMP.name] = LumpHeader(0, 0, version, 0)
                continue
            if current_offset % 4 != 0:  # pad to start at the next multiple of 4 bytes
                current_offset += 4 - current_offset % 4
            offset = current_offset
            length = len(raw_lumps[LUMP.name])
            version = self.HEADERS[LUMP.name].version
            # ^ this will change when multi-version support is added
            fourCC = 0  # fourCC is 0 because we aren't encoding
            if LUMP.name in external_lumps:
                external_lump_filename = f"{os.path.basename(filename)}.{LUMP.value:04x}.bsp_lump"
                header = ExternalLumpHeader(offset, 0, version, fourCC, external_lump_filename, length)
                # ^ offset, length, version, fourCC
            else:
                header = LumpHeader(offset, length, version, fourCC)
            headers[LUMP.name] = header  # recorded for noting padding
            current_offset += length
        del current_offset
        # make file
        os.makedirs(os.path.dirname(os.path.realpath(filename)), exist_ok=True)
        outfile = open(filename, "wb")
        outfile.write(struct.pack("4s3I", self.FILE_MAGIC, self.BSP_VERSION, self.REVISION, 127))
        # write headers
        for LUMP in self.branch.LUMP:
            header = headers[LUMP.name]
            outfile.write(struct.pack("4I", header.offset, header.length, header.version, header.fourCC))
        # write lump contents (cannot be done until headers allocate padding)
        for LUMP in lump_order:
            if LUMP.name not in raw_lumps:
                continue
            # write external lump
            if LUMP.name in external_lumps:
                external_lump = f"{filename}.{LUMP.value:04x}.bsp_lump"
                with open(external_lump, "wb") as out_lumpfile:
                    out_lumpfile.write(raw_lumps[LUMP.name])
            # write lump to file
            else:
                padding_length = headers[LUMP.name].offset - outfile.tell()
                if padding_length > 0:  # NOTE: padding_length should not exceed 3
                    outfile.write(b"\x00" * padding_length)
                outfile.write(raw_lumps[LUMP.name])
        outfile.close()  # main .bsp is written
        # write .ent lumps
        for ent_variant in ("env", "fx", "script", "snd", "spawn"):
            if not hasattr(self, f"ENTITIES_{ent_variant}"):
                continue
            ent_filename = f"{os.path.splitext(filename)[0]}_{ent_variant}.ent"
            with open(ent_filename, "wb") as ent_file:
                # TODO: generate header if none exists
                ent_file.write(self.HEADERS[f"ENTITIES_{ent_variant}"].encode("ascii"))
                ent_file.write(b"\n")
                ent_file.write(getattr(self, f"ENTITIES_{ent_variant}").as_bytes())

    def save(self, single_file: bool = False):
        self.save_as(os.path.join(self.folder, self.filename), single_file)
        self._preload()  # reload lumps, clearing all BspLump._changes
