"""classes for dynamically parsing lumps"""
from __future__ import annotations

import io
import lzma
import struct
from typing import Any, Dict, Union
import warnings


LumpHeader = Any
# all: offset & length
# ValveBsp / RespawnBsp: fourCC & version
# external: filename & filesize
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


def decompress_valve_LZMA(data: bytes) -> bytes:
    """valve LZMA header adapter"""
    magic, true_size, compressed_size, properties = struct.unpack("4s2I5s", data[:17])
    assert magic == b"LZMA"
    _filter = lzma._decode_filter_properties(lzma.FILTER_LZMA1, properties)
    decompressor = lzma.LZMADecompressor(lzma.FORMAT_RAW, None, [_filter])
    decompressed_data = decompressor.decompress(data[17:17 + compressed_size])
    return decompressed_data[:true_size]  # trim any excess bytes


def decompressed(stream: Stream, lump_header: LumpHeader) -> (Stream, LumpHeader):
    """Takes a lump and decompresses it if nessecary. Also corrects lump_header offset & length"""
    if getattr(lump_header, "fourCC", 0) != 0:
        if not hasattr(lump_header, "filename"):
            stream.seek(lump_header.offset)
            data = stream.read(lump_header.length)
        else:  # unlikely, but possible
            data = open(lump_header.filename, "rb").read()
        stream = io.BytesIO(decompress_valve_LZMA(data))
        lump_header.offset = 0
        lump_header.length = lump_header.fourCC
    return stream, lump_header


def create_RawBspLump(stream: Stream, lump_header: LumpHeader) -> RawBspLump:
    if hasattr(lump_header, "fourCC"):
        stream, lump_header = decompressed(stream, lump_header)
    if not hasattr(lump_header, "filename"):
        return RawBspLump.from_header(stream, lump_header)
    else:
        return ExternalRawBspLump.from_header(lump_header)


def create_BasicBspLump(stream: Stream, lump_header: LumpHeader, LumpClass: object) -> BasicBspLump:
    if hasattr(lump_header, "fourCC"):
        stream, lump_header = decompressed(stream, lump_header)
    if not hasattr(lump_header, "filename"):
        return BasicBspLump.from_header(stream, lump_header, LumpClass)
    else:
        return ExternalBasicBspLump.from_header(lump_header, LumpClass)


def create_BspLump(stream: Stream, lump_header: LumpHeader, LumpClass: object = None) -> BspLump:
    if hasattr(lump_header, "fourCC"):
        stream, lump_header = decompressed(stream, lump_header)
    if not hasattr(lump_header, "filename"):
        return BspLump.from_header(stream, lump_header, LumpClass)
    else:
        return ExternalBspLump.from_header(lump_header, LumpClass)


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

    @classmethod
    def from_header(cls, stream: Stream, lump_header: LumpHeader):
        out = cls()
        out._length = lump_header.length
        out.offset = lump_header.offset
        out.stream = stream
        return out

    def __repr__(self):
        return f"<{self.__class__.__name__}; {len(self)} bytes at 0x{id(self):016X}>"

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

    def __getitem__(self, index: Union[int, slice]) -> Union[int, bytearray]:
        """Reads bytes from the start of the lump"""
        if isinstance(index, int):
            return self.get(_remap_index(index, self._length))
        elif isinstance(index, slice):
            # TODO: BspLump[::] returns a copy (doesn't update _changes)
            return bytearray([self[i] for i in _remap_slice_to_range(index, self._length)])
        else:
            raise TypeError(f"list indices must be integers or slices, not {type(index)}")

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

    def __iter__(self):
        return iter([self.get(i, mutable=False) for i in range(self._length)])

    def __len__(self):
        return self._length

    def append(self, entry):
        self._length += 1
        self[-1] = entry

    def extend(self, entries: bytes):
        for entry in entries:
            self.append(entry)

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
    def from_header(cls, stream: Stream, lump_header: LumpHeader, LumpClass: object):
        out = cls()
        out.LumpClass = LumpClass
        out._entry_size = struct.calcsize(LumpClass._format)
        out._length = lump_header.length // out._entry_size
        out.offset = lump_header.offset
        out.stream = stream
        if lump_header.length % out._entry_size != 0:
            raise RuntimeError(f"LumpClass does not divide lump evenly! ({lump_header.length} / {out._entry_size})")
        return out

    def __repr__(self):
        return f"<{self.__class__.__name__}({len(self)} {self.LumpClass.__name__}) at 0x{id(self):016X}>"

    def get_unchanged(self, index: int) -> int:
        """no index remapping, be sure to respect stream data bounds!"""
        # NOTE: no .from_stream(); BasicLumpClasses only specify _format
        self.stream.seek(self.offset + (index * self._entry_size))
        raw_entry = struct.unpack(self.LumpClass._format, self.stream.read(self._entry_size))
        return self.LumpClass(raw_entry[0])

    def __getitem__(self, index: Union[int, slice]):
        """Reads bytes from self.stream & returns LumpClass(es)"""
        if isinstance(index, int):
            return self.get(_remap_index(index, self._length))
        elif isinstance(index, slice):
            return [self[i] for i in _remap_slice_to_range(index, self._length)]
        else:
            raise TypeError(f"list indices must be integers or slices, not {type(index)}")


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


