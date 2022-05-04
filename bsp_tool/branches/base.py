"""Base classes for defining .bsp lump structs"""
from __future__ import annotations
import io
import re
import struct
from typing import Any, Dict, Iterable, List, Union


# TODO: _decode: Dict[str, BytesDecodeArgs] class variable for both Struct & MappedArray
# ^ BytesDecodeArgs = Dict[str, str]
# ^^ {"encoding": "utf-8", "errors": "strict"} -> bytes(...).decode(encoding="utf-8", errors="strict")
# TODO: LumpClass(**{"attr.sub": value}) & MappedArray(**{"attr.sub": value})
# TODO: _subclass: Dict[str, Any] class variable for both Struct & MappedArray
# ^ {"attr": SubClass, "attr2.sub": SubClass}
# child_MappedArray = ...; SubClass.__init__(child_MappedArray)
# allows for nesting vector.Vec3 in Structs
# would need to be reversable into bytes in a standardised way; struct.pack(_format, *subclass_instance) ?
# TODO: bitfields (split & rejoin)
# TODO: {int: Mapping} mappings (list of MappedArray)
# -- e.g. {"triangle": {3: Vertex}}

class Struct:
    """base class for tuple <-> class conversion
    bytes <-> tuple conversion is handled by the struct module"""
    __slots__: List[str] = list()  # names of atributes, in order
    # NOTE: since we are using __slots__, defaults cannot be set as class variables
    # -- override the _defaults() classmethod instead (use super & modify the returned dict)
    _format: str = str()  # struct module format string
    _arrays: Dict[str, Any] = dict()  # slots to be mapped into MappedArrays
    # each value in _arrays is a mapping to generate a MappedArray from
    # TODO: _child_subclasses: dict[str, Any]
    # e.g. {"plane.normal": vector.Vec3}
    # source.DisplacementInfo desperately needs this

    def __init__(self, *args, **kwargs):
        # LumpClass(attr1, [attr2_1, attr2_2])
        # LumpClass(attr1, attr2=[attr2_1, attr2_2])
        # NOTE: can only set top-level value, no partial init of nested attr via kwargs (yet)
        # UNLESS: LumpClass(attr3=MappedArray(x=value, _mapping=LumpClass._arrays["attr3"])
        # BETTER: LumpClass(attr3_x=value)  # parse kwarg as attr3.x & generate attr3 MappedArray (expensive!)
        # BEST: LumpClass(**{"attr3.x": value})  # no chance of overlapping attr names
        assert len(args) <= len(self.__slots__), "Too many arguments! Should match top level attributes!"
        invalid_kwargs = set(kwargs).difference(set(self.__slots__))
        # TODO: could branch here and check for subattr kwargs
        assert len(invalid_kwargs) == 0, f"Invalid kwargs: {invalid_kwargs}"
        if len(args) == len(self.__slots__):  # cheeky recursion avoider
            default_values = dict()
        # NOTE: could also skip generating defaults if arg + kwargs defines the whole struct
        # -- however that's probably more work to detect than could be saved so \_(0.0)_/
        else:
            default_values = self._defaults()
            # ^ {"attr": value}
        default_values.update(dict(zip(self.__slots__, args)))
        default_values.update(kwargs)
        parsed = dict()
        types = split_format(self._format)
        for attr, value in default_values.items():
            if attr not in self._arrays:
                setattr(self, attr, value)
                continue
            mapping = self._arrays[attr]
            if isinstance(value, MappedArray):
                # TODO: the mappings don't quite match?
                # value._mapping seems to only be the top level? so == wont work on nested MappedArrays...
                assert value._mapping == mapping
                setattr(self, attr, value)
            elif isinstance(mapping, int):
                assert len(value) == mapping
                setattr(self, attr, value)
            elif isinstance(mapping, (list, dict)):
                start = mapping_length(parsed)
                length = mapping_length({None: self._arrays.get(attr)})
                child_format = "".join(types[start:start + length])
                if isinstance(mapping, dict):
                    if all([isinstance(k, int) for k in mapping]) and [*mapping] == [*range(max(mapping) + 1)]:
                        setattr(self, attr, list())
                        sub_start = start
                        sub_start_0 = 0
                        for index in mapping:
                            sub_mapping = mapping[index]
                            sub_length = mapping_length({None: sub_mapping})
                            sub_format = "".join(types[sub_start:sub_start + sub_length])
                            sub_end = sub_start_0 + sub_length
                            getattr(self, attr)[index] = MappedArray.from_tuple(value[sub_start_0:sub_end],
                                                                                _format=sub_format,
                                                                                _mapping=sub_mapping)
                            sub_start += sub_length
                            sub_start_0 += sub_length
                        continue
                setattr(self, attr, MappedArray.from_tuple(value, _format=child_format, _mapping=mapping))
            else:
                raise RuntimeError(f"{self.__class__.__name__} has bad _arrays!")
            parsed[attr] = self._arrays.get(attr)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        else:
            return self.flat() == other.flat()

    def __hash__(self):
        return hash(tuple(self.flat()))

    def __iter__(self) -> Iterable:
        return iter([getattr(self, attr) for attr in self.__slots__])

    def __repr__(self) -> str:
        components = {s: getattr(self, s) for s in self.__slots__}
        return f"<{self.__class__.__name__} {components}>"

    def flat(self) -> list:
        """recreates the _tuple this instance was initialised from"""
        _tuple = []
        for slot in self.__slots__:
            value = getattr(self, slot)
            if isinstance(value, MappedArray):
                _tuple.extend(value.flat())
            elif isinstance(value, Iterable):
                _tuple.extend(value)
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
                    value = MappedArray.from_tuple(array, _mapping=child_mapping, _format=child_format)
                elif isinstance(child_mapping, int):
                    length = child_mapping
                    value = _tuple[_tuple_index:_tuple_index + length]
                else:
                    raise RuntimeError(f"Invalid type: {type(child_mapping)} in {cls.__class__.__name__}._arrays")
            out_args.append(value)
            _tuple_index += length
        return cls(*out_args)

    def as_bytes(self) -> bytes:
        return struct.pack(self._format, *self.flat())

    @classmethod
    def as_cpp(self) -> str:  # C++ struct definition
        # TODO: move py_struct_as_cpp here, or import & map
        raise NotImplementedError()


