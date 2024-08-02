# https://developer.valvesoftware.com/wiki/BSPX
# https://github.com/fte-team/fteqw/blob/master/specs/bspx.txt
from __future__ import annotations
import io
from types import MethodType, ModuleType
from typing import Dict, List

from . import base
from . import lumps
from .branches import bspx


class BspX:
    branch: ModuleType = bspx
    bsp: base.Bsp  # for methods
    headers: List[bspx.LumpHeader]
    loading_errors: Dict[str, Exception]

    def __init__(self):
        self.bsp = None  # will break methods
        self.headers = dict()
        self.loading_errors = dict()
        # attach methods
        for method_name, method in self.branch.methods.items():
            method = MethodType(method, self)
            setattr(self, method_name, method)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {len(self.headers)} lumps @ 0x{id(self):016X}>"

    def mount_lump(self, lump_name: str, lump_header: bspx.LumpHeader, stream: io.BytesIO):
        # NOTE: adapted from id_software.QuakeBsp.mount_lump()
        assert lump_header.length != 0, "why?"
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
    def from_bsp(cls, bsp: base.Bsp) -> BspX:
        # NOTE: we don't use bsp._tail() because we need to read from bsp.file
        lumps_end = max(h.offset + h.length for h in bsp.headers.values())
        assert lumps_end < bsp.filesize, "bsp has no tail"
        bsp.file.seek(lumps_end)
        tail = bsp.file.read()
        # TODO: is tail a pakfile?
        assert b"BSPX" in tail, "couldn't find any BSPX data in bsp tail"
        padding_length = tail.index(b"BSPX")
        assert padding_length < 4, "excessively padded tail"
        padding = tail[:padding_length]
        assert padding == b"\x00" * padding_length, "mystery data before BSPX"
        # parse BSPX
        out = cls.from_stream(bsp.file, lumps_end + padding_length)
        out.bsp = bsp  # attached for methods
        return out

    @classmethod
    def from_stream(cls, stream: io.BytesIO, bspx_offset: int) -> BspX:
        out = cls()
        stream.seek(bspx_offset)
        # header
        assert stream.read(4) == b"BSPX"
        num_lumps = int.from_bytes(stream.read(4), "little")
        for i in range(num_lumps):
            header = bspx.LumpHeader.from_stream(stream)
            header_name = header.name.rstrip(b"\x00").decode()
            assert header_name in cls.branch.LUMPS, f"unrecognised BSPX lump: '{header_name}'"
            out.headers[header_name] = header
        # lumps
        for lump_name, lump_header in out.headers.items():
            out.mount_lump(lump_name, lump_header, stream)
        return out
