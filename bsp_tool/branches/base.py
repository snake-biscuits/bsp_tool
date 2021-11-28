"""Base classes for defining .bsp lump structs"""
from __future__ import annotations
import re
import struct
from typing import Any, Dict, Iterable, List, Union


class Struct:
    """base class for tuple <-> class conversion
    bytes <-> tuple conversion is handled by the struct module"""
    __slots__: List[str] = list()  # names of atributes, in order
    # NOTE: since we are using __slots__, defaults cannot be set as class variables
    # -- override the _defaults() classmethod instead (use super & modify the returned dict)
    _format: str = str()  # struct module format string
    _arrays: Dict[str, Any] = dict()  # slots to be mapped into MappedArrays
    # each value in _arrays is a mapping to generate a MappedArray from

    def __init__(self, *args, **kwargs):
        # LumpClass(attr1, [attr2_1, attr2_2])
        # LumpClass(attr1, attr2=[attr2_1, attr2_2])
        # NOTE: can only set top-level value, no partial init of nested attr via kwargs (yet)
        # UNLESS: LumpClass(attr3=MappedArray(attr3_x=value, _mapping=LumpClass._arrays["attr3"])
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
                setattr(self, attr, MappedArray.from_tuple(value, _mapping=mapping))
            else:
                raise RuntimeError(f"{self.__class__.__name__} has bad _arrays!")

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
        assert len(_bytes) == struct.calcsize(cls.format)
        _tuple = struct.unpack(cls._format, _bytes)
        expected_length = len(cls.__slots__) + mapping_length(cls._arrays) - len(cls._arrays)
        assert len(_tuple) == expected_length
        # TODO: ^ test
        return cls.from_tuple(_tuple)

    @classmethod
    def from_tuple(cls, _tuple: Iterable) -> Struct:
        """_tuple comes from: struct.unpack(self._format, bytes)"""
        out_args = list()
        _tuple_index = 0
        for attr in cls.__slots__:
            if attr not in cls._arrays:
                value = _tuple[_tuple_index]
                length = 1
            else:
                # partition up children
                array_map = cls._arrays[attr]
                if isinstance(array_map, list):  # array_map: List[str]
                    length = len(array_map)
                    array = _tuple[_tuple_index:_tuple_index + length]
                    value = MappedArray.from_tuple(array, _mapping=array_map)
                elif isinstance(array_map, dict):  # array_map: Dict[str, List[str]]
                    length = mapping_length(array_map)
                    array = _tuple[_tuple_index:_tuple_index + length]
                    value = MappedArray.from_tuple(array, _mapping=array_map)  # nested
                elif isinstance(array_map, int):
                    length = array_map
                    value = _tuple[_tuple_index:_tuple_index + length]
                else:
                    raise RuntimeError(f"{type(array_map)} {array_map} in {cls.__class__.__name__}._arrays")
            out_args.append(value)
            _tuple_index += length
        return cls(*out_args)

    def as_bytes(self) -> bytes:
        return struct.pack(self._format, *self.flat())

    @classmethod
    def as_cpp(self) -> str:  # C++ struct definition
        # TODO: move py_struct_as_cpp here, or import & map
        raise NotImplementedError()


# TODO: mapping_length of Struct
def mapping_length(mapping: Union[List[str], Dict[str, Any], None]) -> int:
    if isinstance(mapping, list):
        return len(mapping)
    length = 0
    for sub_mapping in mapping.values():
        if isinstance(sub_mapping, list):
            length += len(sub_mapping)
        elif isinstance(sub_mapping, int):
            length += sub_mapping
        elif isinstance(sub_mapping, dict):
            length += mapping_length(sub_mapping)
        elif sub_mapping is None:
            length += 1
        else:
            raise RuntimeError(f"Unexpexted Mapping! ({mapping}, {sub_mapping})")
    return length


