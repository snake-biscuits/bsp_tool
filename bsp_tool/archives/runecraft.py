# https://dcemulation.org/phpBB/viewtopic.php?t=100512
# http://forum.xentax.com/viewtopic.php?f=10&t=4688&view=previous
# -- Echelon & Isozone variants exist w/ other .pak files
# -- partial winrar support?
from __future__ import annotations
import io
from typing import Dict, List

from .. import core
from ..utils import binary
from . import base


# NOTE: very confident there are no gaps between data
# -- spotted multiple `.tga` tails preceeding `.pvr` headers


# TODO: calculate values matching .pvr offsets
class Entry(core.Struct):
    unknown: int  # name hash? unique for every entry
    offset: int  # -8
    length: int
    __slots__ = ["unknown", "offset", "length"]
    _format = "3I"


class Pak(base.Archive):
    ext = "*.pak"
    _file: io.BytesIO
    entries: Dict[str, Entry]
    # NOTE: names are currently placeholders

    def __init__(self):
        super().__init__()
        self.entries = list()

    def __repr__(self) -> str:
        descriptor = f"{len(self.entries)} files"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def namelist(self) -> List[str]:
        return [
            f"{entry.unknown:08X}"
            for entry in sorted(
                self.entries.values(),
                key=lambda e: (e.offset, e.length))]

    def read(self, filepath: str) -> bytes:
        assert filepath in self.entries
        entry = self.entries[filepath]
        self._file.seek(entry.offset + 8)
        return self._file.read(entry.length)

    def sizeof(self, filepath: str) -> int:
        return self.entries[filepath].length

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Pak:
        out = cls()
        out._file = stream
        assert stream.read(4) == b"NPCK", "not a .pak file"
        # guessing
        num_entries = binary.read_struct(stream, "I")
        out.entries = {
            f"{entry.unknown:08X}": entry
            for entry in [
                Entry.from_stream(stream)
                for i in range(num_entries)]}
        # NOTE: entries are listed in ascending `unknown` order
        # -- not in offset order
        # NOTE: some entries are 0 bytes in length
        # NOTE: 80 blank bytes at end of file unaccounted for?
        return out