# mapping_length of Struct = mapping)length({s: Struct._arrays.get(s) for s in Struct.__slots__})
def mapping_length(mapping: Union[List[str], Dict[str, Any], None]) -> int:
    if isinstance(mapping, list):
        return len(mapping)
    length = 0
    for child_mapping in mapping.values():
        if isinstance(child_mapping, list):
            length += len(child_mapping)
        elif isinstance(child_mapping, int):
            length += child_mapping
        elif isinstance(child_mapping, dict):
            length += mapping_length(child_mapping)
        elif child_mapping is None:
            length += 1
        else:
            raise RuntimeError(f"Unexpexted Mapping! ({mapping}, {child_mapping})")
    return length


class MappedArray:
    """Maps a given iterable to a series of names, can even be a nested mapping"""
    _format: str = ""
    _mapping: Union[List[str], Dict[str, Any]] = []
    # _mapping cane be either a list of attr names to map a given array to,
    # or, a dict containing a list of attr names, or another dict
    # this second form is difficult to express as a type hint

    # TODO: test subclass definitions (MappedArray, vector.Vec3)

    def __init__(self, *args, _mapping: Any = None, _format: str = None, **kwargs):
        if _format is None:
            _format = self._format
        self._format = _format
        if _mapping is None:
            _mapping = self._mapping
        self._mapping = _mapping
        assert len(args) <= len(_mapping), "Too many arguments! Should match top level attributes!"
        # NOTE: _mapping & _format might be passed in as regular args
        # TODO: check to see if _mapping or _mapping, _format are on the tail of args
        invalid_kwargs = set(kwargs).difference(set(_mapping))
        # TODO: could branch here and check for subattr kwargs; e.g. "x.i"
        assert len(invalid_kwargs) == 0, f"Invalid kwargs: {invalid_kwargs}"
        if len(args) == len(_mapping):  # cheeky recursion avoider
            default_values = dict()
        # NOTE: could also skip generating defaults if arg + kwargs defines the whole struct
        # -- however that's probably more work to detect than could be saved so \_(0.0)_/
        else:
            default_values = self._defaults(_mapping=_mapping, _format=_format)
            # ^ {"attr": value}
        default_values.update(dict(zip(_mapping, args)))
        default_values.update(kwargs)
        if isinstance(_mapping, list):
            for attr, value in default_values.items():
                setattr(self, attr, value)
            return
        for attr, value in default_values.items():
            child_mapping = _mapping[attr]
            if isinstance(value, MappedArray):
                assert isinstance(child_mapping, (list, dict)), f"Invalid child_mapping for {attr}: {child_mapping}"
                assert value._mapping == child_mapping  # depth doesn't match?
                # TODO: if attr is an integer, we're making a list of MappedArrays
                setattr(self, attr, value)
            elif isinstance(child_mapping, int):
                assert len(value) == child_mapping
                setattr(self, attr, value)
            elif isinstance(child_mapping, (list, dict)):
                setattr(self, attr, MappedArray.from_tuple(value, _mapping=child_mapping))
            elif child_mapping is None:
                setattr(self, attr, value)
            else:
                raise RuntimeError(f"{self.__class__.__name__} has bad _mapping")

    def __eq__(self, other: Iterable) -> bool:
        return all([(a == b) for a, b in zip(self, other)])

    # TODO: __getattr__ swizzle detection (if and only if mapping is a list of single chars)

    def __getitem__(self, index: str) -> Any:
        return getattr(self, self._mapping[index])

    def __hash__(self):
        return hash(tuple(self.flat()))

    def __iter__(self) -> Iterable:
        return iter([getattr(self, attr) for attr in self._mapping])

    def __repr__(self) -> str:
        attrs = []
        for attr, value in zip(self._mapping, self):
            attrs.append(f"{attr}: {value}")
        return f"<{self.__class__.__name__} ({', '.join(attrs)})>"

    def flat(self) -> list:
        """recreates the array this instance was generated from"""
        array = []
        for attr in self._mapping:
            value = getattr(self, attr)
            if isinstance(value, MappedArray):
                array.extend(value.flat())  # recursive call
            elif isinstance(value, list):
                array.extend(value)
            else:
                array.append(value)
        return array

    @classmethod
    def _defaults(cls, _mapping: Any = None, _format: str = None) -> Dict[str, Any]:
        if _format is None:
            _format = cls._format
        if _mapping is None:
            _mapping = cls._mapping
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
    def from_bytes(cls, _bytes: bytes, _mapping: Any = None, _format: str = None) -> MappedArray:
        if _format is None:
            _format = cls._format
        if _mapping is None:
            _mapping = cls._mapping
        assert len(_bytes) == struct.calcsize(_format)
        _tuple = struct.unpack(_format, _bytes)
        assert len(_tuple) == mapping_length(_mapping), f"{_tuple}"
        return cls.from_tuple(_tuple, _mapping=_mapping, _format=_format)

    @classmethod
    def from_stream(cls, stream: io.BytesIO, _mapping: Any = None, _format: str = None) -> MappedArray:
        return cls.from_bytes(stream.read(struct.calcsize(cls._format)), _mapping, _format)

    @classmethod
    def from_tuple(cls, array: Iterable, _mapping: Any = None, _format: str = None) -> MappedArray:
        if _format is None:
            _format = cls._format
        if _mapping is None:
            _mapping = cls._mapping
        assert len(array) == mapping_length({None: _mapping}), f"{cls.__name__}({array}, _mapping={_mapping})"
        out_args = list()
        if not isinstance(_mapping, (dict, list, int)):
            raise RuntimeError(f"Unexpected mapping: {type(_mapping)}")
        elif isinstance(_mapping, dict):
            types = split_format(_format)
            array_index = 0
            for child_mapping in _mapping.values():
                # TODO: child_mapping of type int takes a slice, storing a mutable list
                if child_mapping is not None:
                    length = mapping_length({None: child_mapping})
                    segment = array[array_index:array_index + length]
                    child_format = "".join(types[array_index:array_index + length])
                    array_index += mapping_length({None: child_mapping})
                    child = MappedArray.from_tuple(segment, _mapping=child_mapping, _format=child_format)
                    # NOTE: ^ will recurse again if child_mapping is a dict
                else:  # if {"attr": None}
                    child = array[array_index]  # take a single item, not a slice
                    array_index += 1
                out_args.append(child)
        elif isinstance(_mapping, list):  # List[str]
            out_args = array
        if not isinstance(_mapping, int):
            out = cls(*out_args, _mapping=_mapping, _format=_format)
        else:
            out = list(array)  # LAZY HACK?
        return out

    def as_bytes(self) -> bytes:
        return struct.pack(self._format, *self.flat())

    @classmethod
    def as_cpp(cls, _mapping: Any = None, _format: str = None) -> str:  # C++ struct definition
        if _format is None:
            _format = cls._format
        if _mapping is None:
            _mapping = cls._mapping
        types = split_format(_format)
        assert mapping_length(_mapping) == len(types), "Invalid mapping for format!"
        raise NotImplementedError()
        # out = list()
        # out.append("struct {cls.__name__}" + "{\n")
        # if isinstance(cls._mapping, dict):
        #     i = 0
        #     for attr, attr_mapping in cls._mapping.item():
        #         if child_mapping is None:
        #             type_char = types[i]
        #             i += 1
        # elif isinstance(cls._mapping, list):
        #     for type_char, attr in zip(split_format(_format), cls._mapping):
        #         out.append(f"\t{type_LUT[type_char]} {attr}\n")
        # else:
        #     raise RuntimeError(f"Invalid _mapping type: {type(cls._mapping)}")
        # out.append("};\n")


