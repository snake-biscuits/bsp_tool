# https://github.com/id-Software/Quake/blob/master/WinQuake/bspfile.h  (v29)
# https://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_4.htm  (v23)
from __future__ import annotations
import enum
import io
import itertools
import json
import math
import struct
from typing import Any, Dict, List

from .. import base
from .. import shared  # special lumps
from .. import vector


FILE_MAGIC = None

BSP_VERSION = 29

GAME_PATHS = {"DarkPlaces": "DarkPlaces", "Quake": "Quake",
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
    LIGHTMAPS = 8  # 8bpp 0x00-0xFF black-white
    CLIP_NODES = 9
    LEAVES = 10
    LEAF_FACES = 11
    EDGES = 12
    SURFEDGES = 13
    MODELS = 14


class LumpHeader(base.MappedArray):
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
    LIGHTMAPS = 4  # affects Face LumpClass
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
class ClipNode(base.Struct):  # LUMP 9
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
    _format = "2H"  # List[int]

    def as_tuple(self):
        return self  # HACK

    @classmethod
    def from_tuple(cls, _tuple):
        return cls(_tuple)


class Face(base.Struct):  # LUMP 7
    plane: int
    side: int  # 0 or 1 for side of plane
    first_edge: int
    num_edges: int
    texture_info: int  # index of this face's TextureInfo
    lighting_type: int  # 0x00=lightmap, 0xFF=no-lightmap, 0x01=fast-pulse, 0x02=slow-pulse, 0x03-0x10 other
    base_light: int  # 0x00 bright - 0xFF dark (lowest possible light level)
    light: int  # "additional light models"
    lightmap_offset: int  # index to first byte in LIGHTING lump; -1 if not lightmapped
    # NOTE: the number of texels used by the lightmap is determined by the uv bounds
    __slots__ = ["plane", "side", "first_edge", "num_edges", "texture_info",
                 "lighting_type", "base_light", "light", "lightmap_offset"]
    _format = "2HI2H4Bi"
    _arrays = {"light": 2}
    # TODO: FaceLightingType(enum.IntFlag)


class Leaf(base.Struct):  # LUMP 10
    contents: Contents
    vis_offset: int  # index into the VISIBILITY lump; -1 for none
    bounds: List[vector.vec3]  # uint16_t; very chunky
    # bounds.mins: vector.vec3
    # bounds.maxs: vector.vec3
    first_leaf_face: int  # first LeafFace in this Leaf
    num_leaf_faces: int  # number of LeafFaces after first_leaf_face in this Leaf
    sound: List[int]  # ambient master of all 4 elements (0x00 - 0xFF)
    __slots__ = ["contents", "vis_offset", "bounds", "first_leaf_face",
                 "num_leaf_faces", "sound"]
    _format = "2i6h2H4B"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]},
               "sound": ["water", "sky", "slime", "lava"]}
    _classes = {"contents": Contents, "bounds.mins": vector.vec3, "bounds.maxs": vector.vec3}
    # TODO: ivec3


class Model(base.Struct):  # LUMP 14
    bounds: List[vector.vec3]
    # bounds.mins: vector.vec3
    # bounds.maxs: vector.vec3
    origin: vector.vec3
    # headnode[MAX_MAP_HULLS]:
    first_node: int  # first node in NODES lumps
    clip_nodes: List[int]  # 1st & second CLIP_NODES indices
    unused_node: int  # always 0
    num_leaves: int  # "not counting the solid leaf 0"
    first_face: int  # index to the first Face in this Model
    num_faces: int  # number of faces after first_face in this Model
    __slots__ = ["bounds", "origin", "first_node", "clip_nodes", "unused_node",
                 "num_leaves", "first_face", "num_faces"]
    _format = "9f7i"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}, "origin": [*"xyz"],
               "clip_nodes": 2}
    _classes = {"bounds.mins": vector.vec3, "bounds.maxs": vector.vec3, "origin": vector.vec3}


