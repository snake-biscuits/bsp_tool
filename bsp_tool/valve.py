from __future__ import annotations
import io
import lzma
import os
import struct
from types import ModuleType
from typing import Any, Dict, List

from . import base
from . import id_software
from . import lumps


def decompress(data: bytes) -> bytes:
    """valve LZMA header adapter"""
    magic, true_size, compressed_size, properties = struct.unpack("4s2I5s", data[:17])
    assert magic == b"LZMA"
    _filter = lzma._decode_filter_properties(lzma.FILTER_LZMA1, properties)
    decompressor = lzma.LZMADecompressor(lzma.FORMAT_RAW, None, [_filter])
    decompressed_data = decompressor.decompress(data[17:17 + compressed_size])
    return decompressed_data[:true_size]  # trim any excess bytes


class GameLump:
    endianness: str = "little"
    GameLumpHeaderClass: Any  # used for reads / writes
    headers: Dict[str, Any]
    # ^ {"child_lump": GameLumpHeader}
    loading_errors: Dict[str, Any]
    # ^ {"child_lump": Error}
    LumpClasses: Dict[str, Dict[int, object]]
    # ^ {"child_lump": {version: LumpClass}}
    stream: lumps.Stream

    # NOTE: https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/gamebspfile.h#L25
    # -- ^ lists a few possible child lumps:
    # -- dplh: Detail Prop Lighting HDR
    # -- dplt: Detail Prop Lighting
    # -- dprp: Detail Props (procedural grass on displacements)
    # -- sprp: Static Props

    def __init__(self, endianness: str, GameLumpHeaderClass: object):
        self.endianness = endianness
        self.GameLumpHeaderClass = GameLumpHeaderClass
        self.headers = dict()
        self.loading_errors = dict()

    def as_bytes(self, lump_offset=0):
        """lump_offset makes headers relative to the stream"""
        # NOTE: ValveBsp .lmp external lumps have a 16 byte header
        # NOTE: RespawnBsp .bsp_lump offsets are relative to the internal .bsp GAME_LUMP.offset
        # NOTE: Xbox360 child lumps will not be recompressed
        out = [len(self.headers).to_bytes(4, self.endianness)]
        headers = list()
        # skip the headers (for now)
        cursor_offset = sum([
            lump_offset,
            4,
            len(self.headers) * struct.calcsize(self.GameLumpHeaderClass._format)])
        # write lumps
        # TODO: generate absent headers from lump names
        # -- this will require an endianness check for header.id
        for name, header in self.headers.items():
            lump = getattr(self, name)
            if isinstance(lump, lumps.RawBspLump):
                lump_bytes = lump[::]
            else:
                lump_bytes = lump.as_bytes()  # SpecialLumpClass method
            out.append(lump_bytes)
            # recalculate header
            header.offset = cursor_offset
            header.length = len(lump_bytes)
            cursor_offset += header.length
            headers.append(header)
        # inject header bytes in before writing
        headers = [h.as_bytes() for h in headers]
        out[1:1] = headers
        return b"".join(out)

    def mount_lump(self, name: str, header: object, sub_offset: int = 0):
        stream = self.stream
        offset, length = header.offset, header.length
        offset -= sub_offset
        # decompress lump if compressed
        stream.seek(offset)
        if stream.read(4) == b"LZMA":
            assert header.flags & 0x01 == 0x01, "compression flag unset"
            assert length > 17, "incomplete compressed lump"
            stream.seek(1, -4)
            decompressed_lump = decompress(stream.read(length))
            stream = io.BytesIO(decompressed_lump)
            offset, length = 0, len(decompressed_lump)
        # get LumpClass
        try:
            LumpClass = self.LumpClasses[name][header.version]
        except KeyError:  # no LumpClass for this name & version
            setattr(self, name, lumps.RawBspLump.from_stream(stream, offset, length))
            return
        # bytes -> LumpClass
        try:
            stream.seek(offset)
            raw_lump = stream.read(length)
            assert len(raw_lump) == length, "unexpected EOF; bad offset?"
            lump = LumpClass.from_bytes(raw_lump)
        except Exception as exc:
            self.loading_errors[name] = exc
            lump = lumps.RawBspLump.from_stream(stream, offset, length)
        setattr(self, name, lump)

    @classmethod
    def from_stream(cls, stream: lumps.Stream, bsp, offset=0, length=-1, sub_offset=0) -> GameLump:
        endianness = bsp.endianness
        GameLumpHeaderClass = bsp.branch.GAME_LUMP_HEADER
        LumpClasses = bsp.branch.GAME_LUMP_CLASSES
        out = cls(endianness, GameLumpHeaderClass)
        out.LumpClasses = LumpClasses
        out.stream = stream
        stream.seek(offset)
        # parse header
        # TODO: check for skipped bytes / padding
        game_lumps_count = int.from_bytes(stream.read(4), endianness)
        for i in range(game_lumps_count):
            header = GameLumpHeaderClass.from_stream(stream)
            name = header.id.decode("ascii")
            if endianness == "little":
                name = name[::-1]  # "prps" -> "sprp"
            out.headers[name] = header
        # load child lumps (SpecialLumpClasses)
        for name, header in out.headers.items():
            out.mount_lump(name, header, sub_offset)
        return out


