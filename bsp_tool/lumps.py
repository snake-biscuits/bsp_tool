"""classes for dynamically parsing lumps"""
from __future__ import annotations

import io
import struct
from typing import Any, Dict, Union


LumpHeader = Any
# all: offset & length
# ValveBsp / RespawnBsp: fourCC & version
Stream = Union[io.BufferedReader, io.BytesIO]


def _remap_index(index: int, length: int) -> int:
    """simplify to positive integer"""
    if index < 0:
        index = length + index
    if index >= length or index < 0:
        raise IndexError("list index out of range")
    return index


def _remap_slice_to_range(_slice: slice, length: int) -> slice:
    """simplify to positive start & stop within range(0, length)"""
    start, stop, step = _slice.start, _slice.stop, _slice.step
    start = 0 if (start is None) else max(length + start, 0) if (start < 0) else length if (start > length) else start
    stop = length if (stop is None or stop > length) else max(length + stop, 0) if (stop < 0) else stop
    step = 1 if (step is None) else step
    return range(start, stop, step)


class RawBspLump:
    """Maps an open binary stream to a bytearry-like object"""
    # TODO: be more bytearray-like
    stream: Stream
    offset: int  # position in stream where lump begins
    _changes: Dict[int, bytes]
    # ^ {index: new_byte}
    _length: int  # number of indexable entries

    def __init__(self):
        self._changes = dict()
        self._length = 0
        self.offset = 0
        self.stream = io.BytesIO(b"")

    def __delitem__(self, index: Union[int, slice]):
        if isinstance(index, int):
            index = _remap_index(index, self._length)
            self[index:] = self[index + 1:]
            # NOTE: slice assignment will change length
        elif isinstance(index, slice):
            for i in _remap_slice_to_range(index, self._length):
                del self[i]
        else:
            raise TypeError(f"list indices must be integers or slices, not {type(index)}")

    def __iter__(self):
        return iter([self.get(i, mutable=False) for i in range(self._length)])

    def __getitem__(self, index: Union[int, slice]) -> Union[int, bytearray]:
        """Reads bytes from the start of the lump"""
        if isinstance(index, int):
            return self.get(_remap_index(index, self._length))
        elif isinstance(index, slice):
            # TODO: BspLump[::] returns a copy (doesn't update _changes)
            return bytearray([self[i] for i in _remap_slice_to_range(index, self._length)])
        else:
            raise TypeError(f"list indices must be integers or slices, not {type(index)}")

    def __len__(self):
        return self._length

    def __repr__(self):
        return f"<{self.__class__.__name__}; {len(self)} bytes at 0x{id(self):016X}>"

    def __setitem__(self, index: int | slice, value: Any):
        """remapping slices is allowed, but only slices"""
        if isinstance(index, int):
            index = _remap_index(index, self._length)
            self._changes[index] = value
        elif isinstance(index, slice):
            slice_indices = list(_remap_slice_to_range(index, self._length))
            length_change = len(list(value)) - len(slice_indices)
            slice_changes = dict(zip(slice_indices, value))
            if length_change == 0:  # replace a slice with an equal length slice
                self._changes.update(slice_changes)
            else:  # update a slice in the place of another slice (delete / insert)
                self._length += length_change
                head, tail = min(slice_indices), max(slice_indices)
                # NOTE: slice may have negative step
                # TODO: TEST different slice step
                new_head = {i: v for i, v in self._changes.items() if i < head}
                new_tail = {i + length_change: v for i, v in self._changes.items() if i > tail}
                self._changes = {**new_head, **slice_changes, **new_tail}
        else:
            raise TypeError(f"list indices must be integers or slices, not {type(index)}")

    def append(self, entry):
        self._length += 1
        self[-1] = entry

    def extend(self, entries: bytes):
        for entry in entries:
            self.append(entry)

    def get(self, index: int, mutable: bool = True) -> int:
        # NOTE: don't use get! we can't be sure the given index in bounds
        if index in self._changes:
            return self._changes[index]
        else:
            value = self.get_unchanged(index)
            if mutable:
                self._changes[index] = value
            return value

    def get_unchanged(self, index: int) -> int:
        """no index remapping, be sure to respect stream data bounds!"""
        self.stream.seek(self.offset + index)
        return self.stream.read(1)[0]

    def index(self, *args, **kwargs) -> Any:
        return self[::].index(*args, **kwargs)

    def insert(self, index: int, entry: Any):
        self._length += 1
        self[index + 1:] = self[index:]
        self[index] = entry

    def pop(self, index: Union[int, slice]) -> Union[int, bytes]:
        out = self[index]
        del self[index]
        return out

    @classmethod
    def from_header(cls, stream: Stream, lump_header: LumpHeader) -> RawBspLump:
        out = cls()
        out._length = lump_header.length
        out.offset = lump_header.offset
        out.stream = stream
        return out

    @classmethod
    def from_stream(cls, stream: Stream, offset: int = 0, length: int = -1) -> RawBspLump:
        if length == -1:
            if hasattr(stream, "size"):
                length = stream.size
            else:
                length = stream.seek(0, 2)
            length -= offset
        out = cls()
        out._length = length
        out.offset = offset
        out.stream = stream
        return out


