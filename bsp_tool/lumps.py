import collections
import io
import struct
from typing import Any, Union


def _remap_negative_index(index: int, length: int):
    "simplify to positive integer"
    if index < 0:
        index = length + index
    if index >= length or index < 0:
        raise IndexError("list index out of range")
    return index


def _remap_slice(_slice: slice, length: int):
    "simplify to positive start & stop within range(0, length)"
    start, stop, step = _slice.start, _slice.stop, _slice.step
    if start is None:
        start = 0
    elif start < 0:
        start = max(length + start, 0)
    if start > length:
        start = length
    if stop is None or stop > length:
        stop = length
    elif stop < 0:
        stop = max(length + stop, 0)
    return slice(start, stop, step)


def create_BspLump(file: io.BufferedReader, lump_header: collections.namedtuple, LumpClass: object = None):
    if LumpClass is None:
        return RawBspLump(file, lump_header)
    else:
        return BspLump(file, lump_header, LumpClass)


class RawBspLump:  # list-like
    """Maps an open binary file to a list-like object"""
    file: io.BufferedReader  # file opened in "rb" (read-bytes) mode
    offset: int  # position in file where lump begins
    _length: int  # number of indexable entries

    def __init__(self, file: io.BufferedReader, lump_header: collections.namedtuple):
        self.file = file
        self.offset = lump_header.offset
        self._length = lump_header.length
        # NOTE: ignores fourCC, no decompression is performed

    def __delitem__(self, index: Union[int, slice]):
        # TODO: save changes, but do not edit the file
        # writes must be performed by the external Bsp object
        # since writing deletes all following bytes, the entire binary must be loaded
        raise NotImplementedError()

    def __getitem__(self, index: Union[int, slice]) -> bytes:
        """Reads bytes from the start of the lump"""
        if isinstance(index, int):
            index = _remap_negative_index(index, self._length)
            self.file.seek(self.offset + index)
            return self.file.read(1)[0]  # return 1 0-255 integer, matching bytes behaviour
        elif isinstance(index, slice):
            _slice = _remap_slice(index, self._length)
            if _slice.step in (1, None):
                self.file.seek(self.offset + _slice.start)
                return self.file.read(_slice.stop - _slice.start)
            elif index.step == -1:
                self.file.seek(self.offset + _slice.stop)
                return reversed(self.file.read(_slice.start - _slice.stop))
            else:
                out = list()
                for i in range(_slice.start, _slice.stop, _slice.step):
                    out.append(self.__getitem__(i))
                return b"".join(out)
        else:
            raise TypeError(f"list indices must be integers or slices, not {type(index)}")

    def __setitem__(self, index: Union[int, slice], value: Any):
        # TODO: save changes, but do not edit the file
        # writes must be performed by the external Bsp object
        # since writing deletes all following bytes, the entire binary must be loaded
        raise NotImplementedError()

    def __iter__(self):
        return iter([self[i] for i in range(self._length)])

    def __len__(self):
        return self._length


class BspLump(RawBspLump):  # list-like
    """Dynamically reads LumpClasses from a binary file"""
    # NOTE: this class does not handle compressed lumps
    file: io.BufferedReader  # file opened in "rb" (read-bytes) mode
    offset: int  # position in file where lump begins
    _length: int  # number of indexable entries

    def __init__(self, file, lump_header: collections.namedtuple, LumpClass: object):
        self.file = file
        self.offset = lump_header.offset
        self._entry_size = struct.calcsize(LumpClass._format)
        if lump_header.length % self._entry_size != 0:
            raise RuntimeError(f"{LumpClass} does not divide lump evenly! ({lump_header.length} / {self._entry_size})")
        self._length = lump_header.length // self._entry_size
        self.LumpClass = LumpClass

    def __getitem__(self, index: Union[int, slice]):
        """Reads bytes from self.file & returns LumpClass(es)"""
        # read bytes -> struct.unpack tuples -> LumpClass
        # TODO: handle out of range & negative indices
        # NOTE: BspLump[index] = LumpClass(entry)
        if isinstance(index, int):
            index = _remap_negative_index(index, self._length)
            self.file.seek(self.offset + (index * self._entry_size))
            raw_entry = struct.unpack(self.LumpClass._format, self.file.read(self._entry_size))
            return self.LumpClass(raw_entry)
        elif isinstance(index, slice):
            _slice = _remap_slice(index, self._length)
            if _slice.step == 0:
                raise ValueError("slice step cannot be 0")
            elif _slice.step in (1, None):
                self.file.seek(self.offset + (_slice.start * self._entry_size))
                raw_bytes = self.file.read((_slice.stop - _slice.start) * self._entry_size)
                raw_entries = struct.iter_unpack(self.LumpClass._format, raw_bytes)
                return list(map(lambda t: self.LumpClass(t), raw_entries))
            else:
                out = list()
                for i in range(_slice.start, _slice.stop, _slice.step):
                    out.append(self.__getitem__(i))
                return out
        else:
            raise TypeError(f"list indices must be integers or slices, not {type(index)}")

    def find(self, **kwargs):
        """Returns all lump entries which have the queried values [e.g. find(x=0)]"""
        out = list()
        entire_lump = self[::]  # load all LumpClasses
        for entry in entire_lump:
            if all([getattr(entry, attr) == value for attr, value in kwargs.items()]):
                out.append(entry)
        return out

# TODO: ExternalBspLump; if lump_header has a filename, load that lump
