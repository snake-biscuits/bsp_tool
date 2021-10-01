import collections
import enum
import io
import itertools
import math
import re
import struct
import zipfile
from typing import Dict, List


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


# flag enums
class SPRP_flags(enum.IntFlag):
    FADES = 0x1  # use fade distances
    USE_LIGHTING_ORIGIN = 0x2
    NO_DRAW = 0x4    # computed at run time based on dx level
    # the following are set in a level editor:
    IGNORE_NORMALS = 0x8
    NO_SHADOW = 0x10
    SCREEN_SPACE_FADE = 0x20
    # next 3 are for lighting compiler
    NO_PER_VERTEX_LIGHTING = 0x40
    NO_SELF_SHADOWING = 0x80
    NO_PER_TEXEL_LIGHTING = 0x100
    EDITOR_MASK = 0x1D8


# Basic Lump Classes
class Ints(int):
    _format = "i"


class Shorts(int):
    _format = "h"


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
        for line_no, line in enumerate(raw_entities.decode(errors="ignore").splitlines()):
            if re.match(r"^\s*$", line):  # line is blank / whitespace
                continue
            if "{" in line:  # new entity
                ent = dict()
            elif '"' in line:
                key_value_pair = re.search(r'"([^"]*)"\s"([^"]*)"', line)
                if not key_value_pair:
                    print(f"ERROR LOADING ENTITIES: Line {line_no:05d}:  {line}")
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


class GameLump_SPRP:  # Mostly for Source
    def __init__(self, raw_sprp_lump: bytes, StaticPropClass: object):
        """Get StaticPropClass from GameLump version"""
        # # lambda raw_lump: GameLump_SPRP(raw_lump, StaticPropvXX)
        sprp_lump = io.BytesIO(raw_sprp_lump)
        model_name_count = int.from_bytes(sprp_lump.read(4), "little")
        model_names = struct.iter_unpack("128s", sprp_lump.read(128 * model_name_count))
        setattr(self, "model_names", [t[0].replace(b"\0", b"").decode() for t in model_names])
        leaf_count = int.from_bytes(sprp_lump.read(4), "little")
        leaves = itertools.chain(*struct.iter_unpack("H", sprp_lump.read(2 * leaf_count)))
        setattr(self, "leaves", list(leaves))
        prop_count = int.from_bytes(sprp_lump.read(4), "little")
        read_size = struct.calcsize(StaticPropClass._format) * prop_count
        props = struct.iter_unpack(StaticPropClass._format, sprp_lump.read(read_size))
        setattr(self, "props", list(map(StaticPropClass, props)))
        here = sprp_lump.tell()
        end = sprp_lump.seek(0, 2)
        assert here == end, "Had some leftover bytes, bad format"

    def as_bytes(self) -> bytes:
        if len(self.props) > 0:
            prop_format = self.props[0]._format
        else:
            prop_format = ""
        return b"".join([int.to_bytes(len(self.model_names), 4, "little"),
                         *[struct.pack("128s", n) for n in self.model_names],
                         int.to_bytes(len(self.leaves), 4, "little"),
                         *[struct.pack("H", L) for L in self.leaves],
                         int.to_bytes(len(self.props), 4, "little"),
                         *[struct.pack(prop_format, *p.flat()) for p in self.props]])


class PakFile(zipfile.ZipFile):
    def __init__(self, raw_zip: bytes):
        self._buffer = io.BytesIO(raw_zip)
        super(PakFile, self).__init__(self._buffer)

    def as_bytes(self) -> bytes:
        return self._buffer.getvalue()


# PhysicsBlock headers
CollideHeader = collections.namedtuple("swapcollideheader_t", ["id", "version", "model_type"])
# struct swapcollideheader_t { int size, vphysicsID; short version, model_type; };
SurfaceHeader = collections.namedtuple("swapcompactsurfaceheader_t", ["size", "drag_axis_areas", "axis_map_size"])
# struct swapcompactsurfaceheader_t { int surfaceSize; Vector dragAxisAreas; int axisMapSize; };
MoppHeader = collections.namedtuple("swapmoppsurfaceheader_t", ["size"])
# struct swapmoppsurfaceheader_t { int moppSize; };


class PhysicsBlock:  # TODO: actually process this data
    # byte swapper: https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/utils/common/bsplib.cpp#L1677
    def __init__(self, raw_lump: bytes):
        """Editting not yet supported"""
        self._raw = raw_lump
        lump = io.BytesIO(raw_lump)
        header = CollideHeader(*struct.unpack("4s2h", lump.read(8)))
        assert header.id == b"VPHY", "if 'YHPV' byte order is flipped"
        # version isn't checked by the byteswap, probably important for VPHYSICS
        if header.model_type == 0:
            size, *drag_axis_areas, axis_map_size = struct.unpack("i3fi", lump.read(20))
            surface_header = SurfaceHeader(size, drag_axis_areas, axis_map_size)
        elif header.model_type == 1:
            surface_header = MoppHeader(*struct.unpack("i", lump.read(4)))
        else:
            raise RuntimeError("Invalid model type")
        self.header = (header, surface_header)
        self.data = lump.read(surface_header.size)
        assert lump.tell() == len(raw_lump)

    def as_bytes(self) -> bytes:
        header, surface_header = self.header
        if header.model_type == 0:
            size, drag_axis_areas, axis_map_size = surface_header
            surface_header = struct.pack("i3fi", len(self.data), *drag_axis_areas, axis_map_size)
        elif header.model_type == 1:
            surface_header = struct.pack("i", len(self.data))
        else:
            raise RuntimeError("Invalid model type")
        header = struct.pack("4s2h", *header)
        return b"".join([header, surface_header, self.data])


# PhysicsCollide headers
PhysicsHeader = collections.namedtuple("dphysmodel_t", ["model", "data_size", "script_size", "solid_count"])
# struct dphysmodel_t { int model_index, data_size, keydata_size, solid_count; };


class PhysicsCollide(list):
    """[model_index: int, solids: List[bytes], script: bytes]"""
    # passed to VCollideLoad in vphysics.dll
    def __init__(self, raw_lump: bytes):
        collision_models = list()
        lump = io.BytesIO(raw_lump)
        header = PhysicsHeader(*struct.unpack("4i", lump.read(16)))
        while header != PhysicsHeader(-1, -1, 0, 0) and lump.tell() != len(raw_lump):
            solids = list()
            for i in range(header.solid_count):
                # CPhysCollisionEntry->WriteCollisionBinary
                cb_size = int.from_bytes(lump.read(4), "little")
                solids.append(PhysicsBlock(lump.read(cb_size)))
            # TODO: assert header.data_size bytes were read
            script = lump.read(header.script_size)  # ascii
            collision_models.append([header.model, solids, script])
            header = PhysicsHeader(*struct.unpack("4i", lump.read(16)))
        assert header == PhysicsHeader(-1, -1, 0, 0), "PhysicsCollide ended incorrectly"
        super().__init__(collision_models)

    def as_bytes(self) -> bytes:
        def phy_bytes(collision_model):
            model_index, solids, script = collision_model
            phy_blocks = list()
            for phy_block in solids:
                collision_data = phy_block.as_bytes()
                phy_blocks.append(len(collision_data).to_bytes(4, "little"))
                phy_blocks.append(collision_data)
            phy_block_bytes = b"".join(phy_blocks)
            header = struct.pack("4i", model_index, len(phy_block_bytes), len(script), len(solids))
            return b"".join([header, phy_block_bytes, script])
        tail = struct.pack("4i", -1, -1, 0, 0)
        return b"".join([*map(phy_bytes, self), tail])


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
