# https://en.wikipedia.org/wiki/Cue_sheet_(computing)
# https://wiki.hydrogenaud.io/index.php?title=Cue_sheet
from __future__ import annotations
import io
from typing import List

from . import base


track_mode = {
    "AUDIO": (base.TrackMode.AUDIO, 2352),
    "MODE1/2352": (base.TrackMode.BINARY_1, 2352),
    "MODE2/2336": (base.TrackMode.BINARY_1, 2336),
    "MODE2/2352": (base.TrackMode.BINARY_1, 2352)}


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
        # NOTE: only tested on "Radirgy (JP).cue"
        out = cls()
        state = dict()
        # NOTE: we assume all metadata we need is declated before "TRACK"
        keywords = ("FILE", "REM", "TRACK")
        lba = None
        for line in lines:
            keyword, space, context = line.strip().partition(" ")
            if keyword in keywords:
                state[keyword] = context
                if keyword == "REM" and context.endswith(" AREA"):
                    lba = {
                        "SINGLE-DENSITY AREA": 0,
                        "HIGH-DENSITY AREA": 45000}[context]
                elif keyword == "TRACK":
                    index, mode_str = context.split(" ")
                    mode, sector_size = track_mode[mode_str]
                    name = state["FILE"].rpartition(" ")[0].strip('"')
                    track = base.Track(mode, sector_size, lba, -1, name)
                    out.tracks.append(track)
        return out

    def _recalc_offsets(self):
        """run after getting sector sizes from external files"""
        prev_lba, prev_length = 0, 0
        for track_index, track in enumerate(self.tracks):
            lba = track.start_lba
            if not (track.start_lba == 45000 and prev_lba == 0):
                track.start_lba += prev_length
            self.tracks[track_index] = track
            prev_lba, prev_length = lba, track.length

    @classmethod
    def from_archive(cls, parent_archive: base.Archive, filename: str) -> Cue:
        out = super(Cue, cls).from_archive(parent_archive, filename)
        out._recalc_offsets()
        return out

    @classmethod
    def from_file(cls, filename: str) -> Cue:
        out = super(Cue, cls).from_file(filename)
        out._recalc_offsets()
        return out
