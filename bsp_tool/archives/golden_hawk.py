# https://en.wikipedia.org/wiki/Cue_sheet_(computing)
# https://wiki.hydrogenaud.io/index.php?title=Cue_sheet
from __future__ import annotations
import io
from typing import List

from . import base


class Cue(base.DiscImage):
    """plaintext CUE sheet"""
    ext = "*.cue"

    @classmethod
    def from_bytes(cls, raw_cue: bytes, encoding="latin_1", errors="strict") -> Cue:
        txt_file = io.StringIO(raw_cue.decode(encoding, errors))
        return cls.from_lines(txt_file.readlines())

    @classmethod
    def from_stream(cls, stream: io.BytesIO, encoding="latin_1", errors="strict") -> Cue:
        return cls.from_bytes(stream.read(), encoding, errors)

    @classmethod
    def from_lines(cls, lines: List[str]) -> Cue:
        raise NotImplementedError()
        out = cls()
        # TODO: line -> base.Track
        return out