class BasicBspLump(RawBspLump):
    """Dynamically reads BasicLumpClasses from a binary stream"""
    stream: Stream
    offset: int  # position in stream where lump begins
    LumpClass: object
    _changes: Dict[int, object]
    # ^ {index: LumpClass(new_entry)}
    # NOTE: there are no checks to ensure changes are the correct type or size
    _entry_size: int  # sizeof(LumpClass)
    _length: int  # number of indexable entries

    def __init__(self):
        self._changes = dict()
        self._entry_size = 0
        self._length = 0
        self.offset = 0
        self.stream = io.BytesIO(b"")

    def __getitem__(self, index: Union[int, slice]):
        """Reads bytes from self.stream & returns LumpClass(es)"""
        if isinstance(index, int):
            return self.get(_remap_index(index, self._length))
        elif isinstance(index, slice):
            return [self[i] for i in _remap_slice_to_range(index, self._length)]
        else:
            raise TypeError(f"list indices must be integers or slices, not {type(index)}")

    def __repr__(self):
        return f"<{self.__class__.__name__} ({len(self)} {self.LumpClass.__name__}) at 0x{id(self):016X}>"

    def get_unchanged(self, index: int) -> int:
        """no index remapping, be sure to respect stream data bounds!"""
        # NOTE: no .from_stream(); BasicLumpClasses only specify _format
        self.stream.seek(self.offset + (index * self._entry_size))
        raw_entry = struct.unpack(self.LumpClass._format, self.stream.read(self._entry_size))
        return self.LumpClass(raw_entry[0])

    @classmethod
    def from_count(cls, stream: Stream, count: int, LumpClass: object):
        """starts from cursor; stream.seek() before creating"""
        out = cls()
        out.LumpClass = LumpClass
        out._entry_size = struct.calcsize(LumpClass._format)
        out._length = count
        out.offset = stream.tell()
        out.stream = stream
        # verify size
        size = out._entry_size * out._length
        real_size = len(stream.read(size))  # seek to end of lump
        if size != real_size:
            possible_sizeof = (out.stream.tell() - out.offset) / count
            raise RuntimeError(f"Early end of lump! possible_sizeof={possible_sizeof} (is {out._entry_size})")
        return out

    @classmethod
    def from_header(cls, stream: Stream, lump_header: LumpHeader, LumpClass: object) -> BasicBspLump:
        out = cls()
        out.LumpClass = LumpClass
        out._entry_size = struct.calcsize(LumpClass._format)
        out._length = lump_header.length // out._entry_size
        out.offset = lump_header.offset
        out.stream = stream
        if lump_header.length % out._entry_size != 0:
            raise RuntimeError(f"LumpClass does not divide lump evenly! ({lump_header.length} / {out._entry_size})")
        return out

    @classmethod
    def from_stream(cls, stream: Stream, LumpClass: object, offset: int = 0, length: int = -1) -> BasicBspLump:
        if length == -1:
            if hasattr(stream, "size"):
                length = stream.size
            else:
                length = stream.seek(0, 2)
            length -= offset
        out = cls()
        out.LumpClass = LumpClass
        out._entry_size = struct.calcsize(LumpClass._format)
        out._length = length // out._entry_size
        out.offset = offset
        out.stream = stream
        if length % out._entry_size != 0:
            raise RuntimeError(f"LumpClass does not divide lump evenly! ({length} / {out._entry_size})")
        return out


class BspLump(BasicBspLump):
    """Dynamically reads LumpClasses from a binary stream"""
    stream: Stream
    offset: int  # position in stream where lump begins
    LumpClass: object
    _changes: Dict[int, object]
    # ^ {index: LumpClass(new_entry)}
    # NOTE: there are no checks to ensure changes are the correct type or size
    _entry_size: int  # sizeof(LumpClass)
    _length: int  # number of indexable entries

    def get_unchanged(self, index: int) -> int:
        """no index remapping, be sure to respect stream data bounds!"""
        self.stream.seek(self.offset + (index * self._entry_size))
        # BROKEN: quake.Edge does not support .from_stream()
        # return self.LumpClass.from_stream(self.stream)
        # HACK: required for quake.Edge
        _tuple = struct.unpack(self.LumpClass._format, self.stream.read(self._entry_size))
        return self.LumpClass.from_tuple(_tuple)

    def search(self, **kwargs):
        """Returns all lump entries which have the queried values [e.g. find(x=0)]"""
        return [x for x in self[::] if all([getattr(x, a) == v for a, v in kwargs.items()])]
