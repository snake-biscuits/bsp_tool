__all__ = ["apex_legends", "titanfall2", "read_lump"]
from ..base import LumpHeader
from . import apex_legends, titanfall2


def read_lump(file, header_address: int) -> (LumpHeader, bytes):  # .bsp internal lumps only
    # header
    file.seek(header_address)
    offset = int.from_bytes(file.read(4), "little")
    length = int.from_bytes(file.read(4), "little")
    version = int.from_bytes(file.read(4), "little")
    fourCC = int.from_bytes(file.read(4), "little")
    header = LumpHeader(offset, length, version, fourCC)
    if length == 0:
        return
    # lump data
    file.seek(offset)
    data = file.read(length)
    return header, data
