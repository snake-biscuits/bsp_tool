# https://en.wikipedia.org/wiki/Cue_sheet_(computing)
# https://wiki.hydrogenaud.io/index.php?title=Cue_sheet
from __future__ import annotations
import io
from typing import List

from . import base


class Cue(base.Archive):
    """plaintext CUE sheet"""
    ext = "*.cue"

    @classmethod
    def from_bytes(cls, raw_cue: bytes, encoding: str = "latin_1", errors: str = "strict") -> Cue:
        txt_file = io.StringIO(raw_cue.decode(encoding, errors))
        return cls.from_lines(txt_file.readlines())

    @classmethod
    def from_stream(cls, stream: io.BytesIO, encoding: str = "latin_1", errors: str = "strict") -> Cue:
        return cls.from_bytes(stream.read(), encoding, errors)

    @classmethod
    def from_lines(cls, lines: List[str]) -> Cue:
        out = cls()
        raise NotImplementedError()
        # match lines and append to internal objects
        ...
        return out
