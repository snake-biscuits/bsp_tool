"""Padus, Inc. DiscJuggler .cdi format"""
# https://en.wikipedia.org/wiki/DiscJuggler
# https://github.com/jozip/cdirip
from __future__ import annotations
import io
from typing import List

from .. import external
from ..utils import binary
from . import base


def parse_track(stream: io.BytesIO, cdi_version: int, name: str) -> (base.Track, int):
    def skip(length: int):
        stream.seek(length, 1)

    # cdi.c:ask_type
    tmp = binary.read_struct(stream, "I")
    if tmp != 0:
        skip(8)  # DiscJuggler 3.00.780+
    assert stream.read(20) == b"\x00\x00\x01\x00\x00\x00\xFF\xFF\xFF\xFF" * 2, "no track start marker"
    skip(4)
    filename_length = binary.read_struct(stream, "B")
    # filename = stream.read(filename_length).decode()  # .cdi filename
    skip(filename_length)
    skip(19)  # 11 + 4 + 4
    tmp = binary.read_struct(stream, "I")
    if tmp == 0x80000000:
        skip(8)  # DiscJuggler 4
    skip(2)
    pregap_length, length = binary.read_struct(stream, "2i")
    # NOTE: pregap_length is almost always 150
    if length == 0:  # data is in pregap
        length = pregap_length
        pregap_length = 0
    skip(6)
    mode = base.TrackMode(binary.read_struct(stream, "I"))
    skip(12)
    start_lba, total_length = binary.read_struct(stream, "Ii")
    assert total_length == pregap_length + length
    skip(16)
    sector_size_index = binary.read_struct(stream, "I")
    sector_size = [2048, 2336, 2352][sector_size_index]
    skip(29)
    if cdi_version != "2.0":
        skip(5)
        tmp = binary.read_struct(stream, "I")
        if tmp == 0xFFFFFFFF:
            skip(78)  # DiscJuggler 3.00.780+
    track = base.Track(mode, sector_size, start_lba, length, name)
    return track, pregap_length * sector_size


class Cdi(base.DiscImage):
    ext = "*.cdi"
    version: str  # e.g. "2.0"
    _file: io.BytesIO

    def __repr__(self) -> str:
        descriptor = f"v{self.version} {len(self)} sectors ({len(self.track)} tracks)"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def extra_patterns(self) -> List[str]:
        return list()

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Cdi:
        out = cls()
        out._file = stream
        # version identifier
        out._file.seek(0, 2)  # "header" is on the tail
        length = out._file.tell()
        assert length > 8
        out._file.seek(-8, 2)
        version, header_offset = binary.read_struct(stream, "2I")
        version_code = {
            0x80000004: "2.0",
            0x80000005: "3.0",
            0x80000006: "3.5"}
        assert version in version_code, "unknown .cdi format version"
        assert header_offset != 0, "invalid .cdi file"
        out.version = version_code[version]
        if out.version != "3.5":
            out._file.seek(header_offset)
        else:  # v3.0 header_offset is negative
            out._file.seek(length - header_offset)
        # the "header"
        needle = 0  # track offsets
        track_offsets = list()
        num_sessions = binary.read_struct(stream, "H")
        for session in range(num_sessions):
            num_tracks = binary.read_struct(stream, "H")
            # NOTE: some sessions have 0 tracks
            for track in range(num_tracks):
                name = f"Session {session + 1:02d} Track {track + 1:02d}"
                track, pregap_length = parse_track(stream, out.version, name)
                out.tracks.append(track)
                track_offsets.append(needle + pregap_length)
                needle += pregap_length + (track.length * track.sector_size)
            # cdi.c:CDI_skip_next_session
            out._file.seek(12, 1)  # 4 + 8
            if out.version != "2.0":
                out._file.seek(1, 1)
        # get track data
        for track, offset in zip(out.tracks, track_offsets):
            out._file.seek(offset)
            length = track.length * track.sector_size
            data = out._file.read(length)
            assert len(data) == length
            out.extras[track.name] = external.File.from_bytes(track.name, data)
        return out
