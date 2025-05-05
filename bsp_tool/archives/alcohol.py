# https://en.wikipedia.org/wiki/Alcohol_120%25
# https://github.com/jkbenaim/mds2iso/blob/master/mds2iso.c
from __future__ import annotations
import enum
import io
from typing import List

# from .. import core
from . import base


class MediaType(enum.Enum):
    CD_ROM = 0
    CD_R = 1
    CD_RW = 2
    DVD_ROM = 16
    DVD_R = 18


# class MdsHeader(core.Struct):
#     __slots__ = [
#         "magic", "version", "media_type", "num_sessions",
#         "unknown_1", "bca_length", "unknown_2", "bca_offset",
#         "unknown_3", "disc_struct_offset", "unknown_4",
#         "sessions_offset", "dpm_offset"]
#     _format = "16s2B2HIH15I"  # 88 bytes
#     _arrays = {
#         "version": ["major", "minor"],
#         "unknown_2": 2, "unknown_3": 6, "unknown_4": 3}
#     _classes = {
#         "media_type": MediaType}


# class MdsSessionHeader(core.Struct):
#     __slots__ = [
#         "first_sector", "last_sector", "num_sessions", "num_tracks",
#         "num_tracks_2", "first_track", "last_track", "unknown",
#         "tracks_offset"]
#     _format = "2IH2B2H2I"


class TrackMode(enum.Enum):
    NONE = 0
    DVD = 2
    AUDIO = 0xA9
    MODE1 = 0xAA
    MODE2 = 0xAB
    MODE2_FORM1 = 0xAC
    MODE2_FORM2 = 0xAD
    MODE2_SUB = 0xEC  # Mode2 w/ subchannels


# class MdsTrack(core.Struct):
#     index: int  # track_number
#     __slots__ = [
#         "mode", "num_subchannels", "adr", "index", "point_number",
#         "minutes", "seconds", "frames", "zero", "pmin", "psec", "pframe",
#         "index_block_offset", "sector_size", "unknown_1", "first_sector",
#         "sector_offset", "num_filenames", "filenames_offset", "unknown_2"]
#     _format = "12BI10HIQ2I6I"
#     _arrays = {
#         "unknown_1": 9, "unknown_2": 6}
#     _classes = {
#         "mode": TrackMode}


class Mds(base.DiscImage):
    """Media Descriptor Sidecar"""
    ext = "*.mds"
    # NOTE: needs linked .mdf (Media Descriptor File) data files
    _file: io.BytesIO  # DEBUG
    # header: MdsHeader
    # session_header: MdsSessionHeader  # 1x, not per-session?
    # tracks: List[MdsTrack]
    filenames: List[str]

    def __init__(self):
        self.tracks = list()
        self.filenames = list()

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Mds:
        raise NotImplementedError()
        disc = cls()
        # disc.header = MdsHeader.from_stream(stream)
        # assert disc.header.magic == b"MEDIA DESCRIPTOR"
        # assert disc.header.version.major == 1
        # assert disc.header.version.minor == 3
        # # sessions
        # stream.seek(disc.header.sessions_offset, 1)
        # disc.session_header = MdsSessionHeader.from_stream(stream)  # incorrect?
        # # stream.seek(disc.session_header.tracks_offset, 1)
        # # disc.tracks = [
        # #     MdsTrack.from_stream(stream)
        # #     for i in range(disc.session_header.num_tracks)]
        # # TODO: filenames
        disc._file = stream  # DEBUG
        return disc
