"""Base classes for defining .bsp lump structs"""
from typing import Any, Dict, Iterable, List, Union


class Struct:
    """base class for tuple <-> class conversion
    bytes <-> tuple conversion is handled by the struct module"""
    __slots__: List[str] = list()  # names of atributes, in order
    _format: str = str()  # struct module format string
    _arrays: Dict[str, Any] = dict()  # slots to be mapped into MappedArrays
    # each value in _arrays is a mapping to generate a MappedArray from

    def __init__(self, _tuple):
        # _tuple comes from: struct.unpack(self._format, bytes)
        # usually from struct.iter_unpack(self._format, RAW_LUMP)
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
                    length = 0  # count up the total size of the dict
                    for part in array_map.values():
                        if isinstance(part, list):
                            length += len(part)
                        elif isinstance(part, int):
                            length += part
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


class MappedArray:
    """Maps a given iterable to a series of names, can even be a nested mapping"""
    _mapping: Union[List[str], Dict[str, Any]] = [*"xyz"]
    # _mapping cane be either a list of attr names to map a given array to,
    # or, a dict containing a list of attr names, or another dict
    # this second form is difficult to express as a type hint

    def __init__(self, array: Iterable, mapping: Any = _mapping):
        if isinstance(mapping, dict):
            self._mapping = list(mapping.keys())
            array_index = 0
            for attr, child_mapping in mapping.items():
                if child_mapping is not None:
                    segment = array[array_index:array_index + len(child_mapping)]
                    array_index += len(child_mapping)
                    child = MappedArray(segment, mapping=child_mapping)
                    # ^ will recurse again if child_mapping is a dict
                else:
                    segment = array[array_index:array_index + 1]
                    array_index += 1
                    child = segment  # if {"attr": None}  treat as a list entry
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

    def __iter__(self) -> Iterable:
        return iter([getattr(self, attr) for attr in self._mapping])

    def __repr__(self) -> str:
        out = []
        for attr, value in zip(self._mapping, self):
            out.append(f"{attr}: {value}")
        return f"<{self.__class__.__name__} ({', '.join(out)})>"

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
