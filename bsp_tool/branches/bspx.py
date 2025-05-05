# https://developer.valvesoftware.com/wiki/BSPX
# https://github.com/fte-team/fteqw/blob/master/specs/bspx.txt
from __future__ import annotations
import io
from typing import List, Tuple

from .. import archives
from .. import core
from .. import lumps
from ..utils import vector
from . import shared
from .id_software import quake


LUMPS = {
    "BRUSHLIST",
    "DECOUPLED_LM",  # lightmap w/ uvs
    "ENVMAP",
    "FACENORMALS",  # ericw-tools VERTEXNORMALS
    "LIGHTGRID_OCTREE",
    "LIGHTINGDIR",  # headerless .lux / .dlit (deluxemap)
    "LIGHTING_E5BGR9",  # shared exponent HDR RGBLIGHTING
    "LMOFFSET",  # deprecated
    "LMSHIFT",  # deprecated
    "LMSTYLE",  # deprecated
    "LMSTYLE16",
    "RGBLIGHTING",  # headerless .lit
    "SURFENVMAP",
    "VERTEXNORMALS",
    "ZIP_PAKFILE"}


class LumpHeader(core.MappedArray):
    _mapping = ["name", "offset", "length"]
    _format = "24s2I"


# a rough map of the relationships between lumps:

# SURFENVMAP -> ENVMAP


# classes for each lump, in alphabetical order:
class EnvMap(core.Struct):
    # NOTE: cubemap images are stored at "textures/env/MAPNAME_X_Y_Z" (rounded to ints)
    origin: vector.vec3
    size: int  # texture dimension (each face of a cubemap is square)
    __slots__ = ["origin", "size"]
    _format = "3fi"
    _arrays = {"origin": [*"xyz"]}
    _classes = {"origin": vector.vec3}


# special lump classes, in alphabetical order:
# TODO: BrushList


class FaceNormalIndex(core.Struct):
    normal: int
    tangent: int
    bitangent: int
    __slots__ = ["normal", "tangent", "bitangent"]
    _format = "3I"


class FaceNormal:
    # https://github.com/ericwa/ericw-tools/blob/brushbsp/include/common/bspxfile.hh
    # https://github.com/ericwa/ericw-tools/blob/brushbsp/common/bspxfile.cc
    normals = List[vector.vec3]
    indices = List[FaceNormalIndex]
    # NOTE: indices are per-vertex, per-face
    # -- this means you need to parse the .bsp to index them

    def __init__(self):
        self.normals = list()
        self.indices = list()

    def as_bytes(self) -> bytes:
        return b"".join([
            len(self.normals).to_bytes(4, "little"),
            *[n.as_bytes() for n in self.normals],
            *[i.as_bytes() for i in self.indices]])

    @classmethod
    def from_bytes(cls, raw_lump: bytes) -> FaceNormal:
        return cls.from_stream(io.BytesIO(raw_lump))

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> FaceNormal:
        out = cls()
        num_normals = int.from_bytes(stream.read(4), "little")
        out.normals = lumps.BspLump.from_count(stream, num_normals, quake.Vertex)
        indices_offset = stream.tell()
        index_bytes = stream.read()
        assert len(index_bytes) % len(FaceNormalIndex().as_bytes()) == 0
        num_indices = len(index_bytes) // len(FaceNormalIndex().as_bytes())
        stream.seek(indices_offset)
        out.indices = lumps.BspLump.from_count(stream, num_indices, FaceNormalIndex)
        return out


# {"LUMP_NAME": LumpClass}
BASIC_LUMP_CLASSES = {
    "SURFENVMAP": shared.UnsignedInts}

LUMP_CLASSES = {
    "ENVMAP": EnvMap}

SPECIAL_LUMP_CLASSES = {
    "FACENORMALS": FaceNormal,
    "ZIP_PAKFILE": archives.pkware.Zip}


# branch exclusive methods, in alphabetical order:
def face_normals(bspx, face_index: int) -> List[Tuple[vector.vec3]]:
    bsp = bspx.bsp
    face = bsp.FACES[face_index]
    start = sum(f.num_edges for f in bsp.FACES[:face_index])
    length = face.num_edges
    indices = bspx.FACENORMALS.indices[start:length]
    return [(i.normal, i.tangent, i.bitangent) for i in indices]


methods = [face_normals]
methods = {method.__name__: method for method in methods}
