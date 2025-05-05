"""Base classes for defining .bsp lump structs"""
from __future__ import annotations
import collections
import enum
import itertools
import io
import struct
from typing import Dict, Iterable

from . import common


BitFieldMapping = Dict[str, int]
# ^ {"a": 3, "b": 5}
BitFieldsDict = Dict[str, BitFieldMapping]
# ^ {"a": {"flags": 10, "index": 6}}  # uint16_t
# NOTE: BitFields must fill their provided format


class BitField:
    """Maps sub-integer data"""
    # WARNING: field order & bit order may not match!
    # BitField(0xAA, 0XBBBB, 0xCC, _format="I",
    # -- _fields={"a": 8, "b": 16, "c": 8}).as_int() == 0xCCBBBBAA
    _fields: BitFieldMapping = dict()  # must cover entire int type
    # NOTE: _fields will become an OrderedDict when initialised
    # -- if re-ordering attrs, replace _fields with a new OrderedDict
    # TODO: automatically add padding field w/ a UserWarning
    # -- throw an error if padding is already used
    _format: str = ""  # 1x uint8/16/32_t
    # TODO: endianness, wider BitFields (e.g. 2x)
    _classes: common.ClassesDict = dict()
    # ^ {attr: Class}
    # mostly use Enums/IntFlags & bool

    def __init__(self, *args, _fields=None, _format=None, _classes=None, **kwargs):
        """generate a unique class at runtime, just like MappedArray"""
        if len(args) == 1 and len(kwargs) == 0:  # BasicLumpClass
            args = tuple(self.__class__.from_int(args[0], _fields, _format, _classes))
        self._format = self._format if _format is None else _format
        self._fields = collections.OrderedDict(self._fields if _fields is None else _fields)
        self._classes = self._classes if _classes is None else _classes
        # valid specification
        if not (self._format in [*"BHIQ"] and len(self._format) == 1):  # pls no
            raise NotImplementedError("Only unsigned single integer BitFields are supported")
        if sum(self._fields.values()) != struct.calcsize(self._format) * 8:
            raise RuntimeError("fields do not fill format! add an 'unused' field!")
        # valid data
        if len(args) > len(self._fields):
            raise RuntimeError("too many values for current spec")
        if any({k not in self._fields for k in kwargs}):
            raise RuntimeError("invalid field names passed to __init__")
        # set data w/ defaults
        values = dict(itertools.zip_longest(self._fields, args, fillvalue=0))
        values.update(kwargs)
        invalid_kwargs = set(kwargs).difference(set(self._fields))
        assert len(invalid_kwargs) == 0, f"Invalid kwargs: {invalid_kwargs}"
        for attr, size in self._fields.items():
            setattr(self, attr, values[attr])

    def __iter__(self) -> Iterable:
        return iter([getattr(self, attr) for attr in self._fields])

    def __len__(self) -> int:
        return len(self._fields)

    def __repr__(self) -> str:
        attrs = [f"{a}: {getattr(self, a)!r}" for a in self._fields.keys()]
        return f"<{self.__class__.__name__} ({', '.join(attrs)})>"

    def __setattr__(self, attr, value):
        # NOTE: private variables must pass through untouched
        if attr in self._fields:
            if attr in self._classes and isinstance(value, self._classes[attr]):
                assert isinstance(value, (enum.Enum, enum.IntFlag))
                int_value = value.value
            else:
                assert isinstance(value, int)
                int_value = value
            if int_value < 0:
                raise NotImplementedError("Negative values in bitfields not yet supported")
            limit = 2 ** self._fields[attr] - 1
            if int_value > limit:
                raise OverflowError(f"{attr} is out of range! (max allowed value = {limit})")
            value = common.school(self, attr, value)
        super().__setattr__(attr, value)

    @classmethod
    def from_bytes(cls, raw_bitfield: bytes) -> BitField:
        # TODO: _fields, _format & _classes
        int_ = struct.unpack(cls._format, raw_bitfield)[0]
        return cls.from_int(int_)

    @classmethod
    def from_int(cls, value: int, _fields=None, _format=None, _classes=None) -> BitField:
        out_fields = cls._fields if _fields is None else _fields
        out_format = cls._format if _format is None else _format
        out_classes = cls._classes if _classes is None else _classes
        out_args = list()
        offset = struct.calcsize(out_format) * 8
        for size in out_fields.values():
            offset -= size
            mask = (2 ** size - 1) << offset
            out_args.append((value & mask) >> offset)
        return cls(*out_args, _format=out_format, _fields=out_fields, _classes=out_classes)

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> BitField:
        # TODO: _fields, _format & _classes
        return cls.from_bytes(stream.read(struct.calcsize(cls._format)))

    def as_int(self) -> int:
        out = 0
        offset = struct.calcsize(self._format) * 8
        for attr, size in self._fields.items():
            value = getattr(self, attr)
            if isinstance(value, (enum.Enum, enum.IntFlag)):
                value = int(value.value)
            offset -= size
            out += value << offset  # __setattr__ prevents overflow
        return out

    def as_bytes(self, endianness: str = "little") -> bytes:
        return self.as_int().to_bytes(struct.calcsize(self._format), endianness)
