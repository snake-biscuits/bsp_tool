"""Base classes for defining .bsp lump structs"""
from __future__ import annotations
import itertools
import io
import re
import struct
from typing import Any, Dict, Iterable, List, Union


# TODO: _decode: Dict[str, BytesDecodeArgs] class variable for both Struct & MappedArray
# ^ BytesDecodeArgs = Dict[str, str]
# ^^ {"encoding": "utf-8", "errors": "strict"} -> bytes(...).decode(encoding="utf-8", errors="strict")
# -- this should decode any strings in the type, also for re-encoding into bytes
# TODO: set values in Struct / MappedArray __init__ kwargs w/ "attr.sub" keys
# -- use *NEW* dict_subgroup function
# TODO: {int: Mapping} mappings (list of MappedArray)
# -- e.g. {"triangle": {3: Vertex}}
# -- int dict keys could get dicey, but this is already for rare edge cases
# TODO: type coersion (float -> int if lossless in .as_tuple() method)
# TODO: __setattr__ for Struct & MappedArray:
# -- integer overflow check
# -- string length check (assume zero terminated, unless bytestring)
# TODO: allow _classes to target each member of a list, rather than the whole
# -- {"attr[::]": Class}
# -- would go well with List[MappedArray] mappings

ArraysDict = Dict[str, Union[int, List[str], Dict[str, Any]]]  # recursive
# ^ {"a": 2, "b": [*"xyz"], "c": {"u": [*"xy"], "v": [*"xy"]}}
# TODO: Dict[int, ArraysDict]
# -- generate a list of the same MappedArray
AttrMap = Union[List[str], ArraysDict]
# ^ ["a", "b", "c"]
# NOTE: BitFieldMapping & ClassesDict allow "attr.sub" keys
# -- this is because they index structures defined by ArraysDict / AttrMap
BitFieldMapping = Dict[str, int]
# ^ {"a": 3, "b": 5}
BitFieldsDict = Dict[str, BitFieldMapping]
# ^ {"a": {"flags": 10, "index": 6}}  # uint16_t
# NOTE: BitFields must fill their provided format
ClassesDict = Dict[str, Any]
# ^ {"a": Class, "b.c": MappedArray.from_tuple}
# -- e.g. m = MappedArray(0, (1, 2), _mapping={"a": None, "b": 2}, _classes={"a": Class, "b": Class})
# -- m.a = Class(0); m.b = Class(*(1, 2))
# NOTE: classes must have a __iter__ method (allows Struct/MappedArray to convert to bytes)
# NOTE: classes can hold multiple values, but the attr must gather those values to pass them on


