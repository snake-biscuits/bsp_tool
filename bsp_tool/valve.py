import os
import struct
from types import ModuleType
from typing import Dict

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
    # struct LumpHeader { int offset, length version, fourCC; };
    # struct SourceBspHeader { char file_magic[4]; int version; LumpHeader headers[64]; int revision; };

    def __init__(self, branch: ModuleType, filename: str = "untitled.bsp", autoload: bool = True):
        super(ValveBsp, self).__init__(branch, filename, autoload)

    def _preload(self):
        """Loads filename using the format outlined in this .bsp's branch defintion script"""
        local_files = os.listdir(self.folder)
        def is_related(f): return f.startswith(self.filename.partition(".")[0])
        self.associated_files = [f for f in local_files if is_related(f)]
        # open .bsp
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        file_magic = self.file.read(4)
        if file_magic == self.file_magic:
            self.endianness = "little"
        elif file_magic == bytes(reversed(self.file_magic)):
            self.endianness = "big"
            self.file_magic = file_magic  # b"PSBV"
        else:
            raise RuntimeError(f"{self.file} is not a ValveBsp! file_magic is incorrect")
        self.bsp_version = int.from_bytes(self.file.read(4), self.endianness)
        if self.bsp_version > 0xFFFF:  # major.minor bsp_version
            self.bsp_version = (self.bsp_version & 0xFFFF, self.bsp_version >> 16)  # major, minor
        self.file.seek(0, 2)  # move cursor to end of file
        self.bsp_file_size = self.file.tell()

        self.headers = dict()
        self.loading_errors: Dict[str, Exception] = dict()
        for LUMP in self.branch.LUMP:
            self.file.seek(8 + struct.calcsize(self.branch.LumpHeader._format) * LUMP.value)
            lump_header = self.branch.LumpHeader.from_stream(self.file)
            self.headers[LUMP.name] = lump_header
            if lump_header.length == 0:
                continue
            try:
                if LUMP.name == "GAME_LUMP":
                    # NOTE: lump_header.version is ignored in this case
                    GameLumpClasses = getattr(self.branch, "GAME_LUMP_CLASSES", dict())
                    BspLump = lumps.GameLump(self.file, lump_header, self.endianness,
                                             GameLumpClasses, self.branch.GAME_LUMP_HEADER)
                elif LUMP.name in self.branch.LUMP_CLASSES:
                    LumpClass = self.branch.LUMP_CLASSES[LUMP.name][lump_header.version]
                    BspLump = lumps.create_BspLump(self.file, lump_header, LumpClass)
                elif LUMP.name in self.branch.SPECIAL_LUMP_CLASSES:
                    SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP.name][lump_header.version]
                    decompressed_file, decompressed_header = lumps.decompressed(self.file, lump_header)
                    decompressed_file.seek(decompressed_header.offset)
                    lump_data = decompressed_file.read(decompressed_header.length)
                    BspLump = SpecialLumpClass(lump_data)
                elif LUMP.name in self.branch.BASIC_LUMP_CLASSES:
                    LumpClass = self.branch.BASIC_LUMP_CLASSES[LUMP.name][lump_header.version]
                    BspLump = lumps.create_BasicBspLump(self.file, lump_header, LumpClass)
                else:
                    BspLump = lumps.create_RawBspLump(self.file, lump_header)
            except KeyError:  # lump VERSION not supported
                self.loading_errors[LUMP.name] = KeyError(f"{LUMP.name} v{lump_header.version} is not supported")
                BspLump = lumps.create_RawBspLump(self.file, lump_header)
            except Exception as exc:
                self.loading_errors[LUMP.name] = exc
                BspLump = lumps.create_RawBspLump(self.file, lump_header)
            setattr(self, LUMP.name, BspLump)

    def lump_as_bytes(self, lump_name: str) -> bytes:
        """Converts the named (versioned) lump back into bytes"""
        if not hasattr(self, lump_name):
            return b""  # lump is empty / deleted
        lump_entries = getattr(self, lump_name)
        lump_version = self.headers[lump_name].version
        all_lump_classes = {**self.branch.BASIC_LUMP_CLASSES,
                            **self.branch.LUMP_CLASSES,
                            **self.branch.SPECIAL_LUMP_CLASSES}
        # RawBspLump -> byte
        if lump_name not in all_lump_classes or lump_name in self.loading_errors:
            return bytes(lump_entries)
        elif lump_name in all_lump_classes and lump_name != "GAME_LUMP":
            if lump_version not in all_lump_classes[lump_name]:
                return bytes(lump_entries)
        # BasicBspLump -> bytes
        if lump_name in self.branch.BASIC_LUMP_CLASSES:
            _format = self.branch.BASIC_LUMP_CLASSES[lump_name][lump_version]._format
            raw_lump = struct.pack(f"{len(lump_entries)}{_format}", *lump_entries)
        # BspLump -> bytes
        elif lump_name in self.branch.LUMP_CLASSES:
            _format = self.branch.LUMP_CLASSES[lump_name][lump_version]._format
            raw_lump = b"".join([struct.pack(_format, *x.flat()) for x in lump_entries])
        # SpecialLumpClass -> bytes
        elif lump_name in self.branch.SPECIAL_LUMP_CLASSES:
            raw_lump = lump_entries.as_bytes()
        # GameLump -> bytes
        elif lump_name == "GAME_LUMP":
            raw_lump = lump_entries.as_bytes()
        return raw_lump

    def save_as(self, filename: str = None):
        raise NotImplementedError()
        lump_order = sorted([L for L in self.branch.LUMP],
                            key=lambda L: (self.headers[L.name].offset, self.headers[L.name].length))
        # ^ {"lump.name": LumpHeader}
        # NOTE: messes up on empty lumps, so we can't get an exact 1:1 copy /;
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
                headers[LUMP.name] = self.branch.LumpHeader(offset=current_offset,
                                                            length=0,
                                                            version=self.headers[LUMP.name].version)
                continue
            # wierd hack to align unused lump offsets correctly
            if current_offset == 0:
                current_offset = 16 + (16 * 128)  # first byte after headers
            length = len(raw_lumps[LUMP.name])
            headers[LUMP.name] = self.branch.LumpHeader(offset=current_offset,
                                                        length=length,
                                                        version=self.headers[LUMP.name].version)
            current_offset += length
            if current_offset % 4 != 0:
                current_offset += 4 - current_offset % 4
        del current_offset
        if "GAME_LUMP" in raw_lumps:
            raw_lumps["GAME_LUMP"] = self.GAME_LUMP.as_bytes(headers["GAME_LUMP"].offset)
        # make file
        os.makedirs(os.path.dirname(os.path.realpath(filename)), exist_ok=True)
        outfile = open(filename, "wb")
        bsp_version = self.bsp_version
        if isinstance(self.bsp_version, tuple):
            bsp_version = bsp_version[0] + bsp_version[1] << 16
        outfile.write(struct.pack("4s2I", self.file_magic, bsp_version, self.revision))
        # write headers
        for LUMP in self.branch.LUMP:
            header = headers[LUMP.name]
            outfile.write(struct.pack("4I", header.offset, header.length, header.version, header.fourCC))
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
