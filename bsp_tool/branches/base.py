"""Base classes for defining .bsp lump structs"""
from __future__ import annotations
import struct
from typing import Any, Dict, Iterable, List, Union


class Struct:
    """base class for tuple <-> class conversion
    bytes <-> tuple conversion is handled by the struct module"""
    __slots__: List[str] = list()  # names of atributes, in order
    _format: str = str()  # struct module format string
    _arrays: Dict[str, Any] = dict()  # slots to be mapped into MappedArrays
    # each value in _arrays is a mapping to generate a MappedArray from

    def __init__(self, _tuple: Iterable):
        """_tuple comes from: struct.unpack(self._format, bytes)"""
        # TODO: get defaults (nested values in tuples?)
        # *args = [a, b, (c, d)]  # etc. [not .from_tuple()]
        # **kwargs = {"attr": 0}  # use defaults for absent attrs
        # warn if missing defaults when using kwargs
        _tuple_index = 0
        for attr in self.__slots__:
            if attr not in self._arrays:
                value = _tuple[_tuple_index]
                length = 1
            else:
                array_map = self._arrays[attr]
                if isinstance(array_map, list):  # array_map: List[str]
                    length = len(array_map)
                    array = _tuple[_tuple_index:_tuple_index + length]
                    value = MappedArray(array, mapping=array_map)
                elif isinstance(array_map, dict):  # array_map: Dict[str, List[str]]
                    length = mapping_length(array_map)
                    array = _tuple[_tuple_index:_tuple_index + length]
                    value = MappedArray(array, mapping=array_map)  # nested
                elif isinstance(array_map, int):
                    length = array_map
                    value = _tuple[_tuple_index:_tuple_index + length]
                else:
                    raise RuntimeError(f"{type(array_map)} {array_map} in {self.__class__.__name__}._arrays")
            setattr(self, attr, value)
            _tuple_index += length
        # TODO: throw a warning if the whole tuple won't fit
        # report len(_tuple) & struct.calcsize(self._format)

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

    # convertors
    @classmethod
    def from_bytes(cls, _bytes: bytes) -> Struct:
        assert len(_bytes) == struct.calcsize(cls.format)
        _tuple = struct.unpack(cls._format, _bytes)
        # TODO: get mapping_length of __slots__ (convert to dict, None is special case so using get is messy)
        # _arrays = getattr(cls, _arrays, dict())
        # expected_length = len(__slots__) + mapping_length(_arrays) - len(_arrays)
        # TODO: ^ test
        return cls.from_tuple(_tuple)

    @classmethod
    def from_tuple(cls, _tuple: List[Any]) -> Struct:
        # TODO: move __init__ here
        raise NotImplementedError()

    def as_bytes(self) -> bytes:
        return struct.pack(self._format, *self.flat())

    @classmethod
    def as_cpp(self) -> str:  # C++ struct definition
        # TODO: move py_struct_as_cpp here, or import & map
        raise NotImplementedError()


# TODO: mapping_length of Struct
def mapping_length(mapping: Dict[str, Any]) -> int:
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

    def __init__(self, array: Iterable, mapping: Any = None):
        # TODO: get defaults (nested values in tuples?)
        # *args = [a, b, (c, d)]  # etc. [not .from_tuple()]
        # **kwargs = {"attr": 0}  # use defaults for absent attrs
        # warn if missing defaults when using kwargs
        if mapping is None:
            mapping = self._mapping  # hack to use a default
        if isinstance(mapping, dict):
            self._mapping = list(mapping.keys())
            array_index = 0
            for attr, child_mapping in mapping.items():
                # TODO: child_mapping of type int takes a slice, storing a mutable list
                if child_mapping is not None:
                    segment = array[array_index:array_index + mapping_length({None: child_mapping})]
                    array_index += len(child_mapping)
                    child = MappedArray(segment, mapping=child_mapping)  # will recurse again if child_mapping is a dict
                else:  # if {"attr": None}
                    array_index += 1
                    child = array[array_index]  # take a single item, not a slice
                setattr(self, attr, child)
        elif isinstance(mapping, list):  # List[str]
            for attr, value in zip(mapping, array):
                setattr(self, attr, value)
            self._mapping = mapping
        else:
            raise RuntimeError(f"Unexpected mapping: {type(mapping)}")

    def __eq__(self, other: Iterable) -> bool:
        return all([(a == b) for a, b in zip(self, other)])

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

    # convertors
    @classmethod
    def from_bytes(cls, _bytes: bytes) -> MappedArray:
        assert len(_bytes) == struct.calcsize(cls.format)
        _tuple = struct.unpack(cls._format, _bytes)
        assert len(_tuple) == mapping_length(cls._mapping)
        return cls.from_tuple(_tuple)

    @classmethod
    def from_tuple(cls, _tuple: List[Any]) -> MappedArray:
        # TODO: move __init__ here
        raise NotImplementedError()

    def as_bytes(self) -> bytes:
        return struct.pack(self._format, *self.flat())

    @classmethod
    def as_cpp(self) -> str:  # C++ struct definition
        # TODO: move py_struct_as_cpp here, or import & map
        raise NotImplementedError()
