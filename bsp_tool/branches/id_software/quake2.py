# https://www.flipcode.com/archives/Quake_2_BSP_File_Format.shtml
# https://github.com/id-Software/Quake-2/blob/master/qcommon/qfiles.h#L214
from __future__ import annotations
import enum
import io
import itertools
import math
import struct
from typing import List, Tuple

from ... import core
from ...utils import binary
from ...utils import geometry
from ...utils import texture
from ...utils import vector
from .. import shared
from . import quake


FILE_MAGIC = b"IBSP"

BSP_VERSION = 38

GAME_PATHS = {
    "Anachronox": "Anachronox",
    "Quake II": "Quake 2",
    "Heretic II": "Heretic II",
    "D-Day Normandy": "D-Day_ Normandy/dday"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    ENTITIES = 0
    PLANES = 1
    VERTICES = 2
    VISIBILITY = 3
    NODES = 4
    TEXTURE_INFO = 5
    FACES = 6
    LIGHTING = 7
    LEAVES = 8
    LEAF_FACES = 9
    LEAF_BRUSHES = 10
    EDGES = 11
    SURFEDGES = 12
    MODELS = 13
    BRUSHES = 14
    BRUSH_SIDES = 15
    POP = 16  # QuakeII/pak1 only (multiplayer / deathmatch?)
    AREAS = 17
    AREA_PORTALS = 18


LumpHeader = quake.LumpHeader


# known lump changes from Quake -> Quake 2:
# new:
#   LEAF_BRUSHES
#   BRUSHES
#   BRUSH_SIDES
#   POP
#   AREAS
#   AREA_PORTALS
# deprecated:
#   MIP_TEXTURES
#   CLIP_NODES


# a rough map of the relationships between lumps:

# Entity -> Model -> Node -> Leaf -> LeafFace -> Face
#                                \-> LeafBrush -> Brush

# Visibility -> Node -> Leaf -> LeafFace -> Face
#                   \-> Plane

#     /-> Plane
# Face -> SurfEdge -> Edge -> Vertex
#    \--> TextureInfo
#     \-> Lightmap

# Area -> AreaPortal -> Area
#                   \-> Portal

# POP appears to only be used in Deathmatch maps & is always 256 bytes, cannot find use in source code
# POP seems to be the last lump written and is always null bytes in every map which has this lump


# engine limits:
class MAX(enum.Enum):
    # lumps
    AREAS = 256
    AREA_PORTALS = 1024
    BRUSHES = 8192
    BRUSH_SIDES = 65536
    EDGES = 128000
    ENTITIES = 2048
    FACES = 65536
    LEAF_BRUSHES = 65536
    LEAF_FACES = 65536
    LEAVES = 65536
    LIGHTING_SIZE = 0x200000  # bytesize
    MODELS = 1024
    NODES = 65536
    PLANES = 65536
    # NOTE: no POP limit
    SURFEDGES = 256000
    TEXTURE_INFO = 8192
    VERTICES = 65535
    VISIBILITY_SIZE = 0x100000  # bytesize
    # other
    ENTITY_KEY = 32
    ENTITY_VALUE = 1024
    MAP_SIZE = 4096  # +/- bounds


# flag enums:
class Contents(enum.IntFlag):
    """https://github.com/xonotic/darkplaces/blob/master/bspfile.h"""
    SOLID = 0x00000001  # opaque & transparent
    WINDOW = 0x00000002
    AUX = 0x00000004
    LAVA = 0x00000008
    SLIME = 0x00000010
    WATER = 0x00000020
    MIST = 0x00000040  # FOG?
    AREA_PORTAL = 0x00008000
    PLAYER_CLIP = 0x00010000
    MONSTER_CLIP = 0x00020000
    # bot hints
    CURRENT_0 = 0x00040000
    CURRENT_90 = 0x00080000
    CURRENT_180 = 0x00100000
    CURRENT_270 = 0x00200000
    CURRENT_UP = 0x00400000
    CURRENT_DOWN = 0x00800000
    # end bot hints
    ORIGIN = 0x01000000  # removed during compile
    MONSTER = 0x02000000
    DEAD_MONSTER = 0x04000000
    DETAIL = 0x08000000
    TRANSLUCENT = 0x10000000  # vis splitting brushes
    LADDER = 0x20000000


class Surface(enum.IntFlag):  # qcommon/qfiles.h
    """TextureInfo flags"""  # NOTE: vbsp sets these in src/utils/vbsp/textures.cpp
    LIGHT = 0x0001  # "value will hold the light strength"
    SLICK = 0x0002  # affects game physics (spelt "effects in source")
    SKY = 0x0004  # don't draw, but add to skybox
    WARP = 0x0008  # turbulent water warp
    TRANS33 = 0x0010  # 1/3 transparency?
    TRANS66 = 0x0020  # 2/3 transparency?
    FLOWING = 0x0040  # "scroll towards angle"
    NO_DRAW = 0x0080  # "don't bother referencing the texture"


# classes for lumps, in alphabetical order:
class Area(core.Struct):  # LUMP 17
    num_area_portals: int
    first_area_portal: int
    __slots__ = ["num_area_portals", "first_area_portal"]
    _format = "2i"


class AreaPortal(core.Struct):  # LUMP 18
    portal: int
    area: int  # Area this AreaPortal connects to
    __slots__ = ["portal", "area"]
    _format = "2i"


class Brush(core.MappedArray):  # LUMP 14
    first_brush_side: int  # first BrushSide of this Brush
    num_brush_sides: int  # number of BrushSides after first_brush_side on this Brush
    contents: int
    _mapping = ["first_brush_side", "num_brush_sides", "contents"]
    _format = "3i"
    _classes = {"contents": Contents}


class BrushSide(core.MappedArray):  # LUMP 15
    plane: int  # Plane this BrushSide lies on
    texture_info: int  # TextureInfo of this BrushSide
    _mapping = ["plane", "texture_info"]
    _format = "Hh"


class Leaf(core.Struct):  # LUMP 10
    contents: int  # bitwise OR of all brushes (not needed?)
    cluster: int  # index into the VISIBILITY lump; -1 for always visible
    area: int
    bounds: List[int]
    first_leaf_face: int  # index to this Leaf's first LeafFace
    num_leaf_faces: int  # the number of LeafFaces after first_face in this Leaf
    first_leaf_brush: int  # index to this Leaf's first LeafBrush
    num_leaf_brushes: int  # the number of LeafBrushes after first_brush in this Leaf
    __slots__ = ["contents", "cluster", "area", "bounds", "first_leaf_face",
                 "num_leaf_faces", "first_leaf_brush", "num_leaf_brushes"]
    _format = "Ih11H"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}
    _classes = {"contents": Contents, "bounds.mins": vector.vec3, "bounds.maxs": vector.vec3}


