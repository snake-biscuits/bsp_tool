"""handles dynamically loading entries from lumps of all kinds"""
from __future__ import annotations

import io
import lzma
import struct
from typing import Any, Dict, Union
import warnings


def _remap_negative_index(index: int, length: int) -> int:
    """simplify to positive integer"""
    if index < 0:
        index = length + index
    if index >= length or index < 0:
        raise IndexError("list index out of range")
    return index


def _remap_slice(_slice: slice, length: int) -> slice:
    """simplify to positive start & stop within range(0, length)"""
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


def decompress_valve_LZMA(data: bytes) -> bytes:
    """valve LZMA header adapter"""
    magic, true_size, compressed_size, properties = struct.unpack("4s2I5s", data[:17])
    _filter = lzma._decode_filter_properties(lzma.FILTER_LZMA1, properties)
    decompressor = lzma.LZMADecompressor(lzma.FORMAT_RAW, None, [_filter])
    decompressed_data = decompressor.decompress(data[17:17 + compressed_size])
    return decompressed_data[:true_size]  # trim any excess bytes


def decompressed(file: io.BufferedReader, lump_header: Any) -> (io.BytesIO, Any):
    """Takes a lump and decompresses it if nessecary. Also corrects lump_header offset & length"""
    if getattr(lump_header, "fourCC", 0) != 0:
        # get lump bytes
        if not hasattr(lump_header, "filename"):  # internal compressed lump
            file.seek(lump_header.offset)
            data = file.read(lump_header.length)
        else:  # external compressed lump is unlikely, but possible
            data = open(lump_header.filename, "rb").read()
        file = io.BytesIO(decompress_valve_LZMA(data))
        # modify lump header to point at the decompressed lump (fake file, data starts at offset=0)
        lump_header.offset = 0
        lump_header.length = lump_header.fourCC
    return file, lump_header


def create_BspLump(file: io.BufferedReader, lump_header: Any, LumpClass: object = None) -> BspLump:
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


def create_RawBspLump(file: io.BufferedReader, lump_header: Any) -> RawBspLump:
    if not hasattr(lump_header, "filename"):
        return RawBspLump(file, lump_header)
    else:
        return ExternalRawBspLump(lump_header)


def create_BasicBspLump(file: io.BufferedReader, lump_header: Any, LumpClass: object) -> BasicBspLump:
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
    # NOTE: bytes objects don't support item assignment
    # -- but we want to allow light hex editting with slice overrides
    _length: int  # number of indexable entries

    def __init__(self, file: io.BufferedReader, lump_header: Any):
        self.file = file
        self.offset = lump_header.offset
        self._changes = dict()
        # ^ {index: new_value}
        self._length = lump_header.length

    def __repr__(self):
        return f"<{self.__class__.__name__}; {len(self)} bytes at 0x{id(self):016X}>"

    # NOTE: no __delitem__

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

    def __iadd__(self, other_bytes: bytes):
        if not isinstance(other_bytes, bytes):
            raise TypeError(f"can't concat {other_bytes.__class__.__name__} to bytes")
        start = self._length
        self._length += len(other_bytes)
        self[start:] = other_bytes  # slice insert; TEST!

    def __setitem__(self, index: int | slice, value: Any):
        """remapping slices is allowed, but only slices"""
        if isinstance(index, int):
            index = _remap_negative_index(index, self._length)
            self._changes[index] = value
        elif isinstance(index, slice):
            _slice = _remap_slice(index, self._length)
            slice_indices = list(range(_slice.start, _slice.stop, _slice.step))
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

    def __iter__(self):
        return iter([self[i] for i in range(self._length)])

    def __len__(self):
        return self._length


