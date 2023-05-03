import io
import math
import re
import zipfile
from typing import Any, Dict, List


# Basic Lump Classes
class Bytes(int):
    _format = "b"


class Ints(int):
    _format = "i"


class Shorts(int):
    _format = "h"


class UnsignedBytes(int):
    _format = "b"


class UnsignedInts(int):
    _format = "I"


class UnsignedShort:  # enum.IntFlag base class
    _format = "H"


class UnsignedShorts(int):
    _format = "H"


# Special Lump Classes
class Entities(list):
    def __init__(self, iterable: List[Dict[str, str]] = tuple()):
        super().__init__(iterable)

    def search(self, **search: Dict[str, str]) -> List[Dict[str, str]]:
        """Search for entities by key-values; e.g. .search(key=value) -> [{"key": value, ...}, ...]"""
        # NOTE: all conditions must be satisfied
        return [e for e in self if all([e.get(k, "") == v for k, v in search.items()])]

    # TODO: search_regex

    # TODO: search_any  (any k == v, not all)

    # TODO: search_any_regex

    def as_bytes(self) -> bytes:
        entities = []
        for entity_dict in self:  # Dict[str, Union[str, List[str]]]
            entity = ["{"]
            for key, value in entity_dict.items():
                if isinstance(value, str):
                    entity.append(f'"{key}" "{value}"')
                elif isinstance(value, list):  # multiple entries
                    entity.extend([f'"{key}" "{v}"' for v in value])
                else:
                    raise RuntimeError("Entity values must be")
            entity.append("}")
            entities.append("\n".join(entity))
        return b"\n".join(map(lambda e: e.encode("ascii"), entities)) + b"\n\x00"

    @classmethod
    def from_bytes(cls, raw_lump: bytes):
        entities: List[Dict[str, str]] = list()
        # ^ [{"key": "value"}]
        enumerated_lines = enumerate(raw_lump.decode(errors="ignore").splitlines())
        for line_no, line in enumerated_lines:
            if re.match(r"^\s*$", line):  # line is blank / whitespace
                continue
            elif line.startswith("{"):  # new entity
                ent = dict()
            elif '"' in line:
                key_value_pair = re.search(r'"([^"]*)"\s"([^"]*)"', line)
                # TODO: "key" 'value"
                # -- DDayNormany-mappack mtownbh L18 opens w/ `'` & closes w/ `"`
                # -- this seems illegal but the map runs without complaint
                if key_value_pair is None:  # might be a multi-line value
                    open_key_value_pair = re.search(r'"([^"]*)"\s"([^"]*)', line)
                    if open_key_value_pair is None:
                        raise RuntimeError(f"Unexpected line in entities: L{line_no + 1}: {line.encode()}")
                    key, value = open_key_value_pair.groups()
                    tail = None  # hacky do-while loop
                    while tail is None:  # keep grabbing lines until the end of the value
                        if line.startswith("{") or line.startswith("}"):  # previous value didn't terminate
                            RuntimeError(f"Unexpected line in entities: L{line_no + 1}: {line.encode()}")
                        # grab another line
                        line_no, line = next(enumerated_lines)  # BUG: breaks line_no?
                        tail = re.search(r'([^"]*)"\s*$', line)
                        if tail is None:  # accumulate line
                            value = "\n".join([value, line])
                        print(f">> {value=}, {tail=}")
                    value = "\n".join([value, tail.groups()[0]])
                else:
                    key, value = key_value_pair.groups()
                if key not in ent:
                    ent[key] = value
                else:  # don't override duplicate keys, share a list instead
                    # generally duplicate keys are ouputs
                    if isinstance(ent[key], list):  # more than 2 of this key
                        ent[key].append(value)
                    else:  # second occurance of key
                        ent[key] = [ent[key], value]
            elif line.startswith("}"):  # close entity
                entities.append(ent)
            elif line.strip() == b"\x00".decode():  # ignore null bytes
                continue
            elif line.startswith("//"):  # ignore comments
                continue  # TODO: preserve comments
            else:
                raise RuntimeError(f"Unexpected line in entities: L{line_no + 1}: {line.encode()}")
        return cls(entities)


class PakFile(zipfile.ZipFile):
    _buffer: io.BytesIO

    def __init__(self, file: Any = None):
        """always a read-only copy of the lump"""
        if file is None:
            self._buffer = io.BytesIO(b"")
        elif isinstance(file, io.BytesIO):
            self._buffer = file
        elif isinstance(file, str):
            self._buffer = io.BytesIO(open(file, "rb").read())
        else:
            raise TypeError(f"Cannot create {self.__class__.__name__} from type '{type(file)}'")
        super().__init__(self._buffer, "r")

    def as_bytes(self) -> bytes:
        return self._buffer.getvalue()

    @classmethod
    def from_bytes(cls, raw_lump: bytes):
        return cls(io.BytesIO(raw_lump))


class TextureDataStringData(list):
    def __init__(self, iterable: List[str] = tuple()):
        super().__init__(iterable)

    # TODO: use regex to search
    # def find(self, pattern: str) -> List[str]:
    #     pattern = pattern.lower()
    #     return fnmatch.filter(map(str.lower, self), f"*{pattern}*")

    def as_bytes(self) -> bytes:
        return b"\0".join([t.encode("ascii") for t in self]) + b"\0"

    @classmethod
    def from_bytes(cls, raw_lump: bytes):
        return cls([t.decode("ascii", errors="ignore") for t in raw_lump[:-1].split(b"\0")])


# methods
def worldspawn_volume(bsp):
    """allows for sorting maps by size"""
    worldspawn = bsp.ENTITIES[0]
    maxs = map(float, worldspawn["world_maxs"].split())
    mins = map(float, worldspawn["world_mins"].split())
    return math.sqrt(sum([(b - a) ** 2 for a, b in zip(mins, maxs)]))
