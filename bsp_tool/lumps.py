from __future__ import annotations

import collections
import io
import lzma
import struct
from typing import Any, Dict, Union


def _remap_negative_index(index: int, length: int) -> int:
    "simplify to positive integer"
    if index < 0:
        index = length + index
    if index >= length or index < 0:
        raise IndexError("list index out of range")
    return index


def _remap_slice(_slice: slice, length: int) -> slice:
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
    if step is None:
        step = 1
    return slice(start, stop, step)


def decompressed(file: io.BufferedReader, lump_header: collections.namedtuple) -> io.BytesIO:
    """Takes a lump and decompresses it if nessecary. Also corrects lump_header offset & length"""
    if lump_header.fourCC != 0:
        if not hasattr(lump_header, "filename"):  # internal compressed lump
            file.seek(lump_header.offset)
            data = file.read(lump_header.length)
        else:  # external compressed lump is unlikely, but possible
            data = open(lump_header.filename, "rb").read()
        # have to remap lzma header format slightly
        lzma_header = struct.unpack("4s2I5c", data[:17])
        # b"LZMA" = lzma_header[0]
        actual_size = lzma_header[1]
        assert actual_size == lump_header.fourCC
        # compressed_size = lzma_header[2]
        properties = b"".join(lzma_header[3:])
        _filter = lzma._decode_filter_properties(lzma.FILTER_LZMA1, properties)
        decompressor = lzma.LZMADecompressor(lzma.FORMAT_RAW, None, [_filter])
        decoded_data = decompressor.decompress(data[17:])
        decoded_data = decoded_data[:actual_size]  # trim any excess bytes
        assert len(decoded_data) == actual_size
        file = io.BytesIO(decoded_data)
        # HACK: trick BspLump into recognisind the decompressed lump sze
        LumpHeader = lump_header.__class__  # how2 edit a tuple
        lump_header_dict = dict(zip(LumpHeader._fields, lump_header))
        lump_header_dict["offset"] = 0
        lump_header_dict["length"] = lump_header.fourCC
        lump_header = LumpHeader(*[lump_header_dict[f] for f in LumpHeader._fields])
    return file, lump_header


def create_BspLump(file: io.BufferedReader, lump_header: collections.namedtuple, LumpClass: object = None) -> BspLump:
    if hasattr(lump_header, "fourCC"):
        file, lump_header = decompressed(file, lump_header)
    if not hasattr(lump_header, "filename"):
        if LumpClass is not None:
            return BspLump(file, lump_header, LumpClass)
        else:
            return RawBspLump(file, lump_header)
    else:
        if LumpClass is not None:
            return ExternalBspLump(lump_header, LumpClass)
        else:
            return ExternalRawBspLump(lump_header)


def create_RawBspLump(file: io.BufferedReader, lump_header: collections.namedtuple) -> RawBspLump:
    if not hasattr(lump_header, "filename"):
        return RawBspLump(file, lump_header)
    else:
        return ExternalRawBspLump(lump_header)


def create_BasicBspLump(file: io.BufferedReader, lump_header: collections.namedtuple, LumpClass: object) -> BasicBspLump:  # noqa E502
    if hasattr(lump_header, "fourCC"):
        file, lump_header = decompressed(file, lump_header)
    if not hasattr(lump_header, "filename"):
        return BasicBspLump(file, lump_header, LumpClass)
    else:
        return ExternalBasicBspLump(lump_header, LumpClass)


class RawBspLump:
    """Maps an open binary file to a list-like object"""
    file: io.BufferedReader  # file opened in "rb" (read-bytes) mode
    offset: int  # position in file where lump begins
    _changes: Dict[int, bytes]
    # ^ {index: new_byte}
    _length: int  # number of indexable entries

    def __init__(self, file: io.BufferedReader, lump_header: collections.namedtuple):
        self.file = file
        self.offset = lump_header.offset
        self._changes = dict()
        self._length = lump_header.length

    def __getitem__(self, index: Union[int, slice]) -> bytes:
        """Reads bytes from the start of the lump"""
        if isinstance(index, int):
            index = _remap_negative_index(index, self._length)
            if index in self._changes:
                return self._changes[index]
            else:
                self.file.seek(self.offset + index)
                return self.file.read(1)[0]  # return 1 0-255 integer, matching bytes behaviour
        elif isinstance(index, slice):
            _slice = _remap_slice(index, self._length)
            return bytes([self[i] for i in range(_slice.start, _slice.stop, _slice.step)])
        else:
            raise TypeError(f"list indices must be integers or slices, not {type(index)}")

    def __setitem__(self, index: Union[int, slice], value: Any):
        if isinstance(index, int):
            index = _remap_negative_index(index, self._length)
            self._changes[index] = value
        elif isinstance(index, slice):
            _slice = _remap_slice(index, self._length)
            for i, v in zip(range(_slice.start, _slice.stop, _slice.step), value):
                self[i] = v
        else:
            raise TypeError(f"list indices must be integers or slices, not {type(index)}")

    def __iter__(self):
        return iter([self[i] for i in range(self._length)])

    def __len__(self):
        return self._length


