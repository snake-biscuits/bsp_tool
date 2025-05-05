"""Base classes for defining .bsp lump structs"""
from __future__ import annotations
import enum
import io
import struct
from typing import Any, Dict, Iterable, List, Union

from . import bitfield
from . import common
from . import mapped_array


ArraysDict = Dict[str, Union[int, List[str], Dict[str, Any]]]  # recursive
# ^ {"a": 2, "b": [*"xyz"], "c": {"u": [*"xy"], "v": [*"xy"]}}
# TODO: {int: Mapping} mappings (list of MappedArray)
# -- e.g. {"triangle": {3: Vertex}}
# -- int dict keys could get dicey, but this is already for rare edge cases


struct_attr_formats: Dict[Struct, Dict[str, str]] = dict()
# ^ {LumpClass: {"attr": "sub_format"}}


def mapping_length(mapping: mapped_array.AttrMap) -> int:
    """counts length of tuple required for mapping"""
    # NOTE: designed for MappedArray
    # -- for Struct use:
    # -- {slot: StructClass._arrays.get(slot, None)
    # --  for slots in StructClass.__slots__}
    if isinstance(mapping, list):
        return len(mapping)
    length = 0
    for child_mapping in mapping.values():
        if isinstance(child_mapping, list):  # assumes list of single attrs
            length += len(child_mapping)
        elif isinstance(child_mapping, int):
            length += child_mapping
        elif isinstance(child_mapping, dict):
            length += mapping_length(child_mapping)
        elif child_mapping is None:
            length += 1
        else:
            raise RuntimeError(f"Unexpected Mapping! ({mapping}, {child_mapping})")
    return length


