# https://github.com/id-Software/Quake/blob/master/WinQuake/bspfile.h  (v29)
# https://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_4.htm  (v23)
from __future__ import annotations
import enum
import io
import struct
from typing import Dict, List, Set, Tuple, Union

from ... import core
from ...utils import binary
from ...utils import geometry
from ...utils import physics
from ...utils import texture
from ...utils import vector
from .. import shared  # special lumps


FILE_MAGIC = None

BSP_VERSION = 29

GAME_PATHS = {
    "DarkPlaces": "DarkPlaces",
    "Quake": "Quake",
    "Team Fortress Quake": "QUAKE/FORTRESS"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    ENTITIES = 0
    PLANES = 1
    MIP_TEXTURES = 2
    VERTICES = 3
    VISIBILITY = 4
    NODES = 5
    TEXTURE_INFO = 6
    FACES = 7
    LIGHTING = 8  # 8bpp 0x00-0xFF black-white
    CLIP_NODES = 9
    LEAVES = 10
    LEAF_FACES = 11
    EDGES = 12
    SURFEDGES = 13
    MODELS = 14


class LumpHeader(core.MappedArray):
    _mapping = ["offset", "length"]
    _format = "2I"


# a rough map of the relationships between lumps:

# Entity -> Model -> Node -> Leaf -> LeafFace -> Face
#                \-> ClipNode -> Plane

# Visibility -> Node -> Leaf -> LeafFace -> Face
#                   \-> Plane

#     /-> TextureInfo -> MipTextures -> MipTexture
# Face -> SurfEdge -> Edge -> Vertex
#    \--> Lightmap
#     \-> Plane


# engine limits:
class MAX(enum.Enum):
    BRUSHES = 4096  # for radiant / q2map ?
    CLIP_NODES = 32767
    EDGES = 256000
    ENTITIES = 1024
    ENTITIES_SIZE = 65536  # bytesize
    FACES = 65535
    LEAF_FACES = 65535  # MARKSURFACES
    LEAVES = 8192
    LIGHTING_SIZE = 0x100000  # bytesize
    LIGHTMAPS = 4  # affects Face LumpClass; num lighting styles?
    MIP_LEVELS = 4  # affects MipTexture LumpClass
    MIP_TEXTURES = 512
    MIP_TEXTURES_SIZE = 0x200000  # bytesize
    MODELS = 256
    NODES = 32767  # "because negative shorts are contents"
    PLANES = 32767
    SURFEDGES = 512000
    TEXTURE_INFO = 4096
    VERTICES = 65535
    VISIBILITY_SIZE = 0x100000  # bytesize
    # string buffers
    ENTITY_KEY = 32
    ENTITY_VALUE = 1024
    # other
    MAP_HULLS = 4
    MAP_EXTENTS = 4096  # -4096 to 4096, 8192 ** 3 cubic units of space


# flag enums:
class Contents(enum.IntFlag):
    """Brush flags"""
    # src/public/bspflags.h
    # NOTE: compiler gets these flags from a combination of all textures on the brush
    # e.g. any non opaque face means this brush is non-opaque, and will not block vis
    EMPTY = -1
    SOLID = -2
    WATER = -3
    SLIME = -4
    LAVA = -5
    SKY = -6
    ORIGIN = -7  # removed when compiling from .map to .bsp
    CLIP = -8  # "changed to contents_solid"
    CURRENT_0 = -9
    CURRENT_90 = -10
    CURRENT_180 = -11
    CURRENT_270 = -12
    CURRENT_UP = -13
    CURRENT_DOWN = -14

    def __repr__(self):
        if self < 0:
            return super().__repr__()
        return str(int(self))


class PlaneSide(enum.Enum):
    FRONT = 0
    BACK = 1


class PlaneType(enum.Enum):
    # Axial, perfectly aligned
    X = 0
    Y = 1
    Z = 2
    # Non-axial, nearest axis
    NEAR_X = 3
    NEAR_Y = 4
    NEAR_Z = 5


# classes for lumps, in alphabetical order:
class ClipNode(core.Struct):  # LUMP 9
    # https://en.wikipedia.org/wiki/Half-space_(geometry)
    # NOTE: bounded by associated model
    # basic convex solid stuff
    plane: int
    children: List[int]  # +ve indexes ClipNode, -ve Contents
    __slots__ = ["plane", "children"]
    _format = "I2h"
    _arrays = {"children": ["front", "back"]}
    _classes = {"children.front": Contents, "children.back": Contents}


class Edge(list):  # LUMP 12
    # TODO: replace w/ MappedArray(_mapping=2)
    _format = "2H"  # List[int]

    # hacky methods for working with other systems
    def as_tuple(self):
        return self

    @classmethod
    def from_tuple(cls, _tuple):
        return cls(_tuple)


class Face(core.Struct):  # LUMP 7
    plane: int  # signed for quake, unsigned for quake 2
    side: PlaneSide
    first_edge: int
    num_edges: int
    texture_info: int  # index of this face's TextureInfo
    lighting_type: int  # TODO: FaceLightingType(enum.IntFlag)
    # 0x00=lightmap, 0xFF=no-lightmap
    # 0x01=fast-pulse, 0x02=slow-pulse, 0x03-0x10 other
    base_light: int  # 0x00 bright - 0xFF dark (lowest possible light level)
    light: int  # "additional light models"
    lighting_offset: int  # index to first byte in LIGHTING lump
    # -1 for no baked lighting
    # NOTE: num_texels is determined from uv bounds
    __slots__ = [
        "plane", "side", "first_edge", "num_edges", "texture_info",
        "lighting_type", "base_light", "light", "lighting_offset"]
    _format = "2HI2H4Bi"
    _arrays = {"light": 2}
    _classes = {"side": PlaneSide}


class Leaf(core.Struct):  # LUMP 10
    contents: Contents
    vis_offset: int  # index into the VISIBILITY lump; -1 for none
    bounds: List[vector.vec3]  # uint16_t; very chunky
    # bounds.mins: vector.vec3
    # bounds.maxs: vector.vec3
    first_leaf_face: int  # first LeafFace in this Leaf
    num_leaf_faces: int  # number of LeafFaces after first_leaf_face in this Leaf
    sound: List[int]  # ambient master of all 4 elements (0x00 - 0xFF)
    __slots__ = [
        "contents", "vis_offset", "bounds", "first_leaf_face",
        "num_leaf_faces", "sound"]
    _format = "2i6h2H4B"
    _arrays = {
        "bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]},
        "sound": ["water", "sky", "slime", "lava"]}
    _classes = {
        "contents": Contents,
        "bounds.mins": vector.vec3, "bounds.maxs": vector.vec3}
    # TODO: ivec3 bounds


class Model(core.Struct):  # LUMP 14
    bounds: List[vector.vec3]
    # bounds.mins: vector.vec3
    # bounds.maxs: vector.vec3
    origin: vector.vec3
    # headnode[MAX_MAP_HULLS]:
    first_node: int  # top Node of this Model
    clip_nodes: List[int]  # indices into ClipNodes
    unused_node: int  # always 0
    num_leaves: int  # "not counting the solid leaf 0"
    first_face: int  # index to the first Face in this Model
    num_faces: int  # number of faces after first_face in this Model
    __slots__ = [
        "bounds", "origin", "first_node", "clip_nodes", "unused_node",
        "num_leaves", "first_face", "num_faces"]
    _format = "9f7i"
    _arrays = {
        "bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]},
        "origin": [*"xyz"],
        "clip_nodes": 2}
    _classes = {
        "bounds.mins": vector.vec3, "bounds.maxs": vector.vec3,
        "origin": vector.vec3}


class Node(core.Struct):  # LUMP 5
    plane: int  # Plane that splits this Node (hence front-child, back-child)
    children: List[int]  # +ve Node, -ve Leaf
    # NOTE: -1 (leaf 1) terminates tree searches
    bounds: List[vector.vec3]  # mins & maxs (uint16_t)
    # bounds.mins: vector.vec3
    # bounds.maxs: vector.vec3
    # NOTE: bounds are generous, rounding up to the nearest 16 units
    first_face: int
    num_faces: int
    __slots__ = ["plane", "children", "bounds", "first_face", "num_faces"]
    _format = "I8h2H"
    _arrays = {
        "children": ["front", "back"],
        "bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}
    _classes = {"bounds.mins": vector.vec3, "bounds.maxs": vector.vec3}
    # TODO: ivec3 bounds


class Plane(core.Struct):  # LUMP 1
    normal: vector.vec3
    distance: float
    type: PlaneType
    __slots__ = ["normal", "distance", "type"]
    _format = "4fI"
    _arrays = {"normal": [*"xyz"]}
    _classes = {"normal": vector.vec3, "type": PlaneType}


class TextureInfo(core.Struct):  # LUMP 6
    # NOTE: TextureVector(ProjectionAxis(*s), ProjectionAxis(*t))
    s: Tuple[vector.vec3, float]  # S (U-Axis) projection axis
    t: Tuple[vector.vec3, float]  # T (V-Axis) projection axis
    mip_texture: int  # index to this TextureInfo's target MipTexture
    animated: int  # 0 or 1
    __slots__ = ["s", "t", "mip_texture", "animated"]
    _format = "8f2I"
    _arrays = {
        "s": {"axis": [*"xyz"], "offset": None},
        "t": {"axis": [*"xyz"], "offset": None}}
    _classes = {f"{a}.axis": vector.vec3 for a in "st"}


class Vertex(core.MappedArray, vector.vec3):  # LUMP 3
    """a point in 3D space"""
    x: float
    y: float
    z: float
    _mapping = [*"xyz"]
    _format = "3f"


# special lump classes, in alphabetical order:
class MipTexture(core.Struct):  # LUMP 2
    # http://www.cs.hut.fi/~andy/T-126.101/2004/texture_prefix.html
    # http://www.slackiller.com/tommy14/hltexture.htm
    name: str  # texture name
    # NOTE: may contain multiple values
    # -- e.g. b"+buttontex\0\x03\0..."
    # leading "*": scroll like water / lava
    # leading "+": animate frame-by-frame (first frame must be 0-9)
    # leading "sky": scroll like sky (sky textures have 2 parts)
    # leading "{": transparent via blue chroma key (palette)
    # added in Half-Life:
    # leading "!": water, no entity required
    # leading "~": emit light
    # leading "+a": animated toggle;  cycle through up to 10 frames
    # leading "-": random tiling; (set of 3 or 4)
    size: vector.vec2  # width & height
    offsets: List[int]  # offset from entry start to texture
    __slots__ = ["name", "size", "offsets"]
    _format = "16s6I"
    _arrays = {
        "size": [*"xy"],
        "offsets": ["full", "half", "quarter", "eighth"]}
    _classes = {"size": vector.vec2}
    # TODO: ivec2 size


class MipTextureLump(list):  # LUMP 2
    """see github.com/id-Software/Quake-2/blob/master/ref_soft/r_image.c"""
    # packed texture data, kind of like a WAD
    # goldsrc just uses this lump to list texture names & mounts an external WAD
    MipTextureClass: core.Struct = MipTexture

    def __init__(self, iterable: List[(core.Struct, List[bytes])] = tuple()):
        super().__init__(iterable)

    def as_bytes(self) -> bytes:
        out = [len(self).to_bytes(4, "little")]  # miptex count
        miptex_offsets = list()
        miptex_offset = 4 + len(self) * 4
        for miptex, mips in self:
            miptex_offsets.append(miptex_offset)
            mip_offset = struct.calcsize(self.MipTextureClass._format)
            for i, mip in enumerate(mips):
                miptex.offsets[i] = mip_offset
                mip_offset += len(mip)
            out.append(miptex.as_bytes())
            out.extend(mips)
            miptex_offset += mip_offset
        out[1:1] = miptex_offsets  # splice offsets to each miptex in after the miptex count
        return b"".join(out)

    @classmethod
    def from_bytes(cls, raw_lump: bytes) -> MipTextureLump:
        return cls.from_stream(io.BytesIO(raw_lump), len(raw_lump))

    @classmethod
    def from_stream(cls, stream: io.BytesIO, lump_length: int) -> MipTextureLump:
        out = list()
        start = stream.tell()  # for confirming eof
        num_offsets = binary.read_struct(stream, "I")
        if num_offsets != 1:
            offsets = binary.read_struct(stream, f"{num_offsets}i")
        else:
            offsets = struct.unpack("i", stream.read(4))
        for i, offset in enumerate(offsets):
            if offset == -1:
                out.append((None, [b""] * 4))  # there is no mip
                continue
            stream.seek(offset)
            miptex = cls.MipTextureClass.from_stream(stream)
            mips = list()
            for j, mip_offset in enumerate(miptex.offsets):
                if mip_offset == 0:  # no embedded mips (e.g. gasworks.bsp)
                    mips.append(b"")
                    continue
                stream.seek(offset + mip_offset)
                # don't bother calculating & confirming mip sizes
                # just grab all the bytes
                if j < 3:  # len(miptex.offsets) - 1
                    end_offset = miptex.offsets[j + 1]
                elif i < len(offsets) - 1:
                    end_offset = offsets[i + 1]
                else:  # end of lump (j == 3 and offset == offsets[-1])
                    end_offset = lump_length
                length = end_offset - mip_offset
                mip = stream.read(length)
                mips.append(mip)
            out.append((miptex, mips))
        assert stream.tell() == start + lump_length
        return cls(out)


# TODO: Visibility
# -- decode RLE
# -- Leaf.vislist/cluster is -1 or byte index into compressed array
# -- https://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_4.htm#BL4


# {"LUMP": LumpClass}
BASIC_LUMP_CLASSES = {
    "LEAF_FACES": shared.Shorts,
    "SURFEDGES":  shared.Ints}

LUMP_CLASSES = {
    "CLIP_NODES":   ClipNode,
    "EDGES":        Edge,
    "FACES":        Face,
    "LEAVES":       Leaf,
    "MODELS":       Model,
    "NODES":        Node,
    "PLANES":       Plane,
    "TEXTURE_INFO": TextureInfo,
    "VERTICES":     Vertex}

SPECIAL_LUMP_CLASSES = {
    "ENTITIES":     shared.Entities,
    "MIP_TEXTURES": MipTextureLump}


# branch exclusive methods, in alphabetical order:
def leaves_of_node(bsp, node_index: int) -> Set[int]:
    node = bsp.NODES[node_index]
    out = set()
    for child in node.children:
        if child < 0:
            out.add(-child)
        else:
            out.update(bsp.leaves_of_node(child))
    return out


def lightmap_of_face(bsp, face_index: int) -> Dict[str, Union[int, bytes]]:
    # NOTE: if mapping onto a lightmap page you'll need to calculate a X&Y offset to fit this face into
    # TODO: probably compose a .json with lightmap uv offsets & bounding boxes in extensions.lightmaps
    out = dict()
    # ^ {"width": int, "height": int, "lightmap_bytes": bytes}
    face = bsp.FACES[face_index]
    if face.lighting_offset == -1:
        return dict(width=0, height=0, lightmap_bytes=b"")
    # get lightmap
    polygon = bsp.face_mesh(face_index).polygons[0]
    uv_bounds = sum([v.uv[1] for v in polygon.vertices], start=physics.AABB())
    out["width"] = int(uv_bounds.maxs.x - uv_bounds.mins.x) + 1
    out["height"] = int(uv_bounds.maxs.y - uv_bounds.mins.y) + 1
    start = face.lighting_offset
    length = out["width"] * out["height"]
    out["lightmap_bytes"] = bsp.LIGHTING[start:start + length]
    # TODO: handle multiple light styles
    return out


def parse_vis(bsp, leaf_index: int) -> bytes:
    """grabs the vistree bytes for this leaf"""
    # NOTE: likely maps against the leaf list generated below
    # -- -1 .vis_offset leaves may only occur at the tail? unknown, further testing required
    expected_length = len([L for L in bsp.LEAVES if L.vis_offset != -1]) + 7 >> 3
    # ^ num_cluster_bytes = num_clusters + 7 >> 3
    leaf = bsp.LEAVES[leaf_index]
    if leaf.vis_offset == -1:
        # render everything
        return b"\xFF" * expected_length
    out = []
    i = 0
    while len(out) < expected_length:
        c = bsp.VISIBILITY[leaf.vis_offset + i]
        if c == 0:  # RLE [0, num_0]
            out.extend([0] * bsp.VISIBILITY[leaf.vis_offset + i + 1])
            i += 2
        else:
            out.append(c)
            i += 1
    return bytes(out)


def face_mesh(bsp, face_index: int, lightmap_scale: float = 16) -> geometry.Mesh:
    # TODO: lightmap_scale from worldspawn keyvalues
    face = bsp.FACES[face_index]
    texture_info = bsp.TEXTURE_INFO[face.texture_info]
    mip_texture = bsp.MIP_TEXTURES[texture_info.mip_texture][0]
    texvec = texture.TextureVector(texture.ProjectionAxis(*texture_info.s), texture.ProjectionAxis(*texture_info.t))
    texvec.s.scale = 1 / mip_texture.size.x
    texvec.t.scale = 1 / mip_texture.size.y
    normal = bsp.PLANES[face.plane].normal
    # NOTE: normal might be inverted depending on face.side, haven't tested
    vertices = list()
    for surfedge in bsp.SURFEDGES[face.first_edge:face.first_edge + face.num_edges]:
        if surfedge < 0:
            position = bsp.VERTICES[bsp.EDGES[-surfedge][1]]
        else:
            position = bsp.VERTICES[bsp.EDGES[surfedge][0]]
        texture_uv = texvec.uv_at(position)
        lightmap_uv = texture_uv / lightmap_scale
        vertices.append(geometry.Vertex(position, normal, texture_uv, lightmap_uv))
    material_name = mip_texture.name.partition(b"\0")[0].decode("ascii")
    material = geometry.Material(material_name)
    return geometry.Mesh(material, [geometry.Polygon(vertices)])


def model(bsp, model_index: int) -> geometry.Model:
    # entity
    entities = bsp.ENTITIES.search(model=f"*{model_index}")
    model_entity = entities[0] if len(entities) != 0 else dict()
    origin = model_entity.get("origin", "0 0 0")
    origin = vector.vec3(*origin.split())
    pitch, yaw, roll = model_entity.get("angles", "0 0 0").split()
    yaw = model_entity.get("angle", yaw)
    angles = vector.vec3(roll, pitch, yaw)
    # geometry
    model = bsp.MODELS[model_index]
    face_indices = range(model.first_face, model.first_face + model.num_faces)
    out = geometry.Model([bsp.face_mesh(i) for i in face_indices], origin, angles)
    out.entity = model_entity
    return out


# TODO: reverse brush planes from ClipNodes
# -- will likely require a Brush utility class for convex solids & plane -> mesh conversion
# -- that kind of toolset would be handy in general for various .vmf, .map & .bsp tools
# -- probably split the brush tools of vmf_tool into it's own repo & utilise other repos for parsing?


methods = [leaves_of_node, lightmap_of_face, parse_vis, face_mesh, model]
methods = {method.__name__: method for method in methods}