class DarkMessiahSPGameLump(GameLump):
    endianness: str = "little"
    GameLumpHeaderClass: Any  # used for reads / writes
    headers: Dict[str, Any]
    # ^ {"child_lump": GameLumpHeader}
    loading_errors: Dict[str, Any]
    # ^ {"child_lump": Error}
    stream: lumps.Stream
    unknown: int = 0

    def as_bytes(self, lump_offset=0) -> bytes:
        """lump_offset makes headers relative to the stream"""
        # NOTE: ValveBsp .lmp external lumps have a 16 byte header
        # NOTE: RespawnBsp .bsp_lump offsets are relative to the internal .bsp GAME_LUMP.offset
        # NOTE: Xbox360 child lumps will not be recompressed
        out = [
            len(self.headers).to_bytes(4, self.endianness),
            self.unknown]
        headers = list()
        cursor_offset = sum([
            lump_offset,
            8,
            len(self.headers) * struct.calcsize(self.GameLumpHeaderClass._format)])
        # write child lumps
        # TODO: generate absent headers from lump names
        # -- this will require an endianness check for header.id
        for name, header in self.headers.items():
            lump = getattr(self, name)
            if isinstance(lump, lumps.RawBspLump):
                lump_bytes = lump[::]
            else:
                lump_bytes = lump.as_bytes()  # SpecialLumpClass method
            out.append(lump_bytes)
            # recalculate header
            header.offset = cursor_offset
            header.length = len(lump_bytes)
            cursor_offset += header.length
            headers.append(header)
        # inject header bytes in before writing
        headers = [h.as_bytes() for h in headers]
        out[1:1] = headers
        return b"".join(out)

    @classmethod
    def from_stream(cls, stream: lumps.Stream, bsp, offset=0, length=-1, sub_offset=0) -> GameLump:
        endianness = bsp.endianness
        GameLumpHeaderClass = bsp.branch.GAME_LUMP_HEADER
        LumpClasses = bsp.branch.GAME_LUMP_CLASSES
        out = cls(endianness, GameLumpHeaderClass)
        out.LumpClasses = LumpClasses
        out.stream = stream
        stream.seek(offset)
        # parse header
        # TODO: check for skipped bytes / padding
        game_lumps_count = int.from_bytes(stream.read(4), endianness)
        out.unknown = int.from_bytes(stream.read(4), endianness)
        for i in range(game_lumps_count):
            header = GameLumpHeaderClass.from_stream(stream)
            name = header.id.decode("ascii")
            if endianness == "little":
                name = name[::-1]  # "prps" -> "sprp"
            out.headers[name] = header
        for name, header in out.headers.items():
            out.mount_lump(name, header, sub_offset)
        return out


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
        if lump_header.fourCC != 0:
            self.file.seek(lump_header.offset)
            compressed_lump = self.file.read(lump_header.length)
            stream = io.BytesIO(decompress(compressed_lump))
            offset, length = 0, lump_header.fourCC
        else:
            stream = self.file
            offset, length = lump_header.offset, lump_header.length
        try:
            if lump_name == "GAME_LUMP":
                assert lump_header.fourCC == 0  # shouldn't be compressed
                GameLumpClass = GameLump
                if self.branch.__name__.split(".")[-1] == "dark_messiah_sp":
                    GameLumpClass = DarkMessiahSPGameLump
                BspLump = GameLumpClass.from_stream(self.file, self, offset, length)
            elif lump_name in self.branch.LUMP_CLASSES:
                LumpClass = self.branch.LUMP_CLASSES[lump_name][lump_header.version]
                BspLump = lumps.BspLump.from_stream(stream, LumpClass, offset, length)
            elif lump_name in self.branch.SPECIAL_LUMP_CLASSES:
                SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[lump_name][lump_header.version]
                stream.seek(offset)
                BspLump = SpecialLumpClass.from_bytes(stream.read(length))
            elif lump_name in self.branch.BASIC_LUMP_CLASSES:
                LumpClass = self.branch.BASIC_LUMP_CLASSES[lump_name][lump_header.version]
                BspLump = lumps.BasicBspLump.from_stream(stream, LumpClass, offset, length)
            else:
                BspLump = lumps.RawBspLump.from_stream(stream, offset, length)
        except KeyError:  # lump VERSION not supported
            BspLump = lumps.RawBspLump.from_stream(stream, offset, length)
        except Exception as exc:
            self.loading_errors[lump_name] = exc
            BspLump = lumps.RawBspLump.from_stream(stream, offset, length)
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
            if hasattr(BasicLumpClass, "as_int"):  # core.BitField
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
