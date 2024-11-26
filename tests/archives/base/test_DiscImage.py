from bsp_tool.archives.base import DiscImage
from bsp_tool.archives.base import TrackMode


def test_basic():
    in_bytes = b"\xFF" * 2048
    di = DiscImage.from_bytes(in_bytes)
    # test dummy track assembly
    assert len(di.tracks) == 1
    track = [*di.tracks.keys()][0]
    assert track.mode == TrackMode.BINARY_2
    assert track.sector_size == 2048
    assert track.start_lba == 0
    assert track.length == 1
    assert di._cursor == (track, 0)
    # test read behaviour
    out_bytes = di.sector_read()
    assert in_bytes == out_bytes
    assert di._cursor == (track, 1)
    assert di.sector_tell() == 1