struct_attr_formats: Dict[Struct, Dict[str, str]] = dict()
# ^ {LumpClass: {"attr": "sub_format"}}


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
    _bitfields: BitFieldsDict = dict()
    _classes: ClassesDict = dict()
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
        global struct_attr_formats
        _attr_formats = struct_attr_formats[self.__class__] = dict()
        types = split_format(self._format)
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
            _bitfields = dict_subgroup(self._bitfields, attr)
            _classes = dict_subgroup(self._classes, attr)
            # value is MappedArray / _classes[attr]
            if attr in self._classes:
                setattr(self, attr, value)  # no questions asked
            elif isinstance(value, MappedArray):
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
                sub_kwargs = dict(_mapping=mapping, _format=_attr_formats[attr], _bitfields=_bitfields, classes=_classes)
                setattr(self, attr, MappedArray.from_tuple(value, **sub_kwargs))  # assumes value is Iterable
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

    def __repr__(self) -> str:
        attrs = {s: getattr(self, s) for s in self.__slots__}
        return f"<{self.__class__.__name__} ({attrs})>"

    def __setattr__(self, attr, value):  # NOTE: private variables must pass through untouched
        # NOTE: bitfield & class should be mutually exclusive, so order doesn't matter
        value = handle_child_class(self, attr, value)
        # TODO: enforce BitField spec (_fields, _format, _classes)
        if attr in self._bitfields and not isinstance(value, BitField):
            global struct_attr_formats
            _format = struct_attr_formats[self.__class__][attr]
            value = BitField.from_int(value, _fields=self._bitfields[attr], _format=_format,
                                      _classes=dict_subgroup(self._classes, attr))
        # TODO: enforce MappedArray spec
        super().__setattr__(attr, value)

    def as_tuple(self) -> list:
        """recreates the _tuple this instance was initialised from"""
        _tuple = list()
        for slot in self.__slots__:
            value = getattr(self, slot)
            if isinstance(value, MappedArray):
                _tuple.extend(value.as_tuple())  # unpack the stack
            elif isinstance(value, Iterable):  # includes _classes
                _tuple.extend(value)
            elif isinstance(value, BitField):
                _tuple.append(value.as_int())
            else:
                _tuple.append(value)
        return _tuple

    @classmethod
    def _defaults(cls) -> Dict[str, Any]:
        types = split_format(cls._format)
        global type_defaults
        defaults = cls.from_tuple([type_defaults[t] if not t.endswith("s") else "" for t in types])
        return dict(zip(cls.__slots__, defaults))

    # convertors
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
        types = split_format(cls._format)
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
                    value = MappedArray.from_tuple(array, _mapping=child_mapping, _format=child_format,
                                                   _classes=dict_subgroup(cls._classes, attr),
                                                   _bitfields=dict_subgroup(cls._bitfields, attr))
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

    @classmethod
    def as_cpp(self) -> str:  # C++ struct definition
        # TODO: use struct_attr_formats
        raise NotImplementedError()