class Node(base.Struct):  # LUMP 5
    plane: int  # Plane that splits this Node (hence front-child, back-child)
    children: List[int]  # +ve Node, -ve Leaf
    # NOTE: -1 (leaf 0) is a dummy leaf & terminates tree searches
    bounds: List[vector.vec3]  # uint16_t; very chunky
    # bounds.mins: vector.vec3
    # bounds.maxs: vector.vec3
    first_face: int
    num_faces: int
    __slots__ = ["plane", "children", "bounds", "first_face", "num_faces"]
    _format = "I8h2H"
    _arrays = {"children": ["front", "back"],
               "bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}}
    _classes = {"bounds.mins": vector.vec3, "bounds.maxs": vector.vec3}


class Plane(base.Struct):  # LUMP 1
    normal: vector.vec3
    distance: float
    type: PlaneType
    __slots__ = ["normal", "distance", "type"]
    _format = "4fI"
    _arrays = {"normal": [*"xyz"]}
    _classes = {"normal": vector.vec3, "type": PlaneType}


class TextureInfo(base.Struct):  # LUMP 6
    s: List[float]  # S (U-Axis) texture vector
    t: List[float]  # T (V-Axis) texure vector
    mip_texture: int  # index to this TextureInfo's target MipTexture
    animated: int  # 0 or 1
    __slots__ = ["s", "t", "mip_texture", "animated"]
    _format = "8f2I"
    _arrays = {"s": [*"xyz", "offset"],
               "t": [*"xyz", "offset"]}
    # TODO: TextureVector class (see vmf_tool)


class Vertex(base.MappedArray, vector.vec3):  # LUMP 3
    """a point in 3D space"""
    x: float
    y: float
    z: float
    _mapping = [*"xyz"]
    _format = "3f"


# special lump classes, in alphabetical order:
class MipTextureLump(list):  # LUMP 2
    """see github.com/id-Software/Quake-2/blob/master/ref_soft/r_image.c"""
    # later superseded by TextureData in source
    _buffer: io.BytesIO  # for debugging

    def __init__(self, raw_lump: bytes):
        out = list()
        self._buffer = io.BytesIO(raw_lump)
        length = int.from_bytes(self._buffer.read(4), "little")
        offsets = struct.unpack(f"{length}i", self._buffer.read(4 * length))
        for i, offset in enumerate(offsets):
            if offset == -1:
                out.append((None, [b""] * 4))  # there is no mip
                continue
            self._buffer.seek(offset)
            miptex = MipTexture.from_stream(self._buffer)
            mips = list()
            for j, mip_offset in enumerate(miptex.offsets):
                if mip_offset == 0:  # Half-Life/valve/maps/gasworks.bsp has no embedded mips
                    mips.append(b"")
                    continue
                self._buffer.seek(offset + mip_offset)
                # don't bother accurately calculating & confirming mip sizes, just grab all the bytes
                if j < 3:  # len(miptex.offsets) - 1
                    end_offset = miptex.offsets[j + 1]
                elif i < len(offsets) - 1:
                    end_offset = offsets[i + 1]
                else:  # end of lump (j == 3 and offset == offsets[-1])
                    end_offset = len(raw_lump)
                length = end_offset - mip_offset
                mip = self._buffer.read(length)
                mips.append(mip)
            out.append((miptex, mips))
        assert len(raw_lump) == self._buffer.tell()
        super().__init__(out)

    def as_bytes(self):
        out = [len(self).to_bytes(4, "little")]  # miptex count
        miptex_offsets = list()
        miptex_offset = 4 + len(self) * 4
        for miptex, mips in self:
            miptex_offsets.append(miptex_offset)
            mip_offset = struct.calcsize(MipTexture._format)
            for i, mip in enumerate(mips):
                miptex.offsets[i] = mip_offset
                mip_offset += len(mip)
            out.append(miptex.as_bytes())
            out.extend(mips)
            miptex_offset += mip_offset
        out[1:1] = miptex_offsets  # splice offsets to each miptex in after the miptex count
        return b"".join(out)


class MipTexture(base.Struct):  # LUMP 2
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
    _arrays = {"size": ["width", "height"],
               "offsets": ["full", "half", "quarter", "eighth"]}
    _classes = {"size": vector.renamed_vec2("width", "height")}


# TODO: Visibility
# -- decode RLE
# -- Leaf.vislist/cluster is -1 or byte index into compressed array
# -- https://www.gamers.org/dEngine/quake/spec/quake-spec34/qkspec_4.htm#BL4


# {"LUMP": LumpClass}
BASIC_LUMP_CLASSES = {"LEAF_FACES": shared.Shorts,
                      "SURFEDGES":  shared.Shorts}

LUMP_CLASSES = {"CLIP_NODES":   ClipNode,
                "EDGES":        Edge,
                "FACES":        Face,
                "LEAVES":       Leaf,
                "MODELS":       Model,
                "NODES":        Node,
                "PLANES":       Plane,
                "TEXTURE_INFO": TextureInfo,
                "VERTICES":     Vertex}

SPECIAL_LUMP_CLASSES = {"ENTITIES":     shared.Entities,
                        "MIP_TEXTURES": MipTextureLump}


# branch exclusive methods, in alphabetical order:
def as_lightmapped_obj(bsp):
    obj_file = open(f"{bsp.filename}.lightmapped.obj", "w")
    obj_file.write(f"# generated with bsp_tool from {bsp.filename}\n")
    obj_file.write("\n".join(f"v {v.x} {v.y} {v.z}" for v in bsp.VERTICES))
    obj_file.write("\n".join(f"vn {p.normal.x} {p.normal.y} {p.normal.z}" for p in bsp.PLANES))
    # TODO: unique plane normals for smoothing groups; need to blend neighbouring edges
    faces = list()
    # [[(v, vt, vn)]]
    lightmap_dicts = list()
    for i, face in enumerate(bsp.FACES):
        lightmap_dicts.append(bsp.lightmap_of_face(i))
        face_vertices = bsp.vertices_of_face(i)
        # TODO: triangle fan vertices
        # TODO: remap vertex_position & vertex_normal to indices into bsp.VERTICES & [p.normal for p in bsp.PLANES]
        faces.append(face_vertices)
        # TODO: write & index LIGHTMAP uvs; f"vt {uv.x} {uv.y}"
        # TODO: write face; "f " + " ".join([f"{vi}/{vti}/{vni}" for vi, vti, vni in face_indices])
    obj_file.close()
    print(f"Wrote {bsp.filename}.lightmapped.obj")
    # store lightmap data in json
    json_file = open(f"{bsp.filename}.lightmap_uvs.json")
    json_file.write(json.dumps(lightmap_dicts))
    # NOTE: contains raw bytes of each lightmapped face, this .json will need a second pass
    # -- lightmap_bytes -> extentions.lightmaps.LightmapPage
    # -- map uvs onto faces
    json_file.close()
    print(f"Wrote {bsp.filename}.lightmap_uvs.json")
    # TODO: write a QuakeBsp / GoldSrcBsp function in extensions/lightmaps.py
    # -- should use & remap <bsp filename>.lightmap_uvs.json to work with exported lightmap page


def lightmap_of_face(bsp, face_index: int) -> Dict[Any]:
    # NOTE: if mapping onto a lightmap page you'll need to calculate a X&Y offset to fit this face into
    # TODO: probably compose a .json with lightmap uv offsets & bounding boxes in extensions/lightmaps.py
    out = dict()
    # ^ {"uvs": List[vector.vec2], "lightmap_offset": int, "width": int, "height": int, "lightmap_bytes": bytes}
    face = bsp.FACES[face_index]
    out["uvs"] = [uv for position, uv, normal in bsp.vertices_of_face(face_index)]
    # NOTE: to create a lightmap page you'll need to reposition these uvs onto that sheet
    # -- forcing the top-left of the uv's bounds to (0, 0) might help with that
    out["lightmap_offset"] = face.lightmap_offset
    if face.lightmap_offset == -1:
        out["width"], out["height"] = 0, 0
        out["lightmap_bytes"] = b""
        return out
    # calculate uv bounds
    minU, minV = math.inf, math.inf
    maxU, maxV = -math.inf, -math.inf
    for uv in out["uvs"]:
        minU = min(uv.x, minU)
        minV = min(uv.y, minV)
        maxU = max(uv.x, maxU)
        maxV = max(uv.y, maxV)
    # TODO: use -minUV as an offset to reposition the UV bounds top-left to (0, 0)
    out["width"] = (maxU - minU) // 16  # 16 units per texel, always
    out["height"] = (maxV - minV) // 16
    # collect lightmap bytes
    start = out["lightmap_offset"]
    length = out["width"] * out["height"] * 4  # 4 bytes per texel, RGBA_8888?
    # what about lighting styles? how many copies do we need to load in sequence?
    out["lightmap_bytes"] = bsp.LIGHTING[start:start + length]
    return out


def parse_vis(bsp, leaf_index: int):
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


def vertices_of_face(bsp, face_index: int) -> List[(vector.vec3, vector.vec2, vector.vec3)]:
    """output is [(position.xyz, uv.xy, normal.xyz, colour.rgba)] """
    face = bsp.FACES[face_index]
    uv0 = list()  # texture uv
    first_edge = face.first_edge
    positions = list()
    for surfedge in bsp.SURFEDGES[first_edge:(first_edge + face.num_edges)]:
        if surfedge >= 0:  # index is positive
            positions.append(bsp.VERTICES[bsp.EDGES[surfedge][0]])
            # ^ utils/vrad/trace.cpp:637
        else:  # index is negative
            positions.append(bsp.VERTICES[bsp.EDGES[-surfedge][1]])
            # ^ utils/vrad/trace.cpp:635
    texture_info = bsp.TEXTURE_INFO[face.texture_info]
    # generate uvs
    for P in positions:
        uv = [vector.dot(P, texture_info.s[:3]) + texture_info.s.offset,
              vector.dot(P, texture_info.t[:3]) + texture_info.t.offset]
        # TODO: scale uv against MipTexture width & height
        uv0.append(vector.vec2(*uv))
    # NOTE: vertex normal can be found via bsp.PLANES[face.planes].normal
    # -- however, the normal may be inverted, depending on face.side, haven't tested
    return list(zip(positions, uv0))


def vertices_of_model(bsp, model_index: int) -> List[float]:
    model = bsp.MODELS[model_index]
    # TODO: do we need to walk the leaf/node tree?
    leaf_faces = bsp.LEAF_FACES[model.first_leaf_face:model.first_leaf_face + model.num_leaf_faces]
    return list(itertools.chain(*[bsp.vertices_of_face(i) for i in leaf_faces]))


# TODO: reverse brush planes from ClipNodes
# -- will likely require a Brush utility class for convex solids & plane -> mesh conversion
# -- that kind of toolset would be handy in general for various .vmf, .map & .bsp tools
# -- probably split the brush tools of vmf_tool into it's own repo & utilise other repos for parsing?


methods = [vertices_of_face, lightmap_of_face, as_lightmapped_obj, parse_vis, vertices_of_model]
