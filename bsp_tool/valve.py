from collections import namedtuple  # for type hints
import enum  # for type hints
from types import ModuleType
from typing import Dict, List

from . import base


class ValveBsp(base.Bsp):
    # https://developer.valvesoftware.com/wiki/Source_BSP_File_Format
    FILE_MAGIC = b"VBSP"
    HEADERS: Dict[str, namedtuple]
    # ^ {"LUMP_NAME": LumpHeader}
    VERSION: int = 0  # .bsp format version
    associated_files: List[str]  # files in the folder of loaded file with similar names
    branch: ModuleType
    filesize: int = 0  # size of .bsp in bytes
    filename: str
    folder: str
    loading_errors: Dict[str, Exception]
    # ^ {"LUMP_NAME": Exception encountered}

    def __init__(self, branch: ModuleType, filename: str = "untitled.bsp", autoload: bool = True):
        super(ValveBsp, self).__init__(branch, filename, autoload)

    def _read_header(self, LUMP: enum.Enum) -> namedtuple:  # LumpHeader
        """Get LUMP from self.branch.LUMP; e.g. self.branch.LUMP.ENTITIES"""
        # NOTE: each branch of VBSP has unique headers; so a read_lump_header function is called from branch
        return self.branch.read_lump_header(self.file, LUMP)
