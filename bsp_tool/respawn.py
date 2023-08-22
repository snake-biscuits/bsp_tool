from __future__ import annotations
from collections import namedtuple
import os
import shutil
import struct
from types import MethodType, ModuleType
from typing import Dict

from . import base
from . import lumps
from . import valve
from .branches import shared


ExternalLumpHeader = namedtuple("ExternalLumpHeader", ["offset", "length", "version", "fourCC", "filename", "filesize"])


class ExternalLumpManager:
    """Looks mostly like a .bsp, but only uses external lumps"""
    # copied from bsp on __init__
    branch: ModuleType
    bsp_version: int | (int, int)
    endianness: str = "little"
    file_magic: bytes
    filename: str
    folder: str
    # unique to external lumps
    headers: Dict[str, ExternalLumpHeader]
    # ^ {"LUMP_NAME": ExternalLumpHeader}
    loading_errors: Dict[str, Exception]
    # ^ {"LUMP_NAME": Error}

    def __init__(self, bsp: RespawnBsp):
        self.branch = bsp.branch
        self.bsp_version = bsp.bsp_version
        self.endianness = bsp.endianness
        self.file_magic = bsp.file_magic
        self.filename = bsp.filename
        self.folder = bsp.folder
        self.lump_count = bsp.lump_count
        self.revision = bsp.revision
        # generate headers
        self.headers = dict()
        self.loading_errors = dict()
        for LUMP in bsp.branch.LUMP:
            lump_filename = f"{bsp.filename}.{LUMP.value:04x}.bsp_lump"
            if lump_filename not in bsp.associated_files:
                lump_filename += ".client"  # Apex Legends Season 18
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

    __repr__ = base.Bsp.__repr__

    def __getattr__(self, attr):
        """initialises lumps when created"""
        # NOTE: __getattr__ is only called if the attribute doesn't exist, so we load the lump when the user asks for it
        # -- this has the added benefit that `del bsp.external.LUMP_NAME` unloads it from memory, while allowing reloads
        # TODO: we could use the same deferred loading approach for all bsps for a performance boost
        # -- this would remove the simple check of `assert len(bsp.loading_errors) == 0` to ensure read quality, however
        # -- though if loading errors was a @property it could load all SpecialLumpClasses & the GameLump to verify
        # -- all other lumps can be verified by length alone, though checking for invalid floats would be a neat feature
        if attr not in self.headers:
            raise AttributeError(f"type object '{self.__class__.__name__}' has no attribute '{attr}'")
        lump_name = attr
        lump_header = self.headers[lump_name]
        # NOTE: lump_header should always be an ExternalLumpHeader
        # -- this is a copy of the internal header + filename & filesize for the external file
        # -- if re-implementing for ValveBsp .lmp files, read the header from the start of the .lmp
        if lump_header.filesize == 0:
            raise RuntimeError(f"The .bsp_lump file for the {lump_name} lump is empty!")
        if not os.path.exists(lump_header.filename):
            raise FileNotFoundError(f"Couldn't find .bsp_lump file for {lump_name} lump!")
        # NOTE: near identical to ValveBsp._preload_lump, but uses ExternalRawBspLump subclasses
        try:
            if lump_name == "GAME_LUMP":  # NOTE: lump_header.version is ignored in this case
                GameLumpClasses = getattr(self.branch, "GAME_LUMP_CLASSES", dict())
                lump_file = open(lump_header.filename, "rb")
                ExternalBspLump = lumps.GameLump(lump_file, lump_header, self.endianness,
                                                 GameLumpClasses, self.branch.GAME_LUMP_HEADER)
            elif lump_name in self.branch.LUMP_CLASSES:
                LumpClass = self.branch.LUMP_CLASSES[lump_name][lump_header.version]
                ExternalBspLump = lumps.ExternalBspLump.from_header(lump_header, LumpClass)
            elif lump_name in self.branch.BASIC_LUMP_CLASSES:
                LumpClass = self.branch.BASIC_LUMP_CLASSES[lump_name][lump_header.version]
                ExternalBspLump = lumps.ExternalBasicBspLump.from_header(lump_header, LumpClass)
            elif lump_name in self.branch.SPECIAL_LUMP_CLASSES:
                SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[lump_name][lump_header.version]
                with open(lump_header.filename, "rb") as bsp_lump_file:
                    ExternalBspLump = SpecialLumpClass.from_bytes(bsp_lump_file.read())
            else:
                ExternalBspLump = lumps.ExternalRawBspLump.from_header(lump_header)
        except KeyError:  # lump version not supported
            ExternalBspLump = lumps.ExternalRawBspLump.from_header(lump_header)
        except Exception as exc:
            self.loading_errors[lump_name] = exc
            ExternalBspLump = lumps.from_header.ExternalRawBspLump(lump_header)
        setattr(self, lump_name, ExternalBspLump)
        return getattr(self, lump_name)  # uses __getattribute__

    # NOTE: hasattr / dir won't list available external lumps, but self.headers will (if filtered)
    # -- available_external_lumps = [L for L, h in bsp.external.headers.items() if h.length != 0]
    # -- alternatively, filter by `os.path.exists(bsp.external.headers["LUMP_NAME"].filename)`

    def lump_as_bytes(self, lump_name: str) -> bytes:
        """based on base.Bsp.lump_as_bytes()"""
        # NOTE: LumpClasses are derived from branch, not lump data!
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
            BasicLumpClass = self.branch.BASIC_LUMP_CLASSES[lump_name][lump_version]
            if hasattr(BasicLumpClass, "as_int"):  # branches.base.BitField
                lump_entries = [x.as_int() for x in lump_entries]
            raw_lump = struct.pack(f"{len(lump_entries)}{BasicLumpClass._format}", *lump_entries)
        elif lump_name in self.branch.LUMP_CLASSES:
            _format = self.branch.LUMP_CLASSES[lump_name][lump_version]._format
            raw_lump = b"".join([struct.pack(_format, *x.as_tuple()) for x in lump_entries])
        elif lump_name in self.branch.SPECIAL_LUMP_CLASSES:
            raw_lump = lump_entries.as_bytes()
        elif lump_name == "GAME_LUMP":
            raw_lump = lump_entries.as_bytes()
        else:  # assume lump_entries is RawBspLump
            raw_lump = bytes(lump_entries)
        return raw_lump