class MappedArray:
    """Maps a given iterable to a series of names, can even be a nested mapping"""
    _mapping: Union[List[str], Dict[str, Any]] = [*"xyz"]
    # _mapping cane be either a list of attr names to map a given array to,
    # or, a dict containing a list of attr names, or another dict
    # this second form is difficult to express as a type hint
    # TODO: _format inheritace (slicing from parents)

    def __init__(self, *args, _mapping: Any = None, **kwargs):
        if _mapping is None:
            _mapping = self._mapping
        assert len(args) <= len(_mapping), "Too many arguments! Should match top level attributes!"
        invalid_kwargs = set(kwargs).difference(set(_mapping))
        # TODO: could branch here and check for subattr kwargs
        assert len(invalid_kwargs) == 0, f"Invalid kwargs: {invalid_kwargs}"
        # if len(args) == len(_mapping):  # cheeky recursion avoider
        #     default_values = dict()
        # # NOTE: could also skip generating defaults if arg + kwargs defines the whole struct
        # # -- however that's probably more work to detect than could be saved so \_(0.0)_/
        # else:
        #     # TODO: _format as a kwarg for inheritance
        #     default_values = self._defaults(_mapping)
        #     # ^ {"attr": value}
        # default_values.update(dict(zip(_mapping, args)))
        # default_values.update(kwargs)
        # if isinstance(_mapping, list):
        #     for attr, value in default_values.items():
        #         setattr(self, attr, value)
        #         return
        # for attr, value in default_values.items():
        #     sub_mapping = _mapping[attr]
        #     if isinstance(value, MappedArray):
        #         assert isinstance(sub_mapping, (list, dict)), f"Invalid sub_mapping for {attr}: {sub_mapping}"
        #         assert value._mapping == sub_mapping  # depth doesn't match?
        #         setattr(self, attr, value)
        #     elif isinstance(sub_mapping, int):
        #         assert len(value) == sub_mapping
        #         setattr(self, attr, value)
        #     elif isinstance(sub_mapping, (list, dict)):
        #         setattr(self, attr, MappedArray.from_tuple(value, _mapping=sub_mapping))
        #     else:
        #         raise RuntimeError(f"{self.__class__.__name__} has bad _arrays!")

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
            else:
                array.append(value)
        return array

    @classmethod
    def _defaults(cls, _mapping: None) -> Dict[str, Any]:
        # TODO: _format kwarg
        if _mapping is None:
            _mapping = cls._mapping
        if not hasattr(cls._format):
            raise RuntimeError("format unknown, cannot generate defaults")
        types = split_format(cls._format)
        global type_defaults
        defaults = cls.from_tuple([type_defaults[t] if not t.endswith("s") else "" for t in types])
        return dict(zip(list(_mapping), defaults))

    # convertors
    @classmethod
    def from_bytes(cls, _bytes: bytes, _mapping: Any = None, _format: str = None) -> MappedArray:
        if _mapping is None:  # HACK: use class' default _mapping
            _mapping = cls._mapping
        if _format is None:  # HACK: use class' default _format
            _format = cls._format
        assert len(_bytes) == struct.calcsize(_format)
        _tuple = struct.unpack(_format, _bytes)
        assert len(_tuple) == mapping_length(cls._mapping)
        return cls.from_tuple(_tuple)

    @classmethod
    def from_tuple(cls, array: Iterable, _mapping: Any = None) -> MappedArray:
        if _mapping is None:  # HACK: use class' default _mapping
            _mapping = cls._mapping
        assert len(array) == mapping_length(_mapping), f"{cls.__name__}({array}, {_mapping})"
        out = cls()  # new instance
        if not isinstance(_mapping, (dict, list)):
            raise RuntimeError(f"Unexpected mapping: {type(_mapping)}")
        elif isinstance(_mapping, dict):
            array_index = 0
            for attr, child_mapping in _mapping.items():
                # TODO: child_mapping of type int takes a slice, storing a mutable list
                if child_mapping is not None:
                    segment = array[array_index:array_index + mapping_length({None: child_mapping})]
                    array_index += len(child_mapping)
                    child = MappedArray.from_tuple(segment, _mapping=child_mapping)
                    # NOTE: ^ will recurse again if child_mapping is a dict
                else:  # if {"attr": None}
                    array_index += 1
                    child = array[array_index]  # take a single item, not a slice
                setattr(out, attr, child)
        elif isinstance(_mapping, list):  # List[str]
            for attr, value in zip(_mapping, array):
                setattr(out, attr, value)
        out._mapping = _mapping
        return out

    def as_bytes(self) -> bytes:
        return struct.pack(self._format, *self.flat())

    @classmethod
    def as_cpp(cls, _format: str = "") -> str:  # C++ struct definition
        raise NotImplementedError()
        # out = list()
        # out.append("struct {cls.__name__}" + "{\n")
        # if _format == "":
        #     _format = self._format  # can break, parents must pass on _format sliver
        # types =
        # if isinstance(cls._mapping, dict):
        #     type_tuple = split_format(_format)
        #     i = 0
        #     for attr, attr_mapping in cls._mapping.item():
        #         if child_mapping is None:
        #             type_char = type_tuple[i]
        #             i += 1
        # elif isinstance(cls._mapping, list):
        #     for type_char, attr in zip(split_format(_format), cls._mapping):
        #         out.append(f"\t{type_LUT[type_char]} {attr}\n")
        # else:
        #     raise RuntimeError(f"Invalid _mapping type: {type(cls._mapping)}")
        # out.append("};\n")


def split_format(_format: str) -> List[str]:
    """split a struct format string to zip with tuple"""
    # NOTE: srrings returned as r"/d+s"
    _format = re.findall(r"[0-9]*[xcbB\?hHiIlLqQnNefdspP]", _format.replace(" ", ""))
    out = list()
    for f in _format:
        match_numbered = re.match(r"([0-9]+)([xcbB\?hHiIlLqQnNefdpP])", f)
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

type_defaults = {"c": 0, "?": False, "b": 0, "B": 0, "h": 0, "H": 0,
                 "i": 0, "I": 0, "f": 0.0, "g": 0.0, "s": ""}
