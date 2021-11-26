import collections
import enum
import os
import struct
from types import ModuleType
from typing import Dict
import warnings

from . import base
from . import lumps


LumpHeader = collections.namedtuple("LumpHeader", ["length", "offset"])


class InfinityWardBsp(base.Bsp):
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_1:_d3dbsp
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_2:_d3dbsp
    file_magic = b"IBSP"
    # NOTE: Call of Duty 1 .bsp are stored in .pk3 (.zip) archives
    # NOTE: Call of Duty 2 .d3dbsp are stored in .iwd (.zip) archives

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
        self.file.seek(0, 2)  # move cursor to end of file
        self.bsp_file_size = self.file.tell()

        self.headers = dict()
        self.loading_errors: Dict[str, Exception] = dict()
        for LUMP_enum in self.branch.LUMP:
            # CHECK: is lump external? (are associated_files overriding)
            lump_header = self._read_header(LUMP_enum)
            LUMP_NAME = LUMP_enum.name
            self.headers[LUMP_NAME] = lump_header
            if lump_header.length == 0:
                continue
            try:
                if LUMP_NAME in self.branch.LUMP_CLASSES:
                    LumpClass = self.branch.LUMP_CLASSES[LUMP_NAME]
                    BspLump = lumps.create_BspLump(self.file, lump_header, LumpClass)
                elif LUMP_NAME in self.branch.SPECIAL_LUMP_CLASSES:
                    SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP_NAME]
                    self.file.seek(lump_header.offset)
                    lump_data = self.file.read(lump_header.length)
                    BspLump = SpecialLumpClass(lump_data)
                elif LUMP_NAME in self.branch.BASIC_LUMP_CLASSES:
                    LumpClass = self.branch.BASIC_LUMP_CLASSES[LUMP_NAME]
                    BspLump = lumps.create_BasicBspLump(self.file, lump_header, LumpClass)
                else:
                    BspLump = lumps.create_RawBspLump(self.file, lump_header)
            except Exception as exc:
                self.loading_errors[LUMP_NAME] = exc
                BspLump = lumps.create_RawBspLump(self.file, lump_header)
            setattr(self, LUMP_NAME, BspLump)

    def _read_header(self, LUMP: enum.Enum) -> LumpHeader:
        self.file.seek(self.branch.lump_header_address[LUMP])
        length, offset = struct.unpack("2i", self.file.read(8))
        header = LumpHeader(length, offset)
        return header


CoD4LumpHeader = collections.namedtuple("LumpHeader", ["id", "length", "offset"])
# NOTE: offset is calculated from the sum of preceding lump's lengths (+ padding)


class D3DBsp(base.Bsp):
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_4:_d3dbsp
    # https://github.com/SE2Dev/D3DBSP_Converter/blob/master/D3DBSP_Lib/D3DBSP.cpp
    file_magic = b"IBSP"
    lump_count: int
    # NOTE: Call of Duty 2 [InfinityWardBsp] uses the .d3dbsp extension
    # NOTE: Call of Duty 4 .d3dbsp are stored in .ff archives (see extensions.archive.FastFile)
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

        self.headers = list()  # order matters
        self.loading_errors: Dict[str, Exception] = dict()
        cursor, offset = 0, 0
        for i in range(self.lump_count):
            # read header
            self.file.seek(12 + 8 * i)
            _id, length = struct.unpack("2i", self.file.read(8))
            assert length != 0, "cursed, idk how you got this error"
            offset = cursor + (4 - cursor % 4) if cursor % 4 != 0 else cursor
            cursor += length
            lump_header = CoD4LumpHeader(_id, length, offset)
            # NOTE: offset finding could be very incorrect
            self.headers.append(lump_header)
            # identify lump
            LUMP_enum = self.branch.LUMP(lump_header.id)
            LUMP_NAME = LUMP_enum.name
            # NOTE: very new to this format, may be collecting the wrong data
            try:
                if LUMP_NAME in self.branch.LUMP_CLASSES:
                    LumpClass = self.branch.LUMP_CLASSES[LUMP_NAME]
                    BspLump = lumps.create_BspLump(self.file, lump_header, LumpClass)
                elif LUMP_NAME in self.branch.SPECIAL_LUMP_CLASSES:
                    SpecialLumpClass = self.branch.SPECIAL_LUMP_CLASSES[LUMP_NAME]
                    self.file.seek(lump_header.offset)
                    lump_data = self.file.read(lump_header.length)
                    BspLump = SpecialLumpClass(lump_data)
                elif LUMP_NAME in self.branch.BASIC_LUMP_CLASSES:
                    LumpClass = self.branch.BASIC_LUMP_CLASSES[LUMP_NAME]
                    BspLump = lumps.create_BasicBspLump(self.file, lump_header, LumpClass)
                else:
                    BspLump = lumps.create_RawBspLump(self.file, lump_header)
            except Exception as exc:
                self.loading_errors[LUMP_NAME] = exc
                BspLump = lumps.create_RawBspLump(self.file, lump_header)
            setattr(self, LUMP_NAME, BspLump)

    def _read_header(self, LUMP: enum.Enum) -> CoD4LumpHeader:
        raise NotImplementedError("CoD4LumpHeaders aren't ordered")


# NOTE: XenonBsp also exists (named after the XBox360 processor)
# -- however we aren't supporting console *.bsp