def split_format(_format: str) -> List[str]:
    """split a struct format string to zip with tuple"""
    # NOTE: strings returned as r"/d+s"
    # FIXME: does not check to see if format is valid! invalid chars are thrown out silently
    _format = re.findall(r"[0-9]*[xcbB\?hHiIlLqQnNefgdspP]", _format.replace(" ", ""))
    out = list()
    for f in _format:
        match_numbered = re.match(r"([0-9]+)([xcbB\?hHiIlLqQnNefgdpP])", f)
        # NOTE: does not decompress strings
        if match_numbered is not None:
            count, f = match_numbered.groups()
            out.extend(f * int(count))
        else:
            out.append(f)
    return out


type_LUT = {"c": "char",  "?": "bool",
            "b": "char",  "B": "unsigned char",
            "h": "short", "H": "unsigned short",
            "i": "int",   "I": "unsigned int",
            "f": "float", "g": "double"}
# NOTE: can't detect strings with a dict
# -- to catch strings: type_defaults[t] if not t.endswith("s") else ""
# TODO: make a function to lookup type and check / trim string sizes
# -- a trim / warn / fail setting would be ideal

type_defaults = {"c": b"", "?": False,
                 "b": 0, "B": 0,
                 "h": 0, "H": 0,
                 "i": 0, "I": 0,
                 "f": 0.0, "g": 0.0,
                 "s": ""}
