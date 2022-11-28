from __future__ import annotations
import io
import struct
from typing import List

from .. import shared
from .. import x360
from . import titanfall


FILE_MAGIC = b"PSBr"

BSP_VERSION = 29

GAME_PATHS = {"Titanfall": "Titanfall/r1"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = titanfall.LUMP


LumpHeader = x360.make_big_endian(titanfall.LumpHeader)


# classes for lumps, in alphabetical order:
Grid_x360 = x360.make_big_endian(titanfall.Grid)


# classes for special lumps, in alphabetical order:
class GameLump_SPRP_x360(titanfall.GameLump_SPRP):  # sprp GameLump (LUMP 35)
    """use `lambda raw_lump: GameLump_SPRP(raw_lump, StaticPropvXX)` to implement"""
    StaticPropClass: object
    model_names: List[str]
    leaves: List[int]
    unknown_1: int
    unknown_2: int
    props: List[object] | List[bytes]  # List[StaticPropClass]

    def __init__(self, raw_sprp_lump: bytes, StaticPropClass: object):
        self.StaticPropClass = StaticPropClass
        sprp_lump = io.BytesIO(raw_sprp_lump)
        model_name_count = int.from_bytes(sprp_lump.read(4), "big")
        model_names = struct.iter_unpack("128s", sprp_lump.read(128 * model_name_count))
        setattr(self, "model_names", [t[0].replace(b"\0", b"").decode() for t in model_names])
        leaf_count = int.from_bytes(sprp_lump.read(4), "big")  # usually 0
        leaves = list(struct.iter_unpack("H", sprp_lump.read(2 * leaf_count)))
        setattr(self, "leaves", leaves)
        prop_count, unknown_1, unknown_2 = struct.unpack("3i", sprp_lump.read(12))
        self.unknown_1, self.unknown_2 = unknown_1, unknown_2
        # TODO: if StaticPropClass is None: split into appropriate groups of bytes
        read_size = struct.calcsize(StaticPropClass._format) * prop_count
        props = struct.iter_unpack(StaticPropClass._format, sprp_lump.read(read_size))
        setattr(self, "props", list(map(StaticPropClass.from_tuple, props)))

    def as_bytes(self) -> bytes:
        if len(self.props) > 0:
            prop_bytes = [struct.pack(self.StaticPropClass._format, *p.as_tuple()) for p in self.props]
        else:
            prop_bytes = []
        return b"".join([len(self.model_names).to_bytes(4, "big"),
                         *[struct.pack("128s", n.encode("ascii")) for n in self.model_names],
                         len(self.leaves).to_bytes(4, "big"),
                         *[struct.pack("H", L) for L in self.leaves],
                         struct.pack("3I", len(self.props), self.unknown_1, self.unknown_2),
                         *prop_bytes])


StaticPropv12_x360 = x360.make_big_endian(titanfall.StaticPropv12)


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES, LumpClasses = x360.convert_versioned(titanfall.BASIC_LUMP_CLASSES)
# copy used LumpClasses to globals
for LumpClass_name, LumpClass in LumpClasses.items():
    globals()[LumpClass_name] = LumpClass


LUMP_CLASSES, LumpClasses = x360.convert_versioned(titanfall.LUMP_CLASSES)
# copy used LumpClasses to globals
for LumpClass_name, LumpClass in LumpClasses.items():
    globals()[LumpClass_name] = LumpClass
del LumpClass_name, LumpClass


SPECIAL_LUMP_CLASSES = {"ENTITIES":                 {0: shared.Entities},
                        "ENTITY_PARTITIONS":        {0: titanfall.EntityPartitions},
                        "CM_GRID":                  {0: Grid_x360.from_bytes},
                        "TEXTURE_DATA_STRING_DATA": {0: shared.TextureDataStringData}}
# TODO: big-endian versions of PakFile & PhysicsCollide

GAME_LUMP_HEADER = x360.make_big_endian(titanfall.GAME_LUMP_HEADER)

GAME_LUMP_CLASSES = {"sprp": {12: lambda raw_lump: GameLump_SPRP_x360(raw_lump, StaticPropv12_x360)}}
# ^ {"lump": {version: SpecialLumpClass}}


methods = [*titanfall.methods]
