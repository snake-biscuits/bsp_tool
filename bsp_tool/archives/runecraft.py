# https://dcemulation.org/phpBB/viewtopic.php?t=100512
# http://forum.xentax.com/viewtopic.php?f=10&t=4688&view=previous
# -- Echelon & Isozone variants exist w/ other .pak files
# -- partial winrar support?
from __future__ import annotations
import io
from typing import List

from .. import core
from ..utils import binary
from . import base


# NOTE: very confident there are no gaps between data
# -- spotted multiple `.tga` tails preceeding `.pvr` headers


# TODO: calculate values matching .pvr offsets
class Entry(core.Struct):
    # sum of unknown[2] is less than filesize
    # -- 79 bytes short of the total filesize
    # -- the last 79 bytes of FILES.PAK are NULL
    # look like lengths, but idk
    __slots__ = ["unknown"]
    _format = "3I"
    _arrays = {"unknown": 3}


class Pak(base.Archive):
    ext = "*.pak"
    _file: io.BytesIO
    entries: List[Entry]
    # entries: Dict[str, Entry]

    def __init__(self):
        super().__init__()
        self.entries = list()

    def __repr__(self) -> str:
        descriptor = f"{len(self.entries)} files"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    # TODO: def read(self, filepath: str) -> bytes:
    # TODO: def namelist(self) -> List[str]:

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Pak:
        out = cls()
        out._file = stream
        assert stream.read(4) == b"NPCK", "not a .pak file"
        # guessing
        num_entries = binary.read_struct(stream, "I")
        out.entries = [
            Entry.from_stream(stream)
            for i in range(num_entries)]
        # vaild file data starts right after this
        # unsure of length tho
        # 6942 bytes of configs (likely multiple files)
        # a few bytes of data (likely ints)
        # sega copyright message (small text file?)
        # not seeing any sort of filename table
        # however plaintext files reference filenames
        return out
