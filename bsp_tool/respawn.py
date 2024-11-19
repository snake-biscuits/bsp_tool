from __future__ import annotations
import io
import os
import re
import struct
from types import MethodType, ModuleType
from typing import Dict, List

from . import external
from . import lumps
from . import valve
from .branches import shared


class LumpOverrides(external.LumpOverrides):
    pattern = re.compile(r".*\.bsp\.([0-9a-fA-F]{4})\.bsp_lump(\.client)?")

    def file_lump(self, filename: str, file: external.File) -> str:
        match = self.pattern.match(filename)
        if match is not None:
            lump_index = int(match.group(1), base=16)
            return self.branch.LUMP(lump_index).name

    def mount_lump(self, name: str, header: object, file: external.File):
        if file.size == 0:
            raise RuntimeError(f"The .bsp_lump file for {name} is empty!")
        try:
            if name == "GAME_LUMP":
                lump = valve.GameLump.from_stream(file, self, sub_offset=header.offset)
            elif name in self.branch.LUMP_CLASSES:
                LumpClass = self.branch.LUMP_CLASSES[name][header.version]
                lump = lumps.BspLump.from_stream(file, LumpClass)
            elif name in self.branch.BASIC_LUMP_CLASSES:
                LumpClass = self.branch.BASIC_LUMP_CLASSES[name][header.version]
                lump = lumps.BasicBspLump.from_stream(file, LumpClass)
            elif name in self.branch.SPECIAL_LUMP_CLASSES:
                SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[name][header.version]
                lump = SpecialLumpClass.from_bytes(file.read())
            else:  # unmapped lump
                lump = lumps.RawBspLump.from_stream(file)
        except KeyError:  # lump version not supported
            lump = lumps.RawBspLump.from_stream(file)
        except Exception as exc:
            self.loading_errors[name] = exc
            lump = lumps.RawBspLump.from_stream(file)
        setattr(self, name, lump)

    @classmethod
    def from_bsp(cls, bsp) -> LumpOverrides:
        out = super().from_bsp(bsp)
        # attach methods
        for method_name, method in getattr(bsp.branch, "methods", dict()).items():
            method = MethodType(method, out)
            setattr(out, method_name, method)
        return out


class RespawnBsp(valve.ValveBsp):
    """Respawn Entertainment's Titanfall Engine .bsp (rBSP v29 -> 52.1)"""
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

    def __init__(self, branch: ModuleType, filepath: str = "untitled.bsp"):
        self.entity_headers = dict()
        super(RespawnBsp, self).__init__(branch, filepath)

    def extra_patterns(self) -> List[str]:
        base_filename = self.filename.rpartition(".")[0]
        return [
            f"{self.filename}.*.bsp_lump",
            f"{self.filename}.*.bsp_lump.client",
            f"{base_filename}_*.ent"]

    @classmethod
    def from_file(cls, branch: ModuleType, filepath: str) -> RespawnBsp:
        bsp = super().from_file(branch, filepath)
        # .bsp_lump files
        bsp.external = LumpOverrides.from_bsp(bsp)
        # .ent files
        # TODO: give a warning if available .ent files do not match ENTITY_PARTITIONS
        # NOTE: ENTITY_PARTITIONS contains "01*" as the first entry, does this mean the entity lump?
        # NOTE: vX.1 RespawnBsp must check external.ENTITY_PARITIONS
        base_filename = bsp.filename.rpartition(".")[0]
        for ent_filetype in ("env", "fx", "script", "snd", "spawn"):
            entity_file = f"{base_filename}_{ent_filetype}.ent"
            if entity_file in bsp.extras:
                LUMP_name = f"ENTITIES_{ent_filetype}"
                ent_file = bsp.extras[entity_file]
                bsp.entity_headers[LUMP_name] = ent_file.readline().decode().rstrip()
                # Titanfall:  ENTITIES01
                # Apex Legends:  ENTITIES02 num_models=0
                setattr(bsp, LUMP_name, shared.Entities.from_bytes(ent_file.read()))
                # NOTE: each .ent file also has a null byte at the very end
        return bsp

    @classmethod
    def from_stream(cls, branch: ModuleType, filepath: str, stream: io.BytesIO) -> RespawnBsp:
        bsp = cls(branch, filepath)
        bsp.file = stream
        # collect metadata
        file_magic = bsp.file.read(4)
        if file_magic == bsp.file_magic:
            bsp.endianness = "little"
        elif file_magic == bytes(reversed(bsp.file_magic)):
            bsp.endianness = "big"
            bsp.file_magic = file_magic  # b"PSBr"
        else:
            raise RuntimeError(f"{bsp.file} is not a RespawnBsp! file_magic is incorrect")
        bsp.version = int.from_bytes(bsp.file.read(4), bsp.endianness)
        if bsp.version > 0xFFFF:  # Apex Legends Season 11+
            bsp.version = (bsp.version & 0xFFFF, bsp.version >> 16)  # major, minor
        # NOTE: Legion considers the second half to be a flag for streaming
        # -- Likely because 49.1 & 50.1 b"rBSP" moved all lumps to .bsp_lump
        # NOTE: various mixed bsp versions exist in depot/ for Apex S11+
        bsp.revision = int.from_bytes(bsp.file.read(4), bsp.endianness)
        bsp.lump_count = int.from_bytes(bsp.file.read(4), bsp.endianness)
        assert bsp.lump_count == 127, "irregular RespawnBsp lump_count"
        bsp.file.seek(0, 2)  # move cursor to end of file
        bsp.filesize = bsp.file.tell()
        # collect lumps
        bsp.headers = dict()
        bsp.loading_errors: Dict[str, Exception] = dict()
        for lump_name, lump_header in bsp._header_generator(offset=16):
            if lump_header.offset >= bsp.filesize:
                continue  # or version has flag (e.g. (50, 1))
            bsp.mount_lump(lump_name, lump_header, bsp.file)
        # compiler signature
        bsp._get_signature(16 + (16 * 128))
        return bsp

    def save_as(self, filename: str, no_bsp_lump: bool = False):
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
        version = self.version
        if isinstance(self.version, tuple):  # Apex Legends Season 10+
            version = version[0] + version[1] << 16
        _format = "4s3I" if self.endianness == "little" else ">4s3I"
        outfile.write(struct.pack(_format, self.file_magic, version, self.revision, 127))
        for LUMP in self.branch.LUMP:
            outfile.write(headers[LUMP.name].as_bytes())
        outfile.write(self.signature)
        # write lump contents (cannot be done until headers allocate padding)
        for LUMP in [L for L in lump_order if L.name in raw_lumps]:
            # write INTERNAL .bsp lump
            if not isinstance(self.version, tuple):  # pre Apex Season 10+
                padding_length = headers[LUMP.name].offset - outfile.tell()
                if padding_length > 0:  # pad previous lump
                    outfile.write(b"\0" * padding_length)
                outfile.write(raw_lumps[LUMP.name])
        # final padding
        end = outfile.tell()
        padding_length = 0
        if end % 4 != 0:
            padding_length = 4 - end % 4
        outfile.write(b"\0" * padding_length)
        outfile.close()  # main .bsp is written
