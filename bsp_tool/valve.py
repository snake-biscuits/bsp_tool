from collections import namedtuple  # for type hints
import enum  # for type hints
from types import ModuleType

from . import base


class ValveBsp(base.Bsp):
    # https://developer.valvesoftware.com/wiki/Source_BSP_File_Format
    FILE_MAGIC = b"VBSP"

    def __init__(self, branch: ModuleType, filename: str = "untitled.bsp", autoload: bool = True):
        super(ValveBsp, self).__init__(branch, filename, autoload)

    def _read_header(self, LUMP: enum.Enum) -> namedtuple:  # LumpHeader
        """Get LUMP from self.branch.LUMP; e.g. self.branch.LUMP.ENTITIES"""
        # NOTE: each branch of VBSP has unique headers; so a read_lump_header function is called from branch
        return self.branch.read_lump_header(self.file, LUMP)
