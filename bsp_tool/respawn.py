from collections import namedtuple
import enum
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
    """Respawn Entertainment's Titanfall Engine .bsp (rBSP v29 -> 50.1)"""
    # https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Titanfall
    # https://raw.githubusercontent.com/Wanty5883/Titanfall2/master/tools/TitanfallMapExporter.py
    file_magic = b"rBSP"
    lump_count: int
    entity_headers: Dict[str, str]g
    # {"LUMP_NAME": "header text"}

    def __init__(self, branch: ModuleType, filename: str = "untitled.bsp", autoload: bool = True):
        self.entity_headers = dict()
        super(RespawnBsp, self).__init__(branch, filename, autoload)
        # NOTE: bsp revision appears before headers, not after (as in Valve's variant)

    def _read_header(self, LUMP: enum.Enum) -> LumpHeader:
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
        assert file_magic == self.file_magic, f"{self.file} is not a valid .bsp!"
        self.bsp_version = int.from_bytes(self.file.read(4), "little")
        if self.bsp_version > 0xFFFF:  # Apex Legends Season 11+
            self.bsp_version = (self.bsp_version & 0xFFFF, self.bsp_version >> 16)  # major, minor
        # NOTE: Legion considers the second short to be a flag for streaming
        # Likely because 49.1 & 50.1 b"rBSP" moved all lumps to .bsp_lump
        # NOTE: various mixed bsp versions exist in depot/ for Apex S11+
        self.revision = int.from_bytes(self.file.read(4), "little")
        self.lump_count = int.from_bytes(self.file.read(4), "little")
        assert self.lump_count == 127, "irregular RespawnBsp lump_count"
        self.file.seek(0, 2)  # move cursor to end of file
        self.bsp_file_size = self.file.tell()

        self.loading_errors: Dict[str, Exception] = dict()
        # internal & external lumps
        # TODO: store both internal & external lumps
        # TODO: break down into a _load_lump method, allowing reloading per lump
        for LUMP in self.branch.LUMP:  # external .bsp.00XX.bsp_lump lump
            external = False
            lump_filename = f"{self.filename}.{LUMP.value:04x}.bsp_lump"
            lump_header = self._read_header(LUMP)
            if lump_filename in self.associated_files:  # .bsp_lump file exists
                external = True
                lump_filename = os.path.join(self.folder, lump_filename)
                lump_filesize = os.path.getsize(os.path.join(self.folder, lump_filename))
                lump_header = ExternalLumpHeader(*lump_header, lump_filename, lump_filesize)
            self.headers[LUMP.name] = lump_header
            if lump_header.length == 0:
                continue  # skip empty lumps
            try:
                if LUMP.name == "GAME_LUMP":
                    # NOTE: lump_header.version is ignored in this case
                    GameLumpClasses = getattr(self.branch, "GAME_LUMP_CLASSES", dict())
                    BspLump = lumps.GameLump(self.file, lump_header, GameLumpClasses, self.branch.GAME_LUMP_HEADER)
                elif LUMP.name in self.branch.LUMP_CLASSES:
                    LumpClass = self.branch.LUMP_CLASSES[LUMP.name][lump_header.version]
                    BspLump = lumps.create_BspLump(self.file, lump_header, LumpClass)
                elif LUMP.name in self.branch.BASIC_LUMP_CLASSES:
                    LumpClass = self.branch.BASIC_LUMP_CLASSES[LUMP.name][lump_header.version]
                    BspLump = lumps.create_BasicBspLump(self.file, lump_header, LumpClass)
                elif LUMP.name in self.branch.SPECIAL_LUMP_CLASSES:
                    SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP.name][lump_header.version]
                    if not external:
                        self.file.seek(lump_header.offset)
                        lump_data = self.file.read(lump_header.length)
                    else:
                        lump_data = open(lump_header.filename, "rb").read()
                    BspLump = SpecialLumpClass(lump_data)
                else:
                    BspLump = lumps.create_RawBspLump(self.file, lump_header)
            except KeyError:  # lump version not supported
                BspLump = lumps.create_RawBspLump(self.file, lump_header)
            except Exception as exc:
                self.loading_errors[LUMP.name] = exc
                BspLump = lumps.create_RawBspLump(self.file, lump_header)
            setattr(self, LUMP.name, BspLump)

        # .ent files
        # TODO: give a warning if available .ent files do not match ENTITY_PARTITIONS
        # NOTE: ENTITY_PARTITIONS contains "01*" as the first entry, does this mean the entity lump?
        for ent_filetype in ("env", "fx", "script", "snd", "spawn"):
            entity_file = f"{self.filename[:-4]}_{ent_filetype}.ent"  # e.g. "mp_glitch_env.ent"
            if entity_file in self.associated_files:
                with open(os.path.join(self.folder, entity_file), "rb") as ent_file:
                    LUMP_name = f"ENTITIES_{ent_filetype}"
                    self.entity_headers[LUMP_name] = ent_file.readline().decode().rstrip("\n")
                    # Titanfall:  ENTITIES01
                    # Apex Legends:  ENTITIES02 num_models=0
                    setattr(self, LUMP_name, shared.Entities(ent_file.read()))
                    # each .ent file also has a null byte at the very end

    def save_as(self, filename: str, single_file: bool = False):
        # NOTE: this method is innacurate and inconvenient
        # TODO: catch titanfall2 LIGHTMAP_DATA_REAL_TIME_LIGHTS (9x / 8x)
        lump_order = sorted([L for L in self.branch.LUMP],
                            key=lambda L: (self.headers[L.name].offset, self.headers[L.name].length))
        # ^ {"lump.name": LumpHeader / ExternalLumpHeader}
        # NOTE: messes up on empty lumps, so we can't get an exact 1:1 copy /;
        external_lumps = {L.name for L in self.branch.LUMP if isinstance(self.headers[L.name], ExternalLumpHeader)}
        if single_file:
            external_lumps = set()
        raw_lumps: Dict[str, bytes] = dict()
        # ^ {"LUMP.name": b"raw lump data]"}
        for LUMP in self.branch.LUMP:
            lump_bytes = self.lump_as_bytes(LUMP.name)
            if lump_bytes != b"":  # don't write empty lumps
                raw_lumps[LUMP.name] = lump_bytes
        # recalculate headers
        current_offset = 0
        headers = dict()
        for LUMP in lump_order:
            if LUMP.name not in raw_lumps:  # lump is not present
                version = self.headers[LUMP.name].version  # PHYSICS_LEVEL needs version preserved
                headers[LUMP.name] = LumpHeader(current_offset, 0, version, 0)
                continue
            # wierd hack to align unused lump offsets correctly
            if current_offset == 0:
                current_offset = 16 + (16 * 128)  # first byte after headers
            offset = current_offset
            length = len(raw_lumps[LUMP.name])
            version = self.headers[LUMP.name].version
            fourCC = 0  # fourCC is always 0 because we aren't encoding
            if LUMP.name in external_lumps:
                external_lump_filename = f"{os.path.basename(filename)}.{LUMP.value:04x}.bsp_lump"
                header = ExternalLumpHeader(offset, 0, version, fourCC, external_lump_filename, length)
                # ^ offset, length, version, fourCC
            else:
                header = LumpHeader(offset, length, version, fourCC)
            headers[LUMP.name] = header  # recorded for noting padding
            current_offset += length
            # pad to start at the next multiple of 4 bytes
            # TODO: note the padding so we can remove it when writing .bsp_lump
            if current_offset % 4 != 0:
                current_offset += 4 - current_offset % 4
        del current_offset
        if "GAME_LUMP" in raw_lumps and "GAME_LUMP" not in external_lumps:
            raw_lumps["GAME_LUMP"] = self.GAME_LUMP.as_bytes(headers["GAME_LUMP"].offset)
        # make file
        os.makedirs(os.path.dirname(os.path.realpath(filename)), exist_ok=True)
        outfile = open(filename, "wb")
        bsp_version = self.bsp_version
        if isinstance(self.bsp_version, tuple):
            bsp_version = bsp_version[0] + bsp_version[1] << 16
        outfile.write(struct.pack("4s3I", self.file_magic, bsp_version, self.revision, 127))
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
                # TODO: recalc the GameLump offset & length
                # TODO: cut any padding from the tail
                with open(external_lump, "wb") as out_lumpfile:
                    out_lumpfile.write(raw_lumps[LUMP.name])
            else:  # write lump to file
                padding_length = headers[LUMP.name].offset - outfile.tell()
                if padding_length > 0:  # NOTE: padding_length should not exceed 3
                    outfile.write(b"\0" * padding_length)
                outfile.write(raw_lumps[LUMP.name])
        # final padding
        end = outfile.tell()
        padding_length = 0
        if end % 4 != 0:
            padding_length = 4 - end % 4
        outfile.write(b"\0" * padding_length)
        outfile.close()  # main .bsp is written
        # write .ent lumps
        # NOTE: the ENTITY_PARTITIONS lump should list all used .ent lumps
        for ent_variant in ("env", "fx", "script", "snd", "spawn"):
            if not hasattr(self, f"ENTITIES_{ent_variant}"):
                continue
            ent_filename = f"{os.path.splitext(filename)[0]}_{ent_variant}.ent"
            with open(ent_filename, "wb") as ent_file:
                LUMP_name = f"ENTITIES_{ent_variant}"
                # NOTE: the default .ent header given here only work for titanfall & titanfall2
                # -- apex_legends branch requires a model count f"ENTITIES02 {num_models=}"
                # -- the `num_models` value appears to be for entities across all .ent files
                # NOTE: so far `prop_*` entities have only been observed in `*_script.ent`
                header = self.entity_headers.get(LUMP_name, "ENTITIES01").encode("ascii")
                ent_file.write(header)
                ent_file.write(b"\n")
                ent_file.write(getattr(self, LUMP_name).as_bytes())

    def save(self, single_file: bool = False):
        self.save_as(os.path.join(self.folder, self.filename), single_file)
        self._preload()  # reload lumps, clearing all BspLump._changes