class MappedArray:
    """Maps a given iterable to a series of names, can even be a nested mapping"""
    _mapping: AttrMap = list()
    _format: str = ""  # struct format string
    _attr_formats: Dict[str, str] = dict()  # generated by __init__
    _bitfields: BitFieldsDict = dict()
    _classes: ClassesDict = dict()

    def __init__(self, *args, _mapping: AttrMap = None, _format: str = None,
                 _bitfields: BitFieldsDict = None, _classes: ClassesDict = None, **kwargs):
        self._mapping = self._mapping if _mapping is None else _mapping
        self._format = self._format if _format is None else _format
        self._bitfields = self._bitfields if _bitfields is None else _bitfields
        self._classes = self._classes if _classes is None else _classes
        assert len(args) <= len(self._mapping), "Too many arguments! Should match top level attributes!"
        # NOTE: _mapping & _format might be passed in as regular args
        # TODO: check to see if _mapping or _mapping, _format are on the tail of args
        # CURSED: don't do that
        invalid_kwargs = set(kwargs).difference(set(self._mapping))
        # TODO: could branch here and check for subattr kwargs
        # subattr_values = {a: dict_subgroup(kwargs, a) for a in {k.partition(".")[0] for k in invalid_kwargs}}
        # invalid_kwargs = set(subattr_values).difference(set(self.__slots__))
        # TODO: check each subgroup for invalid values targetting _arrays, also recurse down into BitFields
        assert len(invalid_kwargs) == 0, f"Invalid kwargs: {invalid_kwargs}"
        if len(args) == len(self._mapping):  # all values are defined
            default_values = dict()
        # NOTE: could also skip generating defaults if arg + kwargs defines the whole struct
        # -- however that's probably more work to detect than could be saved so \_(0.0)_/
        else:
            # NOTE: _defaults is a classmethod, so need to pass overrides
            default_values = self._defaults(_mapping=self._mapping, _format=self._format)
        default_values.update(dict(zip(self._mapping, args)))
        default_values.update(kwargs)
        # TODO: set subattr_values
        types = split_format(self._format)
        types_index = 0
        if isinstance(_mapping, list):
            self._attr_formats = dict(zip(_mapping, types))
            for attr, value in default_values.items():
                setattr(self, attr, value)
            return
        self._attr_formats = dict()  # must be unique
        for attr, value in default_values.items():
            # child contructor metadata
            if isinstance(self._mapping, dict):
                sub_mapping = self._mapping[attr]
            else:
                sub_mapping = None
            length = mapping_length({None: sub_mapping})
            self._attr_formats[attr] = "".join(types[types_index:types_index + length])
            types_index += length
            sub_classes = dict_subgroup(self._classes, attr)
            sub_bitfields = dict_subgroup(self._bitfields, attr)
            if isinstance(value, MappedArray):
                assert isinstance(sub_mapping, (list, dict)), f"Invalid sub_mapping for {attr}: {sub_mapping}"
                assert value._mapping == sub_mapping
                value._classes = sub_classes
                value._bitfields = sub_bitfields
                setattr(self, attr, value)
            # TODO: List[MappedArray]
            elif isinstance(sub_mapping, int):
                assert len(value) == sub_mapping
                setattr(self, attr, value)
            elif isinstance(sub_mapping, (list, dict)):  # create MappedArray
                sub_format = self._attr_formats[attr]
                sub_kwargs = dict(_mapping=sub_mapping, _format=sub_format, _classes=sub_classes, _bitfields=sub_bitfields)
                setattr(self, attr, MappedArray.from_tuple(value, **sub_kwargs))
            elif sub_mapping is None:
                setattr(self, attr, value)
            else:
                raise RuntimeError(f"{self.__class__.__name__} has bad _mapping")

    def __eq__(self, other: Iterable) -> bool:
        return all([(a == b) for a, b in zip(self, other)])

    # TODO: __getattr__ swizzle detection (if and only if mapping is a list of single chars)

    def __getitem__(self, index: str) -> Any:
        return getattr(self, self._mapping[index])

    def __hash__(self):
        return hash(tuple(self.as_tuple()))

    def __iter__(self) -> Iterable:
        return iter([getattr(self, attr) for attr in self._mapping])

    def __repr__(self) -> str:
        attrs = []
        for attr, value in zip(self._mapping, self):
            attrs.append(f"{attr}: {value}")
        return f"<{self.__class__.__name__} ({', '.join(attrs)})>"

    def __setattr__(self, attr, value):  # NOTE: private variables must pass through untouched
        # NOTE: bitfield & class should be mutually exclusive, so order doesn't matter
        value = handle_child_class(self, attr, value)
        # TODO: enforce BitField spec (_fields, _format, _classes)
        if attr in self._bitfields and not isinstance(value, BitField):
            child_format = self._attr_formats[attr]
            value = BitField.from_int(value, _fields=self._bitfields[attr], _format=child_format,
                                      _classes=dict_subgroup(self._classes, attr))
        # TODO: enforce child MappedArray spec
        super().__setattr__(attr, value)

    def as_tuple(self) -> list:
        """recreates the array this instance was generated from"""
        _tuple = list()
        for attr in self._mapping:
            value = getattr(self, attr)
            if isinstance(value, MappedArray):
                _tuple.extend(value.as_tuple())  # recursive call
            elif isinstance(value, Iterable):  # includes _classes
                _tuple.extend(value)
            elif isinstance(value, BitField):
                _tuple.append(value.as_int())
            else:
                _tuple.append(value)
        return _tuple

    @classmethod
    def _defaults(cls, _mapping: AttrMap = None, _format: str = None) -> Dict[str, Any]:
        _format = cls._format if _format is None else _format
        _mapping = cls._mapping if _mapping is None else _mapping
        types = split_format(_format)
        assert mapping_length(_mapping) == len(types), "Invalid mapping for format!"
        global type_defaults
        # TODO: allow default strings (requires a type_defaults function (see below))
        # -- pass down type_defaults _string_mode (warn / trim / fail) ?
        defaults = cls.from_tuple([type_defaults[t] if not t.endswith("s") else "" for t in types],
                                  _mapping=_mapping, _format=_format)
        return dict(zip(list(_mapping), defaults))

    # convertors
    @classmethod
    def from_bytes(cls, _bytes: bytes, _mapping: AttrMap = None, _format: str = None,
                   _bitfields: BitFieldsDict = None, _classes: ClassesDict = None) -> MappedArray:
        _format = cls._format if _format is None else _format
        _mapping = cls._mapping if _mapping is None else _mapping
        _classes = cls._classes if _classes is None else _classes
        _bitfields = cls._bitfields if _bitfields is None else _bitfields
        assert len(_bytes) == struct.calcsize(_format)
        _tuple = struct.unpack(_format, _bytes)
        assert len(_tuple) == mapping_length(_mapping), f"{_tuple}"
        return cls.from_tuple(_tuple, _mapping=_mapping, _format=_format, _bitfields=_bitfields, _classes=_classes)

    @classmethod
    def from_stream(cls, stream: io.BytesIO, _mapping: Any = None, _format: str = None,
                    _bitfields: BitFieldsDict = None, _classes: ClassesDict = None) -> MappedArray:
        kwargs = dict(_mapping=_mapping, _format=_format, _bitfields=_bitfields, _classes=_classes)
        return cls.from_bytes(stream.read(struct.calcsize(cls._format)), **kwargs)

    @classmethod
    def from_tuple(cls, array: Iterable, _mapping: Any = None, _format: str = None,
                   _bitfields: BitFieldsDict = None, _classes: ClassesDict = None) -> MappedArray:
        _format = cls._format if _format is None else _format
        _mapping = cls._mapping if _mapping is None else _mapping
        _classes = cls._classes if _classes is None else _classes
        _bitfields = cls._bitfields if _bitfields is None else _bitfields
        assert len(array) == mapping_length({None: _mapping}), f"{cls.__name__}({array}, _mapping={_mapping})"
        out_args = list()
        if not isinstance(_mapping, (dict, list, int)):
            raise RuntimeError(f"Unexpected mapping: {type(_mapping)}")
        elif isinstance(_mapping, dict):
            types = split_format(_format)
            array_index = 0
            for child_mapping in _mapping.values():
                if child_mapping is not None:  # __init__ might make this redundant
                    length = mapping_length({None: child_mapping})
                    segment = array[array_index:array_index + length]
                    child_format = "".join(types[array_index:array_index + length])
                    array_index += mapping_length({None: child_mapping})
                    child = MappedArray.from_tuple(segment, _mapping=child_mapping, _format=child_format)
                    # NOTE: _classes & _bitfields will be passed down in __init__
                else:  # if {"attr": None}
                    child = array[array_index]  # take a single item, not a slice
                    array_index += 1
                out_args.append(child)
        elif isinstance(_mapping, list):  # List[str]
            out_args = array
        # create MappedArray / List
        if not isinstance(_mapping, int):
            out = cls(*out_args, _mapping=_mapping, _format=_format, _bitfields=_bitfields, _classes=_classes)
        # TODO: List[MappedArray]
        else:
            out = list(array)  # LAZY HACK?
        return out

    def as_bytes(self) -> bytes:
        return struct.pack(self._format, *self.as_tuple())

    @classmethod
    def as_cpp(cls, _mapping: Any = None, _format: str = None) -> str:  # C++ struct definition
        _format = cls._format if _format is None else _format
        _mapping = cls._mapping if _mapping is None else _mapping
        # TODO: use cls()._attr_formats
        raise NotImplementedError()