class ExternalRawBspLump(RawBspLump):
    """Maps an open binary stream to a list-like object"""
    stream: Stream
    offset: int  # position in stream where lump begins
    _changes: Dict[int, bytes]
    # ^ {index: new_byte}
    _length: int  # number of indexable entries
    # -- should also override any returned entries with _changes

    @classmethod
    def from_header(cls, lump_header: LumpHeader):
        out = cls()
        out._length = lump_header.filesize
        out.offset = 0
        out.stream = open(lump_header.filename, "rb")
        return out


class ExternalBasicBspLump(BasicBspLump):
    """Dynamically reads LumpClasses from a binary stream"""
    stream: Stream
    offset: int  # position in stream where lump begins
    LumpClass: object
    _changes: Dict[int, object]
    # ^ {index: LumpClass(new_entry)}
    _length: int  # number of indexable entries

    @classmethod
    def from_header(cls, lump_header: LumpHeader, LumpClass: object):
        out = super().from_header(None, lump_header, LumpClass)
        out.offset = 0
        out.stream = open(lump_header.filename, "rb")
        return out


class ExternalBspLump(BspLump):
    """Dynamically reads LumpClasses from a binary stream"""
    stream: Stream
    offset: int  # position in stream where lump begins
    LumpClass: object
    _changes: Dict[int, object]
    # ^ {index: LumpClass(new_entry)}
    # NOTE: there are no checks to ensure changes are the correct type or size
    _entry_size: int  # sizeof(LumpClass)
    _length: int  # number of indexable entries

    @classmethod
    def from_header(cls, lump_header: LumpHeader, LumpClass: object):
        out = super().from_header(None, lump_header, LumpClass)
        out.offset = 0
        out.stream = open(lump_header.filename, "rb")
        return out


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

    def __init__(self, stream: Stream, lump_header: LumpHeader, endianness: str,
                 LumpClasses: Dict[str, object], GameLumpHeaderClass: object):
        self.GameLumpHeaderClass = GameLumpHeaderClass
        self.endianness = endianness
        self.loading_errors = dict()
        lump_offset = 0
        if not hasattr(lump_header, "filename"):
            lump_offset = lump_header.offset
            stream.seek(lump_offset)
        else:
            self.is_external = True
        game_lumps_count = int.from_bytes(stream.read(4), self.endianness)
        self.headers = dict()
        # {"child_name": child_header}
        for i in range(game_lumps_count):
            child_header = GameLumpHeaderClass.from_stream(stream)
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
                setattr(self, child_name, create_RawBspLump(stream, child_header))
            else:
                stream.seek(child_header.offset)
                try:
                    child_lump_bytes = stream.read(child_header.length)
                    compressed = child_lump_bytes[:4] == b"LZMA"
                    if compressed and child_header.flags & 1 != 1:
                        warnings.warn(UserWarning(f"{child_name} game lump is compressed but the flag is unset (Xbox360?)"))
                    if not compressed:
                        child_lump = child_LumpClass.from_bytes(child_lump_bytes)
                    if compressed and child_header.length > 17:  # sizeof(LZMA_Header)
                        child_lump_bytes = decompress_valve_LZMA(child_lump_bytes)
                        child_lump = child_LumpClass.from_bytes(child_lump_bytes)
                    elif compressed:  # but otherwise empty
                        # NOTE: length might be 12, for an empty source.GameLump_SPRP
                        warnings.warn(UserWarning(f"compressed empty {child_name} game lump"))
                        child_lump = None
                except Exception as exc:
                    self.loading_errors[child_name] = exc
                    child_lump = create_RawBspLump(stream, child_header)
                    # NOTE: RawBspLumps are not decompressed
                if child_lump is not None:  # discarding compressed empty lumps
                    setattr(self, child_name, child_lump)
                # TODO: test how empty lumps are written back
                # -- can the branch that produced this wierd case function without this lump?
        if self.is_external:
            stream.close()

    def as_bytes(self, lump_offset=0):
        """lump_offset makes headers relative to the stream"""
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

    def __init__(self, stream: io.BufferedReader, lump_header: Any, endianness: str,
                 LumpClasses: Dict[str, object], GameLumpHeaderClass: object):
        self.endianness = endianness
        self.GameLumpHeaderClass = GameLumpHeaderClass
        self.loading_errors = dict()
        lump_offset = 0
        if not hasattr(lump_header, "filename"):
            lump_offset = lump_header.offset
            stream.seek(lump_offset)
        else:
            self.is_external = True
        game_lumps_count = int.from_bytes(stream.read(4), self.endianness)
        self.unknown = int.from_bytes(stream.read(4), self.endianness)
        self.headers = dict()
        # {"child_name": child_header}
        for i in range(game_lumps_count):
            child_header = GameLumpHeaderClass.from_stream(stream)
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
                setattr(self, child_name, create_RawBspLump(stream, child_header))
            else:
                stream.seek(child_header.offset)
                try:
                    child_lump_bytes = stream.read(child_header.length)
                    # check if GameLump child is LZMA compressed (Xbox360)
                    # -- GameLumpHeader.flags does not appear to inidicate compression
                    if child_lump_bytes[:4] == b"LZMA":
                        child_lump_bytes = decompress_valve_LZMA(child_lump_bytes)
                    child_lump = child_LumpClass.from_bytes(child_lump_bytes)
                except Exception as exc:
                    self.loading_errors[child_name] = exc
                    child_lump = create_RawBspLump(stream, child_header)
                setattr(self, child_name, child_lump)
        if self.is_external:
            stream.close()

    def as_bytes(self, lump_offset=0) -> bytes:
        """lump_offset makes headers relative to the stream"""
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
