from __future__ import annotations
from collections import namedtuple
import enum
import os
import shutil
import struct
from types import MethodType, ModuleType
from typing import Dict

from . import base
from . import lumps
from .base import LumpHeader
from .branches import shared


ExternalLumpHeader = namedtuple("ExternalLumpHeader", ["offset", "length", "version", "fourCC", "filename", "filesize"])


class ExternalLumpManager:
    """Looks mostly like a .bsp, but only uses external lumps"""
    # copied from bsp on __init__
    filename: str
    branch: ModuleType
    bsp_version: int | (int, int)
    file_magic: bytes
    # unique to external lumps
    headers: Dict[str, ExternalLumpHeader]
    # ^ {"LUMP_NAME": ExternalLumpHeader}
    loading_errors: Dict[str, Exception]
    # ^ {"LUMP_NAME": Error}

    def __init__(self, bsp: RespawnBsp):
        self.filename = bsp.filename
        self.branch = bsp.branch
        self.bsp_version = bsp.bsp_version
        self.file_magic = bsp.file_magic
        # generate headers
        self.headers = dict()
        self.loading_errors = dict()
        for LUMP in bsp.branch.LUMP:
            lump_filename = f"{bsp.filename}.{LUMP.value:04x}.bsp_lump"
            if lump_filename not in bsp.associated_files:
                continue
            lump_filename = os.path.join(bsp.folder, lump_filename)
            lump_filesize = os.path.getsize(lump_filename)
            lump_header = ExternalLumpHeader(*bsp.headers[LUMP.name], lump_filename, lump_filesize)
            self.headers[LUMP.name] = lump_header
        # attach methods
        for method in getattr(self.branch, "methods", list()):
            method = MethodType(method, self)
            setattr(self, method.__name__, method)

    def __repr__(self):  # copied from base.Bsp
        version = f"({self.file_magic.decode('ascii', 'ignore')} version {self.bsp_version}"
        branch_script = ".".join(self.branch.__name__.split(".")[-2:])
        return f"<{self.__class__.__name__} '{self.filename}' {branch_script} {version} at 0x{id(self):016X}>"

    def __getattr__(self, lump_name: str):
        """initialises lumps when created"""
        if lump_name not in self.headers:
            raise AttributeError(f"External {lump_name} lump not found!")
        lump_header = self.headers[lump_name]
        if lump_header.filesize == 0:
            raise RuntimeError(f"{lump_name} lump's .bsp_lump is empty!")
        try:
            if lump_name == "GAME_LUMP":  # NOTE: lump_header.version is ignored in this case
                GameLumpClasses = getattr(self.branch, "GAME_LUMP_CLASSES", dict())
                lump_file = open(lump_header.filename, "rb")
                ExternalBspLump = lumps.GameLump(lump_file, lump_header, GameLumpClasses, self.branch.GAME_LUMP_HEADER)
                # TODO: test we didn't break this with the new ExternalLumpHeader
            elif lump_name in self.branch.LUMP_CLASSES:
                LumpClass = self.branch.LUMP_CLASSES[lump_name][lump_header.version]
                ExternalBspLump = lumps.BspLump(self.file, lump_header, LumpClass)
            elif lump_name in self.branch.BASIC_LUMP_CLASSES:
                LumpClass = self.branch.BASIC_LUMP_CLASSES[lump_name][lump_header.version]
                ExternalBspLump = lumps.BasicBspLump(self.file, lump_header, LumpClass)
            elif lump_name in self.branch.SPECIAL_LUMP_CLASSES:
                SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[lump_name][lump_header.version]
                with open(lump_header.filename, "rb") as bsp_lump_file:
                    ExternalBspLump = SpecialLumpClass(bsp_lump_file.read())
            else:
                ExternalBspLump = lumps.RawBspLump(self.file, lump_header)
        except KeyError:  # lump version not supported
            ExternalBspLump = lumps.RawBspLump(self.file, lump_header)
        except Exception as exc:
            self.loading_errors[lump_name] = exc
            ExternalBspLump = lumps.RawBspLump(self.file, lump_header)
        setattr(self, lump_name, ExternalBspLump)
        return getattr(self, lump_name)  # uses __getattribute__

    # NOTE: hasattr won't list available external lumps, but self.headers will

    def lump_as_bytes(self, lump_name: str) -> bytes:
        """based on base.Bsp.lump_as_bytes()"""
        if lump_name in self.loading_errors:
            # opened file, but failed to parse
            assert isinstance(getattr(self, lump_name), lumps.ExternalRawBspLump), "idk how this happened"
            return bytes(getattr(self, lump_name))
        if lump_name in self.headers and not hasattr(self, lump_name):
            # found file, but haven't opened
            with open(self.headers[lump_name].filename, "rb") as bsp_lump_file:
                return bsp_lump_file.read()
        lump_entries = getattr(self, lump_name)
        # NOTE: changing the version won't convert the format, but we respect the header version
        lump_version = self.headers[lump_name].version
        all_lump_classes = {**self.branch.BASIC_LUMP_CLASSES,
                            **self.branch.LUMP_CLASSES,
                            **self.branch.SPECIAL_LUMP_CLASSES}
        if lump_name in all_lump_classes and lump_name != "GAME_LUMP":
            if lump_version not in all_lump_classes[lump_name]:
                return bytes(lump_entries)
        if lump_name in self.branch.BASIC_LUMP_CLASSES:
            _format = self.branch.BASIC_LUMP_CLASSES[lump_name][lump_version]._format
            raw_lump = struct.pack(f"{len(lump_entries)}{_format}", *lump_entries)
        elif lump_name in self.branch.LUMP_CLASSES:
            _format = self.branch.LUMP_CLASSES[lump_name][lump_version]._format
            raw_lump = b"".join([struct.pack(_format, *x.flat()) for x in lump_entries])
        elif lump_name in self.branch.SPECIAL_LUMP_CLASSES:
            raw_lump = lump_entries.as_bytes()
        elif lump_name == "GAME_LUMP":
            raw_lump = lump_entries.as_bytes()
        else:  # assume lump_entries is RawBspLump
            raw_lump = bytes(lump_entries)
        return raw_lump


