import os
import struct
from typing import Dict

from . import base
from . import lumps


class QuakeBsp(base.Bsp):
    file_magic = None

    def __repr__(self):
        branch_script = ".".join(self.branch.__name__.split(".")[-2:])
        version = f"(version {self.bsp_version})"  # no file_magic
        return f"<{self.__class__.__name__} '{self.filename}' {branch_script} {version}>"

    def _preload(self):
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        # struct LumpHeader { int offset, version; };
        # struct BspHeader { int version; LumpHeader headers[]; };
        self.bsp_version = int.from_bytes(self.file.read(4), "little")
        self.file.seek(0, 2)  # move cursor to end of file
        self.bsp_file_size = self.file.tell()
        self.headers = dict()
        self.loading_errors: Dict[str, Exception] = dict()
        for LUMP in self.branch.LUMP:
            self.file.seek(4 + struct.calcsize(self.branch.LumpHeader._format) * LUMP.value)
            lump_header = self.branch.LumpHeader.from_stream(self.file)
            self.headers[LUMP.name] = lump_header
            if lump_header.length == 0:
                continue  # empty lump
            try:
                if LUMP.name in self.branch.LUMP_CLASSES:
                    LumpClass = self.branch.LUMP_CLASSES[LUMP.name]
                    BspLump = lumps.BspLump(self.file, lump_header, LumpClass)
                elif LUMP.name in self.branch.SPECIAL_LUMP_CLASSES:
                    SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP.name]
                    self.file.seek(lump_header.offset)
                    BspLump = SpecialLumpClass(self.file.read(lump_header.length))
                elif LUMP.name in self.branch.BASIC_LUMP_CLASSES:
                    LumpClass = self.branch.BASIC_LUMP_CLASSES[LUMP.name]
                    BspLump = lumps.BasicBspLump(self.file, lump_header, LumpClass)
                else:
                    BspLump = lumps.RawBspLump(self.file, lump_header)
            except Exception as exc:
                self.loading_errors[LUMP.name] = exc
                BspLump = lumps.RawBspLump(self.file, lump_header)
            setattr(self, LUMP.name, BspLump)


class ReMakeQuakeBsp(QuakeBsp):
    """ReMakeQuake BSP2 Format"""
    file_magic = b"BSP2"
    bsp_version = None
    # https://ericwa.github.io/ericw-tools/doc/qbsp.html
    # https://github.com/ericwa/ericw-tools
    # https://quakewiki.org/wiki/BSP2
    # https://github.com/xonotic/darkplaces/blob/master/model_brush.c

    def _preload(self):
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        # struct LumpHeader { int offset, version; };
        # struct BspHeader { char[4] file_magic; LumpHeader headers[]; };
        file_magic = self.file.read(4)
        assert file_magic == self.file_magic, f"{self.filename} is not a {self.__class__.__name__}"
        self.file_magic = file_magic
        self.version = None
        self.file.seek(0, 2)  # move cursor to end of file
        self.bsp_file_size = self.file.tell()
        self.headers = dict()
        self.loading_errors: Dict[str, Exception] = dict()
        for LUMP in self.branch.LUMP:
            self.file.seek(4 + struct.calcsize(self.branch.LumpHeader._format) * LUMP.value)
            lump_header = self.branch.LumpHeader.from_stream(self.file)
            self.headers[LUMP.name] = lump_header
            if lump_header.length == 0:
                continue  # empty lump
            try:
                if LUMP.name in self.branch.LUMP_CLASSES:
                    LumpClass = self.branch.LUMP_CLASSES[LUMP.name]
                    BspLump = lumps.BspLump(self.file, lump_header, LumpClass)
                elif LUMP.name in self.branch.SPECIAL_LUMP_CLASSES:
                    SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP.name]
                    self.file.seek(lump_header.offset)
                    BspLump = SpecialLumpClass(self.file.read(lump_header.length))
                elif LUMP.name in self.branch.BASIC_LUMP_CLASSES:
                    LumpClass = self.branch.BASIC_LUMP_CLASSES[LUMP.name]
                    BspLump = lumps.BasicBspLump(self.file, lump_header, LumpClass)
                else:
                    BspLump = lumps.RawBspLump(self.file, lump_header)
            except Exception as exc:
                self.loading_errors[LUMP.name] = exc
                BspLump = lumps.RawBspLump(self.file, lump_header)
            setattr(self, LUMP.name, BspLump)


class IdTechBsp(base.Bsp):
    file_magic = b"IBSP"
    # https://www.mralligator.com/q3/
    # NOTE: Quake 3 .bsp are usually stored in .pk3 files

    def _preload(self):
        """Loads filename using the format outlined in this .bsp's branch defintion script"""
        local_files = os.listdir(self.folder)
        def is_related(f): return f.startswith(os.path.splitext(self.filename)[0])
        self.associated_files = [f for f in local_files if is_related(f)]
        # open .bsp
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        # struct LumpHeader { int offset, length; };
        # struct BspHeader { char file_magic[4]; int version; LumpHeader headers[]; };
        file_magic = self.file.read(4)
        assert file_magic == self.file_magic, f"{self.file.name} file_magic is invalid: ({file_magic} != {self.file_magic})"
        self.bsp_version = int.from_bytes(self.file.read(4), "little")
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
                if LUMP.name in self.branch.LUMP_CLASSES:
                    LumpClass = self.branch.LUMP_CLASSES[LUMP.name]
                    BspLump = lumps.BspLump(self.file, lump_header, LumpClass)
                elif LUMP.name in self.branch.SPECIAL_LUMP_CLASSES:
                    SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP.name]
                    self.file.seek(lump_header.offset)
                    lump_data = self.file.read(lump_header.length)
                    BspLump = SpecialLumpClass(lump_data)
                elif LUMP.name in self.branch.BASIC_LUMP_CLASSES:
                    LumpClass = self.branch.BASIC_LUMP_CLASSES[LUMP.name]
                    BspLump = lumps.BasicBspLump(self.file, lump_header, LumpClass)
                else:
                    BspLump = lumps.RawBspLump(self.file, lump_header)
            except Exception as exc:
                self.loading_errors[LUMP.name] = exc
                BspLump = lumps.RawBspLump(self.file, lump_header)
            setattr(self, LUMP.name, BspLump)


class FusionBsp(IdTechBsp):
    """QFusion FBSP Format"""
    file_magic = b"FBSP"
    # https://quakewiki.org/wiki/FTEQW_Modding#FBSP_map_support
    # https://github.com/Qfusion/qfusion/blob/master/source/qcommon/qfiles.h