class BspLump(RawBspLump):
    """Dynamically reads LumpClasses from a binary file"""
    file: io.BufferedReader  # file opened in "rb" (read-bytes) mode
    offset: int  # position in file where lump begins
    LumpClass: object
    _changes: Dict[int, Any]
    # ^ {index: LumpClass(new_entry)}
    # NOTE: there are no checks to ensure changes are the correct type or size
    _entry_size: int  # sizeof(LumpClass)
    _length: int  # number of indexable entries

    def __init__(self, file: io.BufferedReader, lump_header: Any, LumpClass: object):
        self.file = file
        self.offset = lump_header.offset
        self._changes = dict()  # changes must be applied externally
        self._entry_size = struct.calcsize(LumpClass._format)
        if lump_header.length % self._entry_size != 0:
            raise RuntimeError(f"LumpClass does not divide lump evenly! ({lump_header.length} / {self._entry_size})")
        self._length = lump_header.length // self._entry_size
        self.LumpClass = LumpClass

    def __repr__(self):
        return f"<{self.__class__.__name__}({len(self)} {self.LumpClass.__name__}) at 0x{id(self):016X}>"

    def __delitem__(self, index: Union[int, slice]):
        if isinstance(index, int):
            index = _remap_negative_index(index, self._length)
            self[index:] = self[index + 1:]
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
                _tuple = struct.unpack(self.LumpClass._format, self.file.read(self._entry_size))
                return self.LumpClass.from_tuple(_tuple)
        elif isinstance(index, slice):  # LAZY HACK
            _slice = _remap_slice(index, self._length)
            out = list()
            for i in range(_slice.start, _slice.stop, _slice.step):
                out.append(self[i])
            return out
        else:
            raise TypeError(f"list indices must be integers or slices, not {type(index)}")

    def append(self, entry):
        self._length += 1
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
        self._length += 1
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
    LumpClass: object
    _changes: Dict[int, Any]
    # ^ {index: LumpClass(new_entry)}
    # NOTE: there are no checks to ensure changes are the correct type or size
    _entry_size: int  # sizeof(LumpClass)
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

    def __init__(self, lump_header: Any):
        self.file = open(lump_header.filename, "rb")
        self.offset = 0
        self._changes = dict()  # changes must be applied externally
        self._length = lump_header.filesize


class ExternalBspLump(BspLump):
    """Dynamically reads LumpClasses from a binary file"""
    # NOTE: this class does not handle compressed lumps
    file: io.BufferedReader  # file opened in "rb" (read-bytes) mode
    offset: int  # position in file where lump begins
    LumpClass: object
    _changes: Dict[int, Any]
    # ^ {index: LumpClass(new_entry)}
    # NOTE: there are no checks to ensure changes are the correct type or size
    _entry_size: int  # sizeof(LumpClass)
    _length: int  # number of indexable entries

    def __init__(self, lump_header: Any, LumpClass: object):
        super(ExternalBspLump, self).__init__(None, lump_header, LumpClass)
        self.file = open(lump_header.filename, "rb")
        self.offset = 0  # NOTE: 16 if ValveBsp
        self._changes = dict()  # changes must be applied externally


class ExternalBasicBspLump(BasicBspLump):
    """Dynamically reads LumpClasses from a binary file"""
    # NOTE: this class does not handle compressed lumps
    file: io.BufferedReader  # file opened in "rb" (read-bytes) mode
    offset: int  # position in file where lump begins
    _changes: Dict[int, Any]
    # ^ {index: LumpClass(new_entry)}
    _length: int  # number of indexable entries

    def __init__(self, lump_header: Any, LumpClass: object):
        super(ExternalBasicBspLump, self).__init__(None, lump_header, LumpClass)
        self.file = open(lump_header.filename, "rb")
        self.offset = 0
        self._changes = dict()  # changes must be applied externally


