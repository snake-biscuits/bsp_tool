import io
import struct
from typing import Any, Generator, List, Union


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


def xxd(stream: io.BytesIO, limit, start=0, row=32, group=4) -> Generator[str, None, None]:
    """inline hex view"""
    # NOTE: start is just to make offset nice and readable; NO SEEKING!
    # TODO: if limit is None: read until end of stream
    # TODO: test we catch tails if they don't divide evenly
    # -- pad tail hex_ with spaces to align txt_
    for offset in range(0, limit, row):
        bytes_ = stream.read(row)
        hex_ = bytes_.hex().upper()
        if group is not None:
            hex_ = " ".join(hex_[i:i + group * 2] for i in range(0, row * 2, group * 2))
        txt_ = "".join(chr(c) if chr(c).isprintable() else "." for c in bytes_)
        yield f"{start + offset:04X} | {hex_}  {txt_}"
