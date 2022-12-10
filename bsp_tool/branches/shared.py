import io
import math
import re
import zipfile
from typing import Dict, List


# TODO: move current special class __init__ to a .from_bytes() method
# TODO: all SpecialLumpClass __init__ methods should create an empty mutable object
# -- this empty object should be able to be populated and saved to a file
# -- end goal is to create a .bsp without touching any bytes / files


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
    # TODO: match "classname" to python classes (optional)
    # -- use fgd-tools?
    # TODO: use a true __init__ & .from_bytes() @classmethod
    def __init__(self, raw_entities: bytes):
        entities: List[Dict[str, str]] = list()
        # ^ [{"key": "value"}]
        # TODO: handle newlines in keys / values
        enumerated_lines = enumerate(raw_entities.decode(errors="ignore").splitlines())
        for line_no, line in enumerated_lines:
            if re.match(r"^\s*$", line):  # line is blank / whitespace
                continue
            if "{" in line:  # new entity
                ent = dict()
            elif '"' in line:
                key_value_pair = re.search(r'"([^"]*)"\s"([^"]*)"', line)
                if not key_value_pair:
                    # TODO: "key" 'value"
                    # NOTE: DDayNormany-mappack mtownbh L18 opens w/ `'` & closes w/ `"`
                    # -- this seems illegal but the map runs without complaint
                    # multi-line value
                    open_key_value_pair = re.search(r'"([^"]*)"\s"([^"]*)', line)
                    if open_key_value_pair is None:
                        raise RuntimeError(f"Unexpected line in entities: L{line_no}: {line.encode()}")
                    key, value = open_key_value_pair.groups()
                    # TODO: use regex to catch CRLF line endings & unexpected whitespace
                    tail = re.search(r'([^"]*)"\s*$', line)
                    while not tail:  # keep grabbing lines until the end of the value
                        if "{" in line or "}" in line:
                            RuntimeError(f"Unexpected line in entities: L{line_no}: {line.encode()}")
                        line_no, line = next(enumerated_lines)
                        # NOTE: ^ might've broken line numbers?
                        value += line
                        tail = re.search(r'([^"]*)"\s*$', line)
                    value += tail.groups()[0]
                    continue
                key, value = key_value_pair.groups()
                if key not in ent:
                    ent[key] = value
                else:  # don't override duplicate keys, share a list instead
                    # generally duplicate keys are ouputs
                    if isinstance(ent[key], list):  # more than 2 of this key
                        ent[key].append(value)
                    else:  # second occurance of key
                        ent[key] = [ent[key], value]
            elif "}" in line:  # close entity
                entities.append(ent)
            elif line.strip() == b"\x00".decode():  # ignore null bytes
                continue
            elif line.startswith("//"):  # ignore comments
                continue  # TODO: preserve comments
            else:
                raise RuntimeError(f"Unexpected line in entities: L{line_no}: {line.encode()}")
            super().__init__(entities)

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


class PakFile(zipfile.ZipFile):
    _buffer: io.BytesIO

    def __init__(self, raw_zip: bytes):
        self._buffer = io.BytesIO(raw_zip)
        super(PakFile, self).__init__(self._buffer)

    def as_bytes(self) -> bytes:
        return self._buffer.getvalue()


class TextureDataStringData(list):
    def __init__(self, raw_texture_data_string_data: bytes):
        super().__init__([t.decode("ascii", errors="ignore") for t in raw_texture_data_string_data[:-1].split(b"\0")])

    # TODO: use regex to search
    # def find(self, pattern: str) -> List[str]:
    #     pattern = pattern.lower()
    #     return fnmatch.filter(map(str.lower, self), f"*{pattern}*")

    def as_bytes(self) -> bytes:
        return b"\0".join([t.encode("ascii") for t in self]) + b"\0"


# methods
def worldspawn_volume(bsp):
    """allows for sorting maps by size"""
    worldspawn = bsp.ENTITIES[0]
    maxs = map(float, worldspawn["world_maxs"].split())
    mins = map(float, worldspawn["world_mins"].split())
    return math.sqrt(sum([(b - a) ** 2 for a, b in zip(mins, maxs)]))
