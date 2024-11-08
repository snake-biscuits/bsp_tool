from __future__ import annotations
import io
from types import ModuleType
from typing import Any, Dict, List

from . import base
from . import lumps


class QuakeBsp(base.Bsp):
    file_magic = None
    # struct LumpHeader { int offset, length; };
    # struct BspHeader { int version; LumpHeader lumps[]; };

    def __repr__(self):
        branch_script = ".".join(self.branch.__name__.split(".")[-2:])
        version = f"(version {self.version})"  # no file_magic
        return f"<{self.__class__.__name__} '{self.filename}' {branch_script} {version}>"

    def extra_patterns(self) -> List[str]:
        # https://quakewiki.org/wiki/Quake_file_formats
        base_filename = self.filename.rpartition(".")[0]
        return [
            f"{base_filename}.dlit",
            f"{base_filename}.ent",
            f"{base_filename}.lit",
            f"{base_filename}.lux",
            f"{base_filename}.vis"]

    def mount_lump(self, lump_name: str, lump_header: Any, stream: io.BytesIO):
        if lump_header.length == 0:
            return
        try:
            if lump_name in self.branch.LUMP_CLASSES:
                LumpClass = self.branch.LUMP_CLASSES[lump_name]
                BspLump = lumps.BspLump.from_header(stream, lump_header, LumpClass)
            elif lump_name in self.branch.SPECIAL_LUMP_CLASSES:
                SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[lump_name]
                stream.seek(lump_header.offset)
                BspLump = SpecialLumpClass.from_bytes(stream.read(lump_header.length))
            elif lump_name in self.branch.BASIC_LUMP_CLASSES:
                LumpClass = self.branch.BASIC_LUMP_CLASSES[lump_name]
                BspLump = lumps.BasicBspLump.from_header(stream, lump_header, LumpClass)
            else:
                BspLump = lumps.RawBspLump.from_header(stream, lump_header)
        except Exception as exc:
            self.loading_errors[lump_name] = exc
            BspLump = lumps.RawBspLump.from_header(stream, lump_header)
        setattr(self, lump_name, BspLump)

    @classmethod
    def from_stream(cls, branch: ModuleType, filename: str, stream: io.BytesIO) -> QuakeBsp:
        bsp = cls(branch, filename)
        bsp.file = stream
        # collect metadata
        bsp.version = int.from_bytes(bsp.file.read(4), "little")
        bsp.file.seek(0, 2)  # move cursor to end of file
        bsp.filesize = bsp.file.tell()
        # collect lumps
        bsp.headers: Dict[str, object] = dict()
        bsp.loading_errors: Dict[str, Exception] = dict()
        for lump_name, lump_header in bsp._header_generator(offset=4):
            bsp.mount_lump(lump_name, lump_header, bsp.file)
        # TODO: detect additional BSPX data appended to end of file
        # -- if b"BSPX" in self._tail(): ...
        return bsp


class ReMakeQuakeBsp(QuakeBsp):
    """ReMakeQuake BSP2 Format"""
    file_magic = b"BSP2"
    version = None
    # https://quakewiki.org/wiki/BSP2
    # https://github.com/xonotic/darkplaces/blob/master/model_brush.c
    # struct LumpHeader { uint32_t offset, length; };
    # struct BspHeader { uint32_t file_magic; LumpHeader lumps[]; };

    def __repr__(self):
        branch_script = ".".join(self.branch.__name__.split(".")[-2:])
        return f"<{self.__class__.__name__} '{self.filename}' {branch_script}>"

    @classmethod
    def from_stream(cls, branch: ModuleType, filepath: str, stream: io.BytesIO) -> ReMakeQuakeBsp:
        bsp = cls(branch, filepath)
        bsp.file = stream
        # collect metadata
        file_magic = bsp.file.read(4)
        if file_magic != bsp.file_magic and file_magic != bytes(reversed(bsp.file_magic)):
            raise RuntimeError(f"{bsp.file} is not a {bsp.__class__.__name__}! file_magic is incorrect")
        bsp.file_magic = file_magic
        bsp.file.seek(0, 2)  # move cursor to end of file
        bsp.filesize = bsp.file.tell()
        # collect lumps
        bsp.headers = dict()
        bsp.loading_errors: Dict[str, Exception] = dict()
        for lump_name, lump_header in bsp._header_generator(offset=4):
            bsp.mount_lump(lump_name, lump_header, bsp.file)
        bsp._get_signature(4 + (8 * len(bsp.branch.LUMP)))
        return bsp


class Quake64Bsp(ReMakeQuakeBsp):
    """QuakeCon 2021 PC Re-release of Midway's Nintendo 64 Port"""
    # https://github.com/sezero/quakespasm/blob/master/Quake/bspfile.h
    # https://github.com/sezero/quakespasm/blob/master/Quake/gl_model.c
    file_magic = b" 46Q"


class IdTechBsp(base.Bsp):
    file_magic = b"IBSP"
    # https://www.mralligator.com/q3/
    # NOTE: Quake 3 .bsp are usually stored in .pk3 files
    # struct LumpHeader { int offset, length; };
    # struct BspHeader { char file_magic[4]; int version; LumpHeader headers[]; };

    mount_lump = QuakeBsp.mount_lump

    @classmethod
    def from_stream(cls, branch: ModuleType, filepath: str, stream: io.BytesIO) -> IdTechBsp:
        bsp = cls(branch, filepath)
        bsp.file = stream
        # collect metadata
        file_magic = bsp.file.read(4)
        if file_magic != bsp.file_magic:
            raise RuntimeError(f"{bsp.file} is not a {bsp.__class__.__name__}! file_magic is incorrect")
        bsp.version = int.from_bytes(bsp.file.read(4), "little")
        bsp.file.seek(0, 2)  # move cursor to end of file
        bsp.filesize = bsp.file.tell()
        # collect lumps
        bsp.headers = dict()
        bsp.loading_errors: Dict[str, Exception] = dict()
        for lump_name, lump_header in bsp._header_generator(offset=8):
            bsp.mount_lump(lump_name, lump_header, bsp.file)
        bsp._get_signature(8 + (8 * len(bsp.branch.LUMP)))
        return bsp


class FusionBsp(IdTechBsp):
    """QFusion FBSP Format"""
    file_magic = b"FBSP"
    # https://quakewiki.org/wiki/FTEQW_Modding#FBSP_map_support
    # https://github.com/Qfusion/qfusion/blob/master/source/qcommon/qfiles.h


class QbismBsp(IdTechBsp):
    """Qbism QBSP Format"""
    file_magic = b"QBSP"
    # https://github.com/qbism/super8
    # https://github.com/qbism/q2tools-220
