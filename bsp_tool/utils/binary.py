import io
import itertools
import struct
from typing import Any, Generator, List, Union


def find_all(data: bytes, substring: bytes):
    """extending bytes.find to be useful"""
    out = list()
    start = 0
    while data.find(substring, start) != -1:
        out.append(data.find(substring, start))
        start = out[-1] + len(substring)
    return out


def read_str(stream: io.BytesIO, encoding="utf-8", errors="strict") -> str:
    out = b""
    c = stream.read(1)
    while c != b"\x00":
        out += c
        c = stream.read(1)
    return out.decode(encoding, errors)


def read_struct(stream: io.BytesIO, format_: str) -> Union[Any, List[Any]]:
    out = struct.unpack(format_, stream.read(struct.calcsize(format_)))
    return out[0] if len(out) == 1 else out


def write_struct(stream: io.BytesIO, format_: str, *args):
    stream.write(struct.pack(format_, *args))


def xxd_stream(stream: io.BytesIO, start=0, limit=None, row=32, group=4) -> Generator[str, None, None]:
    """inline hex view"""
    # NOTE: start is just to make offset nice and readable; NO SEEKING!
    offset = 0
    padding = 0
    row_len = row
    for i in itertools.count():
        if limit is None:
            pass  # can't do math on a limit of None
        elif offset >= limit:
            return  # reached limit
        elif offset + row > limit:  # last row
            row_len = limit - offset
            padding = row - row_len
        # read data
        bytes_ = stream.read(row_len)
        if len(bytes_) == 0:
            return  # reached end of stream
        elif len(bytes_) < row:  # stream ends in this row
            padding = row - len(bytes_)
        # bytes as hex
        hex_ = bytes_.hex().upper()
        hex_ += " " * 2 * padding
        if group is not None:
            hex_ = " ".join(
                hex_[i:i + group * 2]
                for i in range(0, row * 2, group * 2))
        # bytes as text
        txt_ = "".join(
            chr(c) if chr(c).isprintable() else "."
            for c in bytes_)
        yield f"{start + offset:04X} | {hex_}  {txt_}"
        offset += row


def xxd_bytes(bytes_: bytes, start=0, limit=None, row=32, group=4) -> Generator[str, None, None]:
    # NOTE: just a wrapper that feeds bytes into xxd_stream
    if limit is None:
        limit = len(bytes_)
    for line in xxd_stream(
            io.BytesIO(bytes_[start:start + limit]),
            start, limit, row, group):
        yield line


def xxd(stream_or_bytes: Union[io.BytesIO, bytes], limit=None, start=0, row=32, group=4):
    if isinstance(stream_or_bytes, (bytes, bytearray)):
        xxd_func = xxd_bytes
    elif hasattr(stream_or_bytes, "read"):  # io.BytesIO or binary file
        xxd_func = xxd_stream
    else:  # hopefully RawBspLump
        xxd_func = xxd_bytes
        stream_or_bytes = stream_or_bytes[::]
    for line in xxd_func(stream_or_bytes, start, limit, row, group):
        print(line)
