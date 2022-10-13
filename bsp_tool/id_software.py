import os
from typing import Any, Dict

from . import base
from . import lumps


class QuakeBsp(base.Bsp):
    file_magic = None
    # struct LumpHeader { int offset, version; };
    # struct BspHeader { int version; LumpHeader headers[]; };

    def __repr__(self):
        branch_script = ".".join(self.branch.__name__.split(".")[-2:])
        version = f"(version {self.bsp_version})"  # no file_magic
        return f"<{self.__class__.__name__} '{self.filename}' {branch_script} {version}>"

    def _preload_lump(self, lump_name: str, lump_header: Any):
        if lump_header.length == 0:
            return
        try:
            if lump_name in self.branch.LUMP_CLASSES:
                LumpClass = self.branch.LUMP_CLASSES[lump_name]
                BspLump = lumps.BspLump(self.file, lump_header, LumpClass)
            elif lump_name in self.branch.SPECIAL_LUMP_CLASSES:
                SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[lump_name]
                self.file.seek(lump_header.offset)
                BspLump = SpecialLumpClass(self.file.read(lump_header.length))
            elif lump_name in self.branch.BASIC_LUMP_CLASSES:
                LumpClass = self.branch.BASIC_LUMP_CLASSES[lump_name]
                BspLump = lumps.BasicBspLump(self.file, lump_header, LumpClass)
            else:
                BspLump = lumps.RawBspLump(self.file, lump_header)
        except Exception as exc:
            self.loading_errors[lump_name] = exc
            BspLump = lumps.RawBspLump(self.file, lump_header)
        setattr(self, lump_name, BspLump)

    def _preload(self):
        # collect files
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        # collect metadata
        self.bsp_version = int.from_bytes(self.file.read(4), "little")
        self.file.seek(0, 2)  # move cursor to end of file
        self.bsp_file_size = self.file.tell()
        # collect lumps
        self.headers = dict()
        self.loading_errors: Dict[str, Exception] = dict()
        for lump_name, lump_header in self._header_generator(offset=4):
            self._preload_lump(lump_name, lump_header)
        # TODO: detect additional BSPX data appended to end of file


class ReMakeQuakeBsp(QuakeBsp):
    """ReMakeQuake BSP2 Format"""
    file_magic = b"BSP2"
    bsp_version = None
    # https://quakewiki.org/wiki/BSP2
    # https://github.com/xonotic/darkplaces/blob/master/model_brush.c
    # struct LumpHeader { int offset, version; };
    # struct BspHeader { char[4] file_magic; LumpHeader headers[]; };

    def __repr__(self):
        branch_script = ".".join(self.branch.__name__.split(".")[-2:])
        return f"<{self.__class__.__name__} '{self.filename}' {branch_script}>"

    def _preload(self):
        # collect files
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        # collect metadata
        file_magic = self.file.read(4)
        if file_magic != self.file_magic and file_magic != bytes(reversed(self.file_magic)):
            raise RuntimeError(f"{self.file} is not a RemakeQuakeBsp! file_magic is incorrect")
        self.file_magic = file_magic
        self.file.seek(0, 2)  # move cursor to end of file
        self.bsp_file_size = self.file.tell()
        # collect lumps
        self.headers = dict()
        self.loading_errors: Dict[str, Exception] = dict()
        for lump_name, lump_header in self._header_generator(offset=4):
            self._preload_lump(lump_name, lump_header)


class IdTechBsp(base.Bsp):
    file_magic = b"IBSP"
    # https://www.mralligator.com/q3/
    # NOTE: Quake 3 .bsp are usually stored in .pk3 files
    # struct LumpHeader { int offset, length; };
    # struct BspHeader { char file_magic[4]; int version; LumpHeader headers[]; };

    _preload_lump = QuakeBsp._preload_lump

    def _preload(self):
        """Loads filename using the format outlined in this .bsp's branch defintion script"""
        # collect files
        local_files = os.listdir(self.folder)
        def is_related(f): return f.startswith(os.path.splitext(self.filename)[0])
        self.associated_files = [f for f in local_files if is_related(f)]
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        # collect metadata
        file_magic = self.file.read(4)
        if file_magic != self.file_magic:
            raise RuntimeError(f"{self.file} is not an IdTechBsp! file_magic is incorrect")
        self.bsp_version = int.from_bytes(self.file.read(4), "little")
        self.file.seek(0, 2)  # move cursor to end of file
        self.bsp_file_size = self.file.tell()
        # collect lumps
        self.headers = dict()
        self.loading_errors: Dict[str, Exception] = dict()
        for lump_name, lump_header in self._header_generator(offset=8):
            self._preload_lump(lump_name, lump_header)


class FusionBsp(IdTechBsp):
    """QFusion FBSP Format"""
    file_magic = b"FBSP"
    # https://quakewiki.org/wiki/FTEQW_Modding#FBSP_map_support
    # https://github.com/Qfusion/qfusion/blob/master/source/qcommon/qfiles.h
