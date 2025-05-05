"""apparently the same as data found in .rmdl"""
from __future__ import annotations
import base64
import io
from typing import Dict, List

from ... import core


class Header(core.Struct):  # Season14
    # NOTE: Season0 header is shorter
    unknown_1: List[int]  # always (64, 56, 68)?
    unknown_2: bool  # always True?
    unknown_3: bool
    bitfield: int
    # bitfield.unknown: int  # {0x00, 0x40, 0x80}
    # bitfield.num_unknown: int  # 1 for most; goes up as data gets longer
    triplets: List[int]  # always the same 3 numbers; next multiple of 4 after material string
    # start_tail?
    zeroes: List[int]  # always (0,) * 4?
    scale: float  # node scale?
    unknown_4: List[int]  # always (1024, 0, 0xEB1280)
    __slots__ = ["unknown_1", "unknown_2", "unknown_3", "bitfield", "triplets", "zeroes", "scale", "unknown_4"]
    _format = "13If3I"
    _arrays = {"unknown_1": 3, "triplets": 3, "zeroes": 4, "unknown_4": 3}
    _bitfields = {"bitfield": {"unknown": 8, "num_unknown": 24}}
    _classes = {"unknown_2": bool, "unknown_3": bool}


class StarColl:
    """Apex Legends trigger volume physics"""
    header: Header
    material: str
    unknown: bytes

    # TODO: __repr__

    @classmethod
    def from_entity(cls, entity: Dict[str, str]) -> StarColl:
        num_keys = len([k for k in entity if k.startswith("*coll")])
        full_b64 = "".join([entity[f"*coll{i}"] for i in range(num_keys)])
        decoded = base64.b64decode(full_b64)
        return cls.from_stream(io.BytesIO(decoded))

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> StarColl:
        out = cls()
        out.header = Header.from_stream(stream)
        end_string = out.header.triplets[0]
        out.material = stream.read(end_string - stream.tell()).rstrip(b"\0").decode()
        out.unknown = stream.read()
        return out

    @classmethod
    def from_bytes(cls, raw_data: bytes) -> StarColl:
        return cls.from_stream(io.BytesIO(raw_data))