class BitField:
    """Maps sub-integer data"""
    _fields: BitFieldMapping = dict()  # must cover entire int type
    _format: str = ""  # 1x uint8/16/32_t
    _classes: ClassesDict = dict()  # good for enum.IntFlags subclasses; bool also accepted

    def __init__(self, *args, _fields: BitFieldMapping = None, _format: str = None, _classes: ClassesDict = None, **kwargs):
        """generate a unique class at runtime, just like MappedArray"""
        self._format = self._format if _format is None else _format
        self._fields = self._fields if _fields is None else _fields
        self._classes = self._classes if _classes is None else _classes
        # TODO: automatically make 1-bit fields bool?
        # valid specification
        if not (self._format in "BHI" and len(self._format) == 1):  # pls no
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
        # TODO: check for invalid kwargs
        for attr, size in _fields.items():
            setattr(self, attr, values[attr])

    def __repr__(self) -> str:
        attrs = []
        for attr in self._fields.keys():
            attrs.append(f"{attr}: {getattr(self, attr)}")
        return f"<{self.__class__.__name__} ({', '.join(attrs)})>"

    def __setattr__(self, attr, value):  # NOTE: private variables must pass through untouched
        if attr in self._fields:
            assert isinstance(value, int)
            if value < 0:
                raise NotImplementedError("Negative values in bitfields not yet supported")
            limit = 2 ** self._fields[attr] - 1
            if value > limit:
                raise OverflowError(f"{attr} is out of range! (max allowed value = {limit})")
            value = handle_child_class(self, attr, value)
        super().__setattr__(attr, value)

    @classmethod
    def from_int(cls, value: int, _fields: BitFieldMapping = None, _format: str = None,
                 _classes: ClassesDict = None) -> BitField:
        out_fields = cls._fields if _fields is None else _fields
        out_format = cls._format if _format is None else _format
        out_classes = cls._classes if _classes is None else _classes
        out_args = list()
        offset = 0
        for size in out_fields.values():
            mask = 2 ** size - 1 << offset
            out_args.append((value & mask) >> offset)
            offset += size
        return cls(*out_args, _format=out_format, _fields=out_fields, _classes=out_classes)

    def as_int(self) -> int:
        out = 0
        offset = 0
        for attr, size in self._fields.items():
            out += getattr(self, attr) << offset  # __setattr__ prevents overflow
            offset += size
        return out