class GameLump:
    endianness: str = "little"
    GameLumpHeaderClass: Any  # used for reads / writes
    headers: Dict[str, Any]
    # ^ {"child_lump": GameLumpHeader}
    is_external = False
    loading_errors: Dict[str, Any]
    # ^ {"child_lump": Error}

    # NOTE: https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/gamebspfile.h#L25
    # -- ^ lists a few possible child lumps:
    # -- dplh: Detail Prop Lighting HDR
    # -- dplt: Detail Prop Lighting
    # -- dprp: Detail Props (procedural grass on displacements)
    # -- sprp: Static Props

    def __init__(self, file: io.BufferedReader, lump_header: Any, endianness: str,
                 LumpClasses: Dict[str, object], GameLumpHeaderClass: object):
        self.endianness = endianness
        self.GameLumpHeaderClass = GameLumpHeaderClass
        self.loading_errors = dict()
        lump_offset = 0
        if not hasattr(lump_header, "filename"):
            lump_offset = lump_header.offset
            file.seek(lump_offset)
        else:
            self.is_external = True
        game_lumps_count = int.from_bytes(file.read(4), self.endianness)
        self.headers = dict()
        # {"child_name": child_header}
        for i in range(game_lumps_count):
            child_header = GameLumpHeaderClass.from_stream(file)
            if self.is_external:
                child_header.offset = child_header.offset - lump_header.offset
            child_name = child_header.id.decode("ascii")
            if self.endianness == "little":
                child_name = child_name[::-1]  # "prps" -> "sprp"
            self.headers[child_name] = child_header
        # load child lumps (SpecialLumpClasses)
        # TODO: check for skipped bytes / padding
        # TODO: defer loading to __getattr__ ?
        for child_name, child_header in self.headers.items():
            child_LumpClass = LumpClasses.get(child_name, dict()).get(child_header.version, None)
            if child_LumpClass is None:
                setattr(self, child_name, create_RawBspLump(file, child_header))
            else:
                file.seek(child_header.offset)
                try:
                    child_lump_bytes = file.read(child_header.length)
                    compressed = child_lump_bytes[:4] == b"LZMA"
                    if compressed and child_header.flags & 1 != 1:
                        warnings.warn(UserWarning(f"{child_name} game lump is compressed but the flag is unset (Xbox360?)"))
                    if not compressed:
                        child_lump = child_LumpClass(child_lump_bytes)
                    if compressed and child_header.length > 17:  # sizeof(LZMA_Header)
                        child_lump_bytes = decompress_valve_LZMA(child_lump_bytes)
                        child_lump = child_LumpClass(child_lump_bytes)
                    elif compressed:  # but otherwise empty
                        # NOTE: length might be 12, for an empty source.GameLump_SPRP
                        warnings.warn(UserWarning(f"compressed empty {child_name} game lump"))
                        child_lump = None
                except Exception as exc:
                    self.loading_errors[child_name] = exc
                    child_lump = create_RawBspLump(file, child_header)
                    # NOTE: RawBspLumps are not decompressed
                if child_lump is not None:  # discarding compressed empty lumps
                    setattr(self, child_name, child_lump)
                # TODO: test how empty lumps are written back
                # -- can the branch that produced this wierd case function without this lump?
        if self.is_external:
            file.close()

    def as_bytes(self, lump_offset=0):
        """lump_offset makes headers relative to the file"""
        # NOTE: ValveBsp .lmp external lumps have a 16 byte header
        # NOTE: RespawnBsp .bsp_lump offsets are relative to the internal .bsp GAME_LUMP.offset
        # NOTE: Xbox360 child lumps will not be recompressed
        out = []
        out.append(len(self.headers).to_bytes(4, self.endianness))
        headers = []
        # skip the headers
        cursor_offset = lump_offset + 4 + len(self.headers) * struct.calcsize(self.GameLumpHeaderClass._format)
        # write child lumps
        # TODO: generate absent headers from lump names
        # -- this will require an endianness check for header.id
        for child_name, child_header in self.headers.items():
            child_lump = getattr(self, child_name)
            if isinstance(child_lump, RawBspLump):
                child_lump_bytes = child_lump[::]
            else:
                child_lump_bytes = child_lump.as_bytes()  # SpecialLumpClass method
            out.append(child_lump_bytes)
            # recalculate header
            child_header.offset = cursor_offset
            child_header.length = len(child_lump_bytes)
            cursor_offset += child_header.length
            headers.append(child_header)
        # and finally inject the headers back in before "writing"
        headers = [h.as_bytes() for h in headers]
        out[1:1] = headers
        return b"".join(out)


