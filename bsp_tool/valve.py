from collections import namedtuple  # for type hints
import enum  # for type hints
import os
import struct
from types import ModuleType
from typing import Dict

from . import base
from . import id_software
from . import lumps


GoldSrcLumpHeader = namedtuple("GoldSrcLumpHeader", ["offset", "length"])


class GoldSrcBsp(id_software.IdTechBsp):  # TODO: QuakeBsp subclass?
    file_magic = None
    # https://github.com/ValveSoftware/halflife/blob/master/utils/common/bspfile.h
    # http://hlbsp.sourceforge.net/index.php?content=bspdef

    def __repr__(self):
        version = f"(version {self.bsp_version})"  # no file_magic
        branch_script = ".".join(self.branch.__name__.split(".")[-2:])
        return f"<{self.__class__.__name__} '{self.filename}' {branch_script} {version}>"

    def _preload(self):
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        self.bsp_version = int.from_bytes(self.file.read(4), "little")
        self.file.seek(0, 2)  # move cursor to end of file
        self.bsp_file_size = self.file.tell()

        self.headers = dict()
        self.loading_errors: Dict[str, Exception] = dict()
        for LUMP_enum in self.branch.LUMP:
            LUMP_NAME = LUMP_enum.name
            self.file.seek(self.branch.lump_header_address[LUMP_enum])
            offset, length = struct.unpack("2I", self.file.read(8))
            lump_header = GoldSrcLumpHeader(offset, length)
            self.headers[LUMP_NAME] = lump_header
            if length == 0:
                continue  # empty lump
            try:
                if LUMP_NAME in self.branch.LUMP_CLASSES:
                    LumpClass = self.branch.LUMP_CLASSES[LUMP_NAME]
                    BspLump = lumps.create_BspLump(self.file, lump_header, LumpClass)
                elif LUMP_NAME in self.branch.SPECIAL_LUMP_CLASSES:
                    SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP_NAME]
                    self.file.seek(offset)
                    BspLump = SpecialLumpClass(self.file.read(length))
                elif LUMP_NAME in self.branch.BASIC_LUMP_CLASSES:
                    LumpClass = self.branch.BASIC_LUMP_CLASSES[LUMP_NAME]
                    BspLump = lumps.create_BasicBspLump(self.file, lump_header, LumpClass)
                else:
                    BspLump = lumps.create_RawBspLump(self.file, lump_header)
            except Exception as exc:
                self.loading_errors[LUMP_NAME] = exc
                BspLump = lumps.create_RawBspLump(self.file, lump_header)
                # NOTE: doesn't decompress LZMA, fix that
            setattr(self, LUMP_NAME, BspLump)

    def _read_header(self, LUMP: enum.Enum) -> GoldSrcLumpHeader:
        """Reads bytes of lump"""
        self.file.seek(self.branch.lump_header_address[LUMP])
        offset, length = struct.unpack("2I", self.file.read(8))
        header = GoldSrcLumpHeader(offset, length)
        return header


class ValveBsp(base.Bsp):
    # https://developer.valvesoftware.com/wiki/Source_BSP_File_Format
    file_magic = b"VBSP"

    def __init__(self, branch: ModuleType, filename: str = "untitled.bsp", autoload: bool = True):
        super(ValveBsp, self).__init__(branch, filename, autoload)

    # TODO: migrate Source specific functionality from base.Bsp to ValveBsp

    def _read_header(self, LUMP: enum.Enum) -> namedtuple:  # any LumpHeader
        """Get LUMP from self.branch.LUMP; e.g. self.branch.LUMP.ENTITIES"""
        # NOTE: each branch of VBSP has unique headers,
        # -- so branch.read_lump_header function is used
        # TODO: move to a system of using header LumpClasses instead of the above
        return self.branch.read_lump_header(self.file, LUMP)

    def save_as(self, filename: str = None):
        raise NotImplementedError()
        # # TODO: get LumpHeaderClass from branch
        # lump_order = sorted([L for L in self.branch.LUMP],
        #                     key=lambda L: (self.headers[L.name].offset, self.headers[L.name].length))
        # # ^ {"lump.name": LumpHeader / ExternalLumpHeader}
        # # NOTE: messes up on empty lumps, so we can't get an exact 1:1 copy /;
        # raw_lumps: Dict[str, bytes] = dict()
        # # ^ {"LUMP.name": b"raw lump data]"}
        # for LUMP in self.branch.LUMP:
        #     lump_bytes = self.lump_as_bytes(LUMP.name)
        #     if lump_bytes != b"":  # don't write empty lumps
        #         raw_lumps[LUMP.name] = lump_bytes
        # # recalculate headers
        # current_offset = 0
        # headers = dict()
        # for LUMP in lump_order:
        #     if LUMP.name not in raw_lumps:  # lump is not present
        #          version = self.headers[LUMP.name].version  # PHYSICS_LEVEL needs version preserved
        #          headers[LUMP.name] = LumpHeader(current_offset, 0, version, 0)
        #          continue
        #     # wierd hack to align unused lump offsets correctly
        #     if current_offset == 0:
        #         current_offset = 16 + (16 * 128)  # first byte after headers
        #     offset = current_offset
        #     length = len(raw_lumps[LUMP.name])
        #     version = self.headers[LUMP.name].version
        #     fourCC = 0  # fourCC is always 0 because we aren't encoding
        #     header = LumpHeader(offset, length, version, fourCC)
        #     headers[LUMP.name] = header  # recorded for noting padding
        #     current_offset += length
        #     # pad to start at the next multiple of 4 bytes
        #     # TODO: note the padding so we can remove it when writing .bsp_lump
        #     if current_offset % 4 != 0:
        #         current_offset += 4 - current_offset % 4
        # del current_offset
        # if "GAME_LUMP" in raw_lumps:
        #     raw_lumps["GAME_LUMP"] = self.GAME_LUMP.as_bytes(headers["GAME_LUMP"].offset)
        # # make file
        # os.makedirs(os.path.dirname(os.path.realpath(filename)), exist_ok=True)
        # outfile = open(filename, "wb")
        # bsp_version = self.bsp_version
        # if isinstance(self.bsp_version, tuple):
        #     bsp_version = bsp_version[0] + bsp_version[1] << 16
        # outfile.write(struct.pack("4s2I", self.file_magic, bsp_version, self.revision))
        # # write headers
        # for LUMP in self.branch.LUMP:
        #     header = headers[LUMP.name]
        #     outfile.write(struct.pack("4I", header.offset, header.length, header.version, header.fourCC))
        # # write lump contents (cannot be done until headers allocate padding)
        # for LUMP in lump_order:
        #    if LUMP.name not in raw_lumps:
        #        continue
        #    padding_length = headers[LUMP.name].offset - outfile.tell()
        #    if padding_length > 0:  # NOTE: padding_length should not exceed 3
        #        outfile.write(b"\0" * padding_length)
        #    outfile.write(raw_lumps[LUMP.name])
        # # final padding
        # end = outfile.tell()
        # padding_length = 0
        # if end % 4 != 0:
        #     padding_length = 4 - end % 4
        # outfile.write(b"\0" * padding_length)
        # outfile.close()  # main .bsp is written
