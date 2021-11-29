import io
import math
import re
import struct
import zipfile
from typing import Dict, List

from . import physics  # noqa F401


# TODO: adapt SpecialLumpClasses to be more in-line with lumps.BspLump subclasses
# TODO: make special classes __init__ method create an empty mutable object
# TODO: move current special class __init__ to a .from_bytes() method
# TODO: prototype the system for saving game lumps to file
# -- need to know filesize, but modify the headers of each lump to have file relative offsets
# -- NOTE: fully implemented in RespawnBsp.save_as
# TODO: make a base class for SpecialLumpClasses the facilitates dynamic indexing
# -- use the lumps system to dynamically index a file:
# -- do an initial scan for where each entry begins & have a .read_entry() method
# TODO: consider using __repr__ methods, as SpecialLumpClasses can get large


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


class UnsignedShorts(int):
    _format = "H"


# Special Lump Classes
class Entities(list):
    # TODO: match "classname" to python classes (optional)
    # -- use fgd-tools?
    # TODO: use a true __init__ & .from_bytes() @staticmethod
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
                    open_key_value_pair = re.search(r'"([^"]*)"\s"([^"]*)', line)
                    if not open_key_value_pair:
                        RuntimeError(f"Unexpected line in entities: L{line_no}: {line.encode()}")
                    key, value = open_key_value_pair.groups()
                    # TODO: use regex to catch CRLF line endings & unexpected whitespace
                    tail = re.search(r'([^"]*)"\s*$', line)
                    while not tail:
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
            elif line == b"\x00".decode():  # ignore null bytes
                continue
            elif line.startswith("//"):  # ignore comments
                continue
            else:
                raise RuntimeError(f"Unexpected line in entities: L{line_no}: {line.encode()}")
            super().__init__(entities)

    def search(self, **search: Dict[str, str]) -> List[Dict[str, str]]:
        """.search(classname="light_environment") -> [{"classname": "light_environment", ...}]"""
        # NOTE: exact matches only!
        return [e for e in self if all([e.get(k, "") == v for k, v in search.items()])]

    # TODO: find_regex

    # TODO: find_any  (any k == v, not all)

    # TODO: find_any_regex

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


class Visiblity:
    # seems to be the same across Source & Quake engines
    # is Titanfall (v29) the same?
    def __init__(self, raw_visibility: bytes):
        visibility_data = [v[0] for v in struct.iter_unpack("i", raw_visibility)]
        num_clusters = visibility_data
        for i in range(num_clusters):
            i = (2 * i) + 1
            pvs_offset = visibility_data[i]  # noqa: F841
            pas_offset = visibility_data[i + 1]  # noqa: F841
            # ^ pointers into RLE encoded bits mapping the PVS tree
            # from bytes inside the .bsp file?
        raise NotImplementedError("Understanding of Visibility lump is incomplete")

    def as_bytes(self) -> bytes:
        raise NotImplementedError("Visibility lump hard")


# methods
def worldspawn_volume(bsp):
    """allows for sorting maps by size"""
    worldspawn = bsp.ENTITIES[0]
    maxs = map(float, worldspawn["world_maxs"].split())
    mins = map(float, worldspawn["world_mins"].split())
    return math.sqrt(sum([(b - a) ** 2 for a, b in zip(mins, maxs)]))
