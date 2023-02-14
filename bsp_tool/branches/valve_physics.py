"""PhysicsCollide SpecialLumpClasses"""
# SourceIO/library/source1/phy/phy.py
from __future__ import annotations
import collections
import io
import struct
from typing import List

from . import base


# PhysicsCollide headers
ModelHeader = collections.namedtuple("dphysmodel_t", ["model", "data_size", "script_size", "solid_count"])
# struct dphysmodel_t { int model_index, data_size, keydata_size, solid_count; };
PhysicsObject = collections.namedtuple("PhysicsObject", ["header", "solids", "script"])


class CollideLump(list):
    """[model_index: int, solids: List[bytes], script: bytes]"""
    # passed to VCollideLoad in vphysics.dll
    def __init__(self, raw_lump: bytes) -> List[PhysicsObject]:
        collision_models = list()
        lump = io.BytesIO(raw_lump)
        header = ModelHeader(*struct.unpack("4i", lump.read(16)))
        while header != ModelHeader(-1, -1, 0, 0) and lump.tell() != len(raw_lump):
            start = lump.tell()
            solids = list()
            for i in range(header.solid_count):
                # CPhysCollisionEntry->WriteCollisionBinary
                cb_size = int.from_bytes(lump.read(4), "little")
                solids.append(Block(lump.read(cb_size)))
            assert lump.tell() - start == header.data_size
            script = lump.read(header.script_size)  # ascii
            assert len(script) == header.script_size
            collision_models.append(PhysicsObject(header, solids, script))
            # read next header (sets conditions for the while loop)
            header = ModelHeader(*struct.unpack("4i", lump.read(16)))
        assert header == ModelHeader(-1, -1, 0, 0), "PhysicsCollide ended incorrectly"
        super().__init__(collision_models)  # TODO: this is a terrible interface

    def as_bytes(self) -> bytes:
        def phy_bytes(collision_model):
            header, solids, script = collision_model
            phy_blocks = list()
            for phy_block in solids:
                collision_data = phy_block.as_bytes()
                phy_blocks.append(len(collision_data).to_bytes(4, "little"))
                phy_blocks.append(collision_data)
            phy_block_bytes = b"".join(phy_blocks)
            header = struct.pack("4i", header.model, len(phy_block_bytes), len(script), len(solids))
            return b"".join([header, phy_block_bytes, script])
        tail = struct.pack("4i", -1, -1, 0, 0)  # null header
        return b"".join([*map(phy_bytes, self), tail])


# PhysicsBlock headers
CollideHeader = collections.namedtuple("swapcollideheader_t", ["id", "version", "model_type"])
# struct swapcollideheader_t { int size, vphysicsID; short version, model_type; };
SurfaceHeader = collections.namedtuple("swapcompactsurfaceheader_t", ["size", "drag_axis_areas", "axis_map_size"])
# struct swapcompactsurfaceheader_t { int surfaceSize; Vector dragAxisAreas; int axisMapSize; };
MoppHeader = collections.namedtuple("swapmoppsurfaceheader_t", ["size"])
# struct swapmoppsurfaceheader_t { int moppSize; };
# NOTE: the "swap" in the names refers to the format differing across byte-orders
# -- Source swaps byte order for selected fields when compiled for consoles
# -- PC is primarily little-endian, while the Xbox 360 has more big-endian fields


class Block:
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
            # data_start = lump.tell()
            # NOTE: the tree reads are breaking
            # self.collision_model = CollisionModel.from_stream(lump)
            # lump.seek(data_start)
        elif header.model_type == 1:
            surface_header = MoppHeader(*struct.unpack("i", lump.read(4)))
            # yeah, no idea what this does
        else:
            raise RuntimeError("Invalid model type")
        self.header = (header, surface_header)
        self.data = lump.read(surface_header.size)
        assert lump.tell() == len(raw_lump)

    def as_bytes(self) -> bytes:
        header, surface_header = self.header
        if header.model_type == 0:  # SurfaceHeader (swapcompactsurfaceheader_t)
            size, drag_axis_areas, axis_map_size = surface_header
            surface_header = struct.pack("i3fi", len(self.data), *drag_axis_areas, axis_map_size)
        elif header.model_type == 1:  # MoppHeader (swapmoppsurfaceheader_t)
            surface_header = struct.pack("i", len(self.data))
        else:
            raise RuntimeError("Invalid model type")
        header = struct.pack("4s2h", *header)
        return b"".join([header, surface_header, self.data])


# TODO: create a structure that makes navigating the tree optional
# -- ideally just get all the triangles and make a mesh
# -- however using the tree could be useful for reverse engineering
# TODO: find what isn't mapped by these interwoven structures
# -- a linear read might be possible

# NOTE: the order of class definition matters here, since each contains the previous
class Vertex(base.MappedArray):
    """struct Vertex { float x, y, z, w };"""
    _mapping = [*"xyzw"]
    _format = "4f"
    # appear to be 1/72 vs. expected size (roughly)


class ConvexTriangle(base.MappedArray):
    """struct ConvexTriange { int padding; short edges[3][2]; };"""
    padding: int  # is it really padding? check for non-zeroes
    edges: List[int]  # 3 pairs of indices
    _mapping = {"padding": None, "edges": {"AB": 2, "BC": 2, "CA": 2}}
    _format = "i6h"


