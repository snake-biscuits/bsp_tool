from __future__ import annotations

from bsp_tool.archives.base import DiscImage, Track, TrackMode
from bsp_tool.external import File


class RawDiscImage(DiscImage):
    @classmethod
    def from_bytes(cls, raw_data: bytes) -> RawDiscImage:
        """for tests & .iso"""
        out = cls()
        tail_length = len(raw_data) % 2048
        if tail_length != 0:
            raw_data = b"".join([raw_data, b"\x00" * (2048 - tail_length)])
        length = len(raw_data) // 2048
        out.extras = {":memory:": File.from_bytes(":memory:", raw_data)}
        out.tracks = [Track(TrackMode.BINARY_2, 2048, 0, length, ":memory:")]
        return out


def test_basic():
    in_bytes = b"\x00" * 2048
    di = RawDiscImage.from_bytes(in_bytes)
    # test dummy track assembly
    assert isinstance(di.tracks, list)
    assert len(di.tracks) == 1
    track = di.tracks[0]
    assert track.mode == TrackMode.BINARY_2
    assert track.sector_size == 2048
    assert track.start_lba == 0
    assert track.length == 1
    assert di._cursor == (0, 0)
    # test read behaviour
    out_bytes = di.sector_read()
    assert in_bytes == out_bytes
    assert di._cursor == (0, 1)
    assert di.sector_tell() == 1


# TODO: set sub_lba is correct for tracks where start_lba != 0