class DarkMessiahSPGameLump:
    endianness: str = "little"
    GameLumpHeaderClass: Any  # used for reads / writes
    headers: Dict[str, Any]
    # ^ {"child_lump": GameLumpHeader}
    is_external = False
    loading_errors: Dict[str, Any]
    # ^ {"child_lump": Error}
    unknown: int

    def __init__(self, file: io.BufferedReader, lump_header: Any, endianness: str,
                 LumpClasses: Dict[str, object], GameLumpHeaderClass: object):
        self.endianness = endianness
        self.GameLumpHeaderClass = GameLumpHeaderClass
        self.loading_errors = dict()
        lump_offset = 0
        if not hasattr(lump_header, "filename"):
            lump_offset = lump_header.offset
            file.seek(lump_offset)
        else:
            self.is_external = True
        game_lumps_count = int.from_bytes(file.read(4), self.endianness)
        self.unknown = int.from_bytes(file.read(4), self.endianness)
        self.headers = dict()
        # {"child_name": child_header}
        for i in range(game_lumps_count):
            child_header = GameLumpHeaderClass.from_stream(file)
            if self.is_external:
                child_header.offset = child_header.offset - lump_header.offset
            child_name = child_header.id.decode("ascii")
            if self.endianness == "little":
                child_name = child_name[::-1]  # "prps" -> "sprp"
            self.headers[child_name] = child_header
        # load child lumps (SpecialLumpClasses)
        # TODO: check for skipped bytes / padding
        # TODO: defer loading to __getattr__ ?
        for child_name, child_header in self.headers.items():
            child_LumpClass = LumpClasses.get(child_name, dict()).get(child_header.version, None)
            if child_LumpClass is None:
                setattr(self, child_name, create_RawBspLump(file, child_header))
            else:
                file.seek(child_header.offset)
                try:
                    child_lump_bytes = file.read(child_header.length)
                    # check if GameLump child is LZMA compressed (Xbox360)
                    # -- GameLumpHeader.flags does not appear to inidicate compression
                    if child_lump_bytes[:4] == b"LZMA":
                        child_lump_bytes = decompress_valve_LZMA(child_lump_bytes)
                    child_lump = child_LumpClass(child_lump_bytes)
                except Exception as exc:
                    self.loading_errors[child_name] = exc
                    child_lump = create_RawBspLump(file, child_header)
                    # NOTE: RawBspLumps are not decompressed
                setattr(self, child_name, child_lump)
        if self.is_external:
            file.close()

    def as_bytes(self, lump_offset=0) -> bytes:
        """lump_offset makes headers relative to the file"""
        # NOTE: ValveBsp .lmp external lumps have a 16 byte header
        # NOTE: RespawnBsp .bsp_lump offsets are relative to the internal .bsp GAME_LUMP.offset
        # NOTE: Xbox360 child lumps will not be recompressed
        out = []
        out.append(len(self.headers).to_bytes(4, self.endianness))
        out.append(self.unknown)
        headers = []
        # skip the headers
        cursor_offset = lump_offset + 4 + len(self.headers) * struct.calcsize(self.GameLumpHeaderClass._format)
        # write child lumps
        # TODO: generate absent headers from lump names
        # -- this will require an endianness check for header.id
        for child_name, child_header in self.headers.items():
            child_lump = getattr(self, child_name)
            if isinstance(child_lump, RawBspLump):
                child_lump_bytes = child_lump[::]
            else:
                child_lump_bytes = child_lump.as_bytes()  # SpecialLumpClass method
            out.append(child_lump_bytes)
            # recalculate header
            child_header.offset = cursor_offset
            child_header.length = len(child_lump_bytes)
            cursor_offset += child_header.length
            headers.append(child_header)
        # and finally inject the headers back in before "writing"
        headers = [h.as_bytes() for h in headers]
        out[1:1] = headers
        return b"".join(out)
