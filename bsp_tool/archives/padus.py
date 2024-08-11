"""Padus, Inc. DiscJuggler .cdi format"""
# https://en.wikipedia.org/wiki/DiscJuggler
# https://github.com/jozip/cdirip
from __future__ import annotations
import enum
import io
from typing import List

from . import base
from ..utils import binary


version_code = {
    0x80000004: "2.0",
    0x80000005: "3.0",
    0x80000006: "3.5"}


sector_size = {
    0: 2048,
    1: 2336,
    2: 2352}


class TrackMode(enum.Enum):
    Audio = 0
    # binaries
    Mode1 = 1
    Mode2 = 2


sector_header_length = {
    (TrackMode.Mode2, 2352): 24,
    (TrackMode.Mode2, 2336): 8}


extension = {
    TrackMode.Audio: "raw",  # TODO: "wav"
    TrackMode.Mode1: "bin",
    TrackMode.Mode2: "iso"}


class Track:
    filename: str
    mode: TrackMode
    pregap_length: int
    length: int
    start_lba: int  # logical block address
    total_length: int
    sector_size: int
    # NOTE: offset is calculated in CDI._from_stream
    offset: int

    def __init__(self, filename: str = "untitled", mode: int = 0):
        self.filename = filename
        self.mode = TrackMode(mode)

    def __repr__(self) -> str:
        mode = TrackMode(self.mode)
        return f'<Track "{self.filename}" ({mode.name}) @ 0x{id(self):016X}>'

    @classmethod
    def from_stream(cls, stream, cdi_version: int) -> Track:
        out = cls()

        def skip(length: int):
            stream.seek(length, 1)

        # cdi.c:ask_type
        tmp = binary.read_struct(stream, "I")
        if tmp != 0:
            skip(8)  # DiscJuggler 3.00.780+
        assert stream.read(20) == b"\x00\x00\x01\x00\x00\x00\xFF\xFF\xFF\xFF" * 2, "no track start marker"
        skip(4)
        filename_length = binary.read_struct(stream, "B")
        out.filename = stream.read(filename_length).decode()
        skip(19)  # 11 + 4 + 4
        tmp = binary.read_struct(stream, "I")
        if tmp == 0x80000000:
            skip(8)  # DiscJuggler 4
        skip(2)
        out.pregap_length, out.length = binary.read_struct(stream, "2i")
        # NOTE: pregap_length is almost always 150
        # NOTE: if length is 0, the real data is in the pregap
        skip(6)
        out.mode = TrackMode(binary.read_struct(stream, "I"))
        skip(12)
        out.start_lba, out.total_length = binary.read_struct(stream, "Ii")
        # NOTE: total_length should be pregap_length + length
        skip(16)
        sector_size_enum = binary.read_struct(stream, "I")
        out.sector_size = sector_size[sector_size_enum]
        skip(29)
        if version_code[cdi_version] != "2.0":
            skip(5)
            tmp = binary.read_struct(stream, "I")
            if tmp == 0xFFFFFFFF:
                skip(78)  # DiscJuggler 3.00.780+
        return out


class Cdi(base.Archive):
    file: io.BytesIO
    filename: str
    version: int
    sessions: List[List[Track]]

    def __init__(self, filename: str):
        self.filename = filename
        self._from_stream(open(filename, "rb"))

    def __repr__(self) -> str:
        version = version_code[self.version]
        return f"<CDI v{version} '{self.filename}' @ 0x{id(self):016X}>"

    def namelist(self) -> List[str]:
        return [
            f"{i}.{j:02d}.{extension[track.mode]}"
            for i, session in enumerate(self.sessions)
            for j, track in enumerate(session)]

    def read(self, filepath: str) -> bytes:
        # TODO: there's some big spans of empty sectors we seem to miss
        # -- 7Zip extracts these, the code doesn't
        # -- haven't tested CDIrip
        # -- 7Zip .iso can be read by 7Zip, ours is invalid
        session_index, track_index, ext = filepath.split(".")
        session_index = int(session_index)
        track_index = int(track_index)
        # collect our target track
        track = self.sessions[session_index][track_index]
        self.file.seek(track.offset)  # calculated in CDI._from_stream
        self.file.seek(track.pregap_length * track.sector_size, 1)  # skip pregap
        # conversion checks
        if track.mode == TrackMode.Audio and ext != "raw":
            raise NotImplementedError()
        # collect & process sectors
        header_length = sector_header_length.get((track.mode, track.sector_size), 0)
        sectors = list()
        for i in range(track.length):
            raw_sector = self.file.read(track.sector_size)
            raw_sector = raw_sector[header_length:]
            raw_sector = raw_sector[:2048]
            sectors.append(raw_sector)
        return b"".join(sectors)

    def _from_stream(self, stream):
        self.file = stream
        # version identifier
        stream.seek(0, 2)  # "header" is on the tail
        length = stream.tell()
        assert length > 8
        stream.seek(-8, 2)
        version, header_offset = binary.read_struct(stream, "2I")
        assert version in version_code, "unknown .cdi format version"
        assert header_offset != 0, "invalid .cdi file"
        self.version = version
        if version_code[self.version] != "3.5":
            stream.seek(header_offset)
        else:  # v3.0 header_offset is negative
            stream.seek(length - header_offset)
        # the "header"
        needle = 0  # track offsets
        self.sessions = list()
        num_sessions = binary.read_struct(stream, "H")
        for session in range(num_sessions):
            self.sessions.append(list())
            num_tracks = binary.read_struct(stream, "H")
            # NOTE: some sessions have 0 tracks
            for track in range(num_tracks):
                track = Track.from_stream(stream, self.version)
                track.offset = needle
                needle += track.total_length * track.sector_size
                self.sessions[session].append(track)
            # cdi.c:CDI_skip_next_session
            stream.seek(12, 1)  # 4 + 8
            if version_code[self.version] != "2.0":
                stream.seek(1, 1)
