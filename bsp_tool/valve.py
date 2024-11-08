from __future__ import annotations
import io
import os
import struct
from types import ModuleType
from typing import Any, Dict, List

from . import base
from . import id_software
from . import lumps


class GoldSrcBsp(id_software.QuakeBsp):
    file_magic = None
    # https://github.com/ValveSoftware/halflife/blob/master/utils/common/bspfile.h
    # http://hlbsp.sourceforge.net/index.php?content=bspdef


class ValveBsp(base.Bsp):
    # https://developer.valvesoftware.com/wiki/Source_BSP_File_Format
    file_magic = b"VBSP"
    revision: int = 0
    # struct SourceBspHeader { char file_magic[4]; int version; LumpHeader headers[64]; int revision; };

    def extra_patterns(self) -> List[str]:
        # https://developer.valvesoftware.com/wiki/Patching_levels_with_lump_files
        # NOTE: Left 4 Dead (2) might include "_h_" & "_s_" lumps
        # NOTE: ignoring *.nav & graphs/*.ain
        # -- bsp_tool doesn't do anything with navmeshes
        base_filename = self.filename.rpartition(".")[0]
        return [f"{base_filename}_l_*.lmp"]

    def mount_lump(self, lump_name: str, lump_header: Any, stream: io.BytesIO):
        if lump_header.length == 0:
            return
        try:
            if lump_name == "GAME_LUMP":
                # NOTE: lump_header.version is ignored in this case!
                GameLumpClasses = getattr(self.branch, "GAME_LUMP_CLASSES", dict())
                GameLump = lumps.GameLump
                if self.branch.__name__.split(".")[-1] == "dark_messiah_sp":
                    GameLump = lumps.DarkMessiahSPGameLump
                BspLump = GameLump(self.file, lump_header, self.endianness,
                                   GameLumpClasses, self.branch.GAME_LUMP_HEADER)
            elif lump_name in self.branch.LUMP_CLASSES:
                LumpClass = self.branch.LUMP_CLASSES[lump_name][lump_header.version]
                BspLump = lumps.create_BspLump(self.file, lump_header, LumpClass)
            elif lump_name in self.branch.SPECIAL_LUMP_CLASSES:
                SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[lump_name][lump_header.version]
                decompressed_file, decompressed_header = lumps.decompressed(self.file, lump_header)
                decompressed_file.seek(decompressed_header.offset)
                lump_data = decompressed_file.read(decompressed_header.length)
                BspLump = SpecialLumpClass.from_bytes(lump_data)
            elif lump_name in self.branch.BASIC_LUMP_CLASSES:
                LumpClass = self.branch.BASIC_LUMP_CLASSES[lump_name][lump_header.version]
                BspLump = lumps.create_BasicBspLump(self.file, lump_header, LumpClass)
            else:
                BspLump = lumps.create_RawBspLump(self.file, lump_header)
        except KeyError:  # lump VERSION not supported
            BspLump = lumps.create_RawBspLump(self.file, lump_header)
        except Exception as exc:
            self.loading_errors[lump_name] = exc
            try:
                BspLump = lumps.create_RawBspLump(self.file, lump_header)
            except AssertionError:  # LZMA decompression failed / already decompressed
                assert lump_header.offset == 0  # maybe already decompressed
                assert lump_header.length == lump_header.fourCC  # definitely already decompressed
                BspLump = lumps.RawBspLump.from_header(self.file, lump_header)
        setattr(self, lump_name, BspLump)

    @classmethod
    def from_stream(cls, branch: ModuleType, filepath: str, stream: io.BytesIO) -> ValveBsp:
        bsp = cls(branch, filepath)
        bsp.file = stream
        # collect metadata
        file_magic = bsp.file.read(4)
        if file_magic == bsp.file_magic:
            bsp.endianness = "little"
        elif file_magic == bytes(reversed(bsp.file_magic)):
            bsp.endianness = "big"
            bsp.file_magic = file_magic  # b"PSBV"
        else:
            raise RuntimeError(f"{bsp.file} is not a ValveBsp! file_magic is incorrect")
        bsp.version = int.from_bytes(bsp.file.read(4), bsp.endianness)
        if bsp.version > 0xFFFF:  # major.minor version
            bsp.version = (bsp.version & 0xFFFF, bsp.version >> 16)  # major, minor
        lump_count = max([e.value for e in bsp.branch.LUMP]) + 1
        bsp.file.seek(8 + struct.calcsize(bsp.branch.LumpHeader._format) * (lump_count))
        bsp.revision = int.from_bytes(bsp.file.read(4), bsp.endianness)
        bsp.file.seek(0, 2)  # move cursor to end of file
        bsp.filesize = bsp.file.tell()
        # collect lumps
        bsp.headers = dict()
        bsp.loading_errors: Dict[str, Exception] = dict()
        for lump_name, lump_header in bsp._header_generator(offset=8):
            bsp.mount_lump(lump_name, lump_header, bsp.file)
        return bsp

    def lump_as_bytes(self, lump_name: str) -> bytes:
        """Converts the named (versioned) lump back into bytes"""
        # NOTE: LumpClasses are derived from branch, not lump data!
        if not hasattr(self, lump_name):
            return b""  # lump is empty / deleted
        lump_entries = getattr(self, lump_name)
        lump_version = self.headers[lump_name].version
        all_lump_classes = {**self.branch.BASIC_LUMP_CLASSES,
                            **self.branch.LUMP_CLASSES,
                            **self.branch.SPECIAL_LUMP_CLASSES}
        # RawBspLump -> byte
        if lump_name != "GAME_LUMP":  # NOTE: will fail if GAME_LUMP failed to load
            if lump_name not in all_lump_classes or lump_name in self.loading_errors:
                return bytes(lump_entries)
            elif lump_name in all_lump_classes:
                if lump_version not in all_lump_classes[lump_name]:
                    return bytes(lump_entries)
                # NOTE: if the lump's version is mapped, it will be handled below
        # BasicBspLump -> bytes
        if lump_name in self.branch.BASIC_LUMP_CLASSES:
            BasicLumpClass = self.branch.BASIC_LUMP_CLASSES[lump_name][lump_version]
            if hasattr(BasicLumpClass, "as_int"):  # branches.base.BitField
                lump_entries = [x.as_int() for x in lump_entries]
            raw_lump = struct.pack(f"{len(lump_entries)}{BasicLumpClass._format}", *lump_entries)
        # BspLump -> bytes
        elif lump_name in self.branch.LUMP_CLASSES:
            _format = self.branch.LUMP_CLASSES[lump_name][lump_version]._format
            raw_lump = b"".join([struct.pack(_format, *x.as_tuple()) for x in lump_entries])
        # SpecialLumpClass -> bytes
        elif lump_name in self.branch.SPECIAL_LUMP_CLASSES:
            raw_lump = lump_entries.as_bytes()
        # GameLump -> bytes
        elif lump_name == "GAME_LUMP":
            raw_lump = lump_entries.as_bytes()
        return raw_lump

    def save_as(self, filename: str = None):
        lump_order = sorted([L for L in self.branch.LUMP],
                            key=lambda L: (self.headers[L.name].offset, self.headers[L.name].length))
        # ^ {"lump.name": LumpHeader}
        # NOTE: messes up on empty lumps, so we can't get an exact 1:1 copy /;
        raw_lumps: Dict[str, bytes] = dict()
        # ^ {"LUMP.name": b"raw lump data]"}
        for LUMP in self.branch.LUMP:
            try:
                lump_bytes = self.lump_as_bytes(LUMP.name)
            except Exception as exc:
                print(f"Failed to convert {LUMP.name} to bytes!")
                raise exc
            if lump_bytes != b"":  # don't write empty lumps
                raw_lumps[LUMP.name] = lump_bytes
        # recalculate headers
        current_offset = 0
        headers = dict()
        for LUMP in lump_order:
            # NOTE: fourCC should default to zero, we don't repack
            if LUMP.name not in raw_lumps:  # lump is not present
                headers[LUMP.name] = self.branch.LumpHeader(
                    offset=current_offset, length=0, version=self.headers[LUMP.name].version)
                continue
            # wierd hack to align unused lump offsets correctly
            if current_offset == 0:  # shift to end of header section
                # struct SourceBspHeader { char file_magic[4]; int version; LumpHeader headers[64]; int revision; };
                current_offset = 8 + (struct.calcsize(self.branch.LumpHeader._format) * len(self.branch.LUMP)) + 4
            length = len(raw_lumps[LUMP.name])
            headers[LUMP.name] = self.branch.LumpHeader(
                offset=current_offset, length=length, version=self.headers[LUMP.name].version)
            current_offset += length
            if current_offset % 4 != 0:
                current_offset += 4 - current_offset % 4
        del current_offset
        if "GAME_LUMP" in raw_lumps:
            raw_lumps["GAME_LUMP"] = self.GAME_LUMP.as_bytes(headers["GAME_LUMP"].offset)
        # make file
        os.makedirs(os.path.dirname(os.path.realpath(filename)), exist_ok=True)
        outfile = open(filename, "wb")
        outfile.write(self.file_magic)
        version = self.version
        if isinstance(self.version, tuple):
            version = version[0] + version[1] << 16
        outfile.write(version.to_bytes(4, self.endianness))
        # write headers
        for LUMP in self.branch.LUMP:
            outfile.write(headers[LUMP.name].as_bytes())
        outfile.write(self.revision.to_bytes(4, self.endianness))
        # write lump contents (cannot be done until headers allocate padding)
        for LUMP in lump_order:
            if LUMP.name not in raw_lumps:
                continue
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