class Struct:
    """base class for tuple <-> class conversion
    bytes <-> tuple conversion is handled by the struct module"""
    __slots__: List[str] = list()  # names of atributes, in order
    # NOTE: since we are using __slots__, defaults cannot be set as class variables!
    # -- override the _defaults() classmethod instead (use super & modify the returned dict)
    _format: str = str()  # struct module format string
    _arrays: ArraysDict = dict()  # child MappedArray _mappings
    # NOTE: if you aren't using _arrays, use MappedArray instead
    # optional:
    _bitfields: bitfield.BitFieldsDict = dict()
    _classes: common.ClassesDict = dict()
    # NOTE: an attr should only go into either _classes or _bitfields, never both!

    def __init__(self, *args, **kwargs):
        # LumpClass(attr1, [attr2_1, attr2_2]) or LumpClass(attr1, attr2=[attr2_1, attr2_2])
        # NOTE: can only set top-level value, no partial init of nested attr via kwargs (yet)
        assert len(args) <= len(self.__slots__), "Too many arguments! Should match top level attributes!"
        invalid_kwargs = set(kwargs).difference(set(self.__slots__))
        # TODO: could branch here and check for subattr kwargs
        # subattr_values = {a: dict_subgroup(kwargs, a) for a in {k.partition(".")[0] for k in invalid_kwargs}}
        # invalid_kwargs = set(subattr_values).difference(set(self.__slots__))
        # TODO: check each subgroup for invalid values targetting _arrays, also recurse down into BitFields
        assert len(invalid_kwargs) == 0, f"Invalid kwargs: {invalid_kwargs}"
        if len(args) == len(self.__slots__):  # cheeky recursion avoider
            default_values = dict()
        # NOTE: could also skip generating defaults if kwargs defines the whole struct
        # -- however that's probably more work to detect than could be saved so \_(0.0)_/
        else:
            default_values = self._defaults()
        default_values.update(dict(zip(self.__slots__, args)))
        default_values.update(kwargs)
        # TODO: set subattr_values
        global struct_attr_formats  # noqa: F824
        _attr_formats = struct_attr_formats[self.__class__] = dict()
        types = common.split_format(self._format)
        types_index = 0
        for attr, value in default_values.items():
            if attr not in self._arrays:  # Union[int, float, str]
                _attr_formats[attr] = types[types_index]
                types_index += 1
                setattr(self, attr, value)  # handles _classes & _bitfields
                continue  # next attr
            # child contructor metadata
            mapping = self._arrays[attr]
            length = mapping_length({None: mapping})
            _attr_formats[attr] = "".join(types[types_index:types_index + length])
            types_index += length
            _bitfields = common.subgroup(self._bitfields, attr)
            _classes = common.subgroup(self._classes, attr)
            # value is MappedArray / _classes[attr]
            if attr in self._classes:
                setattr(self, attr, value)  # no questions asked
            elif isinstance(value, mapped_array.MappedArray):
                assert value._mapping == mapping
                # NOTE: DON'T need to verify MappedArray._format
                value._classes = _classes
                value._bitfields = _bitfields
                setattr(self, attr, value)
            # TODO: List[MappedArray]
            # value -> MappedArray
            elif isinstance(mapping, int):  # List[Union[int, float, str]]
                assert len(value) == mapping
                setattr(self, attr, value)
            elif isinstance(mapping, (list, dict)):  # create MappedArray
                sub_kwargs = dict(_mapping=mapping, _format=_attr_formats[attr], _bitfields=_bitfields, _classes=_classes)
                setattr(self, attr, mapped_array.MappedArray.from_tuple(value, **sub_kwargs))  # assumes value is Iterable
            else:
                raise RuntimeError(f"{self.__class__.__name__} has bad _arrays!")

    def __eq__(self, other: Struct):
        if not isinstance(other, self.__class__):
            return False
        else:
            return self.as_tuple() == other.as_tuple()

    def __hash__(self):
        return hash(tuple(self.as_tuple()))

    def __iter__(self) -> Iterable:
        return iter([getattr(self, attr) for attr in self.__slots__])

    def __len__(self) -> int:
        return len(self.__slots__)

    def __repr__(self) -> str:
        attrs = [f"{a}={getattr(self, a)!r}" for a in self.__slots__]
        return f"{self.__class__.__name__}({', '.join(attrs)})"

    def __setattr__(self, attr, value):
        # NOTE: private variables must pass through untouched
        # NOTE: bitfield & class should be mutually exclusive, so order doesn't matter
        value = common.school(self, attr, value)
        # TODO: enforce BitField spec (_fields, _format, _classes)
        if attr in self._bitfields and not isinstance(value, bitfield.BitField):
            global struct_attr_formats  # noqa: F824
            _format = struct_attr_formats[self.__class__][attr]
            value = bitfield.BitField.from_int(
                value,
                _fields=self._bitfields[attr],
                _format=_format,
                _classes=common.subgroup(self._classes, attr))
        # TODO: enforce MappedArray spec
        super().__setattr__(attr, value)

    @classmethod
    def _defaults(cls) -> Dict[str, Any]:
        types = common.split_format(cls._format)
        defaults = cls.from_tuple([
            common.type_defaults[t] if not t.endswith("s") else ""
            for t in types])
        return dict(zip(cls.__slots__, defaults))

    @classmethod
    def from_bytes(cls, _bytes: bytes) -> Struct:
        expected_length = struct.calcsize(cls._format)
        assert len(_bytes) == expected_length, f"Not enough bytes! Expected {expected_length} got {len(_bytes)}"
        _tuple = struct.unpack(cls._format, _bytes)
        expected_length = len(cls.__slots__) + mapping_length(cls._arrays) - len(cls._arrays)
        assert len(_tuple) == expected_length, f"{cls.__name__} mappings do not match _format"
        return cls.from_tuple(_tuple)

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Struct:
        return cls.from_bytes(stream.read(struct.calcsize(cls._format)))

    @classmethod
    def from_tuple(cls, _tuple: Iterable) -> Struct:
        """_tuple comes from: struct.unpack(self._format, bytes)"""
        # NOTE: _classes & _bitfields are handled by cls.__init__
        out_args = list()
        types = common.split_format(cls._format)
        _tuple_index = 0
        for attr in cls.__slots__:
            if attr not in cls._arrays:
                value = _tuple[_tuple_index]
                length = 1
            else:  # partition up children
                child_mapping = cls._arrays[attr]
                if isinstance(child_mapping, (list, dict)):  # child_mapping: List[str]
                    length = mapping_length({None: child_mapping})
                    array = _tuple[_tuple_index:_tuple_index + length]
                    child_format = "".join(types[_tuple_index:_tuple_index + length])
                    value = mapped_array.MappedArray.from_tuple(
                        array,
                        _mapping=child_mapping,
                        _format=child_format,
                        _classes=common.subgroup(cls._classes, attr),
                        _bitfields=common.subgroup(cls._bitfields, attr))
                elif isinstance(child_mapping, int):
                    length = child_mapping
                    value = _tuple[_tuple_index:_tuple_index + length]
                else:
                    raise RuntimeError(f"Invalid type: {type(child_mapping)} in {cls.__class__.__name__}._arrays")
            out_args.append(value)
            _tuple_index += length
        return cls(*out_args)

    def as_bytes(self) -> bytes:
        return struct.pack(self._format, *self.as_tuple())

    def as_tuple(self) -> list:
        """recreates the _tuple this instance was initialised from"""
        _tuple = list()
        for slot in self.__slots__:
            value = getattr(self, slot)
            if isinstance(value, mapped_array.MappedArray):
                _tuple.extend(value.as_tuple())  # unpack the stack
            elif isinstance(value, bitfield.BitField):
                _tuple.append(value.as_int())
            elif isinstance(value, str):
                _tuple.append(value.encode("ascii", errors="ignore"))
            elif isinstance(value, bytes):
                _tuple.append(value)
            elif isinstance(value, (enum.Enum, enum.IntFlag)):  # enum _classes -> int
                _tuple.append(value.value)
            elif isinstance(value, Iterable):  # includes _classes
                _tuple.extend(value)
            else:
                _tuple.append(value)
        return [
            int(attr) if format_ in "bBhHiI" else attr
            for attr, format_ in zip(_tuple, common.split_format(self._format))]