def handle_child_class(parent: Union[Struct, MappedArray, BitField], attr: str, value: Any) -> Any:
    """convert value into appropriate class, if nessecary"""
    if attr in parent._classes:
        child_class = parent._classes[attr]
        if not isinstance(value, child_class):
            if isinstance(value, Iterable):
                value = child_class(*value)
            else:
                value = child_class(value)
    return value


def dict_subgroup(dict_: Dict[str, Any], group: str) -> Dict[str, Any]:
    """{'attr.sub': ...}, 'attr' -> {'sub': ...}"""
    return {k.partition(".")[-1]: v for k, v in dict_.items() if "." in k and k.partition(".")[0] == group}


# for Struct: mapping_length({s: Struct._arrays.get(s, None) for s in Struct.__slots__})
def mapping_length(mapping: AttrMap) -> int:  # MappedArray._mapping focused
    """counts length of tuple required for mapping"""
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


def split_format(_format: str) -> List[str]:
    """split a struct format string to zip with tuple"""
    # NOTE: strings returned as f"{count}s" (untouched)
    # FIXME: does not check to see if format is valid! invalid chars are thrown out silently
    _format = re.findall(r"[0-9]*[xcbB\?hHiIlLqQnNefgdspP]", _format.replace(" ", ""))
    out = list()
    for f in _format:
        match_numbered = re.match(r"([0-9]+)([xcbB\?hHiIlLqQnNefgdpP])", f)  # NOTE: does not decompress strings
        if match_numbered is not None:
            count, f = match_numbered.groups()
            out.extend(f * int(count))
        else:
            out.append(f)
    return out


# NOTE: C: #include <stdint.h>; C++: #include <cstdint.h>
type_LUT = {"c": "char",    "?": "bool",
            "b": "int8_t",  "B": "uint8_t",
            "h": "int16_t", "H": "uint16_t",
            "i": "int32_t", "I": "uint32_t",
            "f": "float",   "g": "double"}
# NOTE: can't detect strings with a dict
# -- to catch strings: type_defaults[t] if not t.endswith("s") else ...
# TODO: make a function to lookup type and check / trim string sizes
# -- a trim / warn / fail setting would be ideal

type_defaults = {"c": b"", "?": False,
                 "b": 0, "B": 0,
                 "h": 0, "H": 0,
                 "i": 0, "I": 0,
                 "f": 0.0, "g": 0.0,
                 "s": ""}
