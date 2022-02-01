import os
from types import ModuleType
from typing import Dict
import warnings

from . import base
from . import id_software
from . import lumps
from .branches.id_software.quake import LumpHeader


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


class D3DBsp(base.Bsp):
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_4:_d3dbsp
    # https://github.com/SE2Dev/D3DBSP_Converter/blob/master/D3DBSP_Lib/D3DBSP.cpp
    file_magic = b"IBSP"
    lump_count: int
    # NOTE: Call of Duty 2 [InfinityWardBsp] uses the .d3dbsp extension, but are not D3DBsp
    # NOTE: Call of Duty 4 .d3dbsp are stored in .ff archives (see extensions.archive.FastFile)
    # -- cod3map.exe creates .d3dbsp, but extracting these from fastfiles may prove difficult
    # -- lumps are possibly divided into multiple files, quake3 map compilation generates many files

    def __init__(self, branch: ModuleType, filename: str = "untitled.bsp", autoload: bool = True):
        if not filename.lower().endswith(".d3dbsp"):
            # ^ slight alteration to allow .d3dbsp extension
            raise RuntimeError("Not a .d3dbsp")
        filename = os.path.realpath(filename)
        self.folder, self.filename = os.path.split(filename)
        self.set_branch(branch)
        self.headers = dict()
        if autoload:
            if os.path.exists(filename):
                self._preload()
            else:
                warnings.warn(UserWarning(f"{filename} not found, creating a new .bsp"))
                self.headers = {L.name: LumpHeader(0, 0) for L in self.branch.LUMP}

    def _preload(self):
        """Loads filename using the format outlined in this .bsp's branch defintion script"""
        local_files = os.listdir(self.folder)
        def is_related(f): return f.startswith(os.path.splitext(self.filename)[0])
        self.associated_files = [f for f in local_files if is_related(f)]
        # open .bsp
        self.file = open(os.path.join(self.folder, self.filename), "rb")
        file_magic = self.file.read(4)
        assert file_magic == self.file_magic, f"{self.file} is not a valid .bsp!"
        self.bsp_version = int.from_bytes(self.file.read(4), "little")
        self.lump_count = int.from_bytes(self.file.read(4), "little")
        self.file.seek(0, 2)  # move cursor to end of file
        self.bsp_file_size = self.file.tell()
        # load headers & lumps
        self.headers = list()  # order matters
        self.loading_errors: Dict[str, Exception] = dict()
        cursor = 12 + (self.lump_count * 8)  # end of headers; for "reading" lumps
        for i in range(self.lump_count):
            # read header
            self.file.seek(12 + 8 * i)
            lump_header = self.branch.LumpHeader.from_stream(self.file)
            if lump_header.id != 0x07:  # UNKNOWN_7 is padded to every 2nd byte?
                cursor = cursor + (4 - cursor & 3)
            lump_header.offset = cursor
            cursor += lump_header.length
            LUMP = self.branch.LUMP(lump_header.id)
            lump_header.name = LUMP.name
            self.headers.append(lump_header)
            try:
                if LUMP.name in self.branch.LUMP_CLASSES:
                    LumpClass = self.branch.LUMP_CLASSES[LUMP.name]
                    BspLump = lumps.create_BspLump(self.file, lump_header, LumpClass)
                elif LUMP.name in self.branch.SPECIAL_LUMP_CLASSES:
                    SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP.name]
                    self.file.seek(lump_header.offset)
                    lump_data = self.file.read(lump_header.length)
                    BspLump = SpecialLumpClass(lump_data)
                elif LUMP.name in self.branch.BASIC_LUMP_CLASSES:
                    LumpClass = self.branch.BASIC_LUMP_CLASSES[LUMP.name]
                    BspLump = lumps.create_BasicBspLump(self.file, lump_header, LumpClass)
                else:
                    BspLump = lumps.create_RawBspLump(self.file, lump_header)
            except Exception as exc:
                self.loading_errors[LUMP.name] = exc
                BspLump = lumps.create_RawBspLump(self.file, lump_header)
            setattr(self, LUMP.name, BspLump)

    def print_headers(self):
        print("LUMP.name", " " * 14, "OFFSET", "LENGTH")
        print("-" * 38)
        for header in self.headers:
            print(f"{header.name:<24} {header.offset:06X} {header.length:06X}")


# TODO: XenonBsp (Xbox360, likely in big-endian .ff?)