class ConvexLeaf(base.MappedArray):
    """struct ConvexLeaf { int vertex_offset, padding[2]; short triangle_count, unused; };"""
    # preceded by b"IDST" (IDSTUDIOHEADER) ?
    # -- src/utils/motionmapper/motionmapper.h
    # -- src/utils/vbsp/staticprop.cpp
    vertex_offset: int  # need to calculate vertex count from triangles
    padding: List[int]  # might have non-zeros?
    triange_count: int  # number of ConvexTriangles in this ConvexLeaf
    unused: int
    _mapping = {"vertex_offset": None, "padding": 2, "triangle_count": None, "unused": None}
    _format = "3i2h"

    # NOTE: must load with .from_stream to get these
    triangles: List[ConvexTriangle]
    vertices: List[Vertex]

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> ConvexLeaf:
        base_offset = stream.tell()
        convex_leaf = super().from_stream(stream)
        convex_leaf.triangles = [ConvexTriangle.from_stream(stream) for i in range(convex_leaf.triangle_count)]
        # NOTE: uncertain if this is the best way to gather vertices
        stream.seek(base_offset + convex_leaf.vertex_offset)
        vertex_count = len({v for tri in convex_leaf.triangles for e in tri.edges for v in e})
        convex_leaf.vertices = [Vertex.from_stream(stream) for i in range(vertex_count)]
        stream.seek(base_offset + struct.calcsize(cls._format))
        return convex_leaf


class TreeNode(base.MappedArray):
    """struct TreeNode { int right_node_offset, convex_leaf_offset; float unknown[5]; };"""
    right_node_offset: int  # has no child nodes if 0
    convex_leaf_offset: int  # index to child ConvexLeaf
    unknown: List[float]
    _mapping = {"right_node_offset": None, "convex_leaf_offset": None, "unknown": 5}
    _format = "2i5f"

    # NOTE: must load with .from_stream(); may only have 1 or the other
    children: (TreeNode, TreeNode)
    leaf: ConvexLeaf

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> TreeNode:
        base_offset = stream.tell()
        tree_node = super().from_stream(stream)
        print(base_offset, tree_node)
        if tree_node.right_node_offset == 0:
            stream.seek(base_offset + tree_node.convex_leaf_offset)
            tree_node.leaf = ConvexLeaf.from_stream(stream)
        else:
            tree_node.children = list()
            tree_node.children.append(TreeNode.from_stream(stream))
            stream.seek(tree_node.right_node_offset)
            tree_node.children.append(TreeNode.from_stream(stream))
        stream.seek(base_offset + struct.calcsize(cls._format))
        return tree_node


class CollisionModel(base.Struct):
    """struct CollisionModel { float unknown[7]; int surface, tree_offset, padding[2]; };"""
    unknown: List[float]
    surface: int  # surface type? matches script?
    tree_offset: int  # index into "IVPS" to where the tree starts
    padding: List[int]  # doesn't look like padding, got some non-zeroes in there
    __slots__ = ["unknown", "surface", "tree_offset", "padding"]
    _format = "7f4i"
    _arrays = {"unknown": 7, "padding": 2}

    tree: TreeNode  # must use .from_stream to get the tree

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> CollisionModel:
        base_offset = stream.tell()
        collision_model = super().from_stream(stream)
        stream.seek(base_offset + collision_model.tree_offset)
        # NOTE: we can't stop a bad tree from reading past the end of the block
        collision_model.tree = TreeNode.from_stream(stream)
        stream.seek(base_offset + struct.calcsize(cls._format))
        return collision_model

    def as_bytes(self) -> bytes:
        # header = super(self, CollisionModel).as_bytes()
        # TODO: handle children
        # b"IVPS"
        # regenerate tree (indexes backwards, prefill?)
        # index tree -> leaves -> tris -> verts
        raise NotImplementedError()

    # TODO: a way to navigate the tree

    def as_obj(self) -> str:
        out = ["# generated from IVPS data with bsp_tool"]
        # TODO: navigate the tree and build each leaf
        # -- vertices and triangles, make each leaf an object? how to communicate lineage?
        raise NotImplementedError()
        return "\n".join(out)


class Displacement(list):
    # TODO: https://github.com/ValveSoftware/source-sdk-2013/blob/master/mp/src/public/builddisp.cpp
    _format = "H"

    def __init__(self, raw_lump: bytes):
        lump_size = len(raw_lump)
        blobs = list()
        buffer = io.BytesIO(raw_lump)
        int_size = struct.calcsize(self._format)

        def read_int() -> int:
            return struct.unpack(self._format, buffer.read(int_size))[0]

        blob_count = read_int()
        blob_sizes = [read_int() for i in range(blob_count)]
        blobs = [buffer.read(s) for s in blob_sizes]
        assert buffer.tell() == lump_size
        return super().__init__(blobs)

    def as_bytes(self) -> bytes:
        out = [len(self)]
        out.extend([len(b) for b in self])
        out = [struct.pack(f"{len(out)}{self._format}", *out)]
        out.extend([b for b in self])
        return b"".join(out)
