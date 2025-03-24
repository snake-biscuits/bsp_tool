from __future__ import annotations
import math
import re
from typing import Dict, List


# Basic Lump Classes
class Bytes(int):
    _format = "b"


class Ints(int):
    _format = "i"


class Floats(float):
    _format = "f"


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

    # TODO: make searches stackable (bsp.search(...).search_any(...))
    # -- search(...) -> Entities
    def search(self, **search: Dict[str, str]) -> List[Dict[str, str]]:
        """Search for entities by key-values; e.g. .search(key=value) -> [{"key": value, ...}, ...]"""
        # NOTE: all conditions must be satisfied
        return [e for e in self if all([e.get(k, "") == v for k, v in search.items()])]

    def search_any(self, **search: Dict[str, str]) -> List[Dict[str, str]]:
        """Search for entities by key-values; e.g. .search(key=value) -> [{"key": value, ...}, ...]"""
        return [e for e in self if any([e.get(k, "") == v for k, v in search.items()])]

    def search_regex(self, **search: Dict[str, str]) -> List[Dict[str, str]]:
        return [e for e in self
                if all([re.match(p, e.get(k, "")) is not None
                        for k, p in search.items()])]

    def search_regex_any(self, **search: Dict[str, str]) -> List[Dict[str, str]]:
        return [e for e in self
                if any([re.match(p, e.get(k, "")) is not None
                        for k, p in search.items()])]

    def as_bytes(self) -> bytes:
        entities = list()
        for entity_dict in self:  # Dict[str, Union[str, List[str]]]
            entity = list()
            for key, value in entity_dict.items():
                if isinstance(value, str):
                    entity.append(f'"{key}" "{value}"')
                elif isinstance(value, list):  # multiple entries
                    entity.extend([f'"{key}" "{v}"' for v in value])
                else:
                    raise RuntimeError("Entity values must be either a string or list of strings")
            entities.append("\n".join(["{", *entity, "}"]).encode("ascii", errors="ignore"))
        return b"\n".join(entities) + b"\n\x00"

    @classmethod
    def from_bytes(cls, raw_lump: bytes) -> Entities:
        entities: List[Dict[str, str]] = list()
        # ^ [{"key": "value"}]
        enumerated_lines = enumerate(raw_lump.decode(errors="ignore").splitlines())
        for line_no, line in enumerated_lines:
            if re.match(r"^\s*$", line) is not None:  # line is blank / whitespace
                continue
            elif re.match(r"^\s*{\s*$", line) is not None:  # new entity
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
                    value = "\n".join([value, tail.groups()[0]])
                else:
                    key, value = key_value_pair.groups()
                if key not in ent:
                    ent[key] = value
                else:  # don't override duplicate keys, share a list instead
                    # generally duplicate keys are outputs (e.g. OnMapSpawn)
                    if isinstance(ent[key], list):  # more than 2 of this key
                        ent[key].append(value)
                    else:  # second occurance of key
                        ent[key] = [ent[key], value]
            elif re.match(r"^\s*}\s*(\x00)?\s*$", line) is not None:  # close entity
                entities.append(ent)
            elif line.strip() == b"\0".decode():  # terminating line
                continue
            elif line.startswith("//"):  # ignore comments
                continue  # TODO: preserve comments
            else:
                raise RuntimeError(f"Unexpected line in entities: L{line_no + 1}: {line.encode()}")
        return cls(entities)


# methods
def worldspawn_volume(bsp):
    """allows for sorting maps by size"""
    worldspawn = bsp.ENTITIES[0]
    maxs = map(float, worldspawn["world_maxs"].split())
    mins = map(float, worldspawn["world_mins"].split())
    return math.sqrt(sum([(b - a) ** 2 for a, b in zip(mins, maxs)]))
