from __future__ import annotations
import io
import os
from types import ModuleType
from typing import Dict

from . import id_software


class InfinityWardBsp(id_software.IdTechBsp):
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_1:_d3dbsp
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_2:_d3dbsp
    file_magic = b"IBSP"
    # NOTE: Call of Duty 1 .bsp are stored in .pk3 (.zip) archives
    # NOTE: Call of Duty 2 .d3dbsp are stored in .iwd (.zip) archives
    # NOTE: Call of Duty 2 x360 .d3dbsp are stored in .ff archives
    # -- cod2map.exe creates .d3dbsp, but extracting these from fastfiles may prove difficult
    # -- lumps may be split across multiple files

    def __init__(self, branch: ModuleType, filepath: str = "untitled.bsp"):
        if not (filepath.lower().endswith(".bsp") or filepath.lower().endswith(".d3dbsp")):
            # ^ slight alteration to allow .d3dbsp extension
            raise RuntimeError("Not a .bsp")
        filepath = os.path.realpath(filepath)
        self.folder, self.filename = os.path.split(filepath)
        self.set_branch(branch)
        self.headers = dict()


class D3DBsp(InfinityWardBsp):
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_4:_d3dbsp
    # https://github.com/SE2Dev/D3DBSP_Converter/blob/master/D3DBSP_Lib/D3DBSP.cpp
    file_magic = b"IBSP"
    lump_count: int
    # NOTE: Call of Duty 2 [InfinityWardBsp] uses the .d3dbsp extension, but are not D3DBsp
    # NOTE: Call of Duty 4 .d3dbsp are stored in .ff archives (see extensions.archive.FastFile)
    # -- cod3map.exe creates .d3dbsp, but extracting these from fastfiles may prove difficult
    # -- lumps are possibly divided into multiple files throughout the fastfile (*.ff)

    @classmethod
    def from_stream(cls, branch: ModuleType, filepath: str, stream: io.BytesIO) -> D3DBsp:
        bsp = cls(branch, filepath)
        bsp.file = stream
        # collect metadata
        file_magic = bsp.file.read(4)
        assert file_magic == bsp.file_magic, f"{bsp.file} is not a valid D3DBsp!"
        bsp.version = int.from_bytes(bsp.file.read(4), "little")
        bsp.lump_count = int.from_bytes(bsp.file.read(4), "little")
        bsp.file.seek(0, 2)  # move cursor to end of file
        bsp.filesize = bsp.file.tell()
        # collect lumps
        bsp.headers = dict()
        bsp.loading_errors: Dict[str, Exception] = dict()
        cursor = 12 + (bsp.lump_count * 8)  # end of headers; for "reading" lumps
        for i in range(bsp.lump_count):
            bsp.file.seek(12 + 8 * i)
            lump_header = bsp.branch.LumpHeader.from_stream(bsp.file)
            if lump_header.id != 0x07:  # UNKNOWN_7 is padded to every 2nd byte?
                cursor = cursor + (4 - cursor & 3)
            lump_header.offset = cursor
            cursor += lump_header.length
            lump_header.name = bsp.branch.LUMP(lump_header.id).name
            bsp.headers[lump_header.name] = lump_header
            BspLump = bsp.mount_lump(lump_header.name, lump_header, bsp.file)
            if BspLump is not None:
                setattr(bsp, lump_header.name, BspLump)
        return bsp

    def print_headers(self):
        print(f"{'LUMP.name':<24s} OFFSET LENGTH", "-" * 38, sep="\n")
        for header in self.headers:
            print(f"{header.name:<24s} {header.offset:06X} {header.length:06X}")


# TODO: XenonBsp (Xbox360, likely in big-endian .ff?)
# -- have yet to extract any for testing