class RespawnBsp(base.Bsp):
    """Respawn Entertainment's Titanfall Engine .bsp (rBSP v29 -> 50.1)"""
    # https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Titanfall
    # https://raw.githubusercontent.com/Wanty5883/Titanfall2/master/tools/TitanfallMapExporter.py
    file_magic = b"rBSP"
    lump_count: int
    entity_headers: Dict[str, str]
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
        for LUMP in self.branch.LUMP:
            lump_header = self._read_header(LUMP)
            self.headers[LUMP.name] = lump_header
            if lump_header.length == 0 or lump_header.offset >= self.bsp_file_size:
                continue  # skip empty lumps
            try:
                if LUMP.name == "GAME_LUMP":  # NOTE: lump_header.version is ignored in this case
                    GameLumpClasses = getattr(self.branch, "GAME_LUMP_CLASSES", dict())
                    BspLump = lumps.GameLump(self.file, lump_header, GameLumpClasses, self.branch.GAME_LUMP_HEADER)
                elif LUMP.name in self.branch.LUMP_CLASSES:
                    LumpClass = self.branch.LUMP_CLASSES[LUMP.name][lump_header.version]
                    BspLump = lumps.BspLump(self.file, lump_header, LumpClass)
                elif LUMP.name in self.branch.BASIC_LUMP_CLASSES:
                    LumpClass = self.branch.BASIC_LUMP_CLASSES[LUMP.name][lump_header.version]
                    BspLump = lumps.BasicBspLump(self.file, lump_header, LumpClass)
                elif LUMP.name in self.branch.SPECIAL_LUMP_CLASSES:
                    SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP.name][lump_header.version]
                    self.file.seek(lump_header.offset)
                    BspLump = SpecialLumpClass(self.file.read(lump_header.length))
                else:
                    BspLump = lumps.RawBspLump(self.file, lump_header)
            except KeyError:  # lump version not supported
                BspLump = lumps.RawBspLump(self.file, lump_header)
            except Exception as exc:
                self.loading_errors[LUMP.name] = exc
                BspLump = lumps.RawBspLump(self.file, lump_header)
            setattr(self, LUMP.name, BspLump)

        self.external = ExternalLumpManager(self)

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

    def save_as(self, filename: str):
        lump_order = sorted([L for L in self.branch.LUMP],
                            key=lambda L: (self.headers[L.name].offset, self.headers[L.name].length))
        # ^ {"lump.name": LumpHeader}
        # NOTE: messes up a little on empty lumps, so we can't get an exact 1:1 copy /;
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
            header = LumpHeader(offset, length, version, fourCC)
            if LUMP.name in self.external.headers:
                external_lump_filename = f"{os.path.basename(filename)}.{LUMP.value:04x}.bsp_lump"
                if not hasattr(self.external, LUMP.name):  # unopened, no changes
                    shutil.copyfile(self.external.headers[LUMP.name].filename, external_lump_filename)
                else:
                    with open(external_lump_filename, "wb") as bsp_lump_file:
                        bsp_lump_file.write(self.external.lump_as_bytes(LUMP.name))
            headers[LUMP.name] = header  # recorded for noting padding
            current_offset += length
            # pad to start at the next multiple of 4 bytes
            # TODO: note the padding so we can remove it when writing .bsp_lump
            if current_offset % 4 != 0:
                current_offset += 4 - current_offset % 4
        del current_offset
        # set GAME_LUMP offsets
        if "GAME_LUMP" in raw_lumps:
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
            if LUMP.name in self.external.headers:
                external_lump = f"{filename}.{LUMP.value:04x}.bsp_lump"
                if not hasattr(self.external, LUMP.name):
                    shutil.copy()
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