class Model(core.Struct):  # LUMP 13
    bounds: List[float]  # mins & maxs
    origin: List[float]  # starting position
    first_node: int  # first Node in this Model
    first_face: int  # first Face in this Model
    num_faces: int  # number of Faces in this Model after first_face
    __slots__ = ["bounds", "origin", "first_node", "first_face", "num_faces"]
    _format = "9f3i"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}, "origin": [*"xyz"]}
    _classes = {"bounds.mins": vector.vec3, "bounds.maxs": vector.vec3, "origin": vector.vec3}


class Node(core.Struct):  # LUMP 4
    plane: int  # Plane that splits this Node (hence front-child, back-child)
    children: List[int]  # +ve Node, -ve Leaf
    # NOTE: -1 (leaf 1) terminates tree searches
    bounds: List[vector.vec3]  # mins & maxs (uint16_t)
    # bounds.mins: vector.vec3
    # bounds.maxs: vector.vec3
    # NOTE: bounds are generous, rounding up to the nearest 16 units
    first_face: int  # index of the first Face in this Node
    num_faces: int  # number of Faces in this Node after first_face
    __slots__ = ["plane", "children", "bounds", "first_face", "num_faces"]
    _format = "I2i8h"
    _arrays = {"children": ["front", "back"],
               "bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}
    _classes = {"bounds.mins": vector.vec3, "bounds.maxs": vector.vec3}  # TODO: ivec3


class TextureInfo(core.Struct):  # LUMP 5
    # NOTE: TextureVector(ProjectionAxis(*s), ProjectionAxis(*t))
    s: Tuple[vector.vec3, float]  # S (U-Axis) projection axis
    t: Tuple[vector.vec3, float]  # T (V-Axis) projection axis
    flags: int  # "miptex flags & overrides"
    value: int  # "light emission etc."
    name: bytes  # texture name
    next_frame: int  # index into TextureInfo lump for animations (-1 = last frame)
    __slots__ = ["s", "t", "flags", "value", "name", "next_frame"]
    _format = "8f2I32si"
    _arrays = {
        "s": {"axis": [*"xyz"], "offset": None},
        "t": {"axis": [*"xyz"], "offset": None}}
    _classes = {f"{a}.axis": vector.vec3 for a in "st"}


# special lump classes, in alphabetical order:
class Visibility:
    """Developed with maxdup"""
    # TODO: endianness
    # https://www.flipcode.com/archives/Quake_2_BSP_File_Format.shtml
    # NOTE: cluster index comes from Leaf.cluster
    # -- https://github.com/ericwa/ericw-tools/blob/master/vis/vis.cc
    # -- https://github.com/ericwa/ericw-tools/blob/master/common/bspfile.cc#L4378-L4439
    # -- not RLE encoded in Source Engine branches?
    pvs: List[bytes]  # Potential Visible Set
    pas: List[bytes]  # Potential Audible Set
    # TODO: List[bool] -> bytes
    # -- sum([2 ** i if b else 0 for i, b in enumerate(x)]).to_bytes(math.ciel(len(x) / 8), "big")
    # TODO: bytes -> List[bool]
    # -- [b == "1" for b in f"{int.from_bytes(x, 'big'):b}"[::-1]]

    def __init__(self, pvs_table: List[bytes] = tuple(), pas_table: List[bytes] = tuple()):
        assert len(pvs_table) == len(pas_table)
        self.pvs = pvs_table
        self.pas = pas_table

    @classmethod
    def from_bytes(cls, raw_lump: bytes) -> Visibility:
        return cls.from_stream(io.BytesIO(raw_lump))

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Visibility:
        num_clusters = binary.read_struct(stream, "I")
        offsets = list(struct.iter_unpack("2I", stream.read(8 * num_clusters)))
        pvs, pas = list(), list()
        for pvs_offset, pas_offset in offsets:
            # get Potentially Visible Set
            stream.seek(pvs_offset)
            pvs.append(cls.run_length_decode(stream, num_clusters))
            # get Potentially Audible Set
            stream.seek(pas_offset)
            pas.append(cls.run_length_decode(stream, num_clusters))
        return cls(pvs, pas)

    @staticmethod
    def run_length_decode(stream: io.BytesIO, num_clusters: int) -> bytes:
        out = list()
        out_size = math.ceil(num_clusters / 8)
        while len(out) < out_size:
            byte = int(stream.read(1).hex(), 16)
            if byte == 0:
                count = int(stream.read(1).hex(), 16)
                assert count != 0, "stream is not compressed"
                out.extend([0] * count)
            else:
                out.append(byte)
        return bytes(out)

    @staticmethod
    def run_length_encode(data: bytes) -> bytes:
        out, zeroes = list(), 0
        for byte in data:
            if byte == 0:
                zeroes += 1
                if zeroes == 0xFF:
                    out.extend([0x00, zeroes])
                    zeroes = 0
            else:
                out.extend([0x00, zeroes, byte] if zeroes != 0 else [byte])
                zeroes = 0
        out.extend([0x00, zeroes] if zeroes != 0 else [])
        return bytes(out)

    def as_bytes(self) -> bytes:
        """should be a byte-for-byte match"""
        assert len(self.pvs) == len(self.pas)
        num_clusters = len(self.pvs)
        interleaved_sets = list(itertools.chain(*zip(self.pvs, self.pas)))
        compressed_sets = list()
        offsets = [4 + (num_clusters * 8)]
        for s in interleaved_sets:
            compressed_sets.append(self.run_length_encode(s))
            offsets.append(offsets[-1] + len(compressed_sets[-1]))
        header = struct.pack(f"{len(offsets)}I", num_clusters, *offsets[:-1])
        assert len(header) + sum(map(len, compressed_sets)) == offsets[-1]
        return b"".join([header, *compressed_sets])


# {"LUMP": LumpClass}
BASIC_LUMP_CLASSES = {
    "LEAF_FACES": shared.Shorts,
    "SURFEDGES":  shared.Ints}

LUMP_CLASSES = {
    "AREAS":        Area,
    "AREA_PORTALS": AreaPortal,
    "BRUSHES":      Brush,
    "BRUSH_SIDES":  BrushSide,
    "EDGES":        quake.Edge,
    "FACES":        quake.Face,
    "LEAVES":       Leaf,
    "MODELS":       Model,
    "NODES":        Node,
    "PLANES":       quake.Plane,
    "TEXTURE_INFO": TextureInfo,
    "VERTICES":     quake.Vertex}

SPECIAL_LUMP_CLASSES = {
    "ENTITIES":   shared.Entities,
    "VISIBILITY": Visibility}


def face_mesh(bsp, face_index: int, lightmap_scale: float = 16) -> geometry.Mesh:
    # TODO: lightmap_scale from worldspawn keyvalues
    face = bsp.FACES[face_index]
    texture_info = bsp.TEXTURE_INFO[face.texture_info]
    texvec = texture.TextureVector(
        texture.ProjectionAxis(*texture_info.s),
        texture.ProjectionAxis(*texture_info.t))
    # TODO: double check texvec.s/t.scale
    normal = bsp.PLANES[face.plane].normal
    # NOTE: normal might be inverted depending on face.side, haven't tested
    vertices = list()
    start, length = face.first_edge, face.num_edges
    for surfedge in bsp.SURFEDGES[start:start + length]:
        if surfedge < 0:
            position = bsp.VERTICES[bsp.EDGES[-surfedge][1]]
        else:
            position = bsp.VERTICES[bsp.EDGES[surfedge][0]]
        texture_uv = texvec.uv_at(position)
        lightmap_uv = texture_uv / lightmap_scale
        vertices.append(geometry.Vertex(
            position,
            normal,
            texture_uv,
            lightmap_uv))
    material_name = texture_info.name.partition(b"\0")[0].decode("ascii")
    material = geometry.Material(material_name)
    return geometry.Mesh(material, [geometry.Polygon(vertices)])


methods = [
    face_mesh,
    quake.leaves_of_node, quake.lightmap_of_face, quake.model,
    shared.worldspawn_volume]
methods = {method.__name__: method for method in methods}