class RespawnBsp(valve.ValveBsp):
    """Respawn Entertainment's Titanfall Engine .bsp (rBSP v29 -> 50.1)"""
    # https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Titanfall
    # https://raw.githubusercontent.com/Wanty5883/Titanfall2/master/tools/TitanfallMapExporter.py
    endianness: str = "little"
    file_magic: bytes = b"rBSP"
    lump_count: int = 127
    entity_headers: Dict[str, str]
    # ^ {"LUMP_NAME": "header text"}
    signature: bytes = b""
    # struct LumpHeader { int offset, length, version, fourCC; };
    # struct BspHeader { char file_magic[4]; int version, revision, lump_count;
    #                    LumpHeader headers[128]; };

    def __init__(self, branch: ModuleType, filename: str = "untitled.bsp", autoload: bool = True):
        self.entity_headers = dict()
        super(RespawnBsp, self).__init__(branch, filename, autoload)
        # NOTE: bsp revision appears before headers, not after (as in Valve's variant)

    def _preload(self):
        """Loads filename using the format outlined in this .bsp's branch defintion script"""
        # collect files
        local_files = os.listdir(self.folder)
        def is_related(f): return f.startswith(self.filename.partition(".")[0])
        self.associated_files = [f for f in local_files if is_related(f)]
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        # collect metadata
        file_magic = self.file.read(4)
        if file_magic == self.file_magic:
            self.endianness = "little"
        elif file_magic == bytes(reversed(self.file_magic)):
            self.endianness = "big"
            self.file_magic = file_magic  # b"PSBr"
        else:
            raise RuntimeError(f"{self.file} is not a RespawnBsp! file_magic is incorrect")
        self.bsp_version = int.from_bytes(self.file.read(4), self.endianness)
        if self.bsp_version > 0xFFFF:  # Apex Legends Season 11+
            self.bsp_version = (self.bsp_version & 0xFFFF, self.bsp_version >> 16)  # major, minor
        # NOTE: Legion considers the second half to be a flag for streaming
        # -- Likely because 49.1 & 50.1 b"rBSP" moved all lumps to .bsp_lump
        # NOTE: various mixed bsp versions exist in depot/ for Apex S11+
        self.revision = int.from_bytes(self.file.read(4), self.endianness)
        self.lump_count = int.from_bytes(self.file.read(4), self.endianness)
        assert self.lump_count == 127, "irregular RespawnBsp lump_count"
        self.file.seek(0, 2)  # move cursor to end of file
        self.bsp_file_size = self.file.tell()
        # collect lumps
        self.headers = dict()
        self.loading_errors: Dict[str, Exception] = dict()
        for lump_name, lump_header in self._header_generator(offset=16):
            if lump_header.offset >= self.bsp_file_size:
                continue  # or version has flag (e.g. (50, 1))
            self._preload_lump(lump_name, lump_header)
        # compiler signature
        self._get_signature(16 + (16 * 128))

        self.external = ExternalLumpManager(self)

        # .ent files
        # TODO: give a warning if available .ent files do not match ENTITY_PARTITIONS
        # NOTE: ENTITY_PARTITIONS contains "01*" as the first entry, does this mean the entity lump?
        for ent_filetype in ("env", "fx", "script", "snd", "spawn"):
            entity_file = f"{self.filename.partition('.')[0]}_{ent_filetype}.ent"  # e.g. "mp_glitch_env.ent"
            if entity_file in self.associated_files:
                with open(os.path.join(self.folder, entity_file), "rb") as ent_file:
                    LUMP_name = f"ENTITIES_{ent_filetype}"
                    self.entity_headers[LUMP_name] = ent_file.readline().decode().rstrip("\n")
                    # Titanfall:  ENTITIES01
                    # Apex Legends:  ENTITIES02 num_models=0
                    setattr(self, LUMP_name, shared.Entities.from_bytes(ent_file.read()))
                    # each .ent file also has a null byte at the very end

    def save_as(self, filename: str):
        # lumps -> bytes
        lump_order = sorted([L for L in self.branch.LUMP],
                            key=lambda L: (self.headers[L.name].offset, self.headers[L.name].length))
        # ^ ["LUMP.name"]
        raw_lumps: Dict[str, bytes] = dict()
        # ^ {"LUMP.name": b"raw lump data"}
        for LUMP in self.branch.LUMP:
            if LUMP.name == "GAME_LUMP":
                continue  # need header.offset before generating
            try:
                lump_bytes = self.lump_as_bytes(LUMP.name)
            except Exception as exc:
                print(f"Failed to convert {LUMP.name} to bytes")
                raise exc
            if lump_bytes != b"":  # don't write empty lumps
                raw_lumps[LUMP.name] = lump_bytes
        # recalculate headers
        current_offset = 16 + (16 * 128)
        if len(self.signature) % 4 != 0:  # pad signature
            self.signature += b"\0" * (4 - len(self.signature) % 4)
        current_offset += len(self.signature)
        headers = dict()
        for LUMP in lump_order:
            if LUMP.name == "GAME_LUMP" and hasattr(self, "GAME_LUMP"):  # generate
                raw_lumps["GAME_LUMP"] = self.GAME_LUMP.as_bytes(current_offset)
            if LUMP.name not in raw_lumps:  # lump is empty
                version = self.headers[LUMP.name].version  # preserve PHYSICS_LEVEL version
                header = self.branch.LumpHeader(current_offset, 0, version, 0)
            else:  # lump has data
                offset = current_offset
                length = len(raw_lumps[LUMP.name])
                version = self.headers[LUMP.name].version
                fourCC = 0  # fourCC is always 0 (no LZMA lump compression)
                header = self.branch.LumpHeader(offset, length, version, fourCC)
                current_offset += length
                if current_offset % 4 != 0:  # pad
                    current_offset += 4 - current_offset % 4
            headers[LUMP.name] = header
        del current_offset
        # write to file(s)
        os.makedirs(os.path.dirname(os.path.realpath(filename)), exist_ok=True)
        # TODO: close self.file if overwriting
        outfile = open(filename, "wb")
        bsp_version = self.bsp_version
        if isinstance(self.bsp_version, tuple):  # Apex Legends Season 10+
            bsp_version = bsp_version[0] + bsp_version[1] << 16
        _format = "4s3I" if self.endianness == "little" else ">4s3I"
        outfile.write(struct.pack(_format, self.file_magic, bsp_version, self.revision, 127))
        for LUMP in self.branch.LUMP:
            outfile.write(headers[LUMP.name].as_bytes())
        outfile.write(self.signature)
        # write lump contents (cannot be done until headers allocate padding)
        for LUMP in [L for L in lump_order if L.name in raw_lumps]:
            if not isinstance(self.bsp_version, tuple):  # pre Apex Season 10+
                padding_length = headers[LUMP.name].offset - outfile.tell()
                if padding_length > 0:  # pad previous lump
                    outfile.write(b"\0" * padding_length)
                outfile.write(raw_lumps[LUMP.name])  # write lump
            if LUMP.name in self.external.headers:  # .bsp_lump
                external_lump_filename = f"{filename}.{LUMP.value:04x}.bsp_lump"
                if not hasattr(self.external, LUMP.name):  # no edits
                    shutil.copyfile(self.external.headers[LUMP.name].filename, external_lump_filename)
                else:
                    with open(external_lump_filename, "wb") as out_lumpfile:
                        out_lumpfile.write(raw_lumps[LUMP.name])
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
                ent_LUMP_name = f"ENTITIES_{ent_variant}"
                header = self.entity_headers.get(ent_LUMP_name, "ENTITIES01").encode("ascii")
                # NOTE: the default .ent header will only work for titanfall & titanfall2
                # -- apex_legends(13) requires a model count: f"ENTITIES02 {num_models=}"
                # -- the `num_models` value appears to be for entities across all .ent files
                # NOTE: so far `prop_*` entities have only been observed in `*_script.ent`
                ent_file.write(header + b"\n" + getattr(self, ent_LUMP_name).as_bytes())