class BspLump(RawBspLump):
    """Dynamically reads LumpClasses from a binary file"""
    file: io.BufferedReader  # file opened in "rb" (read-bytes) mode
    offset: int  # position in file where lump begins
    _changes: Dict[int, Any]
    # ^ {index: LumpClass(new_entry)}
    # NOTE: there are no checks to ensure changes are the correct type or size
    _length: int  # number of indexable entries

    def __init__(self, file: io.BufferedReader, lump_header: collections.namedtuple, LumpClass: object):
        self.file = file
        self.offset = lump_header.offset
        self._changes = dict()  # changes must be applied externally
        self._entry_size = struct.calcsize(LumpClass._format)
        if lump_header.length % self._entry_size != 0:
            raise RuntimeError(f"LumpClass does not divide lump evenly! ({lump_header.length} / {self._entry_size})")
        self._length = lump_header.length // self._entry_size
        self.LumpClass = LumpClass

    def __delitem__(self, index: Union[int, slice]):
        if isinstance(index, int):
            index = _remap_negative_index(index, self._length)
            self[index:] = self[index + 1:]
            self._length -= 1
        elif isinstance(index, slice):
            _slice = _remap_slice(index, self._length)
            for i in range(_slice.start, _slice.stop, _slice.step):
                del self[i]
        else:
            raise TypeError(f"list indices must be integers or slices, not {type(index)}")

    def __getitem__(self, index: Union[int, slice]):
        """Reads bytes from self.file & returns LumpClass(es)"""
        # read bytes -> struct.unpack tuples -> LumpClass
        # NOTE: BspLump[index] = LumpClass(entry)
        if isinstance(index, int):
            index = _remap_negative_index(index, self._length)
            if index in self._changes:
                return self._changes[index]
            else:
                self.file.seek(self.offset + (index * self._entry_size))
                raw_entry = struct.unpack(self.LumpClass._format, self.file.read(self._entry_size))
                return self.LumpClass(raw_entry)
        elif isinstance(index, slice):
            _slice = _remap_slice(index, self._length)
            out = list()
            for i in range(_slice.start, _slice.stop, _slice.step):
                out.append(self[i])
            return out
        else:
            raise TypeError(f"list indices must be integers or slices, not {type(index)}")

    def append(self, entry):
        self.length += 1
        self[-1] = entry

    def extend(self, entries: bytes):
        for entry in entries:
            self.append(entry)

    def find(self, **kwargs):
        """Returns all lump entries which have the queried values [e.g. find(x=0)]"""
        out = list()
        entire_lump = self[::]  # load all LumpClasses
        for entry in entire_lump:
            if all([getattr(entry, attr) == value for attr, value in kwargs.items()]):
                out.append(entry)
        return out

    def insert(self, index: int, entry: Any):
        self.length += 1
        self[index + 1:] = self[index:]
        self[index] = entry

    def pop(self, index: Union[int, slice]) -> Union[int, bytes]:
        out = self[index]
        del self[index]
        return out


class BasicBspLump(BspLump):
    """Dynamically reads LumpClasses from a binary file"""
    file: io.BufferedReader  # file opened in "rb" (read-bytes) mode
    offset: int  # position in file where lump begins
    _changes: Dict[int, Any]
    # ^ {index: LumpClass(new_entry)}
    _length: int  # number of indexable entries

    def __getitem__(self, index: Union[int, slice]):
        """Reads bytes from self.file & returns LumpClass(es)"""
        # read bytes -> struct.unpack tuples -> LumpClass
        # NOTE: BspLump[index] = LumpClass(entry)
        if isinstance(index, int):
            index = _remap_negative_index(index, self._length)
            self.file.seek(self.offset + (index * self._entry_size))
            raw_entry = struct.unpack(self.LumpClass._format, self.file.read(self._entry_size))
            # NOTE: only the following line has changed
            return self.LumpClass(raw_entry[0])
        elif isinstance(index, slice):
            _slice = _remap_slice(index, self._length)
            out = list()
            for i in range(_slice.start, _slice.stop, _slice.step):
                out.append(self[i])
            return out
        else:
            raise TypeError(f"list indices must be integers or slices, not {type(index)}")


class ExternalRawBspLump(RawBspLump):
    """Maps an open binary file to a list-like object"""
    file: io.BufferedReader  # file opened in "rb" (read-bytes) mode
    offset: int  # position in file where lump begins
    _changes: Dict[int, bytes]
    # ^ {index: new_byte}
    _length: int  # number of indexable entries
    # -- should also override any returned entries with _changes

    def __init__(self, lump_header: collections.namedtuple):
        self.file = open(lump_header.filename, "rb")
        self.offset = 0
        self._changes = dict()  # changes must be applied externally
        self._length = lump_header.filesize

    def __del__(self):
        self.file.close()


class ExternalBspLump(BspLump):
    """Dynamically reads LumpClasses from a binary file"""
    # NOTE: this class does not handle compressed lumps
    file: io.BufferedReader  # file opened in "rb" (read-bytes) mode
    offset: int  # position in file where lump begins
    _changes: Dict[int, Any]
    # ^ {index: LumpClass(new_entry)}
    _length: int  # number of indexable entries

    def __init__(self, lump_header: collections.namedtuple, LumpClass: object):
        super(ExternalBspLump, self).__init__(None, lump_header, LumpClass)
        self.file = open(lump_header.filename, "rb")
        self.offset = 0  # NOTE: 16 if ValveBsp
        self._changes = dict()  # changes must be applied externally

    def __del__(self):
        self.file.close()


class ExternalBasicBspLump(BasicBspLump):
    """Dynamically reads LumpClasses from a binary file"""
    # NOTE: this class does not handle compressed lumps
    file: io.BufferedReader  # file opened in "rb" (read-bytes) mode
    offset: int  # position in file where lump begins
    _changes: Dict[int, Any]
    # ^ {index: LumpClass(new_entry)}
    _length: int  # number of indexable entries

    def __init__(self, lump_header: collections.namedtuple, LumpClass: object):
        super(ExternalBasicBspLump, self).__init__(None, lump_header, LumpClass)
        self.file = open(lump_header.filename, "rb")
        self.offset = 0
        self._changes = dict()  # changes must be applied externally

    def __del__(self):
        self.file.close()
