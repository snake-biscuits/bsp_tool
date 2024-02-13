import os
from types import ModuleType
from typing import Dict
import warnings

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

    def __init__(self, branch: ModuleType, filename: str = "untitled.bsp", autoload: bool = True):
        if not (filename.lower().endswith(".bsp") or filename.lower().endswith(".d3dbsp")):
            # ^ slight alteration to allow .d3dbsp extension
            raise RuntimeError("Not a .bsp")
        filename = os.path.realpath(filename)
        self.folder, self.filename = os.path.split(filename)
        self.set_branch(branch)
        self.headers = dict()
        if autoload:
            if os.path.exists(filename):
                self._preload()
            else:
                warnings.warn(UserWarning(f"{filename} not found, creating a new .bsp"))
                self.headers = {L.name: self.branch.LumpHeader() for L in self.branch.LUMP}


class D3DBsp(InfinityWardBsp):
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_4:_d3dbsp
    # https://github.com/SE2Dev/D3DBSP_Converter/blob/master/D3DBSP_Lib/D3DBSP.cpp
    file_magic = b"IBSP"
    lump_count: int
    # NOTE: Call of Duty 2 [InfinityWardBsp] uses the .d3dbsp extension, but are not D3DBsp
    # NOTE: Call of Duty 4 .d3dbsp are stored in .ff archives (see extensions.archive.FastFile)
    # -- cod3map.exe creates .d3dbsp, but extracting these from fastfiles may prove difficult
    # -- lumps are possibly divided into multiple files throughout the fastfile (*.ff)

    def _preload(self):
        """Loads filename using the format outlined in this .bsp's branch defintion script"""
        # collect files
        local_files = os.listdir(self.folder)
        def is_related(f): return f.startswith(os.path.splitext(self.filename)[0])
        self.associated_files = [f for f in local_files if is_related(f)]
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        # collect metadata
        file_magic = self.file.read(4)
        assert file_magic == self.file_magic, f"{self.file} is not a valid D3DBsp!"
        self.version = int.from_bytes(self.file.read(4), "little")
        self.lump_count = int.from_bytes(self.file.read(4), "little")
        self.file.seek(0, 2)  # move cursor to end of file
        self.filesize = self.file.tell()
        # collect lumps
        self.headers = dict()
        self.loading_errors: Dict[str, Exception] = dict()
        cursor = 12 + (self.lump_count * 8)  # end of headers; for "reading" lumps
        for i in range(self.lump_count):
            self.file.seek(12 + 8 * i)
            lump_header = self.branch.LumpHeader.from_stream(self.file)
            if lump_header.id != 0x07:  # UNKNOWN_7 is padded to every 2nd byte?
                cursor = cursor + (4 - cursor & 3)
            lump_header.offset = cursor
            cursor += lump_header.length
            lump_header.name = self.branch.LUMP(lump_header.id).name
            self.headers[lump_header.name] = lump_header
            BspLump = self._preload_lump(lump_header.name, lump_header)
            if BspLump is not None:
                setattr(self, lump_header.name, BspLump)

    def print_headers(self):
        print(f"{'LUMP.name':<24s} OFFSET LENGTH", "-" * 38, sep="\n")
        for header in self.headers:
            print(f"{header.name:<24s} {header.offset:06X} {header.length:06X}")


# TODO: XenonBsp (Xbox360, likely in big-endian .ff?)
# -- have yet to extract any for testing
